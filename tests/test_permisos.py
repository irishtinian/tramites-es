"""permisos.py: los permisos que la persona da a su agente (fichero en la casa temporal)."""
from __future__ import annotations

import json
import sys

import pytest


def _ejecutar(mod, monkeypatch, capsys, *args) -> tuple[int, dict | str]:
    monkeypatch.setattr(sys, "argv", ["permisos.py", *args])
    codigo = mod.main()
    out = capsys.readouterr().out
    try:
        return codigo, json.loads(out)
    except json.JSONDecodeError:
        return codigo, out


def test_ver_sin_fichero(permisos, monkeypatch, capsys):
    codigo, r = _ejecutar(permisos, monkeypatch, capsys, "ver")
    assert codigo == 0 and r["permitir"] == [] and r["actos"] == list(permisos.ACTOS)


def test_fijar_sin_terminal_se_niega(permisos, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", type("SinTerminal", (), {"isatty": lambda self: False})())
    codigo, r = _ejecutar(permisos, monkeypatch, capsys, "fijar", "todo")
    assert codigo == 2 and "terminal" in r["error"]
    assert not permisos.FICHERO.exists()


def test_fijar_ver_y_quitar(permisos, terminal, monkeypatch, capsys):
    codigo, r = _ejecutar(permisos, monkeypatch, capsys, "fijar", "firmar, presentar,cita")
    assert codigo == 0 and r["permitir"] == ["firmar", "presentar", "cita"]
    assert permisos.leer()["permitir"] == ["firmar", "presentar", "cita"]

    codigo, r = _ejecutar(permisos, monkeypatch, capsys, "ver")
    assert codigo == 0 and r["permitir"] == ["firmar", "presentar", "cita"] and r["fijado_el"]

    codigo, r = _ejecutar(permisos, monkeypatch, capsys, "quitar")
    assert codigo == 0 and not permisos.FICHERO.exists()


def test_fijar_todo(permisos, terminal, monkeypatch, capsys):
    codigo, r = _ejecutar(permisos, monkeypatch, capsys, "fijar", "todo")
    assert codigo == 0 and permisos.leer()["permitir"] == ["todo"]


def test_fijar_rechaza_actos_desconocidos(permisos, terminal, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["permisos.py", "fijar", "firmar,volar"])
    with pytest.raises(SystemExit, match="permisos desconocidos"):
        permisos.main()
    assert not permisos.FICHERO.exists()


def test_actos_iguales_en_sede_y_permisos(permisos, sede):
    assert permisos.ACTOS == sede.ACTOS


def test_lo_fijado_lo_lee_sede(permisos, sede, terminal, monkeypatch, capsys):
    _ejecutar(permisos, monkeypatch, capsys, "fijar", "todo")
    assert sede.permisos_usuario() == set(sede.ACTOS)
