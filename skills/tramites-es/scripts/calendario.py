# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""calendario.py — próximos vencimientos fiscales y de Seguridad Social del autónomo (salida JSON).

  uv run scripts/calendario.py proximos --territorio comun --dias 45
  uv run scripts/calendario.py proximos --territorio canarias --dias 45 --obligaciones 420,130,111
  uv run scripts/calendario.py proximos --territorio comun --dias 30 --desde 2027-01-10
  uv run scripts/calendario.py obligaciones --territorio canarias
  uv run scripts/calendario.py validar

Única fuente de fechas: assets/calendario.yaml (ver references/calendario-fiscal.md).
Estados: "verificado" (fecha publicada), "regla" (calculada con la norma: confirmar con el
calendario oficial del año) y "no_verificado" (nunca se presenta como plazo; va aparte).
No usa red. No necesita datos personales.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "assets" / "calendario.yaml"
TERRITORIOS = ("comun", "canarias", "ceuta", "melilla", "navarra", "bizkaia", "gipuzkoa", "alava")
ESTADOS = ("verificado", "regla", "no_verificado")
DOMI_ESTADOS = ESTADOS + ("no_aplica",)
TIPOS = ("presentacion", "pago", "solicitud", "cargo", "hito")
MAX_ANTIGUEDAD = 60  # días («Fechas, plazos e importes» en SKILL.md)


def salir(obj: dict, codigo: int = 0) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
    sys.exit(codigo)


def cargar() -> dict:
    import yaml
    if not DATOS.exists():
        salir({"ok": False, "error": f"no existe {DATOS.relative_to(RAIZ)}"}, 2)
    return yaml.safe_load(DATOS.read_text(encoding="utf-8")) or {}


def a_fecha(v) -> date | None:
    if v is None or isinstance(v, date):
        return v
    return date.fromisoformat(str(v))


def aplica(v: dict, territorio: str) -> bool:
    ts = v.get("territorios") or []
    return "todos" in ts or territorio in ts


def fuentes_de(datos: dict, claves: list[str]) -> list[dict]:
    catalogo = datos.get("fuentes") or {}
    return [{"id": k, **catalogo.get(k, {"titulo": "FUENTE DESCONOCIDA"})} for k in claves or []]


def filas(datos: dict, v: dict, desde: date) -> list[dict]:
    """Expande una entrada del YAML a una fila por modelo."""
    catalogo = datos.get("obligaciones") or {}
    fecha = a_fecha(v["fecha"])
    domi = a_fecha(v.get("domiciliacion_hasta"))
    res = []
    for m in v.get("modelos") or []:
        fila = {
            "fecha": fecha.isoformat(),
            "dias_restantes": (fecha - desde).days,
            "modelo": m,
            "nombre": (catalogo.get(m) or {}).get("nombre", m),
            "organismo": v.get("organismo"),
            "periodo": v.get("periodo"),
            "tipo": v.get("tipo"),
            "descripcion": v.get("descripcion"),
            "estado": v.get("estado"),
            "domiciliacion": {
                "hasta": domi.isoformat() if domi else None,
                "estado": v.get("domiciliacion_estado", "no_aplica"),
                "abierta": (domi >= desde) if domi else None,
            },
            "fuentes": fuentes_de(datos, v.get("fuentes")),
            "id": v.get("id"),
        }
        if v.get("regla"):
            fila["regla"] = v["regla"]
        if v.get("nota"):
            fila["nota"] = v["nota"]
        if v.get("estado") == "no_verificado":
            fila["fecha_orientativa"] = fila.pop("fecha")
            fila["aviso"] = "NO es un plazo: fecha sin fuente primaria comprobada. Compruébala en la fuente oficial."
        res.append(fila)
    return res


def cmd_proximos(a: argparse.Namespace) -> None:
    datos = cargar()
    desde = a.desde or date.today()
    if a.dias < 0 or a.dias > 800:
        salir({"ok": False, "error": "--dias debe estar entre 0 y 800"}, 2)
    hasta = desde + timedelta(days=a.dias)
    catalogo = datos.get("obligaciones") or {}
    filtro = [x.strip() for x in (a.obligaciones or "").split(",") if x.strip()]
    avisos = []
    desconocidas = [x for x in filtro if x not in catalogo]
    if desconocidas:
        avisos.append(f"Códigos desconocidos (ignorados): {', '.join(desconocidas)}. Lista: calendario.py obligaciones.")

    verificado_el = a_fecha(datos.get("verificado_el"))
    antig = (desde - verificado_el).days if verificado_el else None
    if antig is None or antig > MAX_ANTIGUEDAD:
        avisos.append(f"Los datos se verificaron el {verificado_el} (hace {antig} días, más de {MAX_ANTIGUEDAD}): "
                      "comprueba cada fecha en su fuente oficial antes de usarla.")
    cob = datos.get("cobertura") or {}
    cob_desde, cob_hasta = a_fecha(cob.get("desde")), a_fecha(cob.get("hasta"))
    if (cob_hasta and hasta > cob_hasta) or (cob_desde and desde < cob_desde):
        avisos.append(f"La ventana {desde}..{hasta} sale de la cobertura del calendario ({cob_desde}..{cob_hasta}): "
                      "fuera de ella no hay datos (solo hitos normativos).")
    info_t = (datos.get("territorios") or {}).get(a.territorio, {})
    if info_t.get("aviso"):
        avisos.append(info_t["aviso"] + (f" Calendario oficial: {info_t['enlace']}" if info_t.get("enlace") else ""))

    plazos, no_verif = [], []
    for v in datos.get("vencimientos") or []:
        fecha = a_fecha(v["fecha"])
        if not (desde <= fecha <= hasta) or not aplica(v, a.territorio):
            continue
        if v.get("tipo") == "hito" and a.sin_hitos:
            continue
        for f in filas(datos, v, desde):
            if filtro and f["modelo"] not in filtro:
                continue
            (no_verif if v.get("estado") == "no_verificado" else plazos).append(f)
    plazos.sort(key=lambda f: (f["fecha"], f["modelo"]))
    no_verif.sort(key=lambda f: (f["fecha_orientativa"], f["modelo"]))
    n_regla = sum(1 for f in plazos if f["estado"] == "regla")
    if n_regla:
        avisos.append(f"{n_regla} fecha(s) en estado 'regla': calculadas con la norma; confírmalas cuando el organismo "
                      "publique su calendario oficial del año.")
    if any(f["domiciliacion"]["estado"] == "no_verificado" for f in plazos):
        avisos.append("Hay domiciliaciones sin fecha publicada: no prometas que se puede domiciliar.")
    salir({
        "ok": True,
        "comando": "proximos",
        "territorio": a.territorio,
        "territorio_nombre": info_t.get("nombre"),
        "cobertura_territorio": info_t.get("cobertura"),
        "desde": desde.isoformat(),
        "hasta": hasta.isoformat(),
        "filtro_obligaciones": filtro or None,
        "datos_verificados_el": str(verificado_el),
        "antiguedad_datos_dias": antig,
        "avisos": avisos,
        "total": len(plazos),
        "vencimientos": plazos,
        "no_verificados": no_verif,
    })


def cmd_obligaciones(a: argparse.Namespace) -> None:
    datos = cargar()
    catalogo = datos.get("obligaciones") or {}
    usados: dict[str, int] = {}
    for v in datos.get("vencimientos") or []:
        if a.territorio and not aplica(v, a.territorio):
            continue
        for m in v.get("modelos") or []:
            usados[m] = usados.get(m, 0) + 1
    salir({
        "ok": True,
        "comando": "obligaciones",
        "territorio": a.territorio,
        "obligaciones": [{"codigo": c, **catalogo.get(c, {}), "entradas": n} for c, n in sorted(usados.items())],
    })


def cmd_validar(_: argparse.Namespace) -> None:
    datos = cargar()
    errores: list[str] = []
    fuentes = datos.get("fuentes") or {}
    catalogo = datos.get("obligaciones") or {}
    cob = datos.get("cobertura") or {}
    try:
        cob_desde, cob_hasta = a_fecha(cob.get("desde")), a_fecha(cob.get("hasta"))
        a_fecha(datos.get("verificado_el"))
    except ValueError as e:
        errores.append(f"cabecera: fecha inválida ({e})")
        cob_desde = cob_hasta = None
    if not datos.get("verificado_el"):
        errores.append("cabecera: falta verificado_el")
    for k, f in fuentes.items():
        if not str((f or {}).get("url", "")).startswith("https://"):
            errores.append(f"fuente {k}: url ausente o no https")
    ids: set[str] = set()
    n_filas, por_estado = 0, {e: 0 for e in ESTADOS}
    for i, v in enumerate(datos.get("vencimientos") or []):
        vid = v.get("id") or f"#{i}"
        if vid in ids:
            errores.append(f"{vid}: id repetido")
        ids.add(vid)
        for campo in ("fecha", "tipo", "modelos", "organismo", "territorios", "descripcion", "estado", "fuentes"):
            if not v.get(campo):
                errores.append(f"{vid}: falta {campo}")
        try:
            fecha, domi = a_fecha(v.get("fecha")), a_fecha(v.get("domiciliacion_hasta"))
        except ValueError as e:
            errores.append(f"{vid}: fecha inválida ({e})")
            continue
        if v.get("estado") not in ESTADOS:
            errores.append(f"{vid}: estado '{v.get('estado')}' no válido")
        if v.get("estado") == "regla" and not v.get("regla"):
            errores.append(f"{vid}: estado regla sin texto de regla")
        if v.get("tipo") not in TIPOS:
            errores.append(f"{vid}: tipo '{v.get('tipo')}' no válido")
        if v.get("domiciliacion_estado", "no_aplica") not in DOMI_ESTADOS:
            errores.append(f"{vid}: domiciliacion_estado no válido")
        if domi and fecha and domi > fecha:
            errores.append(f"{vid}: la domiciliación acaba después del plazo")
        if fecha and v.get("tipo") != "hito" and cob_desde and cob_hasta and not (cob_desde <= fecha <= cob_hasta):
            errores.append(f"{vid}: fecha {fecha} fuera de la cobertura")
        for t in v.get("territorios") or []:
            if t != "todos" and t not in TERRITORIOS:
                errores.append(f"{vid}: territorio '{t}' desconocido")
        for m in v.get("modelos") or []:
            if m not in catalogo:
                errores.append(f"{vid}: modelo '{m}' no está en el catálogo de obligaciones")
        for k in v.get("fuentes") or []:
            if k not in fuentes:
                errores.append(f"{vid}: fuente '{k}' no definida")
        n = len(v.get("modelos") or [])
        n_filas += n
        if v.get("estado") in por_estado:
            por_estado[v["estado"]] += n
    for r in datos.get("reglas") or []:
        for k in r.get("fuentes") or []:
            if k not in fuentes:
                errores.append(f"regla {r.get('id')}: fuente '{k}' no definida")
    salir({
        "ok": not errores,
        "comando": "validar",
        "verificado_el": str(datos.get("verificado_el")),
        "entradas": len(datos.get("vencimientos") or []),
        "filas_por_modelo": n_filas,
        "filas_por_estado": por_estado,
        "fuentes": len(fuentes),
        "errores": errores,
    }, 0 if not errores else 1)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    p = argparse.ArgumentParser(description="Calendario fiscal del autónomo (JSON). Datos: assets/calendario.yaml")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("proximos", help="vencimientos en los próximos N días")
    pp.add_argument("--territorio", required=True, choices=TERRITORIOS)
    pp.add_argument("--dias", type=int, default=45)
    pp.add_argument("--obligaciones", help="códigos separados por comas, p. ej. 303,130,111,cuota_reta")
    pp.add_argument("--desde", type=date.fromisoformat, help="fecha de referencia AAAA-MM-DD (por defecto, hoy)")
    pp.add_argument("--sin-hitos", action="store_true", help="omite los hitos normativos")
    pp.set_defaults(func=cmd_proximos)
    po = sub.add_parser("obligaciones", help="códigos con vencimientos cargados")
    po.add_argument("--territorio", choices=TERRITORIOS)
    po.set_defaults(func=cmd_obligaciones)
    pv = sub.add_parser("validar", help="comprueba la integridad de assets/calendario.yaml")
    pv.set_defaults(func=cmd_validar)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
