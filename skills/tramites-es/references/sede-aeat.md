---
verificado_el: 2026-10-15
fuentes:
  - https://sede.agenciatributaria.gob.es/Sede/mi-area-personal.html
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G304.shtml     # estar al corriente
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G313.shtml     # situación censal
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G322.shtml     # censo / 036
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/ZN01.shtml     # notificaciones
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G601.shtml     # 130
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G414.shtml     # 303
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G412.shtml     # 390
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/GH01.shtml     # 111
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/GH02.shtml     # 115
  - https://sede.agenciatributaria.gob.es/Sede/procedimientoini/RB01.shtml   # aplazamiento
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/consultas-informaticas/otros-servicios-ayuda-tecnica/consulta-declaraciones-presentadas.html
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/consultas-informaticas/notificaciones-electronicas-ayuda-tecnica/consulta-notificaciones-comunicaciones.html
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/horario-interrupciones-sede-electronica.html
  - https://sede.agenciatributaria.gob.es/Sede/identificacion-electronica/clave-movil/uso-personal-clave-prevencion-practicas-autorizadas.html
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3) con certificado de persona física. Consultas verificadas; certificados y modelos recorridos hasta el paso de firma; listado de notificaciones sin obtener todavía."
---

# AEAT: sede electrónica de la Agencia Tributaria

## 1. Para qué sirve

Impuestos estatales del autónomo: deudas, datos censales (036), datos fiscales, declaraciones presentadas y su copia, certificados tributarios, notificaciones y los modelos 130, 303, 111, 115 y 390.

En **Canarias** no hay IVA: el IGIC va a la ATC (`sede-atc.md`). Que el 303 o el 390 salgan vacíos es lo normal allí, no un error.

## 2. Acceso

- **La AEAT no usa la pasarela Cl@ve.** Tiene su propio selector (`SelectorAccesos.html?ref=<ruta>&aut=<letras>`) y cada método de acceso es un host distinto:

| Letra `aut` | Botón | Host | ¿Para el agente? |
|---|---|---|---|
| C | Certificado o DNI electrónico | `www1` (pide certificado) | **Sí** |
| P | Cl@ve Móvil (propio de la AEAT) | `www6` | **No** («Fuera del alcance» en `SKILL.md`) |
| R | Número de referencia (solo Renta) | `www9` | No |
| D | DNI/NIE + dato de contraste | `www12` | No |
| E | Ciudadanos UE (eIDAS) | `www11` | No |

- **Con certificado no hace falta el selector.** El enlace directo `https://www1.agenciatributaria.gob.es/wlpl/<ruta>` entra sin más: `www1` pide el certificado en el handshake TLS.
- **Origins con certificado:** solo `https://www1.agenciatributaria.gob.es`. Es el único que hizo falta en todos los trámites recorridos.
  - `www8` y `www10` también piden certificado en el handshake, pero no aparecen en ningún trámite: no los añadas.
  - `sede`, `www2`, `www6`, `www9`, `www11` y `www12` no lo piden.
- **Entrar:** `uv run scripts/sede.py abrir --sede aeat --titular yo` abre "Mis expedientes" (`/wlpl/TEWV-CORE/ResumenVlt`).
- **Qué certificado:** el `--titular` es el alias de `cert.py`. Persona física: su certificado. Sociedad: el de representante. Si sale "No tiene autorización para realizar el trámite", el certificado no es el adecuado.
- **Cómo saber que entró:**
  - La cabecera muestra el botón `#dropdownUsuario` con el nombre del titular.
  - "Mis expedientes" se titula "Mis expedientes `<NIF>` (resumen)".
  - Sin certificado, `www1` responde `302` a `/Sede/errores/erro4033.html` ("No se detecta certificado electrónico").

Las recetas de abajo se guardan en un fichero local y se ejecutan con:

```bash
uv run scripts/sede.py ejecutar <receta.py> --sede aeat --url "<URL>" --titular yo
```

## 3. Trámites

### 3.1 Consulta de deudas (`aeat-deudas`) · Leer · verificado con certificado

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/SRVO-JDIT/ConsultaDdas?faccion=CONS_DDAS`
- **Pasos:** el campo `#fnif` viene relleno con el NIF del certificado. Pulsa `#ACEPTAR`.

```python
pg.click("#ACEPTAR")
pg.get_by_text("Datos del contribuyente").first.wait_for(timeout=60000)
captura("deudas")
RESULTADO = {"titulo": pg.title(), "texto": redactar(" ".join(pg.inner_text("body").split()))[:3000]}
```

- **Consultar:** la pantalla "Pagar / Consultar deudas". "Exportar" (`#botonFORM`) es libre.
- **Pagar (acto `pagar` + `firmar`):** "Pagar todas mis deudas" (`/wlpl/SRVO-JDIT/PagarTodas`) → "Pago mediante cargo en cuenta" (`/wlpl/OVPP-PAGO/LiquidacionesCuenta`) → "Firmar y Enviar" (firma JS de la AEAT).
  - Con permiso: `--permitir pagar,firmar`.
  - **Antes de pagar**, confirma con tu usuario el **importe** y la **cuenta**, salvo que te haya delegado pagos sin consulta.
  - Prueba: el **NRC** y el justificante (`ImpresionPDF?nrc=…`). Después, la consulta debe decir "No existen deudas para mostrar".
  - Sin permiso: dale el enlace y el botón.
- **Éxito:** título "Pagar / Consultar deudas", con las secciones "Datos del contribuyente" y "Avisos". Sin deudas, "Avisos" dice literalmente "No existen deudas para mostrar" (verificado el 15-10-2026).

### 3.2 Mis datos censales (`aeat-datos-censales`) · Leer · verificado

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/BUGC-JDIT/MdcAcceso`. Basta con `abrir`.
- **Qué muestra:** datos identificativos y domicilio fiscal, y dos pestañas: "Mis Obligaciones" (`/wlpl/BUGC-JDIT/ConsultaObligaciones`) y "Mis Representados".
- **Cambios:** "Cambio de Domicilio Fiscal" y "Alta de Domicilio de Notificaciones" son el acto `cambiar_datos` (y `firmar`). Cualquier cambio censal es un 036 (ficha G322): actos `firmar` + `presentar`. Hazlo solo si tu usuario te lo pide y te lo permite.
- **Éxito:** título "Consulta de Datos Identificativos y Censales". Para deducir obligaciones, ver `perfil-autonomo.md`.

### 3.3 Mis expedientes (`aeat-mis-expedientes`) · Leer · verificado

- **URL directa:** `https://www1.agenciatributaria.gob.es/wlpl/TEWV-CORE/ResumenVlt`.
- **Entrada pública:** `https://sede.agenciatributaria.gob.es/Sede/mi-area-personal.html` → "Mis expedientes". La antigua `/Sede/mis-expedientes.html` da 404 desde el 15-10-2026.
- **Qué muestra:** un árbol por organismo, con accesos a declaraciones presentadas, notificaciones no leídas, domiciliaciones (`ECDM-MANT/DomQueryN`) y asientos registrales (`REGD-JDIT/SvRegMisAsiIntQue`).
- **Notificaciones:** no entres en "notificaciones no leídas" desde aquí: usa el listado de 3.6.
- **Éxito:** título "Mis expedientes `<NIF>` (resumen)". Aquí se ven también los aplazamientos solicitados.

### 3.4 Datos fiscales (`aeat-datos-fiscales`) · Leer · verificado

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/DFPA-D182/SvVisDF25Net`. El sufijo `25` es el ejercicio 2025 y cambia en cada campaña de Renta.
- **Ejercicios anteriores:** `SvVisDF<AA>Net?nif=<NIF>`. La URL lleva el NIF: redáctala antes de mostrarla o guardarla.
- **Éxito:** título "Consulta de Datos Fiscales `<ejercicio>`".

### 3.5 Declaraciones presentadas y su copia (`aeat-declaraciones-presentadas`) · Leer · verificado (listado)

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/SCEJ-MANT/CONSUL/index.zul?MODELO=<100|130|111|115|303|390>&EJERCICIO=<AAAA>`.
  - Es una aplicación ZK: NIF, modelo y ejercicio vienen precargados.
  - `EJERCICIO=-1` es el ejercicio en curso.

```python
pg.get_by_role("button", name="Buscar").click()
# OJO: con resultados, el primer "Fecha y Hora de presentación" es un elemento oculto (menú de columnas):
# hay que esperar al primero VISIBLE o la receta da TimeoutError justo cuando sí hay declaraciones.
pg.locator("text=/Fecha y Hora de presentaci|No se han encontrado resultados/ >> visible=true").first.wait_for(timeout=60000)
captura("declaraciones")
RESULTADO = {"texto": redactar(" ".join(pg.inner_text("body").split()))[:4000]}
```

- **Columnas:** dependen del modelo. Habitual: Desistir, Tipo de solicitud, Observaciones, Expediente, Periodo, Estado, Fecha y Hora de presentación, Obtención de Justificante, Descarga fichero presentado. En el **modelo 100** (Renta) salen solo Expediente, Periodo (`0A`), Fecha y Hora de presentación, Obtención de Justificante y Descarga fichero presentado (verificado el 15-10-2026).
- **Cómo resumirlo:** por cada fila, modelo, periodo, estado y fecha de presentación. El nº de expediente es un dato personal: no lo copies a informes.
- **Copia de la declaración:** botón "Ver" de "Obtención de Justificante" (PDF con justificante y copia, según la ayuda oficial). No se pulsó en el mapeo: **sin verificar**.
- **"Dar de baja"** (columna Desistir) es el acto `cambiar_datos`: desiste de una declaración. Solo con petición expresa de tu usuario.
- **Éxito:** filas con "Estado" y "Fecha y Hora de presentación", o el texto "No se han encontrado resultados para la consulta realizada.".
- **Truco:** busca varios ejercicios en la misma sesión; repetir el login por cada ejercicio daba timeout.

### 3.6 Notificaciones, solo listado (`aeat-notificaciones`) · Leer · verificado (15-10-2026)

Procedimiento completo y cálculo de plazos: `tramite-vigilar-notificaciones.md`.

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/GNNO-JDIT/SvInteresadosQuery?VEZ=BUSCAR1` (título "Consulta de notificaciones y comunicaciones").
- **Campos:**
  - `F_TIPO_CONSULTA`: Todos / Notificación Notificada / Notificación NO Notificada / Comunicación.
  - `F_FECHA_DESDE` y `F_FECHA_HASTA`: obligatorias, `<input type=date>`, se rellenan con `AAAA-MM-DD`.
  - `F_LEIDA`: Todos / Sí / No.

```python
pg.fill("#F_FECHA_DESDE", "<AAAA-MM-DD>")   # p. ej. hace 12 meses: las pendientes antiguas también importan
pg.fill("#F_FECHA_HASTA", "<AAAA-MM-DD>")
with pg.expect_navigation(timeout=60000):
    pg.get_by_role("button", name="Buscar").click()
captura("notificaciones-listado")
RESULTADO = {"texto": redactar(" ".join(pg.inner_text("body").split()))[:4000], "bloqueos": bloqueos()}
```

- **Estado de la guarda:**
  - En el mapeo, "Buscar" llamaba a `form.submit()` hacia `/wlpl/GNNO-JDIT/SvInteresadosQuery` y la guarda lo anulaba. Era un falso positivo: la página cuenta como "de notificaciones" por su título.
  - **Ya está corregido:** `sede.py` permite el `form.submit` a acciones de consulta (`...Query`) mientras el formulario no pida abrir o descargar.
  - **Verificado el 15-10-2026** con certificado de persona física: el listado sale sin ningún "BLOQUEADO" (con y sin filas).
- **Columnas del listado:** Nº Certificado, Concepto, Tipo (Notificación / Comunicación), Titular, Destinatario, Fecha emisión, Fecha notificación, Modo notificación ("Comparecencia Electrónica", "Electrónico accedida"…) y **Leída** (Sí/No).
  - **Pendiente** = Tipo "Notificación" con "Fecha notificación" vacía o Leída "No". Avísalo y calcula el plazo con la "Fecha emisión" como puesta a disposición (`tramite-vigilar-notificaciones.md` §3).
  - Sin filas, la página dice "No se han obtenido resultados para estos datos".
  - Nº Certificado y el concepto llevan referencias de expediente: no los copies fuera de la conversación.
- **Abrir una notificación** es comparecer (acto `comparecer`, empiezan los plazos). Con ese permiso, confirma con tu usuario cuál abrir (`tramite-vigilar-notificaciones.md` §2.1); sin él, para en el listado. Abrir con el agente está **pendiente de verificar en vivo**.
- **No uses** el "Resumen de notificaciones no leídas" (`GNNO-JDIT/ResumenInteresados`) para listar: lleva el subtítulo "(Comparecencia en Sede)" y no está mapeado.

### 3.7 Certificado de estar al corriente, G304 (`aeat-certificado-corriente`) · Actuar (`generar` + `firmar`)

Ver `tramite-certificado-corriente.md`.

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/EMCE-JDIT/ECOTInternetCiudadanosServlet`.
- **Pasos:** elegir con tu usuario representación, tipo de certificado y fecha, y pulsar "Validar solicitud".
- **"Firmar Enviar"** es el acto `firmar` (y `generar`): con esos permisos lo pulsas tú (`--permitir generar,firmar`); sin ellos, para ahí y díselo.

### 3.8 Certificado de situación censal, G313 (`aeat-certificado-situacion-censal`) · Actuar (`generar` + `firmar`) · parcial

- **URL:** `https://www1.agenciatributaria.gob.es/wlpl/EMCE-JDIT/ServletSitCenInternet` ("Certificados Tributarios").
- **Campos:**
  - `fTipoRepresentacion0/1`: en nombre propio o en representación.
  - `fNifT` y `fNombreT`: solo si se actúa en representación.
  - `fTipoModelo0/1`: General, o Revendedor (art. 84.Uno.2º LIVA).
- **Pasos:** rellenarlo y pulsar "Validar solicitud" (`#validarSolicitud`).
- **Después:** el paso siguiente no se ha recorrido. Se espera un resumen con "Firmar Enviar", como en el G304: mismo acto y mismos permisos.

### 3.9 Certificados ya expedidos, G331 (`aeat-certificados-expedidos`) · Leer · pendiente

- **URL:** `https://www1.agenciatributaria.gob.es/L/inwinvoc/es.aeat.dit.adu.emce.recogidaCertInt.RceAcciones?fAccion=0&fTramite=G3311&fTipoPet=2`.
- Sirve para comprobar que un certificado pedido se ha emitido. No recorrido con certificado.

### 3.10 Modelos 130, 303, 111, 115 y 390 · Actuar (`presentar` + `firmar`, y `pagar` si sale a ingresar)

| Modelo | URL (`https://www1.agenciatributaria.gob.es` + …) | Botón final |
|---|---|---|
| 130 (G601) | `/wlpl/PAMW-M130/E2026/CONT/index.zul` (el año cambia) | "Formalizar Ingreso / Devolución" y después la firma |
| 303 (G414) | `/wlpl/TOAE-JDIT/VentanaCensalIva?fOrigen=pre303`: NIF, `select#EJERCICIO`, `select#PERIODO` (1T–4T, 01M–12M) y "Confirmar" | "Seleccionar Ingreso/Devolución" y después la firma |
| 111 (GH01) | `/wlpl/OV17-M111/index.zul` | "Formalizar Ingreso / Devolución" |
| 115 (GH02) | `/wlpl/OV17-M115/index.zul` | "Formalizar Ingreso / Devolución" |
| 390 (G412) | `/wlpl/PAIV-M390/E2025/CONT/index.zul` (18 páginas) | "Presentar declaración" |

- **Preparar (sin efectos):**
  - Abre el formulario para leer su estructura.
  - Calcula las casillas con tu usuario y dale la lista de casilla → valor.
  - Comprueba el plazo en `calendario-fiscal.md`.
- **Presentar** ("Guardar" borrador, "Formalizar…", "Presentar", "Firmar Enviar") es el acto `presentar` + `firmar`; si el resultado es a ingresar con cargo en cuenta, también `pagar`.
  - **Con esos permisos** (`--permitir presentar,firmar[,pagar]`): mete los valores, pulsa "Validar declaración", **enséñale a tu usuario el resultado (a ingresar o a devolver) y la cuenta** antes de firmar, y presenta. Todo en **una sola receta**: el navegador se cierra al acabar y la sesión se pierde. **Pendiente de verificar en vivo** de punta a punta.
  - **Sin ellos:** dale la lista de casillas y el enlace. Lo abre en su navegador, mete los valores, valida y presenta.
- **Éxito:** la declaración aparece en el listado de 3.5 con su "Fecha y Hora de presentación". El justificante (`scripts/justificante.py`) es la prueba.
  - El formato público del nº de justificante (13 dígitos que empiezan por el modelo) **no se ha verificado** en el mapeo.

### 3.11 Aplazamiento o fraccionamiento, RB01 (`aeat-aplazamiento`) · Actuar (`presentar` + `firmar`) · pendiente

- **Consulta:** las solicitudes ya hechas se ven en "Mis expedientes" (3.3).
- **Solicitud:** desde la ficha `https://sede.agenciatributaria.gob.es/Sede/procedimientoini/RB01.shtml`. Es el acto `presentar` + `firmar`. El formulario **no está mapeado**: con permiso, ábrelo con `probe`, acuerda plazos y cuenta con tu usuario y avísale de que es un recorrido sin verificar.

### 3.12 Censo, modelo 036, G322 (`aeat-censo-036`) · Actuar (`cambiar_datos`, `presentar` + `firmar`) · pendiente

- **Leer los datos:** como en 3.2.
- **Presentar un 036:** "Censos WEB" (`/wlpl/BU36-ASIS/M036/index.zul`, ZK) o el formulario 036. Cambia la situación censal: hazlo solo si tu usuario te lo pide y con esos permisos. **No mapeado.**

## 4. Trampas y problemas conocidos

- **ZK (formularios `.zul`):**
  - Los ids son dinámicos (p. ej. `z5QSxa`, con sufijo `-real`). Localiza los campos por texto o etiqueta.
  - `sede.py` acepta el `beforeunload`, así que se puede navegar después de un formulario ZK (verificado: 390 → G313).
- **Firma:** es JavaScript propio de la AEAT ("Firmar Enviar", `MiniGeneraFirma`), no AutoFirma. Sin el permiso `firmar`, `sede.py` la bloquea.
- **Datos personales en URLs y cabeceras:** `?nif=` en datos fiscales, y nombre y NIF en la cabecera. Pasa todo por `redactar()`.
- **WAF:** las rutas tipo `/x/presentar` devuelven 403 "Request forbidden by administrative rules".
- **Paradas técnicas:** si la sede no responde, consulta el horario de interrupciones (en Fuentes) antes de reintentar.
- **Representación:** con el selector y `rep=S` aparece el diálogo "en nombre propio / como representante" (`OVCT-CXEW/DialogoRepresentacion`), que hay que confirmar. Con el enlace directo a `www1` no sale.
- **Selector:** si lo usas, pasa `ref` codificado como URL; sin codificar, a veces no se pintan los botones.
- **Notificaciones obligatorias:** no solo para REDEME y Grandes Empresas. También para los sujetos del art. 14.2 de la Ley 39/2015, como los profesionales con colegiación obligatoria. Pregúntalo (`tramite-vigilar-notificaciones.md`).

## 5. Fuentes

- Fichas oficiales y ayudas de la AEAT: ver la cabecera.
- Mapeo en vivo del 15-10-2026: fases 1 y 2 y ronda 3, con certificado de persona física, sin firmar, presentar ni abrir nada. No se publican datos de ese mapeo.
- Aviso de la AEAT sobre el uso personal de Cl@ve (29-abr-2026): en la cabecera.
