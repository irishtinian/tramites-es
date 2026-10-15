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


def _decidir(sede, url: str, method: str = "GET", navegacion: bool = True, permitidos=None):
    sesion = SimpleNamespace(bloqueos=[])
    ruta = Ruta()
    sede._guarda_red(sesion, permitidos)(ruta, Peticion(url, method, navegacion))
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
        assert b["permiso"] in sede.ACTOS and f"requiere permiso '{b['permiso']}'" in b["why"]


# ------------------------------------------------------------------ permisos: qué acto es cada petición
CASOS_ACTO = [
    # (url, método, navegación, acto que exige)
    ("https://sede.mjusticia.gob.es/redese/clave/solicitarCertificado", "GET", True, "generar"),
    ("https://ayto-ficticio.sedelectronica.es/catalog/tw/0f0f0f0f-0000-4000-8000-000000000000", "GET", True, "presentar"),
    ("https://dehu.redsara.es/es/notifications/123/open", "GET", False, "comparecer"),
    ("https://www1.agenciatributaria.gob.es/wlpl/MODELO-X/presentar", "POST", False, "presentar"),
    ("https://sede.ayto-ficticio.example/firmaDocumento", "POST", False, "firmar"),
    ("https://sis.redsys.es/sis/realizarPago", "GET", True, "pagar"),
    ("https://sede.ayto-ficticio.example/tributos/baja", "POST", False, "cambiar_datos"),
]


@pytest.mark.parametrize("url, method, navegacion, acto", CASOS_ACTO)
def test_acto_de_peticion_sin_permisos(sede, url, method, navegacion, acto):
    r = sede.acto_de_peticion(method, url, navegacion, set())
    assert r is not None and r[0] == acto


@pytest.mark.parametrize("url, method, navegacion, acto", CASOS_ACTO)
def test_acto_de_peticion_con_su_permiso_sigue(sede, url, method, navegacion, acto):
    assert sede.acto_de_peticion(method, url, navegacion, {acto}) is None
    decision, bloqueos = _decidir(sede, url, method, navegacion, permitidos={acto})
    assert decision == "sigue" and not bloqueos


def test_un_permiso_no_abre_otros_actos(sede):
    # Con 'firmar' no se puede presentar ni pagar.
    r = sede.acto_de_peticion("POST", "https://www1.agenciatributaria.gob.es/wlpl/MODELO-X/presentar", False, {"firmar"})
    assert r is not None and r[0] == "presentar"
    r = sede.acto_de_peticion("GET", "https://sis.redsys.es/sis/realizarPago", True, {"firmar", "presentar"})
    assert r is not None and r[0] == "pagar"


def test_todo_permite_todos_los_actos(sede):
    todos = sede._normalizar_permisos("todo", "prueba")
    assert todos == set(sede.ACTOS)
    for url, method, navegacion, _acto in CASOS_ACTO:
        assert sede.acto_de_peticion(method, url, navegacion, todos) is None


@pytest.mark.parametrize("valor, esperado", [
    (None, set()), ("", set()), ([], set()),
    ("firmar,presentar", {"firmar", "presentar"}),
    ("firmar presentar", {"firmar", "presentar"}),
    (["Pagar", " cita "], {"pagar", "cita"}),
    (["todo"], {"generar", "firmar", "presentar", "pagar", "comparecer", "cambiar_datos", "cita"}),
])
def test_normalizar_permisos(sede, valor, esperado):
    assert sede._normalizar_permisos(valor, "prueba") == esperado


def test_normalizar_permisos_rechaza_desconocidos(sede):
    with pytest.raises(SystemExit, match="permisos desconocidos"):
        sede._normalizar_permisos("firmar,volar", "prueba")


def test_permisos_suma_fichero_y_argumento(sede, permisos):
    permisos.FICHERO.write_text("permitir: [cita]\n", encoding="utf-8")
    assert sede.permisos(SimpleNamespace(permitir="firmar")) == {"cita", "firmar"}
    assert sede.permisos(SimpleNamespace(permitir=None)) == {"cita"}
    permisos.FICHERO.unlink()
    assert sede.permisos(SimpleNamespace()) == set()


def test_permisos_del_fichero_invalidos_paran(sede, permisos):
    permisos.FICHERO.write_text("permitir: [volar]\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="permisos desconocidos"):
        sede.permisos(SimpleNamespace())


class Dialogo:
    def __init__(self, tipo: str, mensaje: str):
        self.type, self.message, self.resultado = tipo, mensaje, None

    def accept(self):
        self.resultado = "aceptado"

    def dismiss(self):
        self.resultado = "cancelado"


def _dialogo(sede, tipo, mensaje, permitidos):
    manejadores = []
    sede._dialogos(SimpleNamespace(on=lambda _ev, f: manejadores.append(f)), permitidos)
    d = Dialogo(tipo, mensaje)
    manejadores[0](d)
    return d.resultado


@pytest.mark.parametrize("tipo, mensaje, permitidos, esperado", [
    ("beforeunload", "", set(), "aceptado"),
    ("confirm", "¿Desea enviar la solicitud?", set(), "cancelado"),
    ("confirm", "¿Desea enviar la solicitud?", {"presentar"}, "aceptado"),
    ("confirm", "¿Desea pagar ahora?", {"presentar"}, "cancelado"),
    ("confirm", "¿Confirma la cita?", {"cita"}, "aceptado"),
    ("alert", "Aviso", {"presentar"}, "cancelado"),
])
def test_dialogos_segun_permisos(sede, tipo, mensaje, permitidos, esperado):
    assert _dialogo(sede, tipo, mensaje, permitidos) == esperado


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


@pytest.mark.parametrize("receta, acto", [
    ("pg.set_input_files('input', 'fichero.dec')", "presentar"),
    ("pg.locator('form').evaluate('f => f.submit()')", "presentar"),
    ("pg.evaluate('procesoFirma()')", "firmar"),
    ("pg.evaluate('pagarRecibo()')", "pagar"),
])
def test_receta_con_acto_necesita_su_permiso(sede, receta, acto):
    motivo = sede.receta_prohibida(receta, set())
    assert motivo and f"requiere permiso '{acto}'" in motivo
    assert sede.receta_prohibida(receta, {acto}) is None


@pytest.mark.parametrize("receta", [
    "pg.add_init_script('window.__tGuard = 0')", "ctx.unroute('**/*')", "import subprocess",
    "c = para_playwright('yo')", "ctx.route('**/*', lambda r: r.continue_())", "abrir('AutoFirma')",
    "pg.evaluate('window.__tAfirma(\"afirma://x\")')",
])
def test_receta_que_toca_las_guardas_no_se_permite_nunca(sede, receta):
    assert sede.receta_prohibida(receta, set(sede.ACTOS))


def test_receta_legitima_sin_permisos(sede):
    assert sede.receta_prohibida(RECETA_LEGITIMA, set()) is None


def test_ejecutar_rechaza_la_receta_sin_abrir_el_navegador(sede, tmp_path, capsys):
    receta = tmp_path / "receta.py"
    receta.write_text("pg.add_init_script('window.__tGuard = 0')\n", encoding="utf-8")
    assert sede.cmd_ejecutar(_ns(receta=str(receta))) == 2
    assert "rechazada" in json.loads(capsys.readouterr().out)["error"]


# ------------------------------------------------------------------ guardas de página (texto de la regex)
def test_guard_sin_permisos_lleva_todas_las_regex(sede):
    js = sede.construir_guard(set())
    assert "%" + "BLOQ%" not in js and not re.search(r"%[A-Z_]+%", js)
    for acto, rx in sede.JS_ACTO.items():
        assert json.dumps([acto, rx]) in js, acto
    assert sede.NOTIF_JS in js and sede.CITA_URL_JS in js and sede.CITA_BOTON_JS in js
    for bandera in ("NOTIF_ON", "AF_BLOQ", "CITA_ON"):
        assert f"const {bandera} = true;" in js


def test_guard_con_todos_los_permisos_no_bloquea_actos(sede):
    js = sede.construir_guard(set(sede.ACTOS))
    assert "const BLOQ = [].map(" in js
    for bandera in ("NOTIF_ON", "AF_BLOQ", "CITA_ON"):
        assert f"const {bandera} = false;" in js


def test_guard_solo_quita_lo_permitido(sede):
    js = sede.construir_guard({"firmar", "cita"})
    assert json.dumps(["firmar", sede.JS_ACTO["firmar"]]) not in js
    assert json.dumps(["cita", sede.JS_ACTO["cita"]]) not in js
    assert json.dumps(["pagar", sede.JS_ACTO["pagar"]]) in js
    assert "const AF_BLOQ = false;" in js and "const CITA_ON = false;" in js and "const NOTIF_ON = true;" in js


@pytest.mark.parametrize("url, es_cita", [
    ("https://www.citapreviadnie.es/citaPreviaDni/", True),
    ("https://icp.administracionelectronica.gob.es/icpplus/index.html", True),
    ("https://sedeclave.dgt.gob.es/WEB_CITE_CONSULTA/paginas/inicio.faces", True),
    ("https://www2.agenciatributaria.gob.es/wlpl/TOCP-MUTE/internet/identificacion", True),
    ("https://citaprevia-sede.sepe.gob.es/citapreviasepe/", True),
    ("https://sede.ayto-ficticio.example/cita/nueva", True),
    ("https://sede.mjusticia.gob.es/redese/clave/solicitarCertificado", False),   # "solicitar" contiene "cita"
    ("https://sede.ayto-ficticio.example/datos-del-solicitante", False),
    ("https://www1.agenciatributaria.gob.es/wlpl/TEWV-CORE/ResumenVlt", False),
])
def test_paginas_de_cita(sede, url, es_cita):
    assert bool(re.search(sede.CITA_URL_JS, url, re.I)) is es_cita


@pytest.mark.parametrize("texto, bloquea", [
    ("Confirmar", True), ("CONFIRMAR", True), (" Confirmar cita", True), ("Confirmar y finalizar", True),
    ("Aceptar", False), ("Siguiente", False), ("Volver", False),
])
def test_boton_final_de_cita(sede, texto, bloquea):
    assert bool(re.search(sede.CITA_BOTON_JS, texto, re.I)) is bloquea


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
