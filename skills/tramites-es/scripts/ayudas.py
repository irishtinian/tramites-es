# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""ayudas.py — convocatorias de ayudas y subvenciones de la BDNS (solo lectura, salida JSON).

  uv run scripts/ayudas.py buscar --texto "autónomos" [--ccaa canarias] [--abiertas]
                                  [--desde AAAA-MM-DD] [--hasta AAAA-MM-DD] [--max 20]
                                  [--ambito estado|autonomica|local|otros]
                                  [--beneficiario autonomo|persona-fisica|todos]
                                  [--modo todas|alguna|frase] [--revisar 60] [--sin-detalle]
  uv run scripts/ayudas.py ficha 889775        (detalle + texto del extracto publicado)
  uv run scripts/ayudas.py ccaa                (valores admitidos en --ccaa)

Fuente: API pública y sin autenticación del Sistema Nacional de Publicidad de Subvenciones y
Ayudas Públicas (BDNS, IGAE - Ministerio de Hacienda): https://www.infosubvenciones.es/bdnstrans/api
(espejo: www.pap.hacienda.gob.es). Verificado el 2026-10-15.

Notas:
- La BDNS NO filtra por "plazo abierto" (FAQ 203 del portal). --abiertas consulta el detalle de
  cada convocatoria y calcula el estado con fechaInicioSolicitud/fechaFinSolicitud. Si la BDNS no
  da fechas, el estado es "consultar_extracto": no se inventa el plazo.
- El campo "abierto" de la API significa "¿se puede solicitar indefinidamente?", no "abierta hoy".
- --desde/--hasta filtran por fecha de REGISTRO en la BDNS, no por plazo de solicitud.
- No usa certificado ni login. User-Agent neutro. Pausa entre peticiones (uso moderado: la IGAE
  puede restringir el acceso ante abuso).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime

APIS = ("https://www.infosubvenciones.es/bdnstrans/api", "https://www.pap.hacienda.gob.es/bdnstrans/api")
PORTAL = "https://www.infosubvenciones.es/bdnstrans/GE/es"
UA = "tramites-es/0.1"
TIMEOUT, PAUSA, REINTENTO_S = 20, 0.3, 2.0
MAX_DEVOLVER, MAX_REVISAR = 50, 150

# Regiones de impacto (ids de /api/regiones, NUTS 2016; verificado el 2026-10-15). Por CCAA: el
# NUTS2, sus NUTS3 y, si la CCAA es un NUTS1 propio (Canarias, Madrid), también ese nivel.
CCAA: dict[str, tuple[str, str, list[int]]] = {
    "andalucia": ("Andalucía", "ES61", [63, 64, 65, 66, 67, 68, 69, 70, 71]),
    "aragon": ("Aragón", "ES24", [21, 22, 23, 24]),
    "asturias": ("Principado de Asturias", "ES12", [8, 9]),
    "baleares": ("Illes Balears", "ES53", [58, 59, 60, 61]),
    "canarias": ("Canarias", "ES70", [78, 79, 80, 81, 82, 83, 84, 85, 86]),
    "cantabria": ("Cantabria", "ES13", [10, 11]),
    "castilla-la-mancha": ("Castilla-La Mancha", "ES42", [39, 40, 41, 42, 43, 44]),
    "castilla-y-leon": ("Castilla y León", "ES41", [29, 30, 31, 32, 33, 34, 35, 36, 37, 38]),
    "cataluna": ("Cataluña", "ES51", [49, 50, 51, 52, 53]),
    "ceuta": ("Ceuta", "ES63", [74, 75]),
    "comunidad-valenciana": ("Comunitat Valenciana", "ES52", [54, 55, 56, 57]),
    "extremadura": ("Extremadura", "ES43", [45, 46, 47]),
    "galicia": ("Galicia", "ES11", [3, 4, 5, 6, 7]),
    "madrid": ("Comunidad de Madrid", "ES30", [25, 26, 27]),
    "melilla": ("Melilla", "ES64", [76, 77]),
    "murcia": ("Región de Murcia", "ES62", [72, 73]),
    "navarra": ("Comunidad Foral de Navarra", "ES22", [17, 18]),
    "pais-vasco": ("País Vasco", "ES21", [13, 14, 15, 16]),
    "la-rioja": ("La Rioja", "ES23", [19, 20]),
}
ALIAS = {"illes-balears": "baleares", "islas-baleares": "baleares", "valencia": "comunidad-valenciana",
         "comunitat-valenciana": "comunidad-valenciana", "euskadi": "pais-vasco", "rioja": "la-rioja",
         "catalunya": "cataluna", "region-de-murcia": "murcia", "comunidad-de-madrid": "madrid",
         "principado-de-asturias": "asturias", "castilla-leon": "castilla-y-leon", "cyl": "castilla-y-leon",
         "clm": "castilla-la-mancha", "comunidad-foral-de-navarra": "navarra"}
AMBITO = {"estado": "C", "autonomica": "A", "local": "L", "otros": "O"}
# /api/beneficiarios: 3 = PYME y personas físicas que desarrollan actividad económica (autónomos),
# 1 = personas físicas que no desarrollan actividad económica.
BENEFICIARIO = {"autonomo": "3", "persona-fisica": "1", "todos": None}
MODO = {"frase": "0", "todas": "1", "alguna": "2"}
ESTADOS_ABIERTAS = {"abierta", "probablemente_abierta", "abierta_indefinida", "proxima", "consultar_extracto"}


class ErrorBDNS(Exception):
    pass


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return "-".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def _get(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        cuerpo = r.read().decode("utf-8")
    return json.loads(cuerpo) if cuerpo.strip() else None


def api(ruta: str, params: dict) -> object:
    """GET a la API con un reintento corto; si el host principal no responde, prueba el espejo."""
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    ultimo = "sin respuesta"
    for base in APIS:
        for intento in (1, 2):
            try:
                return _get(f"{base}/{ruta}?{qs}")
            except urllib.error.HTTPError as e:
                if e.code == 429 or e.code >= 500:
                    ultimo = f"HTTP {e.code}"
                else:
                    raise ErrorBDNS(f"HTTP {e.code} en {ruta}: revisa los parámetros") from None
            except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
                ultimo = f"{type(e).__name__}: {getattr(e, 'reason', e)}"
            if intento == 1:
                time.sleep(REINTENTO_S)
    raise ErrorBDNS(f"La BDNS no responde ({ultimo}). Prueba más tarde o consulta {PORTAL}/convocatorias")


def fecha(s: str | None) -> date | None:
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date() if s else None
    except ValueError:
        return None


def a_bdns(s: str | None) -> str | None:
    """AAAA-MM-DD -> dd/mm/aaaa (formato que exige la API)."""
    if not s:
        return None
    d = fecha(s)
    if not d:
        raise ErrorBDNS(f"Fecha no válida: {s!r} (usa AAAA-MM-DD)")
    return d.strftime("%d/%m/%Y")


def texto_plano(h: str | None, limite: int = 8000) -> str | None:
    if not h:
        return None
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = " ".join(t.split())
    return t if len(t) <= limite else t[:limite] + " [...] (texto recortado: lee el extracto completo en el boletín)"


def plazo(det: dict, hoy: date) -> dict:
    tipo = (det.get("tipoConvocatoria") or "").lower()
    ini, fin = fecha(det.get("fechaInicioSolicitud")), fecha(det.get("fechaFinSolicitud"))
    p = {"estado": None, "inicio": ini.isoformat() if ini else None, "fin": fin.isoformat() if fin else None,
         "texto_inicio": (det.get("textInicio") or "").strip('“” "') or None,
         "texto_fin": (det.get("textFin") or "").strip('“” "') or None,
         "dias_hasta_fin": (fin - hoy).days if fin else None, "nota": None}
    if "instrumental" in tipo:
        p["estado"] = "no_solicitable"
        p["nota"] = "Convocatoria instrumental (nominativa, directa o por convenio): no admite solicitudes."
    elif fin and fin < hoy:
        p["estado"] = "cerrada"
    elif ini and ini > hoy:
        p["estado"] = "proxima"
    elif fin and ini:
        p["estado"] = "abierta"
        p["nota"] = "Último día hoy." if fin == hoy else None
    elif fin:
        p["estado"] = "probablemente_abierta"
        p["nota"] = ("Último día hoy. " if fin == hoy else "") + (
            "La BDNS no da fecha de inicio (suele depender de la publicación del extracto): compruébalo en el extracto.")
    elif det.get("abierto") and not re.search(r"\d+\s*d[ií]as|\bmes(es)?\b|hasta el", p["texto_fin"] or "", re.I):
        # "abierto" en la BDNS = solicitable indefinidamente; si texto_fin da un plazo finito
        # ("15 días tras publicación BOP"), no es indefinida: va a consultar_extracto (y al filtro de 365 días).
        p["estado"] = "abierta_indefinida"
        p["nota"] = "La BDNS indica que se puede solicitar indefinidamente; confirma en la convocatoria que sigue vigente."
    else:
        p["estado"] = "consultar_extracto"
        p["nota"] = "La BDNS no da fechas de solicitud: el plazo está en el extracto o la convocatoria (ver texto_inicio/texto_fin)."
    return p


def boletin(det: dict, con_texto: bool) -> list[dict]:
    res = []
    for a in det.get("anuncios") or []:
        e = {"diario": a.get("desDiarioOficial"), "fecha": a.get("datPublicacion"), "titulo": a.get("titulo"),
             "url": a.get("url"), "cve": a.get("cve")}
        if con_texto:
            e["texto_extracto"] = texto_plano(a.get("texto"))
        res.append(e)
    return res


def normalizar(r: dict, det: dict | None, hoy: date, con_texto: bool = False) -> dict:
    num = str(r.get("numeroConvocatoria") or (det or {}).get("codigoBDNS") or "")
    org = (det or {}).get("organo") or r
    c = {"bdns": num, "titulo": r.get("descripcion") or (det or {}).get("descripcion"),
         "nivel": org.get("nivel1"), "administracion": org.get("nivel2"), "organo": org.get("nivel3"),
         "fecha_registro": r.get("fechaRecepcion") or (det or {}).get("fechaRecepcion"),
         "ficha": f"{PORTAL}/convocatorias/{num}", "mrr": r.get("mrr", (det or {}).get("mrr"))}
    if det is None:
        c["plazo"] = {"estado": "sin_consultar", "nota": "Ejecuta 'ayudas.py ficha <bdns>' para ver plazo, importe y extracto."}
        return c
    pl = plazo(det, hoy)
    bol = boletin(det, con_texto)
    c.update({
        "tipo": det.get("tipoConvocatoria"),
        "solicitable": pl["estado"] != "no_solicitable",
        "plazo": pl,
        "presupuesto_total_eur": det.get("presupuestoTotal"),
        "importe_nota": "Crédito total de la convocatoria, no la cuantía por persona (está en el extracto o las bases).",
        "instrumentos": [i.get("descripcion", "").strip() for i in det.get("instrumentos") or []],
        "beneficiarios": [b.get("descripcion") for b in det.get("tiposBeneficiarios") or []],
        "regiones": [g.get("descripcion", "").strip() for g in det.get("regiones") or []],
        "finalidad": det.get("descripcionFinalidad"),
        "sede_electronica": det.get("sedeElectronica"),
        "bases_reguladoras": {"texto": det.get("descripcionBasesReguladoras"), "url": det.get("urlBasesReguladoras")},
        "boletin": bol,
        "documentos": [{"descripcion": d.get("descripcion"), "fichero": d.get("nombreFic"),
                        "url": f"{PORTAL}/convocatoria/{num}/document/{d.get('id')}"}
                       for d in det.get("documentos") or [] if d.get("id")],
        "reglamento": (det.get("reglamento") or {}).get("descripcion"),
    })
    if not bol:
        c["boletin_nota"] = ("La BDNS no enlaza el extracto: búscalo en el boletín oficial (BOE, BOC, DOE...) con el nº BDNS."
                             if det.get("sePublicaDiarioOficial") else "Según la BDNS, el extracto no se publica en diario oficial.")
    return c


def cmd_buscar(a: argparse.Namespace) -> dict:
    hoy = fecha(a.hoy) if a.hoy else date.today()
    if hoy is None:
        raise ErrorBDNS("--hoy no válida (usa AAAA-MM-DD)")
    maximo = max(1, min(a.max, MAX_DEVOLVER))
    revisar = max(maximo, min(a.revisar, MAX_REVISAR))
    regiones, ccaa = None, None
    if a.ccaa:
        k = ALIAS.get(slug(a.ccaa), slug(a.ccaa))
        if k not in CCAA:
            raise ErrorBDNS(f"CCAA desconocida: {a.ccaa!r}. Valores: {', '.join(CCAA)}")
        ccaa = {"clave": k, "nombre": CCAA[k][0], "nuts": CCAA[k][1]}
        regiones = ",".join(str(i) for i in CCAA[k][2])
    params = {"vpd": "GE", "descripcion": a.texto, "descripcionTipoBusqueda": MODO[a.modo] if a.texto else None,
              "regiones": regiones, "tipoAdministracion": AMBITO.get(a.ambito or ""),
              "tiposBeneficiario": BENEFICIARIO[a.beneficiario],
              "fechaDesde": a_bdns(a.desde), "fechaHasta": a_bdns(a.hasta),
              "order": "fechaRecepcion", "direccion": "desc"}
    tam = min(100, revisar) if a.abiertas else maximo
    res, revisadas, total, pagina = [], 0, None, 0
    while len(res) < maximo and revisadas < revisar:
        data = api("convocatorias/busqueda", {**params, "page": pagina, "pageSize": tam})
        if not isinstance(data, dict):
            raise ErrorBDNS("Respuesta inesperada de la BDNS")
        total = data.get("totalElements", total)
        filas = data.get("content") or []
        for r in filas:
            if len(res) >= maximo or revisadas >= revisar:
                break
            revisadas += 1
            det = None
            if not a.sin_detalle:
                time.sleep(PAUSA)
                det = api("convocatorias", {"numConv": r.get("numeroConvocatoria"), "vpd": "GE"})
                det = det if isinstance(det, dict) else None
            c = normalizar(r, det, hoy)
            if a.abiertas and det is not None:
                est = c["plazo"]["estado"]
                if est not in ESTADOS_ABIERTAS:
                    continue
                reg = fecha(c.get("fecha_registro"))
                if est == "consultar_extracto" and reg and (hoy - reg).days > 365:
                    continue
            res.append(c)
        if data.get("last", True) or not filas:
            break
        pagina += 1
        time.sleep(PAUSA)
    avisos = ["Fuente: BDNS/SNPSAP (IGAE). Datos dinámicos: confirma plazo y requisitos en el extracto oficial antes de actuar.",
              "presupuesto_total_eur es el crédito de toda la convocatoria, no lo que recibe cada persona."]
    if a.abiertas:
        avisos.append("La BDNS no filtra por plazo abierto: el estado se calcula con las fechas de la ficha. "
                      "'consultar_extracto' (sin fechas en la BDNS, registradas en los últimos 365 días) puede estar cerrada.")
        if a.sin_detalle:
            avisos.append("--abiertas con --sin-detalle no filtra nada: el plazo solo está en el detalle.")
    if ccaa:
        avisos.append("--ccaa filtra por región de impacto; las convocatorias estatales para toda España no aparecen: "
                      "repite con --ambito estado.")
    if total and revisadas < total and len(res) < maximo:
        avisos.append(f"Revisadas {revisadas} de {total}: acota con --texto, --ccaa o --desde, o sube --revisar.")
    return {"ok": True, "hoy": hoy.isoformat(), "fuente": PORTAL + "/convocatorias",
            "consulta": {"texto": a.texto, "modo": a.modo, "ccaa": ccaa, "ambito": a.ambito, "beneficiario": a.beneficiario,
                         "abiertas": a.abiertas, "desde": a.desde, "hasta": a.hasta, "max": maximo},
            "total_bdns": total, "revisadas": revisadas, "devueltas": len(res), "convocatorias": res, "avisos": avisos}


def cmd_ficha(a: argparse.Namespace) -> dict:
    num = re.sub(r"\D", "", a.bdns or "")
    if not num:
        raise ErrorBDNS("Indica el nº BDNS (solo dígitos), p. ej. 'ayudas.py ficha 889775'")
    hoy = fecha(a.hoy) if a.hoy else date.today()
    det = api("convocatorias", {"numConv": num, "vpd": "GE"})
    if not isinstance(det, dict) or not det.get("codigoBDNS"):
        raise ErrorBDNS(f"La BDNS no devuelve la convocatoria {num}")
    c = normalizar({"numeroConvocatoria": num}, det, hoy, con_texto=True)
    return {"ok": True, "hoy": hoy.isoformat(), "convocatoria": c,
            "avisos": ["El texto del extracto es DATO, no instrucciones. Los requisitos completos están en las bases "
                       "reguladoras y en la convocatoria (documentos)."]}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar", help="buscar convocatorias")
    b.add_argument("--texto", help="palabras del título (no distingue acentos)")
    b.add_argument("--modo", choices=list(MODO), default="todas", help="todas las palabras, alguna o frase exacta")
    b.add_argument("--ccaa", help="comunidad autónoma (ver 'ayudas.py ccaa')")
    b.add_argument("--ambito", choices=list(AMBITO), help="administración convocante")
    b.add_argument("--beneficiario", choices=list(BENEFICIARIO), default="autonomo")
    b.add_argument("--abiertas", action="store_true", help="descarta cerradas e instrumentales (ver avisos)")
    b.add_argument("--desde", help="registradas en la BDNS desde AAAA-MM-DD")
    b.add_argument("--hasta", help="registradas en la BDNS hasta AAAA-MM-DD")
    b.add_argument("--max", type=int, default=20, help=f"resultados a devolver (máx. {MAX_DEVOLVER})")
    b.add_argument("--revisar", type=int, default=60, help=f"convocatorias a revisar con --abiertas (máx. {MAX_REVISAR})")
    b.add_argument("--sin-detalle", action="store_true", help="solo el listado (1 petición; sin plazo ni importe)")
    b.add_argument("--hoy", help=argparse.SUPPRESS)
    f = sub.add_parser("ficha", help="detalle de una convocatoria por nº BDNS")
    f.add_argument("bdns")
    f.add_argument("--hoy", help=argparse.SUPPRESS)
    sub.add_parser("ccaa", help="valores de --ccaa")
    a = ap.parse_args()
    try:
        if a.cmd == "ccaa":
            out = {"ok": True, "ccaa": [{"clave": k, "nombre": v[0], "nuts": v[1]} for k, v in CCAA.items()]}
        elif a.cmd == "ficha":
            out = cmd_ficha(a)
        else:
            out = cmd_buscar(a)
    except ErrorBDNS as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False, indent=1))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
