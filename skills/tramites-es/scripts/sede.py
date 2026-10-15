# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.58.0", "pyyaml==6.0.3", "cryptography==44.0.2", "keyring==25.6.0"]
# ///
"""sede.py — navegador con certificado para sedes electrónicas españolas, con PERMISOS por acto.

Abre Google Chrome (vía Playwright) presentando el certificado del titular SOLO a los
origins oficiales de la sede. Los actos con efectos están agrupados en permisos:

  generar        pedir certificados, informes o documentos (una URL de "solicitar" ya los emite)
  firmar         firmar (AutoFirma, firma JS de la AEAT, MiniApplet)
  presentar      enviar, presentar, registrar, tramitar, guardar borradores, adjuntar ficheros
  pagar          pagar, cargo en cuenta, carta de pago, pasarelas de pago
  comparecer     abrir/descargar notificaciones (abrir = notificado, empiezan los plazos)
  cambiar_datos  domiciliar, dar de baja, anular, borrar, cambiar datos
  cita           reservar o confirmar una cita previa

Los permisos los decide la PERSONA usuaria, no este skill:
  - en su fichero de permisos (scripts/permisos.py), por ejemplo `permitir: todo`, o
  - el agente, con `--permitir firmar,presentar` cuando su usuario se lo ha autorizado.
Lo que no está permitido se bloquea y sale como "BLOQUEADO (requiere permiso 'x')": el agente
pregunta a su usuario y, si le autoriza, repite con --permitir.

Siempre activo (protege al usuario sin pararle): certificado solo a dominios oficiales, almacén
NSS aislado en Linux, "¿abandonar la página?" aceptado, redacción de datos personales en la salida.

Comandos (salida JSON por stdout):
  abrir      --sede ID | --url URL  [--titular ALIAS] [--permitir …]
  probe      --sede ID | --url URL  [--clic "texto"]...
  ejecutar   receta.py --sede ID | --url URL [--titular ALIAS] [--permitir …]
             La receta recibe: pg, nav(url), probe(page), captura(nombre), bloqueos(),
             afirma_vistos(), hosts(), redactar(texto), log(...), DIR, PERMISOS.
  cert-probe URL...     ¿esa ruta pide certificado de cliente? (sin credenciales; usa curl)
  tls-probe  HOST...    ¿el servidor lo pide en el handshake inicial? (sin credenciales; usa openssl)

AutoFirma (con permiso 'firmar'): las URI afirma:// se pasan al AutoFirma instalado en el equipo.
Su diálogo de certificado lo atiende la persona; en Linux sin escritorio, `--autofirma-auto N`
elige el certificado N (0 = el primero de su lista) con xdotool (experimental).

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
import threading
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


# ------------------------------------------------------------------ permisos y actos
ACTOS = ("generar", "firmar", "presentar", "pagar", "comparecer", "cambiar_datos", "cita")

# Guarda de página: texto/atributos de botones y enlaces que ejecutan cada acto.
JS_ACTO = {
    "firmar": r"firmar|firma y env|procesoFirma|w_FirmaAEAT|MiniGeneraFirma|confirmar (el |la )?firma|firma[A-Za-z_]*\(",
    "presentar": (r"\benviar\b|\benv[ií]o\b|\bpresentar\b|\bregistrar\b|\bguardar\b|\bgrabar\b|\btramitar\b|"
                  r"confirmar (el |la )?(env[ií]o|presentaci|solicitud)|enviar[A-Za-z_]*\(|presentar[A-Za-z_]*\(|"
                  r"registrar[A-Za-z_]*\(|guardar[A-Za-z_]*\(|grabar[A-Za-z_]*\("),
    "pagar": r"\bpagar\b|\bpago\b|cargo en cuenta|a[ñn]adir a la cesta|confirmar (el |la )?pago|pagar[A-Za-z_]*\(",
    "comparecer": (r"comparecer|comparecencia|acceder a la notificaci|abrir (la )?notificaci|"
                   r"aceptar (la )?notificaci|rechazar (la )?notificaci"),
    "cambiar_datos": r"domiciliar|\bdar(se)? de baja\b|\banular\b|\beliminar\b|\bborrar\b|confirmar (el |la )?(cambio|baja)",
    "cita": r"reservar (la |una )?cita|confirmar (la )?cita|\breservar\b",
}
DENY_JS = "(" + "|".join(JS_ACTO.values()) + ")"   # todos los actos (sin permisos)
NOTIF_JS = r"""(acceder|abrir|comparecer|aceptar|rechazar|descargar|consultar|leer|ver (el |la )?(documento|contenido|detalle|notificaci))"""
# Páginas de cita previa: el botón final suele ser un "Confirmar" a secas (AEAT, DGT, ICP), que fuera
# de ellas no es un acto. URL (sin casar "solicitar"/"solicitante") y botón, con sintaxis válida en JS y en Python.
CITA_URL_JS = r"(cita[-_+ ]*previa|\bcitas?\b|icpplus|CITE_CONSULTA|TOCP-MUTE)"
CITA_BOTON_JS = r"^\s*confirmar\b"

# Guarda de red, por acto.
RED_POST = {
    "firmar": r"firma",
    "presentar": r"presenta[rc]|presbasica|presdirecta|registrar|submit|/registr(ar|o/(alta|nuevo|crear))|enviar|/envio|guardar|grabar",
    "pagar": r"/pago|pagar|cargo|nrc",
    "comparecer": r"comparec|acuse",
    "cambiar_datos": r"/baja",
}
# Navegaciones de documento que ejecutan el acto con solo abrirlas (caso real: Justicia
# /redese/clave/solicitarCertificado emitió un certificado al abrirla, 15-oct-2026).
RED_GET = {
    "generar": r"solicitar|emitir|expedir|generar",
    "firmar": r"firmar",
    "presentar": r"presentar|registrar|tramitar|/catalog/tw/",   # /catalog/tw/ (Gestiona) puede crear un borrador
    "pagar": r"pagar",
    "comparecer": r"comparec",
}
RED_POST_RX = {k: re.compile(v, re.I) for k, v in RED_POST.items()}
RED_GET_RX = {k: re.compile(v, re.I) for k, v in RED_GET.items()}
PAGO_HOST = re.compile(r"(redsys|pasarelapago|pasarela-pago|pasarela_pago|paycomun|\btpv|ceca\.es|payment|pagos?\.)", re.I)
NOTIF_RED = re.compile(r"(comparec|acuse|aceptaci|rechaz|/document|resguardo|leer|abrir|\bopen\b|voucher|full_detail|appearance)", re.I)  # \b: no casar /opensiac/
NOTIF_PATH = re.compile(r"(notificaci|notification|enotif|buz[oó]n|SINGLE_NOTIF)", re.I)
ACCION_POST = re.compile("(" + "|".join(RED_POST.values()) + ")", re.I)   # todos los actos
ACCION_GET = re.compile("(" + "|".join(RED_GET.values()) + ")", re.I)

# Recetas: lo que nunca pueden hacer (manipular las guardas, tocar secretos, salir del sandbox)…
RECETA_SIEMPRE = (
    r"xdotool|autofirma|unroute|remove_listener|__tGuard|__tReport|__tAfirma|add_init_script|expose_binding|"
    r"client_certificates|passphrase|para_playwright|cert\.py|subprocess|os\.system|__import__|keyring|\.route\(|route_from|"
    r"\.request\b|\bgetattr\b|\bsetattr\b|\bdelattr\b|eval\(|exec\(|"
    # \b y (?<![\w.]): getAttribute (JS) y re.compile( son legítimos en las recetas de las guías
    r"(?<![\w.])compile\(|globals|locals\(|vars\(|__\w+__|import\s|from\s+\w+\s+import|open\(")
# …y lo que solo pueden hacer con el permiso del acto.
RECETA_ACTO = {
    "firmar": r"procesoFirma|w_FirmaAEAT|MiniGeneraFirma|firmar[A-Za-z_]*\(",
    "presentar": r"set_input_files|\.submit\(|requestSubmit|\.onclick|onclick\(|enviar[A-Za-z_]*\(|presentar[A-Za-z_]*\(",
    "pagar": r"\bpagar[A-Za-z_]*\(",
}
RECETA_SIEMPRE_RX = re.compile("(" + RECETA_SIEMPRE + ")", re.I)
RECETA_PROHIBIDO = re.compile("(" + RECETA_SIEMPRE + "|" + "|".join(RECETA_ACTO.values()) + ")", re.I)  # sin permisos


def receta_prohibida(src: str, permitidos: set[str]) -> str | None:
    """Devuelve el motivo si la receta no puede ejecutarse con estos permisos."""
    m = RECETA_SIEMPRE_RX.search(src)
    if m:
        return f"contiene '{m.group(0)}'"
    for acto, rx in RECETA_ACTO.items():
        if acto not in permitidos:
            m = re.search(rx, src, re.I)
            if m:
                return f"contiene '{m.group(0)}' (requiere permiso '{acto}')"
    return None


# Builtins mínimos para las recetas: sin import, open, eval, exec, getattr…
# Las recetas no son un sandbox frente a un agente malicioso (ver SECURITY.md). Sirven para que la vía
# normal no pueda desactivar las guardas ni tocar secretos.
_BUILTINS_RECETA = {n: __builtins__[n] if isinstance(__builtins__, dict) else getattr(__builtins__, n) for n in (
    "print", "len", "range", "enumerate", "list", "dict", "set", "tuple", "str", "int", "float", "bool", "min", "max",
    "sorted", "reversed", "any", "all", "zip", "isinstance", "round", "abs", "sum", "Exception", "ValueError",
    "KeyError", "IndexError", "TimeoutError", "RuntimeError")}


def _normalizar_permisos(v, origen: str) -> set[str]:
    if v in (None, "", []):
        return set()
    if isinstance(v, str):
        v = [x for x in re.split(r"[,\s]+", v) if x]
    vals = [str(x).strip().lower() for x in v]
    if "todo" in vals:
        return set(ACTOS)
    malos = [x for x in vals if x not in ACTOS]
    if malos:
        raise SystemExit(f"permisos desconocidos en {origen}: {malos}. Válidos: {', '.join(ACTOS)} o 'todo'")
    return set(vals)


def permisos_usuario() -> set[str]:
    """Permisos que la persona dejó configurados para su agente (scripts/permisos.py)."""
    try:
        import permisos as _p
        return _normalizar_permisos(_p.leer().get("permitir"), str(_p.FICHERO))
    except SystemExit:
        raise
    except Exception:
        return set()


def permisos(a) -> set[str]:
    return permisos_usuario() | _normalizar_permisos(getattr(a, "permitir", None), "--permitir")


def construir_guard(permitidos: set[str]) -> str:
    bloq = [[acto, rx] for acto, rx in JS_ACTO.items() if acto not in permitidos]
    return (GUARD_JS.replace("%BLOQ%", json.dumps(bloq))
            .replace("%NOTIF_ON%", "false" if "comparecer" in permitidos else "true")
            .replace("%AF_BLOQ%", "false" if "firmar" in permitidos else "true")
            .replace("%CITA_ON%", "false" if "cita" in permitidos else "true")
            .replace("%CITA_URL%", CITA_URL_JS)
            .replace("%CITA_BOTON%", CITA_BOTON_JS)
            .replace("%NOTIF%", NOTIF_JS))


GUARD_JS = r"""
(() => {
  if (window.__tGuard) return; window.__tGuard = true;
  const BLOQ = %BLOQ%.map(([c, r]) => [c, new RegExp(r, 'i')]);
  const quien = (d) => { for (const [c, rx] of BLOQ) if (rx.test(d || '')) return c; return null; };
  const NOTIF_ON = %NOTIF_ON%;
  const AF_BLOQ = %AF_BLOQ%;
  const NOTIF = new RegExp(String.raw`%NOTIF%`, 'i');
  const CITA_ON = %CITA_ON%;
  const CITA_URL = new RegExp(String.raw`%CITA_URL%`, 'i');
  const CITA_BOTON = new RegExp(String.raw`%CITA_BOTON%`, 'i');
  const isCitaPage = () => CITA_URL.test(location.href) || /\bcitas?\b|cita previa/i.test(document.title || '');
  const SAFE_TEXT = /^(buscar|consultar|filtrar|mostrar|listar|ver listado|limpiar|nueva b[uú]squeda)$/i;
  const STRONG = /(firm|present|pag|compare|registr|guard|grab|baja|anul|elimin|borr|domicili)/i;
  const NOTIF_URL = /(notificaci|notification|enotif|buz[oó]n|SINGLE_NOTIF|\/dev\b)/i;  // Gestiona usa /enotifications
  const isNotifPage = () => /dehu\.redsara\.es/i.test(location.host) ||
      NOTIF_URL.test(location.href) || /notificaci|buz[oó]n/i.test(document.title || '');
  const isAuthAction = (a) => /(clave\.gob\.es|pasarela|saml|\/idp|login|auth|sso|IPCE\/Login)/i.test(a || '');
  // Formularios de búsqueda/listado (p. ej. AEAT GNNO-JDIT/SvInteresadosQuery): enviarlos solo filtra un listado…
  const isQueryAction = (a) => /(query|consulta|buscar|busqueda|listado|filtrar)/i.test(a || '') && !quien(a || '');
  // …siempre que ningún campo del formulario pida acceder/comparecer/abrir/descargar (mismo servlet, otra acción).
  const formPideAbrir = (f) => [...(f.elements || [])].some(e => /(acced|compare|abrir|leer|descarg|ver_?not|detalle)/i.test((e.value || '') + ' ' + (e.name || '')));
  const g = (el, a) => (el && el.getAttribute && el.getAttribute(a)) || '';
  const desc = (el) => [el.innerText || '', el.value || '', g(el, 'aria-label'), g(el, 'title'), el.id || '',
      g(el, 'name'), g(el, 'onclick'), g(el, 'formaction'), g(el, 'href')].join(' | ').replace(/\s+/g, ' ');
  const pureNavLink = (el) => el.tagName === 'A' && /^https?:/i.test(g(el, 'href')) && !g(el, 'onclick');
  const verdict = (el) => {   // -> [acto, descripción] o null
    if (!el || !el.getAttribute) return null;
    const d = desc(el); const txt = ((el.innerText || el.value || '') + '').trim();
    if (NOTIF_ON && isNotifPage() && NOTIF.test(txt + ' ' + g(el, 'onclick'))) return ['comparecer', 'notificación: ' + d];
    if (CITA_ON && isCitaPage() && CITA_BOTON.test(txt)) return ['cita', 'cita previa: ' + d];
    if (pureNavLink(el) && !/(pagar|pago|notificaci)/i.test(d)) return null;
    if (SAFE_TEXT.test(txt) && !STRONG.test(txt + ' ' + (el.id || '') + ' ' + g(el, 'name'))) return null;
    const c = quien(d);
    return c ? [c, d] : null;
  };
  const note = (ev, v) => { try { const o = {why: ev + " (requiere permiso '" + v[0] + "')", permiso: v[0],
      d: String(v[1]).slice(0, 200), url: location.origin + location.pathname};
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
    const f = e.target; const ca = f && quien(g(f, 'action'));
    const v = verdict(e.submitter) || (ca ? [ca, 'form ' + g(f, 'action')] : null);
    if (v) { e.preventDefault(); e.stopImmediatePropagation(); note('submit', v); }
  }, true);
  const _submit = HTMLFormElement.prototype.submit;
  HTMLFormElement.prototype.submit = function () {
    const a = g(this, 'action');
    const c = quien(a) || ((NOTIF_ON && isNotifPage() && !isAuthAction(a) && !(isQueryAction(a) && !formPideAbrir(this))) ? 'comparecer' : null);
    if (c) { note('form.submit', [c, a]); return; }
    return _submit.call(this);
  };
  if (HTMLFormElement.prototype.requestSubmit) {
    const _rs = HTMLFormElement.prototype.requestSubmit;
    HTMLFormElement.prototype.requestSubmit = function (s) {
      const ca = quien(g(this, 'action'));
      const v = verdict(s) || (ca ? [ca, g(this, 'action')] : null);
      if (v) { note('requestSubmit', v); return; }
      return _rs.call(this, s);
    };
  }
  // afirma:// — sin permiso 'firmar' se bloquea; con permiso se pasa al AutoFirma del equipo (Python).
  const grab = (u) => { try { if (typeof u === 'string' && /^afirma:/i.test(u)) {
      if (AF_BLOQ) note('afirma', ['firmar', u.slice(0, 120)]); else if (window.__tAfirma) window.__tAfirma(u);
      return true; } } catch (e) {} return false; };
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
"""


# ------------------------------------------------------------------ configuración
def _yaml(path: Path) -> dict:
    import yaml
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def cargar_sedes() -> dict:
    """assets/_sedes-*.yaml (estatal, canarias, plataformas…) y, si existe, assets/sedes.yaml (sedes locales)."""
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
                # alta o media y con plataforma conocida. Con "baja", el agente pregunta.
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
        raise SystemExit(f"sede '{a.sede}' no está en assets/_sedes-*.yaml (usa buscar.py o --url)")
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


# ------------------------------------------------------------------ AutoFirma
def _autofirma_cmd() -> list[str] | None:
    if sys.platform == "win32":
        for base in (os.environ.get("PROGRAMFILES", ""), os.environ.get("PROGRAMFILES(X86)", "")):
            for rel in ("AutoFirma/AutoFirma/AutoFirma.exe", "Autofirma/Autofirma/Autofirma.exe"):
                p = Path(base) / rel
                if base and p.exists():
                    return [str(p)]
        return None
    if sys.platform == "darwin":
        return ["open"] if any(Path(f"/Applications/{n}.app").exists() for n in ("AutoFirma", "Autofirma")) else None
    exe = shutil.which("autofirma") or shutil.which("AutoFirma")
    return [exe] if exe else None


def _ventanas_autofirma() -> list[str]:
    """Ids X11 SOLO de ventanas de AutoFirma (clase Java). Filtrar por clase es obligatorio: un filtro por
    título llegó a teclear en la terminal de su usuario porque su título contenía 'certificados'."""
    out = []
    try:
        ids = subprocess.run(["xdotool", "search", "--onlyvisible", "--class", "."],
                             capture_output=True, text=True, timeout=10).stdout.split()
    except Exception:
        return out
    for w in ids[:80]:
        try:
            cls = subprocess.run(["xprop", "-id", w, "WM_CLASS"], capture_output=True, text=True, timeout=3).stdout.lower()
            nombre = subprocess.run(["xdotool", "getwindowname", w], capture_output=True, text=True, timeout=3).stdout.lower()
        except Exception:
            continue
        if re.search(r"terminal|chrome|firefox|code", cls):
            continue
        if re.search(r"autofirma|sun-awt", cls) or ("almac" in nombre and "nss" in nombre):
            out.append(w)
    return out


def _autofirma_dialogo(indice: int, tmax: int = 60):
    """Experimental (Linux X11 + xdotool): en el diálogo "Seleccione un certificado" de AutoFirma pulsa la
    fila `indice` y "Aceptar". Geometría relativa observada en AutoFirma 1.9."""
    vistos: set[str] = set()
    for _ in range(tmax):
        for w in _ventanas_autofirma():
            if w in vistos:
                continue
            vistos.add(w)
            try:
                subprocess.run(["xdotool", "windowactivate", "--sync", w], timeout=5, capture_output=True)
                time.sleep(0.6)
                g = subprocess.run(["xdotool", "getwindowgeometry", "--shell", w], capture_output=True, text=True, timeout=5).stdout
                mw, mh = re.search(r"WIDTH=(\d+)", g), re.search(r"HEIGHT=(\d+)", g)
                if not (mw and mh):
                    continue
                W, H = int(mw.group(1)), int(mh.group(1))
                subprocess.run(["xdotool", "mousemove", "--window", w, str(int(W * 0.5)), str(int(H * (0.44 + 0.22 * indice))), "click", "1"])
                time.sleep(0.5)
                subprocess.run(["xdotool", "mousemove", "--window", w, str(int(W * 0.87)), str(int(H * 0.89)), "click", "1"])
                log(f"AutoFirma: certificado #{indice} + Aceptar")
            except Exception as ex:
                log("AutoFirma: diálogo no accionable:", type(ex).__name__)
        time.sleep(1)


def lanzar_autofirma(uri: str, s: "Sesion", auto: int | None):
    cmd = _autofirma_cmd()
    if not cmd:
        s.afirma.append({"estado": "AutoFirma no instalado", "operacion": uri[:40]})
        log("firma pedida pero AutoFirma no está instalado (references/setup-autofirma.md)")
        return
    try:
        # Entorno real (HOME real): AutoFirma usa el almacén de certificados del sistema.
        subprocess.Popen(cmd + [uri], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        s.afirma.append({"estado": "lanzado", "operacion": uri[:40]})
        log("AutoFirma lanzado: hay que elegir el certificado en su diálogo")
        if auto is not None and sys.platform.startswith("linux") and shutil.which("xdotool"):
            threading.Thread(target=_autofirma_dialogo, args=(auto,), daemon=True).start()
    except Exception as ex:
        s.afirma.append({"estado": f"error {type(ex).__name__}"})


# ------------------------------------------------------------------ navegador
class Sesion:
    def __init__(self, nombre: str):
        self.dir = datos_dir() / re.sub(r"[^A-Za-z0-9_.-]", "_", nombre) / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.bloqueos: list[dict] = []
        self.afirma: list[dict] = []
        self.hosts: dict[str, dict] = {}
        self.n = 0

    def host(self, h: str, err: str | None = None):
        e = self.hosts.setdefault(h, {"n": 0, "errores": []})
        e["n"] += 1
        if err and len(e["errores"]) < 5:
            e["errores"].append(err[:120])


def acto_de_peticion(method: str, url: str, navegacion: bool, permitidos: set[str]) -> tuple[str, str] | None:
    """(acto, motivo) si la petición ejecuta un acto NO permitido; None si puede seguir."""
    u = urlsplit(url)
    host, path = u.hostname or "", u.path or ""
    if u.scheme not in ("http", "https"):
        return None
    if "pagar" not in permitidos and PAGO_HOST.search(host):
        return "pagar", "pasarela de pago"
    if method != "GET":
        for acto, rx in RED_POST_RX.items():
            if acto not in permitidos and rx.search(path):
                return acto, f"{method} a ruta de acción"
    if navegacion and not re.search(r"\.(s?html?|pdf)$", path, re.I):  # páginas informativas sí
        q = path + "?" + (u.query or "")
        for acto, rx in RED_GET_RX.items():
            if acto not in permitidos and rx.search(q):
                return acto, "URL que ejecuta una acción al abrirla"
    if "comparecer" not in permitidos and (re.search(r"dehu\.redsara\.es", host) or NOTIF_PATH.search(path)) and NOTIF_RED.search(path):
        return "comparecer", "endpoint de notificación"
    return None


def _guarda_red(s: Sesion, permitidos: set[str] | None = None):
    permitidos = permitidos or set()

    def guard(route, req):
        r = acto_de_peticion(req.method, req.url, req.is_navigation_request(), permitidos)
        if r:
            acto, motivo = r
            u = urlsplit(req.url)
            s.bloqueos.append({"why": f"{motivo} (requiere permiso '{acto}')", "permiso": acto,
                               "d": f"{req.method} {u.hostname}{(u.path or '')[:120]}"})
            log(f"BLOQUEADO ({motivo}; requiere permiso '{acto}'): {req.method} {u.hostname}{(u.path or '')[:90]}")
            return route.abort("blockedbyclient")
        return route.continue_()
    return guard


def _dialogos(pg, permitidos: set[str]):
    bloq = [re.compile(rx, re.I) for acto, rx in JS_ACTO.items() if acto not in permitidos]
    con_actos = bool(permitidos - {"generar"})

    def on(d):
        try:
            if d.type == "beforeunload":
                d.accept()
            elif d.type == "confirm" and con_actos and not any(rx.search(d.message or "") for rx in bloq):
                # El agente pulsó un acto permitido y la sede pide confirmación: se acepta.
                log(f"confirmación ACEPTADA (acto permitido): {d.message[:100]!r}")
                d.accept()
            else:
                log(f"diálogo {d.type} CANCELADO: {d.message[:100]!r}")
                d.dismiss()
        except Exception:
            pass
    pg.on("dialog", on)


def lanzar(p, s: Sesion, titular: str, origins: list[str], inseguro: bool = False,
           permitidos: set[str] | None = None, auto: int | None = None):
    permitidos = permitidos or set()
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
    ctx.expose_binding("__tAfirma", lambda _src, uri: lanzar_autofirma(str(uri), s, auto))
    ctx.add_init_script(construir_guard(permitidos))
    ctx.route("**/*", _guarda_red(s, permitidos))
    ctx.on("response", lambda r: s.host(urlsplit(r.url).hostname or ""))
    ctx.on("requestfailed", lambda rq: s.host(urlsplit(rq.url).hostname or "", rq.failure or "failed"))
    ctx.on("page", lambda pg: _dialogos(pg, permitidos))
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
    permitidos = permisos(a)
    if a.titular != "ninguno":
        import cert
        _IDENTIDAD[:] = cert.para_redactar(a.titular)
    s = Sesion(nombre)
    res = {"sede": nombre, "titular": a.titular, "permisos_activos": sorted(permitidos),
           "origins_con_certificado": origins if a.titular != "ninguno" else []}
    with sync_playwright() as p:
        browser, ctx, pg = lanzar(p, s, a.titular, origins, a.inseguro, permitidos, getattr(a, "autofirma_auto", None))

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
                 bloqueos=lambda: list(s.bloqueos), afirma_vistos=lambda: [b["d"] for b in s.bloqueos if b.get("permiso") == "firmar"],
                 hosts=lambda: s.hosts, DIR=str(s.dir), PERMISOS=sorted(permitidos), time=time, re=re, json=json)
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
            if s.bloqueos:
                faltan = sorted({b.get("permiso") for b in s.bloqueos if b.get("permiso")})
                res["permisos_que_faltan"] = faltan
                res["como_seguir"] = ("Esos pasos requieren permiso de tu usuario. Si te lo da, repite con "
                                      f"--permitir {','.join(faltan)} (o que lo deje fijado con scripts/permisos.py).")
            if s.afirma:
                res["autofirma"] = s.afirma
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
    motivo = receta_prohibida(src, permisos(a))
    if motivo:
        salida = json.dumps({"error": f"receta rechazada por las guardas: {motivo}"}, ensure_ascii=False)
        if getattr(a, "json", None):
            Path(a.json).write_text(salida, encoding="utf-8")
        print(salida)
        return 2

    def cuerpo(h):
        scope = dict(h)
        scope.pop("ctx", None)  # sin acceso directo al contexto (rutas, peticiones); para popups: pg.context.pages
        scope["__builtins__"] = _BUILTINS_RECETA
        exec(compile(src, a.receta, "exec"), scope)
        # El RESULTADO pasa siempre por redactar(), lo haga o no la receta.
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
        sp.add_argument("--permitir", help=f"actos autorizados por tu usuario: {','.join(ACTOS)} o 'todo'")
        sp.add_argument("--autofirma-auto", type=int, metavar="N",
                        help="Linux sin escritorio (experimental): elige el certificado N en el diálogo de AutoFirma")
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
