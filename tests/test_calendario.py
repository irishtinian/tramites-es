"""calendario.py: `validar` sobre assets/calendario.yaml y `proximos` con --desde fijo (sin depender de hoy)."""
from __future__ import annotations

import json
import sys
from datetime import date

import pytest

TERRITORIOS = ["comun", "canarias", "ceuta", "melilla", "navarra", "bizkaia", "gipuzkoa", "alava"]


def _correr(calendario, monkeypatch, capsys, *args) -> tuple[int, dict]:
    monkeypatch.setattr(sys, "argv", ["calendario.py", *args])
    with pytest.raises(SystemExit) as fin:
        calendario.main()
    return fin.value.code, json.loads(capsys.readouterr().out)


def _proximos(calendario, monkeypatch, capsys, *args) -> dict:
    codigo, r = _correr(calendario, monkeypatch, capsys, "proximos", *args)
    assert codigo == 0 and r["ok"] is True, r
    return r


def _modelos(r: dict) -> set[str]:
    return {f["modelo"] for f in r["vencimientos"]}


# ------------------------------------------------------------------ validar
def test_validar_datos_reales(calendario, monkeypatch, capsys):
    codigo, r = _correr(calendario, monkeypatch, capsys, "validar")
    assert codigo == 0, r["errores"]
    assert r["ok"] is True and r["errores"] == []
    assert r["entradas"] > 50
    assert r["fuentes"] > 10
    assert sum(r["filas_por_estado"].values()) == r["filas_por_modelo"]


CALENDARIO_ROTO = """\
verificado_el: 2026-10-15
cobertura: {desde: 2026-10-01, hasta: 2026-12-31}
obligaciones:
  "303": {nombre: "IVA", organismo: AEAT}
fuentes:
  buena: {titulo: "Fuente con https", url: "https://www.boe.es/"}
  mala: {titulo: "Fuente sin https", url: "http://www.boe.es/"}
vencimientos:
  - {id: repetido, fecha: 2026-10-20, tipo: presentacion, modelos: ["303"], organismo: AEAT, territorios: [comun],
     descripcion: "x", estado: verificado, fuentes: [buena]}
  - {id: repetido, fecha: 2026-10-20, tipo: presentacion, modelos: ["999"], organismo: AEAT, territorios: [marte],
     descripcion: "x", estado: regla, fuentes: [inventada], domiciliacion_hasta: 2026-10-25}
  - {id: fuera, fecha: 2027-06-01, tipo: rara, modelos: ["303"], organismo: AEAT, territorios: [comun],
     descripcion: "x", estado: dudoso, fuentes: [buena]}
"""


def test_validar_detecta_errores(calendario, tmp_path, monkeypatch, capsys):
    datos = tmp_path / "calendario.yaml"
    datos.write_text(CALENDARIO_ROTO, encoding="utf-8")
    monkeypatch.setattr(calendario, "DATOS", datos)
    codigo, r = _correr(calendario, monkeypatch, capsys, "validar")
    assert codigo == 1 and r["ok"] is False
    esperados = [
        "fuente mala: url ausente o no https",
        "repetido: id repetido",
        "repetido: estado regla sin texto de regla",
        "repetido: la domiciliación acaba después del plazo",
        "repetido: territorio 'marte' desconocido",
        "repetido: modelo '999' no está en el catálogo de obligaciones",
        "repetido: fuente 'inventada' no definida",
        "fuera: estado 'dudoso' no válido",
        "fuera: tipo 'rara' no válido",
        "fuera: fecha 2027-06-01 fuera de la cobertura",
    ]
    for e in esperados:
        assert e in r["errores"], (e, r["errores"])


# ------------------------------------------------------------------ proximos
def test_proximos_territorio_comun(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "comun", "--dias", "10", "--desde", "2026-10-15")
    assert (r["desde"], r["hasta"]) == ("2026-10-15", "2026-10-25")
    assert {"303", "130", "111"} <= _modelos(r)
    assert "420" not in _modelos(r)
    assert r["total"] == len(r["vencimientos"])
    assert r["antiguedad_datos_dias"] == 0
    assert not any("se verificaron" in a for a in r["avisos"])
    desde, hasta = date(2026, 10, 15), date(2026, 10, 25)
    for f in r["vencimientos"]:
        fecha = date.fromisoformat(f["fecha"])
        assert desde <= fecha <= hasta
        assert f["dias_restantes"] == (fecha - desde).days
        assert f["estado"] in ("verificado", "regla")
        assert f["fuentes"] and all(x.get("url", "").startswith("https://") for x in f["fuentes"])
    claves = [(f["fecha"], f["modelo"]) for f in r["vencimientos"]]
    assert claves == sorted(claves)
    iva = next(f for f in r["vencimientos"] if f["modelo"] == "303")
    assert iva["fecha"] == "2026-10-20" and iva["dias_restantes"] == 5
    assert iva["domiciliacion"] == {"hasta": "2026-10-15", "estado": "verificado", "abierta": True}


def test_proximos_canarias_usa_igic_y_no_iva(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "canarias", "--dias", "10", "--desde", "2026-10-15")
    assert {"420", "130"} <= _modelos(r)
    assert not {"303", "349"} & _modelos(r)


def test_proximos_domiciliacion_cerrada(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "comun", "--dias", "5", "--desde", "2026-10-16")
    iva = next(f for f in r["vencimientos"] if f["modelo"] == "303")
    assert iva["domiciliacion"]["abierta"] is False


def test_proximos_filtra_obligaciones(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "comun", "--dias", "10",
                  "--desde", "2026-10-15", "--obligaciones", "303, 999")
    assert _modelos(r) == {"303"}
    assert r["filtro_obligaciones"] == ["303", "999"]
    assert any("999" in a for a in r["avisos"])


def test_proximos_avisa_de_datos_antiguos(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "comun", "--dias", "30", "--desde", "2027-01-10")
    assert r["antiguedad_datos_dias"] == 87
    assert any("más de 60" in a for a in r["avisos"])
    for f in r["vencimientos"]:
        assert "2027-01-10" <= f["fecha"] <= "2027-02-09"


def test_proximos_avisa_fuera_de_cobertura(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "comun", "--dias", "30", "--desde", "2027-12-20")
    assert any("cobertura" in a for a in r["avisos"])


def test_proximos_territorio_parcial_enlaza_su_calendario(calendario, monkeypatch, capsys):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", "navarra", "--dias", "30", "--desde", "2026-10-15")
    assert r["cobertura_territorio"] == "parcial"
    assert any("https://www.navarra.es/es/hacienda/calendario-fiscal" in a for a in r["avisos"])


def test_proximos_rechaza_ventanas_absurdas(calendario, monkeypatch, capsys):
    codigo, r = _correr(calendario, monkeypatch, capsys, "proximos", "--territorio", "comun",
                        "--dias", "801", "--desde", "2026-10-15")
    assert codigo == 2 and r["ok"] is False


def test_territorio_desconocido(calendario, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["calendario.py", "proximos", "--territorio", "marte"])
    with pytest.raises(SystemExit) as fin:
        calendario.main()
    assert fin.value.code == 2


def test_lista_de_territorios(calendario):
    assert list(calendario.TERRITORIOS) == TERRITORIOS


@pytest.mark.parametrize("territorio", TERRITORIOS)
def test_no_verificados_nunca_se_presentan_como_plazo(calendario, monkeypatch, capsys, territorio):
    r = _proximos(calendario, monkeypatch, capsys, "--territorio", territorio, "--dias", "800", "--desde", "2026-10-01")
    for f in r["vencimientos"]:
        assert f["estado"] != "no_verificado" and "fecha" in f
    for f in r["no_verificados"]:
        assert f["estado"] == "no_verificado"
        assert "fecha" not in f and f["fecha_orientativa"]
        assert "NO es un plazo" in f["aviso"]


def test_sin_hitos(calendario, monkeypatch, capsys):
    args = ("--territorio", "canarias", "--dias", "800", "--desde", "2026-10-01")
    con = _proximos(calendario, monkeypatch, capsys, *args)
    sin = _proximos(calendario, monkeypatch, capsys, *args, "--sin-hitos")
    assert any(f["tipo"] == "hito" for f in con["vencimientos"] + con["no_verificados"])
    assert not any(f["tipo"] == "hito" for f in sin["vencimientos"] + sin["no_verificados"])
    assert [f for f in con["vencimientos"] if f["tipo"] != "hito"] == sin["vencimientos"]


def test_obligaciones_por_territorio(calendario, monkeypatch, capsys):
    _, canarias = _correr(calendario, monkeypatch, capsys, "obligaciones", "--territorio", "canarias")
    _, comun = _correr(calendario, monkeypatch, capsys, "obligaciones", "--territorio", "comun")
    en_canarias = {o["codigo"] for o in canarias["obligaciones"]}
    en_comun = {o["codigo"] for o in comun["obligaciones"]}
    assert "420" in en_canarias and "420" not in en_comun
    assert "303" in en_comun and "303" not in en_canarias
    assert all(o["entradas"] > 0 for o in canarias["obligaciones"])
