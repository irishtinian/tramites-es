# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""permisos.py — qué actos con efectos puede hacer TU agente con tramites-es.

Los permisos los decide la persona usuaria, no el skill. Sin permisos, el agente consulta y prepara,
y antes de un acto con efectos te pregunta (o le autorizas en el momento con --permitir).

  uv run scripts/permisos.py ver
  uv run scripts/permisos.py fijar todo
  uv run scripts/permisos.py fijar generar,firmar,presentar,cita
  uv run scripts/permisos.py quitar

Actos: generar (certificados/informes), firmar, presentar (enviar/registrar/adjuntar), pagar,
comparecer (abrir notificaciones: empiezan los plazos), cambiar_datos (domiciliar, bajas…), cita.

`fijar` y `quitar` los ejecuta la PERSONA en su terminal (se niegan sin terminal interactiva):
es una autorización tuya, no algo que el agente se dé a sí mismo. Si tu agente ya tiene tu
autorización por otra vía (sus propias instrucciones), puede pasar --permitir a sede.py.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

ACTOS = ("generar", "firmar", "presentar", "pagar", "comparecer", "cambiar_datos", "cita")


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "tramites-es"
    d.mkdir(parents=True, exist_ok=True)
    return d


FICHERO = _config_dir() / "permisos.yaml"


def leer() -> dict:
    if not FICHERO.exists():
        return {}
    import yaml
    return yaml.safe_load(FICHERO.read_text(encoding="utf-8")) or {}


def _validar(valor: str) -> list[str]:
    vals = [x.strip().lower() for x in valor.replace(" ", ",").split(",") if x.strip()]
    if "todo" in vals:
        return ["todo"]
    malos = [x for x in vals if x not in ACTOS]
    if malos:
        raise SystemExit(f"permisos desconocidos: {malos}. Válidos: {', '.join(ACTOS)} o 'todo'")
    return vals


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2 or sys.argv[1] not in ("ver", "fijar", "quitar"):
        print(__doc__, file=sys.stderr)
        return 2
    cmd = sys.argv[1]
    if cmd == "ver":
        d = leer()
        print(json.dumps({"fichero": str(FICHERO), "permitir": d.get("permitir", []),
                          "fijado_el": d.get("fijado_el"), "actos": list(ACTOS)},
                         ensure_ascii=False, indent=1, default=str))   # YAML lee fijado_el como fecha
        return 0
    if not sys.stdin.isatty():
        print(json.dumps({"error": "Esto lo ejecuta la persona en su terminal: fijar permisos es una autorización suya."},
                         ensure_ascii=False))
        return 2
    if cmd == "quitar":
        FICHERO.unlink(missing_ok=True)
        print(json.dumps({"ok": True, "permitir": []}, ensure_ascii=False))
        return 0
    if len(sys.argv) < 3:
        raise SystemExit("uso: permisos.py fijar todo | fijar firmar,presentar,…")
    vals = _validar(sys.argv[2])
    texto = ("# Permisos que TÚ das a tu agente para tramites-es (scripts/permisos.py).\n"
             "# Actos: generar, firmar, presentar, pagar, comparecer, cambiar_datos, cita — o 'todo'.\n"
             f"permitir: {json.dumps(vals, ensure_ascii=False)}\n"
             f"fijado_el: {dt.date.today().isoformat()}\n")
    FICHERO.write_text(texto, encoding="utf-8")
    if sys.platform != "win32":
        os.chmod(FICHERO, 0o600)
    print(json.dumps({"ok": True, "fichero": str(FICHERO), "permitir": vals}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
