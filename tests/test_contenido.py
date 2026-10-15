"""Contenido del repositorio: guías enlazadas, Unicode invisible, datos personales, dominios y validación.

Usa las mismas guardas que la CI (.github/scripts/content_guard.py y validate.py), así que
`pytest` en local falla por lo mismo que fallaría el PR. Los ejemplos "malos" se construyen al
vuelo para que este fichero no dispare la propia guarda.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / "skills" / "tramites-es"
ASSETS_YAML = sorted(SKILL.glob("assets/*.yaml"))
GUIAS = sorted(SKILL.glob("references/*.md"))

# references/<guía>.md citada en el texto (sin comodines ni plantillas como setup-*.md o plataforma-<slug>.md)
GUIA_EN_TEXTO = re.compile(
    r"(?<![/\w.-])(?:references/)?((?:sede|plataforma|plataformas|tramite|setup|registro|reglas|perfil|calendario"
    r"|canarias|ayudas)(?:-[a-z0-9]+)*\.md)\b")


def _guias(datos):
    if isinstance(datos, dict):
        for k, v in datos.items():
            if k == "guia":
                yield v
            yield from _guias(v)
    elif isinstance(datos, list):
        for v in datos:
            yield from _guias(v)


# ------------------------------------------------------------------ enlaces
@pytest.mark.parametrize("ruta", ASSETS_YAML, ids=lambda p: p.name)
def test_guias_enlazadas_desde_los_yaml_existen(ruta):
    for guia in _guias(yaml.safe_load(ruta.read_text(encoding="utf-8"))):
        assert isinstance(guia, str) and guia.startswith("references/"), (ruta.name, guia)
        assert (SKILL / guia).is_file(), (ruta.name, guia)


def test_los_yaml_enlazan_muchas_guias():
    total = sum(1 for r in ASSETS_YAML for _ in _guias(yaml.safe_load(r.read_text(encoding="utf-8"))))
    assert total > 100


@pytest.mark.parametrize("ruta", [SKILL / "SKILL.md", *GUIAS], ids=lambda p: p.name)
def test_guias_y_scripts_citados_en_el_texto_existen(ruta):
    texto = ruta.read_text(encoding="utf-8")
    for nombre in GUIA_EN_TEXTO.findall(texto):
        assert (SKILL / "references" / nombre).is_file(), nombre
    for nombre in re.findall(r"scripts/([a-z_]+\.py)", texto):
        assert (SKILL / "scripts" / nombre).is_file(), nombre


@pytest.mark.parametrize("ruta", [*sorted(RAIZ.glob("*.md")), SKILL / "SKILL.md", SKILL / "assets" / "FUENTES.md"],
                         ids=lambda p: p.name)
def test_enlaces_relativos_de_markdown(ruta):
    for destino in re.findall(r"\]\(([^)\s]+)\)", ruta.read_text(encoding="utf-8")):
        if re.match(r"[a-z][a-z0-9+.-]*:", destino) or destino.startswith("#"):
            continue
        assert (ruta.parent / destino.split("#", 1)[0]).exists(), destino


# ------------------------------------------------------------------ guarda de contenido sobre el repo
@pytest.fixture(scope="module")
def hallazgos_repo(guarda):
    return guarda.revisar(RAIZ)


@pytest.mark.parametrize("tipo", [
    "unicode-invisible", "dato-personal", "dominio", "dominio-nuevo", "url-acortada", "binario", "certificado",
    "codificacion",
])
def test_repositorio_sin_hallazgos(hallazgos_repo, tipo):
    malos = [h for h in hallazgos_repo if h.tipo == tipo]
    assert not malos, "\n".join(f"{h.fichero}:{h.linea}: {h.detalle}" for h in malos)


def test_repositorio_sin_ningun_hallazgo(hallazgos_repo):
    assert not hallazgos_repo, "\n".join(f"{h.fichero}:{h.linea}: [{h.tipo}] {h.detalle}" for h in hallazgos_repo)


def test_lector_simple_de_dominios_coincide_con_pyyaml(guarda):
    texto = (SKILL / "assets" / "dominios-oficiales.yaml").read_text(encoding="utf-8")
    simple, completo = guarda.listas_yaml_simples(texto), yaml.safe_load(texto)
    assert simple["sufijos"] == completo["sufijos"]
    assert simple["hosts"] == completo["hosts"]


# ------------------------------------------------------------------ detectores (casos sintéticos)
@pytest.mark.parametrize("codigo", [0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x202A, 0x202E, 0x2060, 0x2064,
                                    0x2066, 0x2069, 0xFEFF, 0xE0041])
def test_detecta_unicode_invisible(guarda, codigo):
    assert guarda.INVISIBLES.search("texto" + chr(codigo) + "normal")


@pytest.mark.parametrize("texto", ["ñandú", "Cl@ve", "€", "→", "—", "·", "⚠" + chr(0xFE0F), "«»", "¿?"])
def test_no_confunde_caracteres_normales(guarda, texto):
    assert not guarda.INVISIBLES.search(texto)


def test_detecta_datos_personales(guarda, ficticios):
    iban = ficticios.iban("21000418450200051332")
    positivos = [
        "NIF " + ficticios.nif(12345678),
        "nif:" + ficticios.nif(1),
        "NIE " + ficticios.nie("Y", 7654321),
        "CIF " + ficticios.cif("B", "7654321"),
        "IBAN " + iban,
        "IBAN " + " ".join(iban[i:i + 4] for i in range(0, len(iban), 4)),
        "escribe a " + "nombre.apellido" + "@" + "gmail.com",
    ]
    for texto in positivos:
        assert guarda.datos_personales(texto), texto


def test_permite_marcadores_y_datos_que_no_son_personales(guarda, ficticios):
    negativos = [
        "NIF <NIF>, NIE <NIE>, CIF <CIF>, IBAN <IBAN>, email <EMAIL>, titular <TITULAR>",
        "NIF " + ficticios.nif_erroneo(12345678),            # letra de control incorrecta
        "serialNumber IDCES-12345678A",                       # ídem
        "CIF del ayuntamiento " + ficticios.cif("P", "3800000"),  # ente público
        "IBAN ES" + "00" + "0" * 20,                          # control incorrecto
        "persona@correo.example, buzon@sede.invalid, info@example.com, x@dev.test",
        "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
        "gh skill install x/tramites-es tramites-es@v0.1.0",
        "importe de 12345678 euros; modelo 303",
    ]
    for texto in negativos:
        assert guarda.datos_personales(texto) == [], texto


def test_no_repite_el_dato_en_el_aviso(guarda, ficticios):
    nif = ficticios.nif(12345678)
    (aviso,) = guarda.datos_personales("NIF " + nif)
    assert nif not in aviso


def test_acortadores(guarda):
    assert guarda.es_acortador("bit.ly") and guarda.es_acortador("www.tinyurl.com") and guarda.es_acortador("aka.ms")
    assert not guarda.es_acortador("sede.agenciatributaria.gob.es")


def test_guarda_en_un_repositorio_sintetico(guarda, tmp_path, ficticios):
    assets = tmp_path / "skills" / "demo" / "assets"
    assets.mkdir(parents=True)
    (assets / "dominios-oficiales.yaml").write_text(
        "sufijos:\n  - .gob.es   # AGE\nhosts:\n  - sede.concreta.example\n", encoding="utf-8")
    (assets / "_sedes-demo.yaml").write_text(
        "sedes:\n"
        "  demo:\n"
        '    login: "https://sede.ficticia.gob.es/login"\n'
        '    origins: ["https://sede.concreta.example", "https://sede.revisada.example",\n'
        '              "https://sede.nueva-ficticia.example"]\n'
        '    sin_tls: "http://sede.ficticia.gob.es/"\n'
        '    ip: "https://192.0.2.10/"\n'
        '    puny: "https://xn--sede-9qa.example/"\n',
        encoding="utf-8")
    listas = tmp_path / ".github" / "content-guard"
    listas.mkdir(parents=True)
    (listas / "dominios-revisados.txt").write_text("# revisados\nsede.revisada.example   # fuente\n", encoding="utf-8")
    acortada = "https://" + "bit.ly/abc"
    (tmp_path / "notas.md").write_text(
        f"ver {acortada}\nNIF {ficticios.nif(12345678)}\nhola" + chr(0x200B) + "mundo\n", encoding="utf-8")
    (tmp_path / "imagen.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00")
    (tmp_path / "certificado.p12").write_bytes(b"no importa")

    por_tipo: dict[str, list] = {}
    for h in guarda.revisar(tmp_path):
        por_tipo.setdefault(h.tipo, []).append(h)

    assert [h.detalle.split(" ")[0] for h in por_tipo.pop("dominio-nuevo")] == ["sede.nueva-ficticia.example"]
    problemas = " | ".join(h.detalle for h in por_tipo.pop("dominio"))
    assert "URL sin https" in problemas and "IP" in problemas and "punycode" in problemas
    assert [h.fichero for h in por_tipo.pop("url-acortada")] == ["notas.md"]
    assert [h.fichero for h in por_tipo.pop("dato-personal")] == ["notas.md"]
    assert [h.detalle for h in por_tipo.pop("unicode-invisible")] == ["carácter U+200B"]
    assert [h.fichero for h in por_tipo.pop("binario")] == ["imagen.png"]
    assert [h.fichero for h in por_tipo.pop("certificado")] == ["certificado.p12"]
    assert por_tipo == {}

    # Un binario revisado se autoriza en la lista (protegida por CODEOWNERS); un certificado, nunca.
    (listas / "binarios-permitidos.txt").write_text("imagen.png\ncertificado.p12\n", encoding="utf-8")
    tipos = {h.tipo for h in guarda.revisar(tmp_path)}
    assert "binario" not in tipos and "certificado" in tipos


# ------------------------------------------------------------------ validate.py
def test_validacion_del_repositorio(validador):
    errores = validador.revisar(RAIZ)
    assert errores == [], "\n".join(errores)


def test_validador_detecta_errores(validador, tmp_path):
    s = tmp_path / "skills" / "demo"
    (s / "references").mkdir(parents=True)
    (s / "assets").mkdir()
    (s / "SKILL.md").write_text("---\nname: otro-nombre\ndescription: \"" + "x" * 1025 + "\"\n---\n# Demo\n",
                                encoding="utf-8")
    (s / "references" / "sin-fecha.md").write_text("---\nfuentes: []\n---\n# Guía\n", encoding="utf-8")
    (s / "references" / "futura.md").write_text("---\nverificado_el: 2999-01-01\n---\n", encoding="utf-8")
    (s / "references" / "buena.md").write_text("---\nverificado_el: 2026-10-15\n---\n", encoding="utf-8")
    (s / "assets" / "sedes.yaml").write_text(
        "sedes:\n  x:\n    guia: references/buena.md\n    tramites:\n      - guia: references/no-existe.md\n",
        encoding="utf-8")
    (tmp_path / "roto.json").write_text('{"a": ', encoding="utf-8")
    (tmp_path / "roto.yml").write_text("a: [1, 2\n", encoding="utf-8")

    errores = "\n".join(validador.revisar(tmp_path))
    for esperado in (
        "roto.json: no se puede leer",
        "roto.yml: no se puede leer",
        "name 'otro-nombre' no coincide con la carpeta 'demo'",
        "description tiene 1025 caracteres",
        "sin-fecha.md: falta verificado_el",
        "futura.md: verificado_el 2999-01-01 está en el futuro",
        "la guía 'references/no-existe.md' no existe",
    ):
        assert esperado in errores, (esperado, errores)
    assert "buena.md" not in errores


def test_descripcion_del_skill_cabe(validador):
    fm = validador.frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    assert fm["name"] == SKILL.name
    assert 0 < len(fm["description"]) <= 1024
