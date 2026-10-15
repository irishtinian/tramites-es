"""install.sh e install.ps1: sin red, sin privilegios, sin enlaces simbólicos y con confirmación humana."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SKILL = "tramites-es"

PROHIBIDO = re.compile(
    r"\b(curl|wget|Invoke-WebRequest|Invoke-RestMethod|iwr|irm|iex|Invoke-Expression|Start-BitsTransfer|"
    r"DownloadFile|DownloadString|WebClient|sudo|doas|runas|Start-Process|mklink|SymbolicLink|git\s+clone|"
    r"npx|pip\s+install|ln\s+-s)\b", re.I)


@pytest.mark.parametrize("nombre", ["install.sh", "install.ps1"])
def test_instaladores_sin_red_ni_privilegios(nombre):
    texto = (RAIZ / nombre).read_text(encoding="utf-8")
    m = PROHIBIDO.search(texto)
    assert m is None, f"{nombre} contiene '{m.group(0)}'"
    assert "skills" in texto and SKILL in texto


def test_install_ps1_solo_ascii():
    # Windows PowerShell 5.1 lee los .ps1 sin BOM con la página de códigos del sistema.
    assert (RAIZ / "install.ps1").read_bytes().isascii()


def test_install_sh_posix():
    datos = (RAIZ / "install.sh").read_bytes()
    assert datos.startswith(b"#!/bin/sh\n")
    assert b"\r\n" not in datos
    assert b"set -eu" in datos


def _instalados(casa: Path) -> list[Path]:
    return sorted(p for p in casa.rglob("SKILL.md") if p.parent.name == SKILL)


# ------------------------------------------------------------------ install.sh de verdad (Linux y macOS)
posix = pytest.mark.skipif(sys.platform == "win32" or shutil.which("sh") is None, reason="install.sh es para Linux y macOS")
sin_root = pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="install.sh se niega a ejecutarse como root")


@posix
@sin_root
def test_install_sh_sin_terminal_no_copia_nada(casa):
    r = subprocess.run(["sh", str(RAIZ / "install.sh")], stdin=subprocess.DEVNULL, capture_output=True,
                       timeout=120, env={**os.environ, "HOME": str(casa)})
    assert r.returncode == 1
    salida = r.stdout.decode("utf-8", "replace")
    assert "SKILL.md" in salida and ".agents/skills/tramites-es" in salida  # enseña el plan antes de preguntar
    assert "terminal interactiva" in r.stderr.decode("utf-8", "replace")
    assert _instalados(casa) == []


def _con_terminal(casa: Path, respuesta: bytes) -> subprocess.CompletedProcess:
    import pty
    maestro, esclavo = pty.openpty()
    try:
        proc = subprocess.Popen(["sh", str(RAIZ / "install.sh")], stdin=esclavo, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env={**os.environ, "HOME": str(casa)})
        os.write(maestro, respuesta)
        salida, errores = proc.communicate(timeout=120)
    finally:
        os.close(esclavo)
        os.close(maestro)
    return subprocess.CompletedProcess(proc.args, proc.returncode, salida, errores)


@posix
@sin_root
def test_install_sh_copia_tras_confirmar(casa):
    (casa / ".hermes" / "skills").mkdir(parents=True)   # Hermes instalado con carpeta de skills
    (casa / ".openclaw").mkdir()                         # OpenClaw sin carpeta de skills: solo aviso
    viejo = casa / ".claude" / "skills" / SKILL
    viejo.mkdir(parents=True)
    (viejo / "obsoleto.txt").write_text("de una versión anterior", encoding="utf-8")

    r = _con_terminal(casa, b"s\n")
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    instalados = {p.parent.parent for p in _instalados(casa)}
    assert instalados == {casa / ".agents" / "skills", casa / ".claude" / "skills", casa / ".hermes" / "skills"}
    assert not (casa / ".openclaw" / "skills").exists()
    assert "Aviso" in r.stdout.decode("utf-8", "replace")
    assert not (viejo / "obsoleto.txt").exists()          # la copia anterior se sustituye entera
    for destino in instalados:
        copia = destino / SKILL
        assert (copia / "scripts" / "cert.py").is_file()
        assert not any(p.is_symlink() for p in copia.rglob("*"))
        assert not list(destino.glob(f".{SKILL}.nuevo.*"))  # sin restos temporales
    origen = RAIZ / "skills" / SKILL
    esperados = sorted(p.relative_to(origen) for p in origen.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    copiados = sorted(p.relative_to(casa / ".agents" / "skills" / SKILL)
                      for p in (casa / ".agents" / "skills" / SKILL).rglob("*") if p.is_file())
    assert copiados == esperados


@posix
@sin_root
def test_install_sh_cancelar_no_copia_nada(casa):
    r = _con_terminal(casa, b"n\n")
    assert r.returncode == 0
    assert "Cancelado" in r.stdout.decode("utf-8", "replace")
    assert _instalados(casa) == []


# ------------------------------------------------------------------ install.ps1 (Windows, o pwsh donde exista)
POWERSHELL = shutil.which("pwsh") or (shutil.which("powershell") if sys.platform == "win32" else None)


@pytest.mark.skipif(POWERSHELL is None, reason="no hay PowerShell en este equipo")
def test_install_ps1_sin_consola_no_copia_nada(casa):
    r = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
                        str(RAIZ / "install.ps1")], stdin=subprocess.PIPE, capture_output=True,
                       timeout=180, env={**os.environ, "USERPROFILE": str(casa), "HOME": str(casa)})
    salida = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    assert r.returncode == 1, salida
    if "administrador" in salida:
        # Los runners Windows de GitHub se ejecutan elevados: install.ps1 se niega antes de enseñar el plan.
        assert "no lo ejecutes como administrador" in salida
    else:
        assert "SKILL.md" in salida and "consola interactiva" in salida  # enseña el plan antes de preguntar
    assert _instalados(casa) == []
