# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.58.0", "pyyaml==6.0.3", "cryptography==44.0.2", "keyring==25.6.0"]
# ///
"""entorno.py — comprueba que el equipo está listo para tramites-es (salida JSON).

Revisa: versión de Python, Playwright, Google Chrome, pantalla (Linux), curl/openssl,
AutoFirma y certificados configurados con cert.py (sin mostrar secretos).
Cada problema viene con el paso para resolverlo y la guía de references/ que hay que leer.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
SO = "windows" if sys.platform == "win32" else ("macos" if sys.platform == "darwin" else "linux")
GUIA = f"references/setup-{SO}.md"


def chrome() -> str | None:
    candidatos = {
        "windows": [Path(os.environ.get(v, "")) / "Google/Chrome/Application/chrome.exe"
                    for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")],
        "macos": [Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")],
        "linux": [Path(p) for p in ("/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/opt/google/chrome/chrome")],
    }[SO]
    for c in candidatos:
        if c.exists():
            return str(c)
    return shutil.which("google-chrome") or shutil.which("chrome")


def autofirma() -> str | None:
    candidatos = {
        "windows": [Path(os.environ.get("PROGRAMFILES", "")) / "AutoFirma/AutoFirma/AutoFirmaCommandLine.exe",
                    Path(os.environ.get("PROGRAMFILES", "")) / "Autofirma/Autofirma/AutofirmaCommandLine.exe"],
        "macos": [Path("/Applications/AutoFirma.app"), Path("/Applications/Autofirma.app")],
        "linux": [Path("/usr/bin/autofirma"), Path("/usr/bin/AutoFirma")],
    }[SO]
    for c in candidatos:
        if c.exists():
            return str(c)
    return None


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    checks, pasos = {}, []
    checks["so"] = SO
    checks["python"] = sys.version.split()[0]
    if sys.version_info < (3, 11):
        pasos.append(f"Instala Python 3.11 o superior ({GUIA}).")
    try:
        import playwright  # noqa: F401
        from importlib.metadata import version
        checks["playwright"] = version("playwright")
    except Exception:
        checks["playwright"] = None
        pasos.append("Instala las dependencias: ejecuta los scripts con 'uv run' (las instala solo) o 'pip install playwright'.")
    checks["chrome"] = chrome()
    if not checks["chrome"]:
        pasos.append(f"Instala Google Chrome ({GUIA}).")
    avisos = []  # no impiden usar el skill
    if SO == "linux":
        hay = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
        checks["xvfb_run"] = bool(shutil.which("xvfb-run"))
        checks["pantalla"] = True if hay else ("xvfb-run" if checks["xvfb_run"] else False)
        if not hay and checks["xvfb_run"]:
            avisos.append("Sin escritorio: lanza sede.py como 'xvfb-run -a python3 scripts/sede.py … --json salida.json'. "
                          "buscar.py, calendario.py y ayudas.py no necesitan pantalla.")
        elif not hay:
            pasos.append("No hay pantalla ni xvfb-run: la persona debe instalar xvfb (requiere sudo) o usar el escritorio.")
    checks["curl"] = bool(shutil.which("curl"))
    checks["openssl"] = bool(shutil.which("openssl"))
    checks["autofirma"] = autofirma()
    if not checks["autofirma"]:
        pasos.append("AutoFirma no está instalado. Solo hace falta para que TÚ firmes en algunas sedes (references/setup-autofirma.md).")
    try:
        # PYTHONIOENCODING: en Windows, la salida por tubería usa la página de códigos (cp1252), no UTF-8.
        r = subprocess.run([sys.executable, str(AQUI / "cert.py"), "listar"], capture_output=True, timeout=60,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        tit = json.loads(r.stdout.decode("utf-8") or "{}").get("titulares", [])
        checks["certificados"] = [{k: t.get(k) for k in ("alias", "tipo", "organizacion", "caduca", "dias_restantes", "aviso", "error")} for t in tit]
        if not tit:
            pasos.append("No hay certificado configurado: la PERSONA debe ejecutar en su terminal "
                         "'uv run scripts/cert.py configurar --alias yo --p12 <ruta al .p12/.pfx>'.")
        for t in tit:
            if t.get("error"):
                pasos.append(f"El certificado '{t['alias']}' no abre ({t['error']}): revisa {GUIA}.")
            elif t.get("aviso"):
                pasos.append(f"Certificado '{t['alias']}': {t['aviso']} ({t.get('caduca')}). Renuévalo en la FNMT o tu emisor.")
    except Exception as ex:
        checks["certificados"] = f"error: {type(ex).__name__}"
    ok = not [p for p in pasos if "AutoFirma" not in p]
    print(json.dumps({"ok": ok, "comprobaciones": checks, "pasos": pasos, "avisos": avisos, "guia": GUIA},
                     ensure_ascii=False, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
