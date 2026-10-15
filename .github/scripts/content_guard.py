#!/usr/bin/env python3
"""content_guard.py — guarda de contenido de tramites-es (solo biblioteca estándar, sin red).

Revisa todos los ficheros versionados (o, sin git, el árbol de la carpeta) y falla si encuentra:
  1. Unicode invisible o de control bidi (zero-width, bidi, etiquetas Unicode, BOM...).
  2. Datos personales: NIF, NIE y CIF con dígito de control válido, IBAN ES válido y emails reales.
     Los marcadores (<NIF>, <IBAN>, <EMAIL>...) y los dominios reservados (example.com, *.example,
     *.invalid, *.test) están permitidos. Los CIF de entes públicos (P, Q, S) no son datos personales.
  3. Dominios de assets/*.yaml que no estén en assets/dominios-oficiales.yaml ni en
     .github/content-guard/dominios-revisados.txt, URLs sin https, IPs, punycode o hosts no ASCII.
  4. URLs acortadas (ocultan el destino real).
  5. Ficheros binarios que no estén en .github/content-guard/binarios-permitidos.txt, y cualquier
     fichero de certificado o clave privada (.p12, .pfx, .pem, .key...).

Uso:  python .github/scripts/content_guard.py [--raiz RUTA]
Sale con 1 si hay hallazgos. En GitHub Actions los escribe como anotaciones y en el resumen del job.
"""
from __future__ import annotations

import argparse
import ipaddress
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

LISTAS = Path(".github") / "content-guard"

# ------------------------------------------------------------------ 1. Unicode invisible
# Rangos de puntos de código (se construye la clase con chr() para que este fichero no los contenga).
_RANGOS_INVISIBLES = (
    (0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C), (0x115F, 0x1160), (0x17B4, 0x17B5),
    (0x180E, 0x180E), (0x200B, 0x200F), (0x202A, 0x202E), (0x2060, 0x2064), (0x2066, 0x2069),
    (0x3164, 0x3164), (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xE0000, 0xE007F),
)
INVISIBLES = re.compile("[" + "".join(re.escape(chr(a)) + ("-" + re.escape(chr(b)) if b != a else "")
                                       for a, b in _RANGOS_INVISIBLES) + "]")

# ------------------------------------------------------------------ 2. datos personales
LETRAS_NIF = "TRWAGMYFPDXBNJZSQVHLCKE"
RE_NIF = re.compile(r"(?<![A-Za-z0-9])(\d{8})[- ]?([A-Za-z])(?![A-Za-z0-9])")
RE_NIE = re.compile(r"(?<![A-Za-z0-9])([XYZxyz])[- ]?(\d{7})[- ]?([A-Za-z])(?![A-Za-z0-9])")
# Sin P, Q ni S: son entes públicos (ayuntamientos, organismos), su CIF no es un dato personal.
RE_CIF = re.compile(r"(?<![A-Za-z0-9])([ABCDEFGHJNRUVW])[- ]?(\d{7})([0-9A-J])(?![A-Za-z0-9])")
RE_IBAN = re.compile(r"(?<![A-Za-z0-9])ES(\d{2})((?: ?\d{4}){5})(?![0-9])")
RE_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@((?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})(?![\w-])")
DOMINIOS_EMAIL_PERMITIDOS = ("example.com", "example.org", "example.net", "users.noreply.github.com")
TLD_RESERVADOS = (".example", ".invalid", ".test", ".localhost")


def nif_valido(numero: str, letra: str) -> bool:
    return LETRAS_NIF[int(numero) % 23] == letra.upper()


def nie_valido(prefijo: str, numero: str, letra: str) -> bool:
    return nif_valido(str("XYZ".index(prefijo.upper())) + numero, letra)


def cif_valido(digitos: str, control: str) -> bool:
    pares = sum(int(d) for d in digitos[1::2])
    impares = sum(sum(divmod(2 * int(d), 10)) for d in digitos[0::2])
    c = (10 - (pares + impares) % 10) % 10
    return control in (str(c), "JABCDEFGHI"[c])


def iban_valido(control: str, bban: str) -> bool:
    return int(bban + "1428" + control) % 97 == 1


def email_permitido(dominio: str) -> bool:
    d = dominio.lower()
    return d in DOMINIOS_EMAIL_PERMITIDOS or d.endswith(TLD_RESERVADOS)


def datos_personales(linea: str) -> list[str]:
    """Devuelve una descripción (enmascarada) de cada dato personal válido de la línea."""
    res = []
    for m in RE_NIF.finditer(linea):
        if nif_valido(m.group(1), m.group(2)):
            res.append(f"NIF válido (…{m.group(1)[-3:]}{m.group(2)})")
    for m in RE_NIE.finditer(linea):
        if nie_valido(m.group(1), m.group(2), m.group(3)):
            res.append(f"NIE válido ({m.group(1)}…{m.group(3)})")
    for m in RE_CIF.finditer(linea):
        if cif_valido(m.group(2), m.group(3)):
            res.append(f"CIF válido ({m.group(1)}…{m.group(3)})")
    for m in RE_IBAN.finditer(linea):
        if iban_valido(m.group(1), m.group(2).replace(" ", "")):
            res.append("IBAN español válido")
    for m in RE_EMAIL.finditer(linea):
        if not email_permitido(m.group(1)):
            res.append(f"email (…@{m.group(1)})")
    return res


# ------------------------------------------------------------------ 3 y 4. URLs y dominios
RE_URL = re.compile(r"(https?)://([^\s/?#\"'<>()\[\]{}|\\^`,;*]+)", re.I)
ACORTADORES = frozenset("""
    bit.ly bitly.com tinyurl.com t.co goo.gl ow.ly is.gd v.gd buff.ly rebrand.ly cutt.ly shorturl.at
    tiny.cc rb.gy t.ly lnkd.in s.id bl.ink soo.gd qr.ae adf.ly shorte.st x.gd tiny.one trib.al dlvr.it
    ift.tt aka.ms amzn.to forms.gle g.co goo.su clck.ru wp.me fb.me git.io surl.li short.gy urlz.fr
    cutt.us t1p.de 2no.co
""".split())


def host_de(autoridad: str) -> str:
    """'usuario@host:443' -> 'host' (en minúsculas y sin punto final)."""
    return autoridad.rsplit("@", 1)[-1].split(":", 1)[0].rstrip(".").lower()


def es_acortador(host: str) -> bool:
    return host in ACORTADORES or host.removeprefix("www.") in ACORTADORES


def leer_lista(ruta: Path) -> list[str]:
    """Una entrada por línea; '#' empieza un comentario."""
    if not ruta.exists():
        return []
    res = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        v = linea.split("#", 1)[0].strip()
        if v:
            res.append(v.lower())
    return res


def listas_yaml_simples(texto: str) -> dict[str, list[str]]:
    """Lee las listas de primer nivel de un YAML sencillo (clave:\\n  - valor) sin depender de PyYAML."""
    res: dict[str, list[str]] = {}
    clave = None
    for linea in texto.splitlines():
        sin = linea.split("#", 1)[0].rstrip()
        if not sin.strip():
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):", sin)
        if m:
            clave = m.group(1)
            res.setdefault(clave, [])
            continue
        m = re.match(r"^\s+-\s+(['\"]?)([^'\"]+)\1\s*$", sin)
        if m and clave:
            res[clave].append(m.group(2).strip())
    return res


def dominios_permitidos(raiz: Path) -> tuple[tuple[str, ...], frozenset[str]]:
    sufijos: list[str] = []
    hosts: list[str] = []
    for p in sorted(raiz.glob("skills/*/assets/dominios-oficiales.yaml")):
        listas = listas_yaml_simples(p.read_text(encoding="utf-8"))
        sufijos += [s.lower() for s in listas.get("sufijos", [])]
        hosts += [h.lower() for h in listas.get("hosts", [])]
    for v in leer_lista(raiz / LISTAS / "dominios-revisados.txt"):
        (sufijos if v.startswith(".") else hosts).append(v)
    return tuple(sufijos), frozenset(hosts)


def dominio_permitido(host: str, sufijos: tuple[str, ...], hosts: frozenset[str]) -> bool:
    return host in hosts or ("." + host).endswith(sufijos)


def problema_de_host(esquema: str, host: str) -> str | None:
    if esquema.lower() != "https":
        return "URL sin https"
    if not host.isascii():
        return "host no ASCII (posible homógrafo)"
    if host.startswith("xn--") or ".xn--" in host:
        return "host en punycode (posible homógrafo)"
    try:
        ipaddress.ip_address(host.strip("[]"))
        return "IP en lugar de dominio"
    except ValueError:
        return None


# ------------------------------------------------------------------ 5. binarios
CERTIFICADOS = (".p12", ".pfx", ".pem", ".key", ".jks", ".keystore", ".der", ".cer", ".crt", ".p7b", ".p8")


def es_binario(ruta: Path) -> bool:
    with ruta.open("rb") as f:
        return b"\0" in f.read(8192)


# ------------------------------------------------------------------ recorrido
class Hallazgo(NamedTuple):
    tipo: str
    fichero: str
    linea: int
    detalle: str


IGNORAR_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules", ".mypy_cache", ".ruff_cache"}


def ficheros(raiz: Path) -> list[Path]:
    """Ficheros versionados (o pendientes de añadir) según git; sin git, el árbol entero."""
    try:
        r = subprocess.run(["git", "-C", str(raiz), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, timeout=60, check=False)
        if r.returncode == 0 and r.stdout:
            rutas = {raiz / p for p in r.stdout.decode("utf-8").split("\0") if p}
            return sorted(p for p in rutas if p.is_file())
    except (OSError, subprocess.SubprocessError):
        pass
    res = []
    for dirpath, dirnames, filenames in os.walk(raiz):
        dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIRS]
        res += [Path(dirpath) / f for f in filenames]
    return sorted(res)


def es_asset_yaml(rel: str) -> bool:
    partes = rel.split("/")
    return (len(partes) == 4 and partes[0] == "skills" and partes[2] == "assets"
            and partes[3].endswith((".yaml", ".yml")))


def revisar(raiz: Path) -> list[Hallazgo]:
    raiz = raiz.resolve()
    sufijos, hosts = dominios_permitidos(raiz)
    binarios_ok = set(leer_lista(raiz / LISTAS / "binarios-permitidos.txt"))
    hallazgos: list[Hallazgo] = []
    for p in ficheros(raiz):
        rel = p.relative_to(raiz).as_posix()
        if rel.lower().endswith(CERTIFICADOS):
            hallazgos.append(Hallazgo("certificado", rel, 0, "fichero de certificado o clave privada: nunca se sube al repositorio"))
            continue
        if es_binario(p):
            if rel.lower() not in binarios_ok:
                hallazgos.append(Hallazgo("binario", rel, 0, "fichero binario nuevo: necesita revisión y estar en "
                                          f"{(LISTAS / 'binarios-permitidos.txt').as_posix()}"))
            continue
        try:
            texto = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            hallazgos.append(Hallazgo("codificacion", rel, 0, "no es UTF-8"))
            continue
        asset = es_asset_yaml(rel)
        for n, linea in enumerate(texto.splitlines(), 1):
            for m in INVISIBLES.finditer(linea):
                hallazgos.append(Hallazgo("unicode-invisible", rel, n, f"carácter U+{ord(m.group(0)):04X}"))
            for d in datos_personales(linea):
                hallazgos.append(Hallazgo("dato-personal", rel, n, d))
            for m in RE_URL.finditer(linea):
                esquema, host = m.group(1), host_de(m.group(2))
                if es_acortador(host):
                    hallazgos.append(Hallazgo("url-acortada", rel, n, f"{host}: enlaza al destino real"))
                if asset:
                    problema = problema_de_host(esquema, host)
                    if problema:
                        hallazgos.append(Hallazgo("dominio", rel, n, f"{host}: {problema}"))
                    elif not dominio_permitido(host, sufijos, hosts):
                        hallazgos.append(Hallazgo("dominio-nuevo", rel, n,
                                                  f"{host} no está en la lista blanca. Si es una Administración pública, "
                                                  "añádelo con su fuente oficial a assets/dominios-oficiales.yaml (si se le "
                                                  "presenta el certificado) o a .github/content-guard/dominios-revisados.txt. "
                                                  "Necesita revisión de CODEOWNERS."))
    return hallazgos


def _escapar(v: str, propiedad: bool = False) -> str:
    """Escapado de los comandos de flujo de GitHub Actions (::error ...::)."""
    v = v.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return v.replace(":", "%3A").replace(",", "%2C") if propiedad else v


def informar(hallazgos: list[Hallazgo]) -> None:
    en_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for h in hallazgos:
        if en_actions:
            linea = f",line={h.linea}" if h.linea else ""
            print(f"::error file={_escapar(h.fichero, True)}{linea},"
                  f"title={_escapar('content-guard ' + h.tipo, True)}::{_escapar(h.detalle)}")
        else:
            print(f"{h.fichero}:{h.linea}: [{h.tipo}] {h.detalle}")
    resumen = os.environ.get("GITHUB_STEP_SUMMARY")
    if resumen:
        with open(resumen, "a", encoding="utf-8") as f:
            if not hallazgos:
                f.write("### content-guard: sin hallazgos\n")
            else:
                f.write(f"### content-guard: {len(hallazgos)} hallazgo(s)\n\n| Tipo | Fichero | Línea | Detalle |\n|---|---|---|---|\n")
                for h in hallazgos:
                    f.write(f"| {h.tipo} | `{h.fichero}` | {h.linea or ''} | {h.detalle.replace('|', '/')} |\n")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", default=Path(__file__).resolve().parents[2], type=Path)
    a = ap.parse_args()
    hallazgos = revisar(a.raiz)
    informar(hallazgos)
    if hallazgos:
        print(f"content-guard: {len(hallazgos)} hallazgo(s). Revisa el detalle arriba.", file=sys.stderr)
        return 1
    print("content-guard: sin hallazgos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
