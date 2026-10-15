# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.58.0", "pyyaml==6.0.3", "cryptography==44.0.2", "keyring==25.6.0"]
# ///
"""sede.py — navegador con certificado y BLOQUEOS para sedes electrónicas españolas.

Abre Google Chrome (vía Playwright) presentando el certificado del titular SOLO a los
origins oficiales de la sede, y con estas guardas siempre activas:
  - afirma:// (AutoFirma) se captura y se registra; el agente nunca firma.
  - Se bloquean clics/submits sobre elementos de firmar, enviar, presentar, pagar,
    registrar, guardar, comparecer, dar de baja…  ("BLOQUEADO" = ese paso es de la persona).
  - En páginas de notificaciones se bloquea abrir/consultar/descargar (abrir = notificado).
  - Los confirm()/alert() se cancelan; "¿abandonar la página?" se acepta (salir no envía nada).
  - Se abortan peticiones de red a pasarelas de pago y a rutas de presentación/pago/comparecencia.
  - Linux: almacén NSS aislado (el navegador no ve otros certificados del usuario).

Comandos (salida JSON por stdout):
  abrir      --sede ID | --url URL  [--titular ALIAS]      entra y resume la página
  probe      --sede ID | --url URL  [--clic "texto"]...    inventario de campos y botones (sin valores)
  ejecutar   receta.py --sede ID | --url URL [--titular ALIAS]
             La receta recibe: pg, ctx, nav(url), probe(page), captura(nombre), bloqueos(),
             afirma_vistos(), hosts(), redactar(texto), log(...), DIR.
  cert-probe URL...     ¿esa ruta pide certificado de cliente? (sin credenciales; usa curl)
  tls-probe  HOST...    ¿el servidor lo pide en el handshake inicial? (sin credenciales; usa openssl)

Titular: alias configurado con cert.py (por defecto 'ninguno' = sin certificado).
Las capturas y textos crudos se guardan en local (pueden contener datos personales) y nunca se envían.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
sys.path.insert(0, str(AQUI))


def datos_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    d = base / "tramites-es" / "sesiones"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log(*a):
    print("[sede]", *a, file=sys.stderr, flush=True)


# ------------------------------------------------------------------ guardas
DENY_JS = r"""(firmar|firma y env|\benviar\b|\benv[ií]o\b|\bpresentar\b|\bpagar\b|\bpago\b|cargo en cuenta|a[ñn]adir a la cesta|domiciliar|\bregistrar\b|\bguardar\b|\bgrabar\b|comparecer|comparecencia|acceder a la notificaci|abrir (la )?notificaci|aceptar (la )?notificaci|rechazar (la )?notificaci|\bdar(se)? de baja\b|\banular\b|\beliminar\b|\bborrar\b|confirmar (el |la )?(pago|env[ií]o|presentaci|firma|solicitud|cambio|baja)|\btramitar\b|procesoFirma|w_FirmaAEAT|MiniGeneraFirma|firma[A-Za-z_]*\(|enviar[A-Za-z_]*\(|presentar[A-Za-z_]*\(|registrar[A-Za-z_]*\(|guardar[A-Za-z_]*\(|pagar[A-Za-z_]*\(|grabar[A-Za-z_]*\()"""
NOTIF_JS = r"""(acceder|abrir|comparecer|aceptar|rechazar|descargar|consultar|leer|ver (el |la )?(documento|contenido|detalle|notificaci))"""

GUARD_JS = r"""
(() => {
  if (window.__tGuard) return; window.__tGuard = true;
  const DENY = new RegExp(String.raw`%DENY%`, 'i');
  const NOTIF = new RegExp(String.raw`%NOTIF%`, 'i');
  const SAFE_TEXT = /^(buscar|consultar|filtrar|mostrar|listar|ver listado|limpiar|nueva b[uú]squeda)$/i;
  const STRONG = /(firm|present|pag|compare|registr|guard|grab|baja|anul|elimin|borr|domicili)/i;
  const NOTIF_URL = /(notificaci|notification|enotif|buz[oó]n|SINGLE_NOTIF|\/dev\b)/i;  // Gestiona usa /enotifications
  const isNotifPage = () => /dehu\.redsara\.es/i.test(location.host) ||
      NOTIF_URL.test(location.href) || /notificaci|buz[oó]n/i.test(document.title || '');
  const isAuthAction = (a) => /(clave\.gob\.es|pasarela|saml|\/idp|login|auth|sso|IPCE\/Login)/i.test(a || '');
  // Formularios de búsqueda/listado (p. ej. AEAT GNNO-JDIT/SvInteresadosQuery): enviarlos solo filtra un listado.
  const isQueryAction = (a) => /(query|consulta|buscar|busqueda|listado|filtrar)/i.test(a || '') && !DENY.test(a || '');
  // ...siempre que ningún campo del formulario pida acceder/comparecer/abrir/descargar (mismo servlet, otra acción).
  const formPideAbrir = (f) => [...(f.elements || [])].some(e => /(acced|compare|abrir|leer|descarg|ver_?not|detalle)/i.test((e.value || '') + ' ' + (e.name || '')));
  const g = (el, a) => (el && el.getAttribute && el.getAttribute(a)) || '';
  const desc = (el) => [el.innerText || '', el.value || '', g(el, 'aria-label'), g(el, 'title'), el.id || '',
      g(el, 'name'), g(el, 'onclick'), g(el, 'formaction'), g(el, 'href')].join(' | ').replace(/\s+/g, ' ');
  const pureNavLink = (el) => el.tagName === 'A' && /^https?:/i.test(g(el, 'href')) && !g(el, 'onclick');
  const verdict = (el) => {
    if (!el || !el.getAttribute) return null;
    const d = desc(el); const txt = ((el.innerText || el.value || '') + '').trim();
    if (isNotifPage() && NOTIF.test(txt + ' ' + g(el, 'onclick'))) return 'notificación: ' + d;
    if (pureNavLink(el) && !/(pagar|pago|notificaci)/i.test(d)) return null;
    if (SAFE_TEXT.test(txt) && !STRONG.test(txt + ' ' + (el.id || '') + ' ' + g(el, 'name'))) return null;
    return DENY.test(d) ? d : null;
  };
  const note = (why, d) => { try { const o = {why, d: String(d).slice(0, 200), url: location.origin + location.pathname};
      if (window.__tReport) window.__tReport(o); } catch (e) {} };
  const pick = (e) => e.target && e.target.closest ? e.target.closest(
      'button,a,input[type=submit],input[type=button],input[type=image],[role=button],[onclick]') : null;
  for (const ev of ['click', 'dblclick', 'auxclick', 'mousedown', 'mouseup', 'pointerdown', 'pointerup', 'keydown']) {
    window.addEventListener(ev, (e) => {
      if (ev === 'keydown' && !(e.key === 'Enter' || e.key === ' ')) return;
      const v = verdict(ev === 'keydown' ? document.activeElement : pick(e));
      if (v) { e.preventDefault(); e.stopImmediatePropagation(); if (ev === 'click' || ev === 'keydown') note(ev, v); }
    }, true);
  }
  window.addEventListener('submit', (e) => {
    const f = e.target; const v = verdict(e.submitter) || (f && DENY.test(g(f, 'action')) ? 'form ' + g(f, 'action') : null);
    if (v) { e.preventDefault(); e.stopImmediatePropagation(); note('submit', v); }
  }, true);
  const _submit = HTMLFormElement.prototype.submit;
  HTMLFormElement.prototype.submit = function () {
    const a = g(this, 'action');
    if (DENY.test(a) || (isNotifPage() && !isAuthAction(a) && !(isQueryAction(a) && !formPideAbrir(this)))) { note('form.submit', a); return; }
    return _submit.call(this);
  };
  if (HTMLFormElement.prototype.requestSubmit) {
    const _rs = HTMLFormElement.prototype.requestSubmit;
    HTMLFormElement.prototype.requestSubmit = function (s) {
      const v = verdict(s) || (DENY.test(g(this, 'action')) ? g(this, 'action') : null);
      if (v) { note('requestSubmit', v); return; }
      return _rs.call(this, s);
    };
  }
  const grab = (u) => { try { if (typeof u === 'string' && /^afirma:/i.test(u)) { note('afirma', u.slice(0, 120)); return true; } } catch (e) {} return false; };
  const _open = window.open;
  window.open = function (u, ...r) { if (grab(u)) return null; return _open.call(window, u, ...r); };
  try {
    const proto = Object.getPrototypeOf(window.location); const d = Object.getOwnPropertyDescriptor(proto, 'href');
    if (d && d.set) Object.defineProperty(window.location, 'href', { set(v) { if (!grab(v)) d.set.call(window.location, v); },
      get() { return d.get.call(window.location); }, configurable: true });
  } catch (e) {}
  try { const _as = window.location.assign.bind(window.location); window.location.assign = (u) => { if (!grab(u)) _as(u); }; } catch (e) {}
  try { const _re = window.location.replace.bind(window.location); window.location.replace = (u) => { if (!grab(u)) _re(u); }; } catch (e) {}
  const _setAttr = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (n, v) { if (/^(src|href)$/i.test(n) && grab(v)) return; return _setAttr.call(this, n, v); };
  document.addEventListener('click', (e) => { const a = e.target && e.target.closest && e.target.closest('a[href^="afirma:"]');
    if (a) { grab(a.getAttribute('href')); e.preventDefault(); e.stopImmediatePropagation(); } }, true);
})();
""".replace("%DENY%", DENY_JS).replace("%NOTIF%", NOTIF_JS)

PAGO_HOST = re.compile(r"(redsys|pasarelapago|pasarela-pago|pasarela_pago|paycomun|\btpv|ceca\.es|payment|pagos?\.)", re.I)
ACCION_POST = re.compile(r"(firma|presenta[rc]|presbasica|presdirecta|registrar|submit|/registr(ar|o/(alta|nuevo|crear))|/pago|pagar|cargo|nrc|comparec|acuse|enviar|/envio|guardar|grabar|/baja)", re.I)
NOTIF_RED = re.compile(r"(comparec|acuse|aceptaci|rechaz|/document|resguardo|leer|abrir|\bopen\b|voucher|full_detail|appearance)", re.I)  # \b: no casar /opensiac/
NOTIF_PATH = re.compile(r"(notificaci|notification|enotif|buz[oó]n|SINGLE_NOTIF)", re.I)
# URLs que ejecutan una acción con solo cargarlas (caso real: Justicia /redese/clave/solicitarCertificado
# emitió un certificado al abrirla, 15-oct-2026). Se bloquean en cualquier navegación de documento.
ACCION_GET = re.compile(r"(solicitar|emitir|expedir|generar|firmar|presentar|pagar|comparec|registrar|tramitar|/catalog/tw/)", re.I)
# /catalog/tw/ = asistente de tramitación de Gestiona: entrar puede crear un borrador a nombre del titular.
RECETA_PROHIBIDO = re.compile(
    r"(xdotool|autofirma|set_input_files|unroute|remove_listener|__tGuard|__tReport|add_init_script|expose_binding|"
    r"client_certificates|passphrase|para_playwright|cert\.py|\.submit\(|requestSubmit|\.onclick|onclick\(|procesoFirma|"
    r"w_FirmaAEAT|MiniGeneraFirma|firmar[A-Za-z_]*\(|enviar[A-Za-z_]*\(|presentar[A-Za-z_]*\(|\bpagar[A-Za-z_]*\(|"
    r"subprocess|os\.system|__import__|keyring|\.route\(|route_from|\.request\b|\bgetattr\b|\bsetattr\b|\bdelattr\b|eval\(|exec\(|"
    # \b y (?<![\w.]): getAttribute (JS) y re.compile( son legítimos en las recetas de las guías
    r"(?<![\w.])compile\(|globals|locals\(|vars\(|__\w+__|import\s|from\s+\w+\s+import|open\()", re.I)
# Builtins mínimos para las recetas: sin import, open, eval, exec, getattr…
# Las recetas no son un sandbox frente a un agente malicioso (ver SECURITY.md). Sirven para evitar errores
# y para que la vía normal no pueda desactivar las guardas.
_BUILTINS_RECETA = {n: __builtins__[n] if isinstance(__builtins__, dict) else getattr(__builtins__, n) for n in (
    "print", "len", "range", "enumerate", "list", "dict", "set", "tuple", "str", "int", "float", "bool", "min", "max",
    "sorted", "reversed", "any", "all", "zip", "isinstance", "round", "abs", "sum", "Exception", "ValueError",
    "KeyError", "IndexError", "TimeoutError", "RuntimeError")}


# ------------------------------------------------------------------ configuración
def _yaml(path: Path) -> dict:
    import yaml
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def cargar_sedes() -> dict:
    """assets/sedes.yaml + assets/_sedes-*.yaml (estatal, canarias, plataformas…)."""
    sedes: dict = {}
    for p in [ASSETS / "sedes.yaml", *sorted(ASSETS.glob("_sedes-*.yaml"))]:
        sedes.update(_yaml(p).get("sedes", {}) or {})
    return sedes


def dominios_oficiales() -> tuple[tuple[str, ...], set[str]]:
    d = _yaml(ASSETS / "dominios-oficiales.yaml")
    hosts = set(d.get("hosts", []))
    csv_path = ASSETS / "municipios.csv"  # sedes municipales del censo (columna sede_url)
    if csv_path.exists():
        import csv
        with csv_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                # El censo lo genera un rastreador: solo cuentan las sedes identificadas con confianza
                # alta o media y con plataforma conocida. Con "baja", el agente pregunta (regla 6).
                if (row.get("confianza") or "").strip() not in ("alta", "media") or not (row.get("plataforma") or "").strip():
                    continue
                h = urlsplit(row.get("sede_url") or "").hostname
                if h:
                    hosts.add(h.lower())
    return tuple(d.get("sufijos", [])), hosts


def origin_oficial(o: str, sede: dict) -> bool:
    u = urlsplit(o)
    if u.scheme != "https" or not u.hostname:
        return False
    if o in sede.get("origins", []):
        return True
    sufijos, hosts = dominios_oficiales()
    h = u.hostname.lower()
    return h in hosts or ("." + h).endswith(sufijos)


def resolver(a):
    sedes = cargar_sedes()
    sede = sedes.get(a.sede, {}) if a.sede else {}
    if a.sede and not sede:
        raise SystemExit(f"sede '{a.sede}' no está en assets/sedes.yaml (usa buscar.py o --url)")
    url = a.url or sede.get("login")
    if not url:
        raise SystemExit("falta --url o 'login' en la sede")
    origins = list(sede.get("origins", []))
    m = re.match(r"https://[^/]+", url)
    # Solo con --url sin origins declarados: si la sede los declara, el certificado va SOLO a esos
    # (p. ej. dehu.redsara.es no lo pide y presentarlo ahí dio "client-certificate error: ECONNRESET").
    if m and not origins:
        origins.append(m.group(0))
    if a.titular != "ninguno":
        malos = [o for o in origins if not origin_oficial(o, sede)]
        # Defensa en profundidad: con certificado, la URL de partida también tiene que ser oficial,
        # aunque el certificado solo vaya a los origins declarados (un phishing no debe ni abrirse).
        if m and not origin_oficial(m.group(0), sede) and m.group(0) not in malos:
            malos.append(m.group(0))
        if malos:
            raise SystemExit(f"estos dominios no son oficiales según assets/: {malos}. No se presenta el certificado.")
    return (a.sede or urlsplit(url).hostname), sorted(set(origins)), url


# ------------------------------------------------------------------ navegador
class Sesion:
    def __init__(self, nombre: str):
        self.dir = datos_dir() / re.sub(r"[^A-Za-z0-9_.-]", "_", nombre) / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.bloqueos: list[dict] = []
        self.hosts: dict[str, dict] = {}
        self.n = 0

    def host(self, h: str, err: str | None = None):
        e = self.hosts.setdefault(h, {"n": 0, "errores": []})
        e["n"] += 1
        if err and len(e["errores"]) < 5:
            e["errores"].append(err[:120])


def _guarda_red(s: Sesion):
    def guard(route, req):
        u = urlsplit(req.url)
        host, path = u.hostname or "", u.path or ""
        motivo = None
        if u.scheme in ("http", "https"):
            if PAGO_HOST.search(host):
                motivo = "pasarela de pago"
            elif req.method != "GET" and ACCION_POST.search(path):
                motivo = f"{req.method} a ruta de acción"
            elif (req.is_navigation_request() and ACCION_GET.search(path + "?" + (u.query or ""))
                  and not re.search(r"\.(s?html?|pdf)$", path, re.I)):  # páginas informativas sí
                motivo = "URL que ejecuta una acción al abrirla"
            elif (re.search(r"dehu\.redsara\.es", host) or NOTIF_PATH.search(path)) and NOTIF_RED.search(path):
                motivo = "endpoint de notificación"
        if motivo:
            s.bloqueos.append({"why": motivo, "d": f"{req.method} {host}{path[:120]}"})
            log(f"BLOQUEADO ({motivo}): {req.method} {host}{path[:90]}")
            return route.abort("blockedbyclient")
        return route.continue_()
    return guard


def _dialogos(pg):
    def on(d):
        try:
            if d.type == "beforeunload":
                d.accept()
            else:
                log(f"diálogo {d.type} CANCELADO: {d.message[:100]!r}")
                d.dismiss()
        except Exception:
            pass
    pg.on("dialog", on)


def lanzar(p, s: Sesion, titular: str, origins: list[str], inseguro: bool = False):
    kw = {}
    if titular != "ninguno":
        import cert
        c = cert.para_playwright(titular)
        kw["client_certificates"] = [{"origin": o, **c} for o in origins]
        del c
    env = None
    if sys.platform.startswith("linux"):
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            raise SystemExit("no hay pantalla: ejecuta con 'xvfb-run -a uv run scripts/sede.py …' o desde el escritorio")
        casa = s.dir / ".home"  # NSS aislado
        casa.mkdir(exist_ok=True)
        env = {k: v for k, v in os.environ.items() if k not in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME")}
        env["HOME"] = str(casa)
    browser = p.chromium.launch(channel="chrome", headless=False, env=env,
                                args=["--no-first-run", "--no-default-browser-check"])
    ctx = browser.new_context(locale="es-ES", viewport={"width": 1366, "height": 900},
                              accept_downloads=True, ignore_https_errors=inseguro, **kw)
    kw.clear()

    def reportar(_src, o):
        s.bloqueos.append(o)
        log(f"BLOQUEADO en página ({o.get('why')}): {str(o.get('d'))[:90]}")
    ctx.expose_binding("__tReport", reportar)
    ctx.add_init_script(GUARD_JS)
    ctx.route("**/*", _guarda_red(s))
    ctx.on("response", lambda r: s.host(urlsplit(r.url).hostname or ""))
    ctx.on("requestfailed", lambda rq: s.host(urlsplit(rq.url).hostname or "", rq.failure or "failed"))
    ctx.on("page", _dialogos)
    return browser, ctx, ctx.new_page()


def probe(page) -> dict:
    return page.evaluate("""()=>{
      const F=[],B=[],H=[];
      document.querySelectorAll('input,textarea,select').forEach(e=>F.push({tag:e.tagName,type:e.type||'',id:e.id||'',
        name:e.name||'',label:(e.labels&&e.labels[0]&&e.labels[0].innerText||'').slice(0,60),oculto:!(e.offsetParent)||e.type==='hidden',
        obligatorio:!!e.required,opciones:e.tagName==='SELECT'?[...e.options].slice(0,15).map(o=>o.text.slice(0,40)):undefined}));
      document.querySelectorAll('button,a,input[type=submit],input[type=button],[role=button]').forEach(e=>{
        const t=(e.innerText||e.value||'').trim().replace(/\\s+/g,' ');const oc=e.getAttribute('onclick');
        if(t||oc) B.push({texto:t.slice(0,70),onclick:(oc||'').slice(0,90),href:(e.getAttribute('href')||'').replace(/\\?.*/,'?…').slice(0,120)});});
      document.querySelectorAll('h1,h2,h3,h4,legend,label,th').forEach(e=>{const t=(e.innerText||'').replace(/\\s+/g,' ').trim();if(t&&t.length<90)H.push(t);});
      return {titulo:document.title,url:location.origin+location.pathname,campos:F,botones:B.slice(0,250),
              encabezados:[...new Set(H)].slice(0,120)};
    }""")


def redactar(t: str, extra=()) -> str:
    t = re.sub(r"(?<![A-Za-z])[XYZ]\d{7}[A-Z]\b", "<NIE>", t)   # sin \b inicial: la TGSS antepone "6-0"
    t = re.sub(r"(?<![A-Za-z])\d{8}[A-Z]\b", "<NIF>", t)
    t = re.sub(r"\b[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]\b", "<CIF>", t)
    t = re.sub(r"\bES\d{2}(?:\s?\d{4}){5}\b", "<IBAN>", t)
    t = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "<EMAIL>", t)
    t = re.sub(r"\b[6789]\d{2}\s?\d{3}\s?\d{3}\b", "<TEL>", t)
    # Domicilios (p. ej. la columna "Tributo / Referencia" de STA): tipo de vía + nombre + número
    t = re.sub(r"\b(?:CALLE|C/|CL\.?|AVDA\.?|AVENIDA|PLAZA|PZA\.?|CTRA\.?|CARRETERA|CAMINO|PASEO|TRAVES[IÍ]A|URB\.?|"
               r"URBANIZACI[OÓ]N|RAMBLA|RONDA|PASAJE|GLORIETA)\s[^\n|\x22]{1,60}?\d+[^\s|\x22]*(?:\s[A-Z]{0,2}-?\d[^\s|\x22]*)?", "<DOMICILIO>", t, flags=re.I)
    for x in sorted({x for x in (list(extra) + list(_IDENTIDAD)) if x and len(x) >= 3}, key=len, reverse=True):
        t = re.sub(r"\b" + re.escape(x) + r"\b", "<TITULAR>", t, flags=re.I)
    return re.sub(r"<TITULAR>(?:[\s,]+<TITULAR>)+", "<TITULAR>", t)


_IDENTIDAD: list[str] = []   # nombre, apellidos y NIF del titular (solo en memoria; los rellena _sesion)


def _sesion(a, cuerpo) -> int:
    from playwright.sync_api import sync_playwright
    nombre, origins, url = resolver(a)
    if a.titular != "ninguno":
        import cert
        _IDENTIDAD[:] = cert.para_redactar(a.titular)
    s = Sesion(nombre)
    res = {"sede": nombre, "titular": a.titular, "origins_con_certificado": origins if a.titular != "ninguno" else []}
    with sync_playwright() as p:
        browser, ctx, pg = lanzar(p, s, a.titular, origins, a.inseguro)

        def captura(nombre_c, page=None):
            page = page or pg
            s.n += 1
            base = s.dir / f"{s.n:02d}-{re.sub(r'[^A-Za-z0-9_-]', '_', nombre_c)[:40]}"
            try:
                page.screenshot(path=str(base) + ".png", full_page=True)
                (Path(str(base) + ".txt")).write_text(page.url + "\n\n" + page.inner_text("body"), encoding="utf-8")
            except Exception as ex:
                log("captura incompleta:", type(ex).__name__)
            return str(base)

        def nav(u, page=None, espera=2500):
            page = page or pg
            time.sleep(1.5)
            page.goto(u, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(espera)
            return page

        h = dict(pg=pg, page=pg, ctx=ctx, nav=nav, probe=probe, captura=captura, redactar=redactar, log=log,
                 bloqueos=lambda: list(s.bloqueos), afirma_vistos=lambda: [b["d"] for b in s.bloqueos if b.get("why") == "afirma"],
                 hosts=lambda: s.hosts, DIR=str(s.dir), time=time, re=re, json=json)
        try:
            nav(url)
            res.update(cuerpo(h) or {})
        except Exception as ex:
            res["error"] = f"{type(ex).__name__}: {str(ex)[:300]}"
            try:
                captura("error")
            except Exception:
                pass
        finally:
            res["url_final"] = re.sub(r"\?.*", "?…", pg.url) if not pg.is_closed() else None
            res["bloqueos"] = s.bloqueos
            res["hosts_con_error"] = {k: v["errores"] for k, v in s.hosts.items() if v["errores"]}
            res["capturas_locales"] = str(s.dir)
            try:
                ctx.close()
                browser.close()
            except Exception:
                pass
    salida = json.dumps(res, ensure_ascii=False, indent=1)
    if getattr(a, "json", None):
        Path(a.json).write_text(salida, encoding="utf-8")
    print(salida)
    return 1 if "error" in res else 0


def cmd_abrir(a) -> int:
    def cuerpo(h):
        base = h["captura"]("abrir")
        txt = Path(base + ".txt").read_text(encoding="utf-8") if Path(base + ".txt").exists() else ""
        # Con titular: también cuenta como sesión que el nombre o el NIF del certificado salgan en la página
        # (la AEAT no muestra "salir" ni "mis datos" en el cuerpo de MdcAcceso).
        ident = any(re.search(r"\b" + re.escape(x) + r"\b", txt, re.I) for x in _IDENTIDAD if len(x) >= 5)
        return {"titulo": h["pg"].title()[:120],
                "sesion_iniciada": ident or bool(re.search(r"(cerrar sesi|desconectar|salir|mis datos|bienvenid)", txt, re.I)),
                # 600 caracteres no llegaban al resultado (Granadilla: "No tiene recibos pendientes." iba más abajo)
                "texto_inicio": redactar(" ".join(txt.split())[:3000])}
    return _sesion(a, cuerpo)


def cmd_probe(a) -> int:
    def cuerpo(h):
        for t in (a.clic or []):
            h["pg"].get_by_text(t, exact=False).first.click(timeout=10000)
            h["pg"].wait_for_timeout(3500)
        h["captura"]("probe")
        return {"probe": probe(h["pg"])}
    return _sesion(a, cuerpo)


def cmd_ejecutar(a) -> int:
    src = Path(a.receta).read_text(encoding="utf-8")
    m = RECETA_PROHIBIDO.search(src)
    if m:
        salida = json.dumps({"error": f"receta rechazada por las guardas: contiene '{m.group(0)}'"}, ensure_ascii=False)
        if getattr(a, "json", None):
            Path(a.json).write_text(salida, encoding="utf-8")
        print(salida)
        return 2

    def cuerpo(h):
        scope = dict(h)
        scope.pop("ctx", None)  # sin acceso directo al contexto (rutas, peticiones); para popups: pg.context.pages
        scope["__builtins__"] = _BUILTINS_RECETA
        exec(compile(src, a.receta, "exec"), scope)
        # Defensa en profundidad (regla 8): el RESULTADO pasa siempre por redactar(), lo haga o no la receta.
        bruto = json.dumps(scope.get("RESULTADO"), ensure_ascii=False, default=str)
        return {"resultado": json.loads(redactar(bruto))}
    return _sesion(a, cuerpo)


def cmd_cert_probe(a) -> int:
    curl = shutil.which("curl")
    res = []
    for url in a.urls:
        if not curl:
            res.append({"url": url, "error": "curl no disponible"})
            continue
        r = subprocess.run([curl, "-sv", "--max-time", "25", "-o", os.devnull, url], capture_output=True, timeout=40)
        err = r.stderr.decode("utf-8", "replace")
        st = re.findall(r"< HTTP/[\d.]+ (\d{3})", err)
        res.append({"url": url.split("?")[0], "pide_certificado": bool(re.search(r"Request CERT", err)),
                    "http": st[-1] if st else None,
                    "nota": None if "Request CERT" in err or sys.platform != "win32" else "en Windows (Schannel) la detección no es fiable"})
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


def cmd_tls_probe(a) -> int:
    ossl = shutil.which("openssl")
    res = []
    for host in a.hosts:
        if not ossl:
            res.append({"host": host, "error": "openssl no disponible"})
            continue
        out = subprocess.run([ossl, "s_client", "-connect", f"{host}:443", "-servername", host],
                             input=b"", capture_output=True, timeout=15).stdout.decode("utf-8", "replace")
        res.append({"host": host, "pide_en_handshake": "Acceptable client certificate CA names" in out
                    or "Client Certificate Types" in out})
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    os.environ.setdefault("NODE_NO_WARNINGS", "1")  # el DeprecationWarning de Node ensuciaba el JSON de stdout
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def comun(sp):
        sp.add_argument("--sede")
        sp.add_argument("--url")
        sp.add_argument("--titular", default="ninguno", help="alias de cert.py (por defecto: ninguno)")
        sp.add_argument("--inseguro", action="store_true", help="ignorar errores TLS del servidor (explica por qué)")
        sp.add_argument("--json", help="escribe también el resultado JSON en este fichero (xvfb-run mezcla stderr y stdout)")
    comun(sub.add_parser("abrir"))
    sp = sub.add_parser("probe")
    comun(sp)
    sp.add_argument("--clic", action="append")
    se = sub.add_parser("ejecutar")
    se.add_argument("receta")
    comun(se)
    cp = sub.add_parser("cert-probe")
    cp.add_argument("urls", nargs="+")
    tp = sub.add_parser("tls-probe")
    tp.add_argument("hosts", nargs="+")
    a = ap.parse_args()
    return {"abrir": cmd_abrir, "probe": cmd_probe, "ejecutar": cmd_ejecutar,
            "cert-probe": cmd_cert_probe, "tls-probe": cmd_tls_probe}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
