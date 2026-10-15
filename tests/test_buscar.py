"""buscar.py: trámites sobre los assets/_sedes-*.yaml reales y municipios con un municipios.csv de prueba."""
from __future__ import annotations

import json
import shutil
import sys

import pytest

CABECERA = "municipio,provincia,ccaa,ine,sede_url,web,plataforma,confianza,recaudador\n"
FILAS = [
    "Villa Ficticia de Abajo,Provincia Ficticia,Comunidad Ficticia,99001,"
    "https://villaficticia.sedelectronica.es,,gestiona,alta,Consorcio Ficticio",
    "Villa Ficticia,Provincia Ficticia,Comunidad Ficticia,99002,,,tao-sta,media,",
    "Pueblo Inventado,Provincia Ficticia,Comunidad Ficticia,99003,,,plataforma-inexistente,baja,",
    "Aldea Sin Plataforma,Provincia Ficticia,Comunidad Ficticia,99004,,,,baja,",
]


def _csv(carpeta, filas) -> None:
    (carpeta / "municipios.csv").write_text(CABECERA + "\n".join(filas) + "\n", encoding="utf-8")


@pytest.fixture
def municipios(buscar, skill, tmp_path, monkeypatch):
    """assets/ temporal: las sedes reales más un municipios.csv ficticio (las guías siguen siendo las reales)."""
    for p in (skill / "assets").glob("*sedes*.yaml"):
        shutil.copy(p, tmp_path / p.name)
    _csv(tmp_path, FILAS)
    monkeypatch.setattr(buscar, "ASSETS", tmp_path)
    return tmp_path


def _tramites(res: list[dict]) -> list[str]:
    return [r["tramite"] for r in res if r["tipo"] == "tramite"]


# ------------------------------------------------------------------ municipios
def test_municipio_exacto_con_receta(buscar, municipios):
    (r,) = buscar.buscar_municipio("Villa Ficticia de Abajo")
    assert r["tipo"] == "municipio"
    assert r["municipio"] == "Villa Ficticia de Abajo"
    assert r["plataforma"] == "gestiona"
    assert r["guia"] == "references/plataforma-gestiona.md"
    assert r["sede_url"] == "https://villaficticia.sedelectronica.es"
    assert r["web"] is None
    assert r["recaudador"] == "Consorcio Ficticio"
    assert r["nota"] is None


@pytest.mark.parametrize("consulta", [
    "villa ficticia de abajo",
    "VILLA FICTÍCIA DE ABAJO",
    "Villa-Ficticia-de-Abajo",
    "  villa   ficticia de_abajo ",
])
def test_municipio_ignora_mayusculas_tildes_y_separadores(buscar, municipios, consulta):
    assert [r["municipio"] for r in buscar.buscar_municipio(consulta)] == ["Villa Ficticia de Abajo"]


def test_municipio_exacto_gana_al_parcial(buscar, municipios):
    assert [r["municipio"] for r in buscar.buscar_municipio("Villa Ficticia")] == ["Villa Ficticia"]


def test_municipio_parcial(buscar, municipios):
    assert [r["municipio"] for r in buscar.buscar_municipio("Ficticia de Abajo")] == ["Villa Ficticia de Abajo"]
    assert len(buscar.buscar_municipio("Ficticia")) == 2
    assert len(buscar.buscar_municipio("Ficticia", limite=1)) == 1


@pytest.mark.parametrize("consulta, plataforma", [
    ("Pueblo Inventado", "plataforma-inexistente"),
    ("Aldea Sin Plataforma", "desconocida"),
])
def test_municipio_sin_receta_va_a_reg_sir(buscar, municipios, consulta, plataforma):
    (r,) = buscar.buscar_municipio(consulta)
    assert r["plataforma"] == plataforma
    assert r["guia"] == "references/registro-reg-sir.md"
    assert "REG/SIR" in r["nota"]


def test_municipio_con_otra_receta(buscar, municipios, skill):
    (r,) = buscar.buscar_municipio("Villa Ficticia")
    assert r["guia"] == "references/plataforma-tao-sta.md"
    assert (skill / r["guia"]).is_file()


def test_sin_municipios_csv(buscar, tmp_path, monkeypatch):
    monkeypatch.setattr(buscar, "ASSETS", tmp_path)
    assert buscar.buscar_municipio("Villa Ficticia") == []


def test_municipio_corto_no_casa_dentro_de_palabras(buscar, tmp_path, monkeypatch):
    _csv(tmp_path, ["Ea,Provincia Ficticia,Comunidad Ficticia,99005,,,,baja,"])
    monkeypatch.setattr(buscar, "ASSETS", tmp_path)
    assert buscar.buscar_municipio("consultar una tarea pendiente") == []


def test_consulta_vacia_no_devuelve_municipios(buscar, municipios):
    assert buscar.buscar_municipio("") == []


# ------------------------------------------------------------------ trámites (assets reales)
def test_carga_las_sedes_reales(buscar):
    sedes = buscar.cargar_sedes()
    assert {"aeat", "tgss", "dehu", "atc", "reg-age"} <= set(sedes)
    assert sum(len(s.get("tramites") or []) for s in sedes.values()) > 50


def test_norm_y_palabras(buscar):
    assert buscar.norm("Árbol-Ñandú_x  y") == "arbol nandu x y"
    assert buscar.palabras("Certificado de estar al corriente") == {"certificado", "estar", "corriente"}


def test_certificado_estar_al_corriente(buscar):
    res = buscar.buscar_tramite("certificado de estar al corriente")
    # Los dos estatales con las tres palabras van primero (lo general antes que lo local).
    assert set(_tramites(res)[:2]) == {"aeat-certificado-corriente", "tgss-certificado-corriente"}
    aeat = next(r for r in res if r.get("tramite") == "aeat-certificado-corriente")
    assert aeat["sede"] == "aeat"
    assert aeat["riesgo"] == "actuar"
    assert aeat["guia"] == "references/tramite-certificado-corriente.md"
    assert aeat["verificado_el"]


def test_vida_laboral(buscar):
    res = buscar.buscar_tramite("vida laboral")
    r = next(r for r in res if r.get("tramite") == "tgss-vida-laboral")
    assert r["sede"] == "tgss"
    assert r["riesgo"] == "leer"
    assert r["guia"] == "references/sede-tgss-importass.md"


def test_notificaciones_empieza_por_el_playbook(buscar):
    res = buscar.buscar_tramite("notificaciones")
    assert res[0] == {"tipo": "guia", "guia": "references/tramite-vigilar-notificaciones.md"}
    assert len(res) <= 6


@pytest.mark.parametrize("consulta", [
    "certificado de estar al corriente", "vida laboral", "notificaciones", "recibos IBI",
    "modelo 420", "deudas hacienda", "instancia general", "datos censales",
])
def test_las_guias_devueltas_existen(buscar, skill, consulta):
    res = buscar.buscar_tramite(consulta)
    assert res, consulta
    for r in res:
        assert r["guia"].startswith("references/"), r
        assert (skill / r["guia"]).is_file(), r


def test_tildes_y_mayusculas_no_cambian_el_resultado(buscar):
    assert buscar.buscar_tramite("VIDA LABORAL") == buscar.buscar_tramite("vida laboral")
    assert (buscar.buscar_tramite("certificado de estár al corriente")
            == buscar.buscar_tramite("certificado de estar al corriente"))


def test_tramite_inexistente(buscar):
    assert buscar.buscar_tramite("xyzzy qwerty") == []


# ------------------------------------------------------------------ main() (JSON por stdout)
def _main(buscar, monkeypatch, capsys, *args) -> dict:
    monkeypatch.setattr(sys, "argv", ["buscar.py", *args])
    assert buscar.main() == 0
    return json.loads(capsys.readouterr().out)


def test_main_tramite(buscar, municipios, monkeypatch, capsys):
    salida = _main(buscar, monkeypatch, capsys, "vida laboral")
    assert salida["consulta"] == "vida laboral"
    assert "tgss-vida-laboral" in _tramites(salida["resultados"])


def test_main_municipio(buscar, municipios, monkeypatch, capsys):
    salida = _main(buscar, monkeypatch, capsys, "--municipio", "Villa Ficticia de Abajo")
    assert [r["municipio"] for r in salida["resultados"]] == ["Villa Ficticia de Abajo"]


def test_main_sin_resultados(buscar, municipios, monkeypatch, capsys):
    salida = _main(buscar, monkeypatch, capsys, "xyzzy qwerty")
    assert [r["tipo"] for r in salida["resultados"]] == ["sin_resultados"]
