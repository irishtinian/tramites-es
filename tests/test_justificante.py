"""justificante.py: CSV, nº de registro y NRC en justificantes sintéticos (sin datos reales)."""
from __future__ import annotations

import json
import sys

import pytest


def _extraer(justificante, tmp_path, texto: str, nombre: str = "justificante.txt") -> dict:
    p = tmp_path / nombre
    p.write_text(texto, encoding="utf-8")
    return justificante.extraer(p)


CERTIFICADO_AEAT = """AGENCIA TRIBUTARIA
Certificado de estar al corriente de obligaciones tributarias
Titular: <TITULAR>   NIF: <NIF>
Código Seguro de Verificación: ABCD1234EFGH5678
Fecha de expedición: 15/10/2026 10:21:33
"""

JUSTIFICANTE_REG = """REGISTRO ELECTRÓNICO GENERAL DE LA AGE
Justificante de presentación
Número de registro: REGAGE26e00012345678
Fecha y hora de presentación: 15-10-2026 09:05
Organismo destinatario: <ORGANISMO>
"""

CARTA_DE_PAGO = """Recibo de pago - carta de pago
NRC: 0123456789ABCDEFGHIJKL
Importe: <IMPORTE>
"""

INFORME_TGSS_HTML = """<html><body><h1>Seguridad Social</h1><p>Informe de situación</p>
<p>CSV: <b>QWERTY12345ASDFG</b></p></body></html>
"""


def test_certificado_con_csv(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, CERTIFICADO_AEAT)
    assert r["csv"] == "ABCD1234EFGH5678"
    assert r["registro"] is None and r["nrc"] is None
    assert r["fecha"] == ["15/10/2026 10:21:33"]
    assert r["organismo"] == "AEAT"
    assert r["tipo_documento"].startswith("Certificado de estar al corriente")
    assert r["prueba_de_exito"] is True
    assert "aviso" not in r
    assert r["fichero"] == "justificante.txt"


def test_justificante_con_numero_de_registro(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, JUSTIFICANTE_REG)
    assert r["registro"] == "REGAGE26e00012345678"
    assert r["csv"] is None
    assert r["fecha"] == ["15-10-2026 09:05"]
    assert r["tipo_documento"].startswith("Justificante de presentación")
    assert r["prueba_de_exito"] is True


def test_carta_de_pago_con_nrc(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, CARTA_DE_PAGO)
    assert r["nrc"] == "0123456789ABCDEFGHIJKL"
    assert r["prueba_de_exito"] is True


def test_html_sin_etiquetas(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, INFORME_TGSS_HTML, nombre="informe.html")
    assert r["csv"] == "QWERTY12345ASDFG"
    assert r["organismo"] == "Seguridad Social"
    assert r["prueba_de_exito"] is True


def test_pantalla_de_exito_no_es_prueba(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, "Bienvenido a la sede. Su solicitud se ha procesado correctamente.")
    assert r["csv"] is None and r["registro"] is None and r["nrc"] is None
    assert r["prueba_de_exito"] is False
    assert "no des el trámite por terminado" in r["aviso"]


def test_atc_no_se_confunde_con_la_aeat(justificante, tmp_path):
    texto = "AGENCIA TRIBUTARIA CANARIA\nCertificado de estar al corriente\nCódigo Seguro de Verificación: ZXCV0987LKJH6543\n"
    r = _extraer(justificante, tmp_path, texto)
    assert r["organismo"] == "ATC (Canarias)"
    assert r["csv"] == "ZXCV0987LKJH6543"


def test_enmascara_nif_en_el_tipo_de_documento(justificante, tmp_path, ficticios):
    nif = ficticios.nif(12345678)
    r = _extraer(justificante, tmp_path, f"Certificado expedido a favor de {nif} con domicilio en <DOMICILIO>. "
                                         "CSV: ABCDEFGH12345678")
    assert nif not in r["tipo_documento"]
    assert "*****678" + nif[-1] in r["tipo_documento"]
    assert r["csv"] == "ABCDEFGH12345678"


def test_enmascara_iban_en_el_tipo_de_documento(justificante, tmp_path, ficticios):
    iban = ficticios.iban("21000418450200051332")
    con_espacios = " ".join(iban[i:i + 4] for i in range(0, len(iban), 4))
    r = _extraer(justificante, tmp_path, f"Recibo domiciliado en {con_espacios}. NRC: 0123456789ABCDEFGHIJKL")
    assert "<IBAN>" in r["tipo_documento"]
    assert iban[4:] not in r["tipo_documento"].replace(" ", "")


@pytest.mark.parametrize("texto", [
    "Puede descargar el listado en formato CSV completo.",
    "Oficina de registro de entrada general del ayuntamiento.",
])
def test_palabras_normales_no_son_codigos(justificante, tmp_path, texto):
    r = _extraer(justificante, tmp_path, texto)
    assert r["prueba_de_exito"] is False


def test_csv_con_sigla_entre_parentesis(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, "Código Seguro de Verificación (CSV): ABCD1234EFGH5678")
    assert r["csv"] == "ABCD1234EFGH5678"


# ------------------------------------------------------------------ main()
def test_main_extraer(justificante, tmp_path, monkeypatch, capsys):
    p = tmp_path / "certificado.txt"
    p.write_text(CERTIFICADO_AEAT, encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["justificante.py", "extraer", str(p)])
    assert justificante.main() == 0
    assert json.loads(capsys.readouterr().out)["csv"] == "ABCD1234EFGH5678"


def test_main_fichero_inexistente(justificante, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["justificante.py", "extraer", str(tmp_path / "no-existe.pdf")])
    assert justificante.main() == 1
    assert "error" in json.loads(capsys.readouterr().out)


def test_main_uso_incorrecto(justificante, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["justificante.py"])
    assert justificante.main() == 2
    assert capsys.readouterr().out == ""


# ------------------------------------------------------------------ CEA de la Seguridad Social
CEA_FICTICIO = "ABC1D-EFGHI-2JKLM-NO3PQ-RST45-6U789"


def test_cea_tras_su_etiqueta(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, f"Tesorería General de la Seguridad Social. Código CEA: {CEA_FICTICIO} Página: 1")
    assert r["cea"] == CEA_FICTICIO
    assert r["prueba_de_exito"] is True
    assert "nota" in r


def test_cea_en_tabla_con_etiqueta_y_valor_separados(justificante, tmp_path):
    texto = ("Id. CEA: Fecha: Código CEA: Página: 1234AB5678CD 01/01/2026 " + CEA_FICTICIO + " 1 "
             "La autenticidad de este documento puede ser comprobada mediante el Código Electrónico de Autenticidad.")
    r = _extraer(justificante, tmp_path, texto)
    assert r["cea"] == CEA_FICTICIO
    assert r["organismo"] is None or r["organismo"] == "Seguridad Social"


def test_sin_etiqueta_cea_no_se_inventa(justificante, tmp_path):
    r = _extraer(justificante, tmp_path, f"Referencia interna {CEA_FICTICIO} sin más contexto.")
    assert r["cea"] is None
