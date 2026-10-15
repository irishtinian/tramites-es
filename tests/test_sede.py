"""sede.py sin navegador: dominios oficiales, resolver, guardas de red, recetas prohibidas y redacción.

La guarda de red se prueba llamando a _guarda_red() con una petición y una ruta falsas,
igual que haría Playwright, pero sin abrir Chrome.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from types import SimpleNamespace

import pytest


def _ns(**kw) -> argparse.Namespace:
    base = {"sede": None, "url": None, "titular": "ninguno", "inseguro": False}
    base.update(kw)
    return argparse.Namespace(**base)


# ------------------------------------------------------------------ origin_oficial
@pytest.mark.parametrize("origin", [
    "https://www1.agenciatributaria.gob.es",
    "https://sede.agenciatributaria.gob.es",
    "https://dehu.redsara.es",
    "https://ipce.seg-social.es",
    "https://sede.gobiernodecanarias.org",
    "https://carpeta.justicia.es",
    "https://sede.tributostenerife.es",          # host concreto de dominios-oficiales.yaml
    "https://SEDE.DGT.GOB.ES",
    "https://pasarela-ident.clave.gob.es:443",
])
def test_origin_oficial_acepta(sede, origin):
    assert sede.origin_oficial(origin, {}) is True


@pytest.mark.parametrize("origin", [
    "http://www1.agenciatributaria.gob.es",                      # sin TLS
    "ftp://sede.agenciatributaria.gob.es",
    "https://agenciatributaria.gob.es.example.com",              # sufijo oficial en medio
    "https://falsogob.es",                                       # acaba igual, pero no es subdominio
    "https://www1.agenciatributaria.gob.es@phishing.example",   # userinfo engañoso
    "https://sede.example",
    "https://",
    "https://cualquiera.sedelectronica.es",                      # comodín de una plataforma: no basta
])
def test_origin_oficial_rechaza(sede, origin):
    assert sede.origin_oficial(origin, {}) is False


def test_origin_de_la_propia_sede(sede):
    s = {"origins": ["https://sede.ayuntamiento-ficticio.example"]}
    assert sede.origin_oficial("https://sede.ayuntamiento-ficticio.example", s) is True
    assert sede.origin_oficial("http://sede.ayuntamiento-ficticio.example", s) is False
    assert sede.origin_oficial("https://otra.ayuntamiento-ficticio.example", s) is False


def test_hosts_del_censo_de_municipios(sede, skill, tmp_path, monkeypatch):
    shutil.copy(skill / "assets" / "dominios-oficiales.yaml", tmp_path / "dominios-oficiales.yaml")
    (tmp_path / "municipios.csv").write_text(
        "municipio,provincia,ccaa,ine,sede_url,web,plataforma,confianza,recaudador\n"
        "Villa Ficticia,Provincia Ficticia,Comunidad Ficticia,99001,"
        "https://villaficticia.sedelectronica.es/info.0,,gestiona,alta,\n",
        encoding="utf-8")
    monkeypatch.setattr(sede, "ASSETS", tmp_path)
    assert sede.origin_oficial("https://villaficticia.sedelectronica.es", {}) is True
    assert sede.origin_oficial("https://otraficticia.sedelectronica.es", {}) is False
    assert sede.origin_oficial("https://www1.agenciatributaria.gob.es", {}) is True


# ------------------------------------------------------------------ resolver
def test_resolver_sede_conocida(sede):
    nombre, origins, url = sede.resolver(_ns(sede="aeat", titular="prueba"))
    assert nombre == "aeat"
    assert url.startswith("https://www1.agenciatributaria.gob.es/")
    assert origins == ["https://www1.agenciatributaria.gob.es"]


def test_resolver_rechaza_dominio_no_oficial_con_titular(sede):
    with pytest.raises(SystemExit) as fin:
        sede.resolver(_ns(url="https://sede-agenciatributaria.example/login", titular="prueba"))
    assert "no son oficiales" in str(fin.value)
    assert "https://sede-agenciatributaria.example" in str(fin.value)


def test_resolver_rechaza_url_no_oficial_aunque_la_sede_si_lo_sea(sede):
    with pytest.raises(SystemExit, match="no son oficiales"):
        sede.resolver(_ns(sede="aeat", url="https://phishing.example/aeat", titular="prueba"))


def test_resolver_sin_titular_no_comprueba_porque_no_presenta_certificado(sede):
    nombre, _origins, url = sede.resolver(_ns(url="https://phishing.example/login"))
    assert nombre == "phishing.example" and url == "https://phishing.example/login"


def test_resolver_sede_desconocida(sede):
    with pytest.raises(SystemExit, match="no está en assets"):
        sede.resolver(_ns(sede="no-existe", titular="prueba"))


def test_resolver_sede_sin_login(sede):
    with pytest.raises(SystemExit, match="falta --url"):
        sede.resolver(_ns(sede="clave", titular="prueba"))


def test_todas_las_sedes_con_login_resuelven_con_titular(sede):
    probadas = 0
    for sid, s in sede.cargar_sedes().items():
        if not s.get("login"):
            continue
        _nombre, origins, url = sede.resolver(_ns(sede=sid, titular="prueba"))
        assert url.startswith("https://"), sid
        for o in origins:
            assert re.fullmatch(r"https://[a-z0-9.-]+(:\d+)?", o), (sid, o)
        probadas += 1
    assert probadas > 20


# ------------------------------------------------------------------ guarda de red
class Peticion:
    def __init__(self, url: str, method: str, navegacion: bool):
        self.url, self.method, self._navegacion = url, method, navegacion

    def is_navigation_request(self) -> bool:
        return self._navegacion


class Ruta:
    def __init__(self):
        self.decision = None

    def abort(self, _codigo=None):
        self.decision = "bloqueada"

    def continue_(self):
        self.decision = "sigue"


def _decidir(sede, url: str, method: str = "GET", navegacion: bool = True):
    sesion = SimpleNamespace(bloqueos=[])
    ruta = Ruta()
    sede._guarda_red(sesion)(ruta, Peticion(url, method, navegacion))
    return ruta.decision, sesion.bloqueos


CASOS_RED = [
    # Caso real (15-oct-2026): cargar esta URL de Justicia emitía un certificado.
    ("https://sede.mjusticia.gob.es/redese/clave/solicitarCertificado", "GET", True, "bloqueada"),
    # Página informativa de la AEAT: dice "presentar", pero es un .html.
    ("https://sede.agenciatributaria.gob.es/Sede/presentar-y-consultar.html", "GET", True, "sigue"),
    # Asistente de tramitación de Gestiona: entrar puede crear un borrador.
    ("https://ayto-ficticio.sedelectronica.es/catalog/tw/0f0f0f0f-0000-4000-8000-000000000000", "GET", True, "bloqueada"),
    # Ficha del catálogo de Gestiona: solo información.
    ("https://ayto-ficticio.sedelectronica.es/catalog/t/0f0f0f0f-0000-4000-8000-000000000000", "GET", True, "sigue"),
    # OpenSIAC: /opensiac/ no es "open"; el buzón (listado) se puede ver.
    ("https://seu.sabadell.cat/opensiac/carpetaciudadana/buzonnotificaciones_enter.action", "GET", True, "sigue"),
    ("https://seu.sabadell.cat/opensiac/main.action", "GET", True, "sigue"),
    # DEHú: listar sí, abrir o comparecer no.
    ("https://dehu.redsara.es/es/notifications", "GET", True, "sigue"),
    ("https://dehu.redsara.es/es/notifications/123/open", "GET", False, "bloqueada"),
    ("https://dehu.redsara.es/api/notifications/123/appearance", "POST", False, "bloqueada"),
    ("https://sede.ayto-ficticio.example/notificaciones/comparecer?id=1", "GET", False, "bloqueada"),
    # POST de acción.
    ("https://www1.agenciatributaria.gob.es/wlpl/MODELO-X/presentar", "POST", False, "bloqueada"),
    ("https://sede.ayto-ficticio.example/registro/alta", "POST", False, "bloqueada"),
    # POST de búsqueda en el listado de notificaciones de la AEAT: permitido.
    ("https://www1.agenciatributaria.gob.es/wlpl/GNNO-JDIT/SvInteresadosQuery", "POST", True, "sigue"),
    # Pasarelas de pago.
    ("https://sis.redsys.es/sis/realizarPago", "GET", True, "bloqueada"),
    ("https://pagos.ayto-ficticio.example/", "GET", True, "bloqueada"),
    # Consulta normal.
    ("https://www1.agenciatributaria.gob.es/wlpl/TEWV-CORE/ResumenVlt", "GET", True, "sigue"),
]


@pytest.mark.parametrize("url, method, navegacion, esperado", CASOS_RED)
def test_guarda_de_red(sede, url, method, navegacion, esperado):
    decision, bloqueos = _decidir(sede, url, method, navegacion)
    assert decision == esperado
    assert bool(bloqueos) == (esperado == "bloqueada")
    for b in bloqueos:
        assert "?" not in b["d"]  # el registro no guarda la query (puede llevar identificadores)


# ------------------------------------------------------------------ expresiones regulares
@pytest.mark.parametrize("ruta", [
    "/redese/clave/solicitarCertificado",
    "/catalog/tw/0f0f0f0f",
    "/certificados/emitirCertificado",
    "/sta/tramitarSolicitud",
    "/x/firmar",
    "/x?accion=presentar",
    "/Sede/presentar-y-consultar.html",  # la regex casa; la guarda de red lo deja pasar por ser .html
])
def test_accion_get_positivos(sede, ruta):
    assert sede.ACCION_GET.search(ruta)


@pytest.mark.parametrize("ruta", [
    "/catalog/t/0f0f0f0f",
    "/wlpl/TEWV-CORE/ResumenVlt",
    "/sede/procedimientos_servicios/tramites/4015",
    "/opensiac/main.action",
    "/es/notifications",
])
def test_accion_get_negativos(sede, ruta):
    assert not sede.ACCION_GET.search(ruta)


@pytest.mark.parametrize("ruta", [
    "/wlpl/MODELO-X/presentar", "/registro/alta", "/pago", "/firmaDocumento", "/enviarSolicitud",
    "/notificacion/comparecer", "/acuse", "/baja",
])
def test_accion_post_positivos(sede, ruta):
    assert sede.ACCION_POST.search(ruta)


@pytest.mark.parametrize("ruta", ["/wlpl/GNNO-JDIT/SvInteresadosQuery", "/registro/consulta", "/buscar", "/listado"])
def test_accion_post_negativos(sede, ruta):
    assert not sede.ACCION_POST.search(ruta)


@pytest.mark.parametrize("ruta", [
    "/notifications/123/open", "/notificaciones/comparecer", "/enotifications/acuse", "/notificacion/abrir",
    "/notificacion/leer", "/notifications/full_detail", "/notificaciones/document/123",
])
def test_notif_red_positivos(sede, ruta):
    assert sede.NOTIF_RED.search(ruta)


@pytest.mark.parametrize("ruta", [
    "/opensiac/",
    "/opensiac/carpetaciudadana/buzonnotificaciones_enter.action",
    "/notificaciones/listado",
    "/es/notifications",
])
def test_notif_red_negativos(sede, ruta):
    assert not sede.NOTIF_RED.search(ruta)


RECETA_LEGITIMA = '''
nav("https://www1.agenciatributaria.gob.es/wlpl/TEWV-CORE/ResumenVlt")
datos = probe(pg)
captura("resumen")
pg.get_by_role("button", name="Buscar").click()
RESULTADO = {"titulo": pg.title(), "texto": redactar(pg.inner_text("body"))[:500], "campos": len(datos["campos"])}
'''


def test_receta_legitima_no_se_rechaza(sede):
    assert sede.RECETA_PROHIBIDO.search(RECETA_LEGITIMA) is None


@pytest.mark.parametrize("receta", [
    "pg.add_init_script('window.__tGuard = 0')",
    "ctx.unroute('**/*')",
    "pg.evaluate('window.__tGuard = false')",
    "pg.locator('form').evaluate('f => f.submit()')",
    "pg.evaluate('document.forms[0].requestSubmit()')",
    "pg.locator('#boton').evaluate('e => e.onclick()')",
    "import subprocess",
    "os.system('xdotool key Return')",
    "__import__('os')",
    "import keyring",
    "pg.set_input_files('input', 'fichero')",
    "c = para_playwright('yo')",
    "ctx.expose_binding('x', print)",
    "pg.evaluate('procesoFirma()')",
    "pg.evaluate('firmarDocumento()')",
    "pg.evaluate('enviarSolicitud()')",
    "pg.evaluate('presentarDeclaracion()')",
    "pg.evaluate('pagarRecibo()')",
    "abrir('AutoFirma')",
])
def test_receta_prohibida(sede, receta):
    assert sede.RECETA_PROHIBIDO.search(receta)


@pytest.mark.parametrize("receta", [
    "ctx.route('**/*', lambda r: r.continue_())",
    "pg.route('**/*', lambda r: r.continue_())",
    "ctx.request.post('https://sede.ayto-ficticio.example/presentar')",
])
def test_recetas_que_esquivan_la_guarda_de_red(sede, receta):
    assert sede.RECETA_PROHIBIDO.search(receta)


def test_ejecutar_rechaza_la_receta_sin_abrir_el_navegador(sede, tmp_path, capsys):
    receta = tmp_path / "receta.py"
    receta.write_text("pg.add_init_script('window.__tGuard = 0')\n", encoding="utf-8")
    assert sede.cmd_ejecutar(_ns(receta=str(receta))) == 2
    assert "rechazada" in json.loads(capsys.readouterr().out)["error"]


# ------------------------------------------------------------------ guardas de página (texto de la regex)
def test_guard_js_lleva_las_regex(sede):
    assert "%DENY%" not in sede.GUARD_JS and "%NOTIF%" not in sede.GUARD_JS
    assert sede.DENY_JS in sede.GUARD_JS and sede.NOTIF_JS in sede.GUARD_JS


@pytest.mark.parametrize("texto, bloquea", [
    ("Firmar y enviar", True), ("Presentar declaración", True), ("Pagar", True), ("Registrar solicitud", True),
    ("Comparecer", True), ("Acceder a la notificación", True), ("Dar de baja", True), ("Confirmar el pago", True),
    ("Tramitar", True), ("Buscar", False), ("Consultar", False), ("Ver listado", False), ("Volver", False),
])
def test_deny_js_botones(sede, texto, bloquea):
    # Aproximación en Python de la regex que usa el navegador (mismas palabras; \b es equivalente en ASCII).
    assert bool(re.search(sede.DENY_JS, texto, re.I)) is bloquea


# ------------------------------------------------------------------ redactar
def test_redactar_datos_personales(sede, ficticios):
    nif, nie, cif = ficticios.nif(12345678), ficticios.nie("X", 1234567), ficticios.cif("B", "1234567")
    iban = ficticios.iban("21000418450200051332")
    texto = (f"Titular: Persona Ficticia, NIF {nif}, NIE {nie}, CIF {cif}, IBAN {iban}, "
             "correo persona@correo.example, tel. 612 345 678")
    r = sede.redactar(texto, extra=["Persona Ficticia"])
    for dato in (nif, nie, cif, iban, "persona@correo.example", "612 345 678", "Persona Ficticia"):
        assert dato not in r
    for marca in ("<NIF>", "<NIE>", "<CIF>", "<IBAN>", "<EMAIL>", "<TEL>", "<TITULAR>"):
        assert marca in r
