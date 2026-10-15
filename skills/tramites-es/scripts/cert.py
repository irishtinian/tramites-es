# /// script
# requires-python = ">=3.11"
# dependencies = ["cryptography==44.0.2", "keyring==25.6.0"]
# ///
"""cert.py — ÚNICO módulo de tramites-es que toca el certificado digital.

Comandos (salida JSON por stdout; diagnósticos por stderr):
  configurar --alias A --p12 RUTA [--fichero-contrasena RUTA]
      LO EJECUTA LA PERSONA en su propia terminal (se niega si no hay terminal interactiva).
      Pide la contraseña del .p12/.pfx, comprueba que abre y la guarda en el llavero del
      sistema (Windows: Administrador de credenciales; macOS: Llavero; Linux: Secret Service).
      En Linux sin llavero, --fichero-contrasena usa un fichero que ya exista con permisos 600.
  listar                 titulares configurados: tipo, caducidad y NIF enmascarado (sin secretos)
  comprobar --alias A    abre el certificado con la contraseña guardada y dice si es válido
  olvidar --alias A      borra la contraseña del llavero y la entrada de configuración

Uso interno (solo desde scripts/sede.py):  para_playwright(alias) -> dict con pfxPath y passphrase

Reglas: la contraseña nunca se imprime, nunca va en argv y nunca se escribe en logs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import getpass
import json
import os
import stat
import sys
from pathlib import Path

SERVICIO = "tramites-es"


def config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "tramites-es"
    d.mkdir(parents=True, exist_ok=True)
    return d


CONFIG = config_dir() / "certificados.json"


def _out(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def _err(msg: str) -> None:
    print(f"[cert] {msg}", file=sys.stderr)


def _cargar_config() -> dict:
    if CONFIG.exists():
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {}


def _guardar_config(cfg: dict) -> None:
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")
    if sys.platform != "win32":
        os.chmod(CONFIG, 0o600)


def _lineas_candidatas(ruta: str) -> list[str]:
    p = Path(ruta)
    if sys.platform != "win32" and stat.S_IMODE(p.stat().st_mode) & 0o077:
        raise PermissionError("el fichero de contraseña debe tener permisos 600 (chmod 600)")
    lineas = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()]
    return [ln for ln in lineas if ln]


def _leer_fichero_contrasena(ruta: str, linea: int | None = None) -> str:
    """Devuelve la contraseña del fichero. Lo normal es que sea su única línea; si el fichero
    tiene más texto (títulos, notas), `configurar` averigua qué línea abre el certificado y la recuerda."""
    cand = _lineas_candidatas(ruta)
    if not cand:
        raise ValueError("fichero de contraseña vacío")
    return cand[linea] if linea is not None and linea < len(cand) else cand[0]


def _contrasena(alias: str, entrada: dict) -> str:
    if entrada.get("almacen") == "fichero":
        return _leer_fichero_contrasena(entrada["fichero_contrasena"], entrada.get("linea"))
    import keyring
    try:
        pw = keyring.get_password(SERVICIO, alias)
    except Exception as ex:  # p. ej. Linux sin Secret Service
        raise LookupError(f"el llavero del sistema no está disponible ({type(ex).__name__}); "
                          "en Linux sin llavero, configura con --fichero-contrasena (ver references/setup-linux.md)") from None
    if pw is None:
        raise LookupError(f"no hay contraseña guardada para '{alias}'; la persona debe ejecutar 'cert.py configurar'")
    return pw


def _abrir(p12: str, pw: str):
    from cryptography.hazmat.primitives.serialization import pkcs12
    key, cert, _chain = pkcs12.load_key_and_certificates(Path(p12).read_bytes(), pw.encode())
    if key is None or cert is None:
        raise ValueError("el fichero no contiene clave privada y certificado")
    return cert


def _mascara(nif: str | None) -> str | None:
    if not nif:
        return None
    nif = nif.replace("IDCES-", "").replace("VATES-", "")
    return "*" * max(0, len(nif) - 4) + nif[-4:]


def _info(cert) -> dict:
    from cryptography.x509.oid import NameOID

    def attr(oid):
        v = cert.subject.get_attributes_for_oid(oid)
        return v[0].value if v else None

    org = attr(NameOID.ORGANIZATION_NAME)
    nif = attr(NameOID.SERIAL_NUMBER)
    org_id = None
    try:
        from cryptography.x509 import ObjectIdentifier
        v = cert.subject.get_attributes_for_oid(ObjectIdentifier("2.5.4.97"))  # organizationIdentifier
        org_id = v[0].value if v else None
    except Exception:
        pass
    caduca = cert.not_valid_after_utc
    dias = (caduca - dt.datetime.now(dt.timezone.utc)).days
    return {
        "tipo": "representante de persona jurídica" if org or org_id else "persona física",
        "organizacion": org,
        "nif_titular": _mascara(nif),
        "nif_entidad": _mascara(org_id),
        # Solo CN y O del emisor: el DN completo de un certificado autofirmado incluye el NIF del titular.
        "emisor": ", ".join(str(a.value) for oid in (NameOID.COMMON_NAME, NameOID.ORGANIZATION_NAME)
                            for a in cert.issuer.get_attributes_for_oid(oid))[:120],
        "caduca": caduca.date().isoformat(),
        "dias_restantes": dias,
        # La FNMT deja renovar por internet en los 60 días previos a la caducidad.
        "aviso": "CADUCADO" if dias < 0 else (
            "caduca en 60 días o menos: ya se puede renovar (references/tramite-renovar-certificado-fnmt.md)"
            if dias <= 60 else None),
    }


# --------------------------------------------------------------------- API interna
def para_playwright(alias: str) -> dict:
    """Devuelve {'pfx': bytes, 'passphrase'} para client_certificates de Playwright. Solo para sede.py.

    El PKCS#12 se re-empaqueta EN MEMORIA con cifrado moderno (PBES2 + AES-256, HMAC SHA-256):
    Playwright/Node rechaza los .p12 antiguos (RC2/3DES) que aún emiten algunas gestorías.
    Nada se escribe en disco.
    """
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.serialization import PrivateFormat, pkcs12

    cfg = _cargar_config()
    if alias not in cfg:
        raise LookupError(f"titular '{alias}' no configurado (cert.py listar)")
    e = cfg[alias]
    pw = _contrasena(alias, e)
    key, cert, chain = pkcs12.load_key_and_certificates(Path(e["p12"]).read_bytes(), pw.encode())
    enc = (PrivateFormat.PKCS12.encryption_builder()
           .kdf_rounds(50000)
           .key_cert_algorithm(pkcs12.PBES.PBESv2SHA256AndAES256CBC)
           .hmac_hash(hashes.SHA256())
           .build(pw.encode()))
    pfx = pkcs12.serialize_key_and_certificates(alias.encode(), key, cert, chain or None, enc)
    return {"pfx": pfx, "passphrase": pw}


def para_redactar(alias: str) -> list[str]:
    """Nombre, apellidos y NIF del titular, para que sede.redactar() los enmascare. Solo para sede.py; no se imprime."""
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives.serialization import pkcs12

    cfg = _cargar_config()
    e = cfg[alias]
    _key, cert, _chain = pkcs12.load_key_and_certificates(Path(e["p12"]).read_bytes(), _contrasena(alias, e).encode())
    del _key
    vals: list[str] = []
    for oid in (NameOID.GIVEN_NAME, NameOID.SURNAME, NameOID.SERIAL_NUMBER):
        for a in cert.subject.get_attributes_for_oid(oid):
            v = str(a.value).replace("IDCES-", "").replace("VATES-", "")
            vals += [v] + v.split()
    particulas = {"DEL", "LAS", "LOS", "SAN", "SANTA"}  # "DE LA" etc.: enmascararlas taparía texto normal de la sede
    return [v for v in dict.fromkeys(vals) if len(v) >= 3 and v.upper() not in particulas]


# --------------------------------------------------------------------- comandos
def cmd_configurar(a) -> int:
    if not sys.stdin.isatty():
        _err("Este comando lo tiene que ejecutar la PERSONA en su terminal: el agente no puede introducir la contraseña.")
        return 2
    p12 = str(Path(a.p12).expanduser().resolve())
    if not Path(p12).exists():
        _err(f"no existe el fichero {p12}")
        return 1
    info = None
    if a.fichero_contrasena:
        entrada = {"p12": p12, "almacen": "fichero", "fichero_contrasena": str(Path(a.fichero_contrasena).resolve())}
        try:
            cand = _lineas_candidatas(a.fichero_contrasena)
        except Exception as ex:
            _err(f"no se pudo leer el fichero de contraseña: {ex}")
            return 1
        ultimo = None
        for i, linea in enumerate(cand):  # la contraseña suele ser la única línea; si hay más texto, se prueba cada una
            try:
                info = _info(_abrir(p12, linea))
                pw, entrada["linea"] = linea, i
                break
            except Exception as ex:
                ultimo = ex
        if info is None:
            _err(f"ninguna línea del fichero abre el certificado ({type(ultimo).__name__ if ultimo else 'vacío'}). "
                 "¿Contraseña correcta? ¿Formato antiguo (RC2/3DES)? Ver references/setup-*.md")
            return 1
    else:
        pw = getpass.getpass("Contraseña del certificado (no se mostrará): ")
        entrada = {"p12": p12, "almacen": "llavero"}
        try:
            info = _info(_abrir(p12, pw))
        except Exception as ex:
            _err(f"no se pudo abrir el certificado: {type(ex).__name__}. ¿Contraseña correcta? ¿Formato antiguo (RC2/3DES)? Ver references/setup-*.md")
            return 1
    if entrada["almacen"] == "llavero":
        import keyring
        try:
            keyring.set_password(SERVICIO, a.alias, pw)
        except Exception as ex:
            _err(f"no se pudo guardar en el llavero del sistema ({type(ex).__name__}). En Linux sin llavero usa "
                 "--fichero-contrasena con un fichero chmod 600 (references/setup-linux.md).")
            return 1
    del pw
    cfg = _cargar_config()
    entrada["anadido"] = dt.date.today().isoformat()
    cfg[a.alias] = entrada
    _guardar_config(cfg)
    _out({"ok": True, "alias": a.alias, **info})
    return 0


def cmd_listar(_a) -> int:
    cfg = _cargar_config()
    res = []
    for alias, e in cfg.items():
        item = {"alias": alias, "almacen": e.get("almacen")}
        try:
            item.update(_info(_abrir(e["p12"], _contrasena(alias, e))))
        except Exception as ex:
            item["error"] = type(ex).__name__
        res.append(item)
    _out({"titulares": res, "config": str(CONFIG)})
    return 0


def cmd_comprobar(a) -> int:
    cfg = _cargar_config()
    if a.alias not in cfg:
        _out({"ok": False, "error": f"'{a.alias}' no configurado"})
        return 1
    try:
        info = _info(_abrir(cfg[a.alias]["p12"], _contrasena(a.alias, cfg[a.alias])))
        _out({"ok": True, "alias": a.alias, **info})
        return 0
    except Exception as ex:
        _out({"ok": False, "alias": a.alias, "error": type(ex).__name__})
        return 1


def cmd_olvidar(a) -> int:
    cfg = _cargar_config()
    e = cfg.pop(a.alias, None)
    if e and e.get("almacen") == "llavero":
        try:
            import keyring
            keyring.delete_password(SERVICIO, a.alias)
        except Exception:
            pass
    _guardar_config(cfg)
    _out({"ok": e is not None, "alias": a.alias})
    return 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("configurar")
    c.add_argument("--alias", required=True)
    c.add_argument("--p12", required=True)
    c.add_argument("--fichero-contrasena")
    sub.add_parser("listar")
    for n in ("comprobar", "olvidar"):
        s = sub.add_parser(n)
        s.add_argument("--alias", required=True)
    a = ap.parse_args()
    return {"configurar": cmd_configurar, "listar": cmd_listar, "comprobar": cmd_comprobar, "olvidar": cmd_olvidar}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
