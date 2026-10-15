---
verificado_el: 2026-10-15
fuentes:
  - https://carpetaciudadana.gob.es/carpeta/mcc/clave
  - https://carpetaciudadana.gob.es/mis-expedientes
  - https://carpetaciudadana.gob.es/carpeta/mcc/mis-documentos
  - https://carpetaciudadana.gob.es/carpeta/mcc/mis-apoderamientos
  - https://sede.administracion.gob.es/pagSedeFront/servicios/consultaCSV.htm
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3) con certificado de persona física. Login y 15 servicios /carpeta/mcc/* verificados en solo lectura; Carpeta Empresa pendiente."
---

# Mi Carpeta Ciudadana

## 1. Para qué sirve

Es un **atajo**: con una sola sesión de Cl@ve se ven datos que viven en muchos organismos, sin entrar en cada sede.

- Vida laboral resumida.
- Vehículos.
- Inmuebles del Catastro.
- Padrón y municipios de residencia.
- Prestaciones.
- Subvenciones concedidas.
- Anuncios del Tablón Edictal Único (TEU).

Sirve para orientarse rápido. Para documentos con validez (certificados, informes en PDF), usa la sede del organismo: `sede-tgss-importass.md`, `sede-catastro.md`, etc.

## 2. Acceso

- **Flujo:**
  1. `https://carpetaciudadana.gob.es/carpeta/mcc/clave` → "Acceder a la carpeta".
  2. `/carpeta/mcc/carpeta-empresa`, "Elige tu rol": `select#valorSelect` = **Ciudadano**. Después, botón "Acceder" (`button.rounded-2xl`; `text-is` no funciona por los espacios).
  3. Keycloak `auth-api.redsara.es` (realm `sgad-appfactory`) → pasarela Cl@ve → "DNIe / Certificado" (`sede-clave.md`).
  4. Vuelta a `/carpeta/mcc/home`.
- **Origins con certificado:** solo `https://pasarela-ident.clave.gob.es`. `carpetaciudadana.gob.es` y `auth-api.redsara.es` no lo piden.
- **Qué certificado:** el rol **Empresa** solo vale con certificado de representante y para esa sociedad. El autónomo persona física entra como **Ciudadano**.
- **Cómo saber que entró:** URL `/carpeta/mcc/home`, título "Página de inicio - Carpeta Ciudadana", con "Centro de mensajes", "Resumen personal" y "Mis datos".

**Receta** (`mcc.py`; cambia `SERVICIO` y `API` por una fila de la tabla de 3.1):

```python
SERVICIO, API = "vida-laboral", "/api/consultaVidaLaboral"
pg.get_by_text("Acceder a la carpeta").first.click()
pg.wait_for_selector("select#valorSelect", timeout=60000)
pg.select_option("select#valorSelect", label="Ciudadano")
pg.click("button.rounded-2xl:has-text('Acceder')")
pg.wait_for_selector("button.idp-button", timeout=60000)
pg.click("button.idp-button:has-text('DNIe / Certificado')")
pg.wait_for_url(lambda u: "/carpeta/mcc/home" in u, timeout=90000)
with pg.expect_response(lambda r: API in r.url, timeout=60000) as resp:
    nav("https://carpetaciudadana.gob.es/carpeta/mcc/" + SERVICIO)
pg.wait_for_timeout(3000)
captura(SERVICIO)
RESULTADO = {"http": resp.value.status, "titulo": pg.title(),
             "texto": redactar(" ".join(pg.inner_text("body").split()))[:4000]}
```

```bash
uv run scripts/sede.py ejecutar mcc.py --sede carpeta-ciudadana --titular yo
```

## 3. Trámites

### 3.1 Consultas del ciudadano · Leer · verificado

- **Cómo funciona:** cada servicio es una ruta Angular, `https://carpetaciudadana.gob.es/carpeta/mcc/<servicio>`, que llama a `GET https://carpetaciudadana.gob.es/api/<recurso>` con la cookie de sesión. Tarda entre 5 y 9 segundos: **espera a la respuesta de la API, no a un tiempo fijo**.
- **Éxito:** respuesta 200 de la API y título "`<Servicio>` - Carpeta Ciudadana".

| Id (`assets/`) | Servicio | API | Qué muestra |
|---|---|---|---|
| `mcc-vida-laboral` | `vida-laboral` | `/api/consultaVidaLaboral` | Días cotizados; periodos con fecha de alta y de baja, días y nº de afiliación |
| `mcc-vehiculos` | `vehiculos` | `/api/conductor` | Fichas de vehículo: matriculación, distintivo, seguro, validez de la ITV |
| `mcc-inmuebles` | `bienes-inmuebles` | `/api/inmueblesCatastro` | Inmuebles del Catastro (vacío si no hay titularidad) |
| `mcc-padron` | `domicilio` | `/api/domicilio` | Padrón: domicilio, municipio, tipo y fecha de variación |
| `mcc-subvenciones` | `concesiones-ayudas-subvenciones` | (al pulsar Buscar) | Subvenciones y ayudas concedidas (BDNS) por periodo |
| `mcc-teu` | `teu` | `/api/consultaTEU` | Anuncios a su nombre en el Tablón Edictal Único |

- **Otros servicios** vistos con la misma mecánica:
  - `prestaciones-sociales` (`/api/datosEconomicos`) y `historico-municipios` (`/api/municipiosResidencia`);
  - `RSPSB`, `RCP`, `consulta-afiliaciones-muface` y `pension-clases-pasivas`;
  - `familia-numerosa`, `titulos-no-universitarios` y `condicion-becado`.
- **Dónde para el agente:** en la pantalla del servicio.
  - "Descargar justificante PDF" del padrón genera un documento nuevo. Solo si la persona lo pide.
- **Los TEU importan:** un anuncio en el TEU puede ser una notificación que no se pudo entregar. Si hay alguno, avísalo como en `tramite-vigilar-notificaciones.md`.

### 3.2 Contador de notificaciones (`mcc-notificaciones`) · Leer · verificado (15-10-2026)

- **Qué es:** al cargar `/carpeta/mcc/home`, la SPA llama sola a `GET /api/notificacionesTotaliza?estado=pendiente&tipoEnvio=1` y **solo muestra el número** de notificaciones pendientes, con un enlace a DEHú. No comparece.
  - Respuesta: `{"notificacionesRespuesta":{"codigoRespuesta":{"codRespuesta":0,"textoRespuesta":"OK"},"numNotificaciones":"<N>","numComunicaciones":"<N>","enlace":"https://dehu.redsara.es/es/notifications"}}`.
  - En la portada se lee además "No tienes ninguna notificación pendiente de comparecer" cuando es 0.
  - Funcionó el 15-10-2026 con el mismo certificado con el que DEHú daba `error=1000`.

```python
# mcc_notificaciones.py — contador DEHú + TEU, solo lectura
apis = {}
def _r(r):
    if "/api/notificacionesTotaliza" in r.url or "/api/consultaTEU" in r.url:
        try:
            apis[r.url.split("/api/")[1].split("?")[0]] = [r.status, redactar(r.text()[:400])]
        except Exception as ex:
            apis[r.url[-40:]] = [r.status, str(ex)[:80]]   # sede.py rechaza los nombres con doble guion bajo
pg.on("response", _r)
pg.get_by_text("Acceder a la carpeta").first.click()
pg.wait_for_selector("select#valorSelect", timeout=60000)
pg.select_option("select#valorSelect", label="Ciudadano")
pg.click("button.rounded-2xl:has-text('Acceder')")
pg.wait_for_selector("button.idp-button", timeout=60000)
pg.click("button.idp-button:has-text('DNIe / Certificado')")
pg.wait_for_url(lambda u: "/carpeta/mcc/home" in u, timeout=90000)
pg.wait_for_timeout(12000)                     # el contador tarda en llegar
nav("https://carpetaciudadana.gob.es/carpeta/mcc/teu", espera=9000)
captura("teu")
RESULTADO = {"apis": apis}
```
- **Cuándo usarlo:** mientras DEHú rechace el login (`sede-dehu.md`), es la mejor señal de "hay algo pendiente".
- **Dónde para:** "Mis notificaciones" lleva a DEHú (`https://dehu.redsara.es/api/login/login-clave-sso?selectedLanguage=es`). Sigue en `sede-dehu.md`.

### 3.3 Carpeta Empresa (`mcc-carpeta-empresa`) · Leer · pendiente

- Información tributaria, propiedades y documentación de una sociedad, con certificado de representante.
- No recorrida.

## 4. Trampas y problemas conocidos

- **`/carpeta/mcc/comunicar-cambio-domicilio`:** acto `cambiar_datos`. Solo si tu usuario quiere comunicar su nuevo domicilio. **No mapeado.**
- **`GET /api/guardarEmail`:** algunas pantallas lo llaman solas al cargar; lo hace la SPA. No lo llames tú directamente: para cambiar el correo, usa la pantalla (acto `cambiar_datos`).
- **Chatbot "Ada":** la burbuja puede tapar botones. Si un clic falla, haz `probe` y busca el elemento.
- **Banner de cookies** ("Aceptar todas" / "Configuración"): desde "Configuración", deja solo las necesarias.
- **Errores que no afectan:** fallos de `estaticoscarpeta.carpetaciudadana.gob.es` (`ERR_FAILED`) y bloqueos CSP de analítica.
- **WAF:** hay un F5 delante. Navega a ritmo humano, un servicio tras otro, sin llamadas en ráfaga.

## 5. Fuentes

- Carpeta Ciudadana (accesos públicos) y el verificador de CSV de la AGE: ver la cabecera.
- Mapeo en vivo del 15-10-2026: 15 servicios en solo lectura, sin descargar nada.
