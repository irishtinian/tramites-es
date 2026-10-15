# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf==5.4.0"]
# ///
"""justificante.py — extrae de un justificante o certificado los datos que prueban el resultado.

  uv run scripts/justificante.py extraer <fichero.pdf|.txt|.html>

Devuelve (JSON): CSV (código seguro de verificación), nº de registro o anotación, fechas,
tipo de documento y organismo, con el NIF/NIE enmascarado. Sirve para verificar el éxito
(no basta con que la pantalla diga "correcto") y para archivar con el CSV en el nombre.
El cotejo del CSV se hace en la sede del organismo emisor (ver la guía de la sede).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PATRONES = {
    # Etiqueta sin distinguir mayúsculas; el código, en MAYÚSCULAS y con al menos un dígito
    # ("formato CSV completo" no es un CSV). Admite "Código Seguro de Verificación (CSV): XXXX".
    "csv": r"(?i:C[oó]digo Seguro de Verificaci[oó]n|\bCSV\b)(?:\s*\((?i:CSV)\))?\s*[:\-]?\s*((?=[A-Z0-9]*\d)[A-Z0-9]{8,30})\b",
    # Igual que el CSV: la etiqueta sin distinguir mayúsculas y el valor con al menos un dígito
    # ("registro de entrada general" no es un número de registro).
    "registro": r"(?i:n[uú]mero de (?:registro|anotaci[oó]n|entrada)|n[ºo°]\.? de registro|registro de entrada)\s*[:\-]?\s*((?=[0-9A-Za-z/\-]*\d)[0-9A-Za-z/\-]{6,40})",
    "nrc": r"(?i:\bNRC)\s*[:\-]?\s*((?=[0-9A-Z]*\d)[0-9A-Z]{16,25})\b",
    # Seguridad Social: "Código CEA" (Código Electrónico de Autenticidad), grupos de 5 separados por guiones.
    "cea": r"(?i:C[oó]digo CEA|C[oó]digo Electr[oó]nico de Autenticidad)\s*[:\-]?\s*([A-Z0-9]{5}(?:-[A-Z0-9]{5}){3,7})\b",
    "fecha": r"\b(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)",
}
ORGANISMOS = {  # se prueba en orden: la ATC antes que la AEAT ("agencia tributaria canaria" contiene "agencia tributaria")
    "ATC (Canarias)": r"agencia tributaria canaria",
    "AEAT": r"agencia (estatal de administraci[oó]n )?tributaria|agenciatributaria",
    "Seguridad Social": r"seguridad social|tesorer[ií]a general",
    "DGT": r"direcci[oó]n general de tr[aá]fico",
    "Catastro": r"catastro",
    "Justicia": r"ministerio de justicia|registro central de penados",
}


def texto(p: Path) -> str:
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
            return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
        except ImportError:
            # Sin uv ni pypdf: pdftotext (poppler-utils) si está instalado.
            import shutil
            import subprocess
            exe = shutil.which("pdftotext")
            if not exe:
                raise SystemExit("Para leer PDF hace falta pypdf (lo instala 'uv run' solo) o pdftotext (poppler-utils).")
            r = subprocess.run([exe, str(p), "-"], capture_output=True, timeout=60)  # orden de lectura, no -layout
            return r.stdout.decode("utf-8", errors="replace")
    t = p.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"<[^>]+>", " ", t) if p.suffix.lower() in (".html", ".htm") else t


def enmascarar(t: str) -> str:
    t = re.sub(r"\b([XYZ]?\d{7,8})([A-Z])\b", lambda m: "*" * (len(m.group(1)) - 3) + m.group(1)[-3:] + m.group(2), t)
    return re.sub(r"\bES\d{2}(?:\s?\d{4}){5}\b", "<IBAN>", t)


def extraer(p: Path) -> dict:
    t = texto(p)
    plano = " ".join(t.split())
    res = {"fichero": p.name, "caracteres": len(plano)}
    for k, pat in PATRONES.items():
        m = re.findall(pat, plano, 0 if k in ("csv", "registro", "nrc", "cea") else re.I)
        res[k] = (m[0] if k != "fecha" else m[:3]) if m else None
    if not res["cea"] and re.search(r"(?i)c[oó]digo CEA|electr[oó]nico de autenticidad", plano):
        # El PDF de la TGSS maqueta etiqueta y valor en filas distintas: se busca el formato del código.
        m = re.search(r"\b([A-Z0-9]{5}(?:-[A-Z0-9]{5}){5})\b", plano)
        res["cea"] = m.group(1) if m else None
    res["organismo"] = next((o for o, pat in ORGANISMOS.items() if re.search(pat, plano, re.I)), None)
    m = re.search(r"(certificado[^.]{0,80}|justificante[^.]{0,80}|recibo[^.]{0,60})", plano, re.I)
    res["tipo_documento"] = enmascarar(m.group(1)[:100]) if m else None
    res["prueba_de_exito"] = bool(res["csv"] or res["registro"] or res["nrc"] or res["cea"])
    if res["csv"] or res["cea"]:
        res["nota"] = ("El CSV/CEA permite a cualquiera descargar este documento en la sede: trátalo como dato "
                       "personal y no lo pegues en sitios públicos.")
    if not res["prueba_de_exito"]:
        res["aviso"] = "No se ha encontrado CSV, CEA, nº de registro ni NRC: no des el trámite por terminado; comprueba el listado oficial de la sede."
    return res


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    if len(sys.argv) != 3 or sys.argv[1] != "extraer":
        print(__doc__, file=sys.stderr)
        return 2
    p = Path(sys.argv[2])
    if not p.exists():
        print(json.dumps({"error": f"no existe {p}"}, ensure_ascii=False))
        return 1
    print(json.dumps(extraer(p), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
