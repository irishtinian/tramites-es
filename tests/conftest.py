"""Fixtures comunes de las pruebas de tramites-es.

Reglas de estas pruebas:
- sin red (cualquier conexión hace fallar la prueba) y sin navegador;
- sin tocar la configuración real de la persona (HOME, APPDATA y XDG_* temporales);
- datos ficticios generados al vuelo: en el código nunca aparece un NIF, NIE, CIF o IBAN válido
  (la guarda de contenido de la CI también revisa estos ficheros).
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / "skills" / "tramites-es"
SCRIPTS = SKILL / "scripts"
GUARDAS_CI = RAIZ / ".github" / "scripts"

LETRAS_NIF = "TRWAGMYFPDXBNJZSQVHLCKE"


def cargar_modulo(ruta: Path, nombre: str):
    """Importa un script del skill como módulo, sin ejecutar su main()."""
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    assert spec is not None and spec.loader is not None, ruta
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ aislamiento
@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Ninguna prueba puede abrir conexiones: si algo lo intenta, falla."""
    def prohibido(*_a, **_k):
        raise RuntimeError("las pruebas de tramites-es no pueden usar la red")
    monkeypatch.setattr(socket.socket, "connect", prohibido)
    monkeypatch.setattr(socket.socket, "connect_ex", prohibido)
    monkeypatch.setattr(socket, "create_connection", prohibido)
    monkeypatch.setattr(socket, "getaddrinfo", prohibido)


@pytest.fixture(autouse=True)
def casa(tmp_path_factory, monkeypatch) -> Path:
    """Carpeta personal temporal: ninguna prueba lee ni escribe la configuración real."""
    d = tmp_path_factory.mktemp("casa")
    monkeypatch.setenv("HOME", str(d))
    monkeypatch.setenv("USERPROFILE", str(d))
    monkeypatch.setenv("APPDATA", str(d / "AppData" / "Roaming"))
    monkeypatch.setenv("LOCALAPPDATA", str(d / "AppData" / "Local"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(d / ".config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(d / ".local" / "share"))
    return d


# ------------------------------------------------------------------ rutas y módulos
@pytest.fixture(scope="session")
def raiz() -> Path:
    return RAIZ


@pytest.fixture(scope="session")
def skill() -> Path:
    return SKILL


@pytest.fixture(scope="session")
def buscar():
    return cargar_modulo(SCRIPTS / "buscar.py", "tramites_buscar")


@pytest.fixture(scope="session")
def calendario():
    return cargar_modulo(SCRIPTS / "calendario.py", "tramites_calendario")


@pytest.fixture(scope="session")
def justificante():
    return cargar_modulo(SCRIPTS / "justificante.py", "tramites_justificante")


@pytest.fixture(scope="session")
def sede():
    # sede.py solo importa la biblioteca estándar al cargarse: Playwright se importa al abrir el navegador.
    return cargar_modulo(SCRIPTS / "sede.py", "tramites_sede")


@pytest.fixture
def cert(casa):
    """cert.py recién importado: calcula CONFIG al importarse, así que debe verse la casa temporal."""
    mod = cargar_modulo(SCRIPTS / "cert.py", "tramites_cert")
    assert casa in mod.CONFIG.parents, f"cert.py usaría una configuración real: {mod.CONFIG}"
    return mod


@pytest.fixture
def permisos(casa):
    """permisos.py recién importado (su FICHERO vive en la casa temporal). Se registra como 'permisos'
    para que sede.permisos_usuario() lo encuentre en sys.modules en vez del fichero real."""
    mod = cargar_modulo(SCRIPTS / "permisos.py", "permisos")
    assert casa in mod.FICHERO.parents, f"permisos.py usaría una configuración real: {mod.FICHERO}"
    yield mod
    sys.modules.pop("permisos", None)


@pytest.fixture(scope="session")
def guarda():
    return cargar_modulo(GUARDAS_CI / "content_guard.py", "tramites_content_guard")


@pytest.fixture(scope="session")
def validador():
    return cargar_modulo(GUARDAS_CI / "validate.py", "tramites_validate")


# ------------------------------------------------------------------ terminal simulada
class TerminalFalsa:
    """stdin que dice ser una terminal interactiva (cert.py configurar lo exige)."""

    def isatty(self) -> bool:
        return True

    def read(self, *_a):
        raise AssertionError("la prueba no debe leer de stdin")

    readline = read


@pytest.fixture
def terminal(monkeypatch):
    monkeypatch.setattr(sys, "stdin", TerminalFalsa())


# ------------------------------------------------------------------ identificadores ficticios
def _nif(numero: int) -> str:
    return f"{numero:08d}{LETRAS_NIF[numero % 23]}"


def _nie(prefijo: str, numero: int) -> str:
    n = int(str("XYZ".index(prefijo)) + f"{numero:07d}")
    return f"{prefijo}{numero:07d}{LETRAS_NIF[n % 23]}"


def _cif(letra: str, digitos: str) -> str:
    pares = sum(int(d) for d in digitos[1::2])
    impares = sum(sum(divmod(2 * int(d), 10)) for d in digitos[0::2])
    return f"{letra}{digitos}{(10 - (pares + impares) % 10) % 10}"


def _iban(bban: str) -> str:
    return f"ES{98 - int(bban + '142800') % 97:02d}{bban}"


def _nif_letra_erronea(numero: int) -> str:
    return f"{numero:08d}{LETRAS_NIF[(numero + 1) % 23]}"


@pytest.fixture(scope="session")
def ficticios():
    """Generadores de identificadores con dígito de control válido, solo para probar detectores."""
    return SimpleNamespace(nif=_nif, nie=_nie, cif=_cif, iban=_iban, nif_erroneo=_nif_letra_erronea)


# ------------------------------------------------------------------ certificados de prueba
@pytest.fixture(scope="session")
def clave_rsa():
    from cryptography.hazmat.primitives.asymmetric import rsa
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def generar_p12(clave_rsa):
    """Crea un PKCS#12 autofirmado con datos ficticios. Devuelve el certificado (x509)."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs12
    from cryptography.x509.oid import NameOID

    def generar(ruta: Path, contrasena: str, *, serie: str = "IDCES-12345678A",
                nombre: str = "PERSONA FICTICIA DE PRUEBA", organizacion: str | None = None,
                id_entidad: str | None = None, dias: int = 365, antiguo: bool = False):
        # serie: letra de control incorrecta a propósito (no es un NIF válido).
        attrs = [x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
                 x509.NameAttribute(NameOID.SERIAL_NUMBER, serie),
                 x509.NameAttribute(NameOID.COMMON_NAME, nombre)]
        if organizacion:
            attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organizacion))
        if id_entidad:
            attrs.append(x509.NameAttribute(x509.ObjectIdentifier("2.5.4.97"), id_entidad))
        sujeto = x509.Name(attrs)
        ahora = dt.datetime.now(dt.timezone.utc)
        fin = ahora + dt.timedelta(days=dias)
        inicio = min(ahora, fin) - dt.timedelta(days=30)
        certificado = (x509.CertificateBuilder()
                       .subject_name(sujeto).issuer_name(sujeto)
                       .public_key(clave_rsa.public_key())
                       .serial_number(x509.random_serial_number())
                       .not_valid_before(inicio).not_valid_after(fin)
                       .sign(clave_rsa, hashes.SHA256()))
        if antiguo:  # como los .p12 de algunas gestorías: 3DES + SHA-1 (Playwright/Node los rechaza)
            cifrado = (serialization.PrivateFormat.PKCS12.encryption_builder()
                       .kdf_rounds(2048)
                       .key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)
                       .hmac_hash(hashes.SHA1())
                       .build(contrasena.encode()))
        else:
            cifrado = serialization.BestAvailableEncryption(contrasena.encode())
        Path(ruta).write_bytes(pkcs12.serialize_key_and_certificates(b"prueba", clave_rsa, certificado, None, cifrado))
        return certificado

    return generar
