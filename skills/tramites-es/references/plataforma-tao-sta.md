---
verificado_el: 2026-10-15
estado_mapeo: parcial   # recibos verificados con certificado en el Consorcio de Tenerife y en Granadilla; Santa Cruz y Arona se detienen en la confirmación de datos de contacto
fuentes:
  - https://sede.tributostenerife.es/sta/Relec/CatalogBrowse
  - https://sede.granadilladeabona.es/sta/Relec/CatalogBrowse
  - https://sede.santacruzdetenerife.es/sede/inicio
  - https://sta.arona.org/sta/Relec/CatalogBrowse
  - https://www.tao.es
---

# Receta TAO / STA (T-Systems): `…/sta/CarpetaPublic` y `…/sta/CarpetaPrivate`

## Para qué sirve

STA («Servicios Telemáticos Avanzados», de TAO / T-Systems) es la plataforma municipal más frecuente en **grandes ciudades**. La investigación del proyecto la vio en unos 80 municipios, 19 de ellos de más de 100.000 habitantes: Málaga, A Coruña, Elche, Granada, Badalona, Gijón, Santa Cruz de Tenerife, Almería, Alcalá de Henares, Leganés, Getafe, Burgos, Salamanca… También la usan **consorcios y organismos de recaudación**, como el Consorcio de Tributos de Tenerife.

Con ella el agente puede:
- **leer** recibos, anotaciones o registros de entrada, expedientes y el **listado** de notificaciones;
- localizar la ficha de un trámite del catálogo y prepararlo;
- con los permisos de su usuario, hacer los **actos**: firmar y presentar (`firmar`, `presentar`), pagar recibos (`pagar`), abrir notificaciones (`comparecer`) o confirmar datos (`cambiar_datos`).

**Cómo reconocerla:** rutas `/sta/CarpetaPublic/…` o `/sta/CarpetaPrivate/…` con `APP_CODE=STA&PAGE_CODE=…`; en el HTML, `web_author="T-Systems / TAO"` o «STA. Servicios Telemáticos Avanzados». Las sedes nuevas («PTS2») usan `PAGE_CODE=PTS2_HOME`.

## Parámetros y rutas

```text
ORIGIN          = https://<host-STA>                (cambia por instalación)
PAGE_CODE       = pantalla de la carpeta            (cambia por instalación: RECIBOS, OVC_RECIBOS…)
DBOID_REQUEST   = trámite del catálogo              (propio de cada instalación)
DBOID_PROCEDURE = familia del trámite               (propio de cada instalación)

Catálogo:     {ORIGIN}/sta/Relec/CatalogBrowse
Ficha:        {ORIGIN}/sta/Relec/CatalogDetail?action=make&dboidProcedure={DBOID_PROCEDURE}&dboidRequest={DBOID_REQUEST}&urlBack=
Frontal:      {ORIGIN}/sta/CarpetaPublic/doEvent?APP_CODE=STA&PAGE_CODE={FRONTAL_OVC | OVC_HOME | PTS2_HOME}
Selector:     {ORIGIN}/sta/CarpetaPrivate/Login?APP_CODE=STA&PAGE_CODE={PAGE_CODE}
Certificado:  {ORIGIN}/sta/CarpetaPrivate/Certificate?APP_CODE=STA&PAGE_CODE={PAGE_CODE}
Cl@ve:        {ORIGIN}/sta/CarpetaPrivate/Clave2Request?APP_CODE=STA&PAGE_CODE={PAGE_CODE}
```

Los nombres de carpetas y parámetros son comunes. El host, los `PAGE_CODE` y los `dboid*` **no**: nunca copies un `dboid` ni un `PAGE_CODE` de una sede a otra sin comprobarlo.

## Acceso

| Vía | Ruta | Certificado |
|---|---|---|
| **Directa con certificado** | `…/CarpetaPrivate/Certificate?APP_CODE=STA&PAGE_CODE=<X>` | **Sí, por ruta** (renegociación): `cert-probe` lo confirma en las 4 instalaciones; `tls-probe` no lo ve en el *handshake* |
| Selector | `…/CarpetaPrivate/Login?…` | No; muestra los métodos |
| Cl@ve | `…/CarpetaPrivate/Clave2Request?…` | No en la sede; en la pasarela, solo «DNIe / Certificado electrónico» (`sede-clave.md`) |

- **Origins:** el `{ORIGIN}` de la instalación. Si usas Cl@ve, añade `https://pasarela.clave.gob.es` y `https://pasarela-ident.clave.gob.es`.
- La vía directa entra en la pantalla pedida: `Certificate?…&PAGE_CODE=RECIBOS` lleva a los recibos (verificado en el Consorcio).
  ```bash
  uv run scripts/sede.py abrir --sede consorcio-tenerife --titular <ALIAS> \
    --url "https://sede.tributostenerife.es/sta/CarpetaPrivate/Certificate?APP_CODE=STA&PAGE_CODE=RECIBOS"
  ```
- **Cómo saber que entró:** cabecera **Mi Cuenta** y mensaje de bienvenida en la carpeta privada (`sesion_iniciada: true` en `sede.py abrir`). Comprueba que el titular es la persona antes de leer nada.
- **Confirmación de datos de contacto.** En Santa Cruz de Tenerife y en Arona, el certificado se aceptó, pero el primer acceso llevó a `CONFIRMACION_DATOS_PERSONALES`. Esa pantalla pide confirmar teléfono y correo con el botón **GUARDAR**: es el acto `cambiar_datos`.
  - **Con ese permiso:** comprueba con tu usuario que el teléfono y el correo son los suyos y guarda (`sede.py --permitir cambiar_datos`).
  - **Sin él:** `sede.py` lo bloquea. Pregúntale, o que lo confirme él en su navegador y vuelves a intentarlo.
  - No se ha comprobado si después la pantalla deja de salir.

## Pantallas de la carpeta (`PAGE_CODE`)

| Función | `PAGE_CODE` observados | Riesgo o acto |
|---|---|---|
| Recibos (pendientes en voluntaria, en ejecutiva y pagados) | `RECIBOS`, `OVC_RECIBOS` | leer; pagar: `pagar` |
| Anotaciones o registros de entrada | `ANOTACIONES`, `OVC_ANOTACIONES`, `REGISTRO_ENTRADA` | leer |
| Expedientes | `EXPEDIENTES_FULL`, `OVC_EXPEDIENTES_FULL` | leer |
| Notificaciones | `SINGLE_NOTIF` | listar: leer; abrir: `comparecer` |
| Posición global | `OVC_POSICIONGLOBAL` | leer |
| Domiciliaciones | `OTRIBDOMI` | `cambiar_datos` |
| Autoliquidaciones | `CREARLIQ`, `OVC_CREARLIQ` | `presentar`, `pagar` |
| Certificados tributarios | `SOLDOC_COR` | `generar` |
| Carta de pago sin acceso (pública) | `ACCESO_DEUDA` | `pagar` |
| Verificación de documentos (pública) | `VALDOCS` | leer, con posible CAPTCHA |

Son nombres observados en 4 instalaciones, **no una garantía**: compruébalos en cada una (ver «Cómo adaptarla»).

- **Recibos:** muestran las pestañas pendientes en voluntaria, en ejecutiva y pagados. Los botones «Pagar ahora», «Añadir a la cesta» y «Generar carta de pago» son el acto `pagar`: con ese permiso, confirma con tu usuario recibo e importe antes de pagar; sin él, dile cuáles tiene pendientes y dónde pagarlos. El pago con el agente está **pendiente de verificar en vivo**.
  - Sin recibos, la pestaña dice «No tiene recibos pendientes.» (Granadilla, 15-10-2026).
  - Columnas en el Consorcio: Tributo / Referencia, Ejercicio, Num. recibo, Institución, Periodo (Voluntaria/Ejecutiva), Importe principal, Carta Pago. **No hay fecha límite de pago**: para el plazo de voluntaria, remite al calendario del contribuyente del recaudador (en el CTT, `https://www.tributostenerife.es`) y dilo como "a confirmar".
  - Granadilla avisa de que agua y alcantarillado **no** están en su carpeta, y remite al Consorcio para lo demás: consulta siempre los dos.
- **Notificaciones:** abrir una notificación es comparecer (acto `comparecer`, empiezan los plazos). Sin ese permiso, `sede.py` bloquea abrir, consultar o descargar en esas páginas.

## Trámites del catálogo (actos: `firmar`, `presentar`)

- **Buscar:** `{ORIGIN}/sta/Relec/CatalogBrowse` tiene un buscador (`#palabraClave`) y un filtro de canal. Cada resultado enlaza a `CatalogDetail` con sus dos `dboid*`.
  ```bash
  uv run scripts/sede.py probe --url "https://<ORIGIN>/sta/Relec/CatalogBrowse"
  ```
- **Ficha:** muestra requisitos y el botón **Tramitar**. Prepara el texto, los datos y la lista de adjuntos.
- **Tramitar, adjuntar y enviar** son el acto `presentar`; firmar cada adjunto y la solicitud, `firmar`.
  - **Con esos permisos** (`sede.py --permitir firmar,presentar`): rellena, adjunta, confirma el contenido con tu usuario y envía. Cada firma lanza AutoFirma (`setup-autofirma.md`). **Pendiente de verificar en vivo** de punta a punta.
  - **Sin ellos:** para en la ficha y dale a tu usuario el texto, los adjuntos y el enlace.
- **Adjuntos y firma:** el formulario abre una ventana de adjuntos (`openUploader`, campo `#fichero`, «Pulse para adjuntar»). Llama a `procesoFirma()` y `firmar()` (AutoFirma) y después aparece **Continuar**.
- **Cómo verificar:**
  - justificante con número de anotación (en el historial del proyecto, con forma AAAA + 6 dígitos) y CSV;
  - y, sobre todo, la entrada nueva en la pantalla de anotaciones o registro de entrada.
  - El justificante suele servirse por `GetDocumentServlet?CUD=…`, sin evento de descarga del navegador: usa `scripts/justificante.py` sobre la captura o el PDF que guarde la persona.
  - Antes de reintentar un envío fallido, revisa ese listado para no duplicar.

## Cómo adaptarla a tu ayuntamiento

1. **Localiza la instalación:**
   ```bash
   uv run scripts/buscar.py --municipio "Nombre del municipio"
   ```
   La `sede_url` del censo puede ser la página editorial del ayuntamiento, no el host STA. Por ejemplo, el censo da `www.granadilladeabona.org/sede-electronica/` y el STA está en `sede.granadilladeabona.es`. Busca en esa página el enlace que contenga `/sta/`: su host es el ORIGIN.
2. **Ojo con las dos capas:** algunas sedes tienen un catálogo editorial y ejecutan en otro host. Santa Cruz de Tenerife tiene fichas en `sede.santacruzdetenerife.es/sede/tramite/t<ID>` y ejecuta en `ovc.santacruzdetenerife.es`. Arona tiene fichas en `sede.arona.org` y ejecuta en `sta.arona.org`.
3. **Averigua los `PAGE_CODE`** de esa instalación en su frontal o menú, sin certificado, con la receta `sta_pagecodes.py` de abajo. Si `OVC_HOME` no existe, prueba con la `sede_url` del censo o con `FRONTAL_OVC` / `PTS2_HOME`.
4. **Trámites:** busca en `CatalogBrowse` y copia los dos `dboid*` de la ficha de **esa** instalación.
5. **Origins para `sede.py`:** el ORIGIN (más las pasarelas Cl@ve si usas `Clave2Request`). Si la instalación no está en `assets/sedes.yaml` y su dominio no está en `assets/dominios-oficiales.yaml` ni en el censo, pregunta a la persona antes de usar el certificado («Solo sedes oficiales» en `SKILL.md`).
6. **Tributos:** puede que los recibos no estén en el ayuntamiento sino en su recaudador (en Tenerife, casi siempre el Consorcio): `canarias-recaudacion.md`.

Receta de solo lectura para el paso 3 (no probada en vivo tal cual):

```python
# sta_pagecodes.py — lista los PAGE_CODE enlazados en la página
codigos = pg.evaluate("""() => [...new Set([...document.querySelectorAll('a[href*="PAGE_CODE="]')]
    .map(a => (a.href.match(/PAGE_CODE=([A-Za-z0-9_]+)/) || [])[1]).filter(Boolean))]""")
RESULTADO = {"page_codes": codigos}
```

```bash
uv run scripts/sede.py ejecutar sta_pagecodes.py --url "https://<ORIGIN>/sta/CarpetaPublic/doEvent?APP_CODE=STA&PAGE_CODE=OVC_HOME"
```

## Trampas

- **`PAGE_CODE` y `dboid*` locales.** Lo que vale en una sede no vale en otra.
- **Confirmación de datos de contacto** (`CONFIRMACION_DATOS_PERSONALES`, botón GUARDAR): acto `cambiar_datos` (ver «Acceso»).
- **Enlaces de plantilla ajenos:** el frontal de Granadilla conserva enlaces de demostración a `dipcas.es` (Diputación de Castellón). No los sigas: usa su `Relec/CatalogBrowse`.
- **Enlaces antiguos** `CarpetaPublic/doEvent?APP_CODE=STA&DETALLE=<id>&PAGE_CODE=CATALOGO`: `DETALLE` también es local.
- **CAPTCHA** en la validación o cotejo de documentos: lo resuelve la persona y tú sigues («Fuera del alcance» en `SKILL.md`).
- **Interfaz antigua:** navegación por POST, ventanas emergentes, botones duplicados invisibles (ancho 0) y campos ocultos. Guarda solo enlaces públicos estables, nunca los que llevan sesión.
- **No hay evento de descarga** en los justificantes.

## Instalaciones verificadas (15-10-2026)

| Entidad | ORIGIN | Acceso directo | Estado |
|---|---|---|---|
| Consorcio de Tributos de Tenerife | `https://sede.tributostenerife.es` | `Certificate?…&PAGE_CODE=HOME` | Recibos leídos con certificado |
| Granadilla de Abona | `https://sede.granadilladeabona.es` | `Certificate?…&PAGE_CODE=HOME` | Recibos leídos con certificado |
| Santa Cruz de Tenerife | `https://ovc.santacruzdetenerife.es` | `Certificate?…&PAGE_CODE=HOME` | Certificado aceptado; para en la confirmación de contacto |
| Arona | `https://sta.arona.org` | `Certificate?…&PAGE_CODE=OVC_POSICIONGLOBAL` | Certificado aceptado; para en la confirmación de contacto |

Los trámites concretos de cada una (con sus `dboid*` y `PAGE_CODE`) están en `assets/sedes.yaml`.

## Fuentes

- Mapeo en vivo de tramites-es del 15-10-2026 en las cuatro instalaciones, con certificado solo para consultas y sin datos personales. No se rellenó, firmó, pagó ni guardó nada.
- Investigación del proyecto: R1 §3.2 (huella, cobertura, `PTS2`), R2 §6 (Canarias) e informe 01 §4.2 (adjuntos, firma y justificantes).
