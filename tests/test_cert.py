"""cert.py con un PKCS#12 de PRUEBA generado aquí (autofirmado, datos ficticios).

La configuración vive en una carpeta personal temporal (fixture `casa`) y el llavero del sistema
se sustituye por uno falso en memoria: nunca se toca la configuración ni el llavero reales.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import pytest

CONTRASENA = "clave-de-prueba-123"

# OIDs en DER (sin etiqueta ni longitud) para comprobar el cifrado del PKCS#12.
OID_PBES2 = bytes.fromhex("2a864886f70d01050d")                 # 1.2.840.113549.1.5.13
OID_AES256_CBC = bytes.fromhex("60864801650304012a")             # 2.16.840.1.101.3.4.1.42
OID_SHA256 = bytes.fromhex("608648016503040201")                # 2.16.840.1.101.3.4.2.1
OID_PBE_3DES = bytes.fromhex("2a864886f70d010c0103")            # pbeWithSHAAnd3-KeyTripleDES-CBC
OID_PBE_RC2_40 = bytes.fromhex("2a864886f70d010c0106")          # pbeWithSHAAnd40BitRC2-CBC


def _ns(**kw) -> argparse.Namespace:
    return argparse.Namespace(**kw)


def _salida(capsys) -> dict:
    return json.loads(capsys.readouterr().out)


def _fichero_contrasena(ruta, texto: str):
    ruta.write_text(texto, encoding="utf-8")
    if os.name != "nt":
        os.chmod(ruta, 0o600)
    return ruta


@pytest.fixture
def p12(tmp_path, generar_p12):
    ruta = tmp_path / "certificado-prueba.p12"
    certificado = generar_p12(ruta, CONTRASENA)
    return ruta, certificado


@pytest.fixture
def configurado(cert, p12, tmp_path, terminal, capsys):
    """Titular 'prueba' configurado con fichero de contraseña (una sola línea)."""
    ruta, _ = p12
    pw = _fichero_contrasena(tmp_path / "pw.txt", CONTRASENA + "\n")
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=str(pw))) == 0
    capsys.readouterr()
    return pw


class LlaveroFalso:
    """Sustituye al módulo keyring: guarda en memoria."""

    def __init__(self):
        self.datos: dict[tuple[str, str], str] = {}

    def set_password(self, servicio, alias, pw):
        self.datos[(servicio, alias)] = pw

    def get_password(self, servicio, alias):
        return self.datos.get((servicio, alias))

    def delete_password(self, servicio, alias):
        self.datos.pop((servicio, alias), None)


# ------------------------------------------------------------------ configurar
def test_configurar_exige_terminal(cert, p12, tmp_path, monkeypatch, capsys):
    ruta, _ = p12
    pw = _fichero_contrasena(tmp_path / "pw.txt", CONTRASENA)

    class SinTerminal:
        def isatty(self):
            return False
    monkeypatch.setattr(sys, "stdin", SinTerminal())
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=str(pw))) == 2
    salida = capsys.readouterr()
    assert salida.out == "" and "PERSONA" in salida.err
    assert not cert.CONFIG.exists()


def test_configurar_con_fichero_de_contrasena(cert, p12, tmp_path, terminal, capsys):
    ruta, _ = p12
    pw = _fichero_contrasena(tmp_path / "pw.txt", CONTRASENA + "\n")
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=str(pw))) == 0
    salida = capsys.readouterr()
    r = json.loads(salida.out)
    assert r["ok"] is True and r["alias"] == "prueba"
    assert r["tipo"] == "persona física"
    assert r["nif_titular"] == "*****678A"
    assert r["dias_restantes"] > 300 and r["aviso"] is None
    cfg = json.loads(cert.CONFIG.read_text(encoding="utf-8"))
    assert cfg["prueba"]["almacen"] == "fichero"
    assert cfg["prueba"]["linea"] == 0
    assert cfg["prueba"]["p12"] == str(ruta.resolve())
    # La contraseña no sale nunca: ni por stdout, ni por stderr, ni en la configuración.
    for texto in (salida.out, salida.err, cert.CONFIG.read_text(encoding="utf-8")):
        assert CONTRASENA not in texto
    if os.name != "nt":
        assert oct(cert.CONFIG.stat().st_mode & 0o777) == oct(0o600)


def test_configurar_fichero_con_varias_lineas(cert, p12, tmp_path, terminal, capsys):
    ruta, _ = p12
    pw = _fichero_contrasena(tmp_path / "notas.txt",
                             "Certificado de prueba\n\ncontraseña:\n  " + CONTRASENA + "  \n(guardado en un USB)\n")
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=str(pw))) == 0
    capsys.readouterr()
    cfg = json.loads(cert.CONFIG.read_text(encoding="utf-8"))
    assert cfg["prueba"]["linea"] == 2  # tercera línea no vacía
    assert cert.cmd_comprobar(_ns(alias="prueba")) == 0
    assert _salida(capsys)["ok"] is True
    assert cert.para_playwright("prueba")["passphrase"] == CONTRASENA


def test_configurar_fichero_sin_la_contrasena(cert, p12, tmp_path, terminal, capsys):
    ruta, _ = p12
    pw = _fichero_contrasena(tmp_path / "pw.txt", "esta no es\nni esta\n")
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=str(pw))) == 1
    assert "ninguna línea" in capsys.readouterr().err
    assert not cert.CONFIG.exists()


@pytest.mark.skipif(os.name == "nt", reason="los permisos 600 solo se comprueban en Linux y macOS")
def test_configurar_rechaza_fichero_legible_por_otros(cert, p12, tmp_path, terminal, capsys):
    ruta, _ = p12
    pw = tmp_path / "pw.txt"
    pw.write_text(CONTRASENA, encoding="utf-8")
    os.chmod(pw, 0o644)
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=str(pw))) == 1
    assert "600" in capsys.readouterr().err


def test_configurar_p12_inexistente(cert, tmp_path, terminal, capsys):
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(tmp_path / "no-existe.p12"), fichero_contrasena=None)) == 1


def test_configurar_con_llavero(cert, p12, terminal, monkeypatch, capsys):
    ruta, _ = p12
    llavero = LlaveroFalso()
    monkeypatch.setitem(sys.modules, "keyring", llavero)
    monkeypatch.setattr(cert.getpass, "getpass", lambda *_a, **_k: CONTRASENA)
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=None)) == 0
    salida = capsys.readouterr()
    assert CONTRASENA not in salida.out + salida.err
    assert llavero.datos == {(cert.SERVICIO, "prueba"): CONTRASENA}
    cfg = json.loads(cert.CONFIG.read_text(encoding="utf-8"))
    assert cfg["prueba"]["almacen"] == "llavero"
    assert CONTRASENA not in cert.CONFIG.read_text(encoding="utf-8")
    assert cert.cmd_comprobar(_ns(alias="prueba")) == 0
    capsys.readouterr()
    # olvidar borra el llavero y la entrada
    assert cert.cmd_olvidar(_ns(alias="prueba")) == 0
    assert _salida(capsys)["ok"] is True
    assert llavero.datos == {}
    assert "prueba" not in json.loads(cert.CONFIG.read_text(encoding="utf-8"))


def test_contrasena_incorrecta_en_el_llavero(cert, p12, terminal, monkeypatch, capsys):
    ruta, _ = p12
    monkeypatch.setitem(sys.modules, "keyring", LlaveroFalso())
    monkeypatch.setattr(cert.getpass, "getpass", lambda *_a, **_k: "otra-cosa")
    assert cert.cmd_configurar(_ns(alias="prueba", p12=str(ruta), fichero_contrasena=None)) == 1
    salida = capsys.readouterr()
    assert "otra-cosa" not in salida.out + salida.err
    assert not cert.CONFIG.exists()


# ------------------------------------------------------------------ listar / comprobar
def test_listar_sin_secretos(cert, configurado, capsys):
    assert cert.cmd_listar(_ns()) == 0
    salida = capsys.readouterr()
    r = json.loads(salida.out)
    assert r["config"] == str(cert.CONFIG)
    (t,) = r["titulares"]
    assert t["alias"] == "prueba" and t["almacen"] == "fichero"
    assert "error" not in t
    assert t["tipo"] == "persona física" and t["nif_titular"] == "*****678A"
    assert CONTRASENA not in salida.out + salida.err
    assert "12345678A" not in salida.out


def test_listar_vacio(cert, capsys):
    assert cert.cmd_listar(_ns()) == 0
    assert _salida(capsys)["titulares"] == []


def test_listar_informa_del_error_sin_detalles(cert, configurado, capsys):
    configurado.write_text("contraseña-cambiada\n", encoding="utf-8")
    assert cert.cmd_listar(_ns()) == 0
    (t,) = _salida(capsys)["titulares"]
    assert t["error"] == "ValueError"


def test_comprobar(cert, configurado, capsys):
    assert cert.cmd_comprobar(_ns(alias="prueba")) == 0
    r = _salida(capsys)
    assert r["ok"] is True and r["alias"] == "prueba" and r["caduca"]


def test_comprobar_alias_desconocido(cert, configurado, capsys):
    assert cert.cmd_comprobar(_ns(alias="otro")) == 1
    assert _salida(capsys)["ok"] is False


def test_comprobar_contrasena_cambiada(cert, configurado, capsys):
    configurado.write_text("contraseña-cambiada\n", encoding="utf-8")
    assert cert.cmd_comprobar(_ns(alias="prueba")) == 1
    r = _salida(capsys)
    assert r["ok"] is False and r["error"] == "ValueError"


def test_certificado_caducado(cert, tmp_path, generar_p12, terminal, capsys):
    ruta = tmp_path / "caducado.p12"
    generar_p12(ruta, CONTRASENA, dias=-5)
    pw = _fichero_contrasena(tmp_path / "pw.txt", CONTRASENA)
    assert cert.cmd_configurar(_ns(alias="viejo", p12=str(ruta), fichero_contrasena=str(pw))) == 0
    r = _salida(capsys)
    assert r["aviso"] == "CADUCADO" and r["dias_restantes"] < 0


def test_certificado_de_representante(cert, tmp_path, generar_p12, terminal, capsys):
    ruta = tmp_path / "representante.p12"
    generar_p12(ruta, CONTRASENA, organizacion="EMPRESA FICTICIA SL", id_entidad="VATES-B12345670")
    pw = _fichero_contrasena(tmp_path / "pw.txt", CONTRASENA)
    assert cert.cmd_configurar(_ns(alias="empresa", p12=str(ruta), fichero_contrasena=str(pw))) == 0
    r = _salida(capsys)
    assert r["tipo"] == "representante de persona jurídica"
    assert r["organizacion"] == "EMPRESA FICTICIA SL"
    assert r["nif_entidad"] == "*****5670"


def test_mascara(cert):
    assert cert._mascara("IDCES-12345678A") == "*****678A"
    assert cert._mascara("VATES-B12345670") == "*****5670"
    assert cert._mascara(None) is None


# ------------------------------------------------------------------ para_playwright
def test_para_playwright_devuelve_pfx_moderno(cert, configurado, p12):
    from cryptography.hazmat.primitives.serialization import pkcs12
    _, original = p12
    c = cert.para_playwright("prueba")
    assert set(c) == {"pfx", "passphrase"}
    assert c["passphrase"] == CONTRASENA
    clave, certificado, _cadena = pkcs12.load_key_and_certificates(c["pfx"], CONTRASENA.encode())
    assert clave is not None and certificado == original
    assert OID_PBES2 in c["pfx"] and OID_AES256_CBC in c["pfx"] and OID_SHA256 in c["pfx"]
    assert OID_PBE_3DES not in c["pfx"] and OID_PBE_RC2_40 not in c["pfx"]
    with pytest.raises(ValueError):
        pkcs12.load_key_and_certificates(c["pfx"], b"otra-contrasena")


def test_para_playwright_reempaqueta_p12_antiguo(cert, tmp_path, generar_p12, terminal, capsys):
    from cryptography.hazmat.primitives.serialization import pkcs12
    ruta = tmp_path / "antiguo.p12"
    original = generar_p12(ruta, CONTRASENA, antiguo=True)
    assert OID_PBE_3DES in ruta.read_bytes()  # el de entrada es de verdad 3DES
    pw = _fichero_contrasena(tmp_path / "pw.txt", CONTRASENA)
    assert cert.cmd_configurar(_ns(alias="antiguo", p12=str(ruta), fichero_contrasena=str(pw))) == 0
    capsys.readouterr()
    c = cert.para_playwright("antiguo")
    assert OID_PBE_3DES not in c["pfx"] and OID_PBES2 in c["pfx"] and OID_AES256_CBC in c["pfx"]
    _clave, certificado, _cadena = pkcs12.load_key_and_certificates(c["pfx"], CONTRASENA.encode())
    assert certificado == original
    assert ruta.read_bytes() != c["pfx"]  # no se reescribe el fichero original


def test_para_playwright_no_escribe_en_disco(cert, configurado, tmp_path, casa):
    antes = {p for p in list(tmp_path.rglob("*")) + list(casa.rglob("*"))}
    cert.para_playwright("prueba")
    despues = {p for p in list(tmp_path.rglob("*")) + list(casa.rglob("*"))}
    assert despues == antes


def test_para_playwright_alias_desconocido(cert):
    with pytest.raises(LookupError):
        cert.para_playwright("nadie")


# ------------------------------------------------------------------ main()
def test_main_listar(cert, configurado, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cert.py", "listar"])
    assert cert.main() == 0
    assert [t["alias"] for t in _salida(capsys)["titulares"]] == ["prueba"]
