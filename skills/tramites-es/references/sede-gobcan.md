---
verificado_el: 2026-10-15
estado_mapeo: parcial   # catálogos y fichas públicas verificados; con certificado, el acceso se detiene en «Validarme» (AutoFirma) y en el Cabildo la sesión no persistió
fuentes:
  - https://sede.gobiernodecanarias.org/sede/
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites
  - https://sede.gobiernodecanarias.org/sede/la_sede/sistemas_firma
  - https://sede.gobiernodecanarias.org/sede/la_sede/requisitos_tecnicos
  - https://sede.gobiernodecanarias.org/sede/la_sede/interrupciones
  - https://sede.gobiernodecanarias.org/sede/area_personal
  - https://sede.gobiernodecanarias.org/sede/notificaciones
  - https://sede.gobiernodecanarias.org/sede/rge
  - https://www.gobiernodecanarias.org/transformaciondigital/platino/infogeneral/
  - https://www.gobiernodecanarias.org/empleo/sce/principal
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/3885    # SCE: empleo autónomo
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/10923   # SCE: Concilia autónomos
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/4049    # SCE: renovación con certificado
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/4050    # SCE: renovación sin certificado
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/5538    # alta de terceros
  - https://sede.tenerife.es/es
---

# Gobierno de Canarias (sede y tramitador), Servicio Canario de Empleo y Cabildo de Tenerife

Los impuestos de la comunidad (IGIC, 400, 420, 425) **no** están aquí: van en `sede-atc.md`. Los tributos municipales, en `canarias-recaudacion.md`.

## Para qué sirve

- **Sede del Gobierno de Canarias** (`sede.gobiernodecanarias.org/sede/`): catálogo de procedimientos autonómicos con código **SICAC** (y SIA), Registro General Electrónico, área personal (registros, expedientes, borradores, buzón de notificaciones) y verificación de documentos. Ayudas para autónomos de la DG de Autónomos, alta de terceros para cobrar subvenciones, turismo, industria, sanidad…
- **Servicio Canario de Empleo (SCE):** sus procedimientos son fichas de la misma sede (mismo host y mismo acceso). Para autónomos: subvenciones de empleo autónomo, Concilia y renovación de la demanda de empleo.
- **Cabildo de Tenerife** (`sede.tenerife.es`): sede propia. Solicitud general, ayudas insulares, transporte (taxi, VTC, alquiler sin conductor), pago de tasas y área personal.

**Sobre el nombre «PLATINO».** El mapeo y el historial del proyecto llaman «PLATINO» al tramitador y a su acceso con certificado. Según el propio Gobierno, PLATINO es su plataforma de **interoperabilidad** (notificaciones, portafirmas, verificación de datos), no el tramitador. Aquí decimos «el tramitador de la sede».

## Acceso

### Sede del Gobierno de Canarias y SCE

| Dato | Valor |
|---|---|
| Menú de identificación | `https://sede.gobiernodecanarias.org/sede/identificacionmenu` |
| Pantalla de certificado | `https://sede.gobiernodecanarias.org/sede/identificacion` |
| Métodos | Certificado o DNIe (con AutoFirma) y Cl@ve. El certificado software da nivel **medio**, el DNIe nivel alto |
| Origins | `https://sede.gobiernodecanarias.org` (el portal del SCE está en `https://www.gobiernodecanarias.org`) |
| `sede.py` | `--sede gobcan` o `--sede sce` |

- **Secuencia con certificado:** «Certificado Digital / DNI-E» → **Validarme**. Ese botón ejecuta `firmar(formData)`, que abre AutoFirma para firmar el acceso. `sede.py` lo bloquea (**BLOQUEADO**) antes de AutoFirma: es lo esperado. **El acceso lo hace la persona.**
- No hay certificado por TLS (ni en el *handshake* ni en `/sede/identificacion`; comprobado el 15-10-2026). El certificado se elige desde AutoFirma, **no** desde el navegador: el desplegable `#validCertificates` sale vacío con el certificado de `sede.py`.
- **Nunca rellenes ni toques** los campos ocultos `certificadoSeleccionado`, `hiddenInfoCertificado` y `firma`, ni intentes sortear el bloqueo.
- La rama Cl@ve → «DNIe / Certificado electrónico» **no se ha probado** en esta sede. Si la pruebas, añade `https://pasarela-ident.clave.gob.es` a los origins y documenta el resultado (`sede-clave.md`). Cl@ve PIN, Móvil y Permanente, nunca.
- **Cómo saber que entró:** no verificado en el mapeo. Pide a la persona que confirme que ve su nombre en el área personal.
- La página de requisitos técnicos pide AutoFirma, Java y Acrobat Reader (`setup-autofirma.md`).

### Cabildo de Tenerife

| Dato | Valor |
|---|---|
| Login | `https://sede.tenerife.es/es/acceso?returnBack=personal%2Fvista-general` |
| Ruta | Área personal → **Identificarme** → Cl@ve → **DNIe / Certificado electrónico** |
| Origins | `https://sede.tenerife.es`, `https://pasarela.clave.gob.es`, `https://pasarela-ident.clave.gob.es` (aquí pide el certificado; ver `sede-clave.md`) |
| `sede.py` | `--sede cabildo-tenerife` |

- `sede.tenerife.es` no pide certificado por TLS. **Identificarme** envía un POST SAML a la pasarela Cl@ve.
- **Estado:** con certificado, Cl@ve devolvió a la sede (`/api/auth/val`, 303), pero **la sesión no se mantuvo** y el área personal volvió a la pantalla de acceso. En una revisión anónima posterior, `/es/acceso` cargó sin bucles. No se ha repetido con certificado. Si falla igual, para: lo hace la persona en su navegador.
- **Cómo saber que entró:** en el área personal (`https://sede.tenerife.es/es/personal/vista-general`) ya no aparece **Identificarme**. No verificado.

### Mantenimiento

El Gobierno publica sus cortes en `https://sede.gobiernodecanarias.org/sede/la_sede/interrupciones` (más de 700 avisos en el histórico). Son frecuentes **por la tarde** y afectan también a Cl@ve: trabaja por la mañana.

## Trámites

### Buscar un procedimiento del Gobierno (riesgo: leer)

- **Buscador por URL:** `https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites?titulo=<texto>`. Por ejemplo, `?titulo=autónomos` devolvió 5 procedimientos de la DG de Autónomos el 15-10-2026.
- **Ficha:** `https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/<SICAC>` (alias corto `/sede/tramites/<SICAC>`). Muestra plazo, requisitos y el botón «Trámite electrónico».
  ```bash
  uv run scripts/sede.py abrir --sede gobcan --url "https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites?titulo=autónomos"
  uv run scripts/sede.py abrir --sede gobcan --url "https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/<SICAC>"
  ```
- Lee en la ficha si está **en plazo** antes de seguir. El botón «Trámite electrónico» lleva a uno de estos destinos:
  - tramitador genérico: `/sede/tramitador/creacion/tramites/<ID>`;
  - salto a una aplicación del departamento: `/sede/ticketsso/tramites/<ID>` o `/sede/ticketsso3/tramites/<ID>`;
  - aplicaciones de la ATC: `/tributos/…` (`sede-atc.md`).
- **Dónde para el agente:** en la ficha. Entrar al tramitador **puede crear un borrador** («solicitudes pendientes de firmar o presentar»): no lo abras sin que la persona lo pida.

### Registro General Electrónico (riesgo: persona)

- **Ficha:** `https://sede.gobiernodecanarias.org/sede/rge`. Tramitador: `https://sede.gobiernodecanarias.org/sede/tramitador/creacion/tramites/registro_electronico`.
- Sirve para escritos a cualquier órgano de la comunidad. Hay documentos excepcionados cuya presentación no surte efecto, y los modelos 400, 420 y 425 **no** valen por aquí.
- El agente redacta el texto del escrito y la lista de adjuntos. La persona entra (Validarme), rellena, firma y presenta.
- **Cómo verificar:** justificante con número de registro y el asiento en el área personal, «Consulta de documentos presentados».

### Área personal y notificaciones (riesgo: leer; pendientes)

- **Área personal:** `https://sede.gobiernodecanarias.org/sede/area_personal`. Secciones:
  - documentos presentados: `/sede/area_personal/asientos_registrales`;
  - documentos de respuesta inmediata (certificados, licencias): `/sede/area_personal/documentos_respuesta_inmediata`;
  - solicitudes pendientes, es decir, borradores: `/sede/area_personal/solicitudes_pendientes`;
  - consulta de expedientes: `/sede/area_personal/consulta_expedientes`;
  - buzón de notificaciones: `/sede/area_personal/buzon_notificaciones`.
  Todo está tras Validarme: **no mapeado con sesión**. Si la persona entra y comparte pantalla, solo se lee.
- **Notificaciones:** el Gobierno notifica por **DEHú** (convenio con la AGE) y por comparecencia en su sede. Para vigilar, usa primero `tramite-vigilar-notificaciones.md`. Información pública: `https://sede.gobiernodecanarias.org/sede/destacados_l/notificaciones_telematicas`. Solo **listar**, nunca abrir.
- **Gestión de datos personales** (`/sede/area_personal/datos_personales`): cambiar datos es de la persona (regla 7 de `SKILL.md`).

### Alta o modificación de terceros, SICAC 5538 (riesgo: persona)

- **Ficha:** `https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/5538`. Tramitador: `/sede/tramitador/creacion/tramites/5538`. Respuesta inmediata.
- Es el alta de la cuenta bancaria para **cobrar subvenciones** del Gobierno; muchas convocatorias la exigen. Contiene el IBAN: la persona introduce y firma sus datos. El agente solo le avisa de que hace falta.

### Servicio Canario de Empleo (riesgo: persona)

| Trámite | Ficha | Notas del 15-10-2026 |
|---|---|---|
| Subvenciones de promoción del empleo autónomo | `…/tramites/3885` | Convocatoria 2026 **cerrada** (plazo hasta el 30-06-2026). Exigía alta previa en RETA o mutualidad, IAE, IGIC (salvo exención), plan de viabilidad validado y alta de terceros |
| Concilia para autónomos | `…/tramites/10923` | Ficha y normativa 2026 verificadas; no se inició |
| Renovación de la demanda con certificado | `…/tramites/4049` | Va por salto SSO (`/sede/ticketsso3/tramites/4049`). **Renovar cambia el estado** de la demanda |
| Renovación de la demanda sin certificado | `…/tramites/4050` | Abre un iframe `SERELE-Inter` bajo el mismo host. No introduzcas datos |

`…` = `https://sede.gobiernodecanarias.org/sede/procedimientos_servicios`.

El agente lee la ficha, comprueba plazo y requisitos, y prepara la documentación. Solicitar o renovar lo hace la persona. Para buscar ayudas abiertas, usa también `ayudas.md`.

### Cabildo de Tenerife

| Trámite | URL | Riesgo | Estado |
|---|---|---|---|
| Área personal (expedientes, notificaciones) | `https://sede.tenerife.es/es/personal/vista-general` | leer | Sesión no persistió |
| Solicitud general (SIA 1246253) | `https://sede.tenerife.es/es/tramites/1246253-Solicitud-general` | persona | Ficha verificada |
| Ayudas 2026 a proyectos industriales de pymes y autónomos (SIA 3246163) | `https://sede.tenerife.es/es/tramites/3246163-Subvenciones-para-la-creacion-de-nuevos-proyectos-industriales-pymes-y-autonomos-convocatoria-2026` | persona | Ficha verificada |
| Vivienda vacacional, declaración responsable de inicio (SIA 1161501) | `https://sede.tenerife.es/es/tramites/1161501-Declaracion-responsable-de-inicio-de-la-actividad-de-vivienda-vacacional` | persona | El botón deriva a otra administración; destino no seguido |
| Taxi, VTC, alquiler sin conductor | buscador `https://sede.tenerife.es/es/tramites` | persona | Ejemplos: SIA 3036014 (visado VTC), 3231056 (visado taxi), 3178266 (alquiler sin conductor) |
| Pago de tasas y sanciones | `https://sede.tenerife.es/es/pago-tasas-sanciones` | persona | Solo inventariado |
| Cambio de canal de notificación (SIA 2307462) | `https://sede.tenerife.es/es/tramites/2307462-Solicitud-de-cambio-de-canal-de-notificacion` | persona | Cambia datos: solo si la persona lo pide |

- Las fichas tienen la forma `/es/tramites/<SIA>-<slug>`. La tramitación está en `/es/tramitar/<SIA>-<versión>-<slug>`: `sede.py` bloquea abrir esa ruta directamente y es de la persona.
- Es una aplicación Angular: usa el buscador de la página, no llames a su API interna.

## Trampas

- **BLOQUEADO en «Validarme»** es lo normal: el acceso al tramitador del Gobierno pasa por AutoFirma.
- **Borradores:** entrar en `/sede/tramitador/creacion/…` puede crear una solicitud pendiente. Si la persona retoma un borrador, puede haber que encadenar varios «Continuar».
- **Firmar por partes:** en el tramitador se firma cada adjunto y la instancia por separado, y antes hay que pulsar «Guardar y validar». Todo eso lo hace la persona en AutoFirma.
- **Representación:** si actúa una sociedad con su propio certificado, la persona debe revisar la casilla de «representa a un tercero» (en el historial del proyecto hubo que desmarcarla).
- **Fichas fuera de plazo:** la ficha avisa antes de llegar al tramitador. Léela siempre.
- **Revisa el resumen campo a campo** antes de que la persona firme: en el historial del proyecto se coló una errata en el email de una solicitud.
- **Cabildo:** sesión inestable tras Cl@ve. No insistas con cookies ni reintentos en bucle.

## Fuentes

- Mapeo en vivo de tramites-es del 15-10-2026 (solo lectura, sin datos personales): Registro General Electrónico hasta «Validarme», fichas del SCE (3885, 10923, 4049, 4050, 5538), sede del Cabildo hasta la pasarela Cl@ve con y sin certificado.
- Investigación del proyecto (R4 §3, informe 01 §4.2): catálogo SICAC, tipos de tramitador, área personal y notificaciones, lecciones del tramitador.
- Páginas oficiales citadas en la cabecera; área personal y buscador comprobados por GET el 15-10-2026.
