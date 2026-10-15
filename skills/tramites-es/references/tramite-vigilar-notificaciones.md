---
verificado_el: 2026-10-15
fuentes:
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565   # Ley 39/2015: arts. 14.2, 30, 41.5 y 43
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/folleto-actividades-economicas/11-notificaciones-electronicas/11_2-notificaciones-electronicas-obligatorias-neo.html
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/ZN01.shtml
  - https://www.seg-social.es/wps/portal/wss/internet/HerramientasWeb/51148
  - https://www.boe.es/buscar/doc.php?id=BOE-A-2018-3080       # Orden ESS/214/2018 (TGSS)
  - https://dehu.redsara.es/es/public
  - https://sede.dgt.gob.es/es/multas/direccion-electronica-vial/
estado_mapeo: "Playbook transversal. Validación del 15-10-2026: listado AEAT y contador DEHú de Carpeta Ciudadana verificados de punta a punta; DEHú directo sigue con error=1000; TGSS y buzones municipales sin mapear con certificado; DGT DEV verificada solo hasta el acceso."
---

# Vigilar notificaciones sin abrirlas

**Riesgo: Leer.** El agente **lista** remitente, asunto, fecha de puesta a disposición y estado. **Abrir, aceptar, rechazar, descargar o "ver el detalle" es comparecer**: la persona queda notificada y empiezan a correr los plazos. Eso es siempre `riesgo: persona` (regla dura 2). `sede.py` bloquea esos clics en las páginas de notificaciones; si ves "BLOQUEADO", has llegado al límite.

## 1. Qué buzones mirar

Pregúntalo o dedúcelo del perfil (`perfil-autonomo.md`):

| Buzón | ¿Le afecta? | Guía | Estado del listado |
|---|---|---|---|
| **DEHú** | A casi todos: buzón común del Estado y de muchos organismos | `sede-dehu.md` | ✅ **verificado** (15-10-2026, pestaña de pendientes). El `error=1000` de la mañana no se repitió por la tarde: es intermitente |
| **AEAT** (NEO) | Obligatorio para los del art. 14.2 de la Ley 39/2015 (p. ej. **profesionales con colegiación obligatoria**), los inscritos en REDEME y Grandes Empresas. El alta es automática. Pregunta si está colegiado o en el REDEME. Aunque no esté obligado, la AEAT deja aquí las notificaciones de embargos, compensaciones o requerimientos: **míralo siempre** | `sede-aeat.md` §3.6 | ✅ **verificado** (15-10-2026) |
| **Seguridad Social** | **Todo autónomo** desde el 1-oct-2018 (Orden ESS/214/2018). También le llegan por DEHú | `sede-tgss-importass.md` §3.12 | ⏳ **pendiente**: no mapeado |
| **DGT, buzón DEV** | Solo si tiene DEV. Si no la tiene, la DGT redirige a `ErrorBuzon.faces`, que es un estado válido | `sede-dgt.md` §3.3 | ◐ **parcial**: acceso verificado; listado pendiente de verificar con una cuenta que tenga DEV |
| **ATC** (Canarias) | Autónomos en Canarias: "Mis notificaciones" de la sede de la ATC | `sede-atc.md` | Ver esa guía |
| **Ayuntamiento** | Si se relaciona con él por vía electrónica | `plataforma-*.md` + `buscar.py` | ⏳ **pendiente** en todas las plataformas |
| **Carpeta Ciudadana** (contador) | Atajo: número de notificaciones y comunicaciones pendientes en DEHú. **Úsalo primero** y como plan B si DEHú da `error=1000` | `sede-carpeta-ciudadana.md` §3.2 | ✅ **verificado** (15-10-2026) |
| **Tablón Edictal Único** | Notificaciones que no se pudieron entregar | `sede-carpeta-ciudadana.md` §3.1 (`mcc-teu`) | ✅ verificado |

**Verificados de punta a punta (15-10-2026):** AEAT, DEHú (pestaña de pendientes), contador DEHú de Carpeta Ciudadana y TEU. El resto, díselo a la persona y, si algo falla, pídele que mire ella el buzón.

## 2. Cómo listar en cada buzón

Usa solo `abrir`, `probe` (sin `--clic` sobre filas) o las recetas de las guías. Nunca hagas clic en una fila, en el identificador ni en "Acciones".

- **DEHú (contador, recomendado):** receta `mcc_notificaciones.py` de `sede-carpeta-ciudadana.md` §3.2. Da `numNotificaciones` y `numComunicaciones` pendientes en DEHú sin entrar en DEHú. Si es 0, no hace falta más. Si es > 0, el detalle lo ve la persona en DEHú (o tú, si DEHú ya acepta el login).
- **DEHú (listado):**
  1. Receta `dehu_listado.py` de `sede-dehu.md` §3.1 (login + pestaña de pendientes, con el texto del shadow DOM). Si acaba en `/es/public`, mira la cadena de navegaciones: el `error=` solo aparece un instante.
  2. La pestaña de pendientes ya muestra los dos contadores (pendientes y realizadas). Solo si hay realizadas que mirar, `?realized=true` en **otra** ejecución (tres cargas seguidas dieron `ECONNRESET`).
  3. Columnas útiles: Concepto, Organismo emisor, Fecha disposición y **Fecha caducidad**.
  4. Ventanas de fechas de 30 días como máximo, sin ráfagas.
- **AEAT:** receta de `sede-aeat.md` §3.6, sobre `GNNO-JDIT/SvInteresadosQuery?VEZ=BUSCAR1`.
  - Pon `F_TIPO_CONSULTA` = "Notificación NO Notificada" para ver solo las pendientes, y fechas en `AAAA-MM-DD`.
  - **No uses** `ResumenInteresados`, con el subtítulo "Comparecencia en Sede".
- **Seguridad Social:** sin mapear.
  - La investigación previa sitúa el buzón en la sede, en "Notificaciones telemáticas" (`https://sede.seg-social.gob.es/wps/portal/sede/sede/Inicio/NotificacionesTelematicas`).
  - Entra con la receta de login TGSS y haz solo `probe`. Documenta lo que veas en un issue, sin datos personales.
- **DGT DEV:** `abrir` sobre `https://auth-sedeweb.dgt.gob.es/WEB_NTRA_CONSULTA/listadoNotificacionesIdiomaPostback.faces?idioma=es`. `ErrorBuzon.faces` significa "no tiene DEV".
- **Ayuntamientos:** rutas observadas en la fase pública, **ninguna verificada con certificado**:
  - Gestiona (`*.sedelectronica.es`): `https://<municipio>.sedelectronica.es/enotifications`.
  - TAO/STA: área privada con `PAGE_CODE=SINGLE_NOTIF`. En algunos municipios el primer acceso exige confirmar teléfono o email con "GUARDAR". Eso es un cambio de datos: para.
  - OpenSIAC: `…/opensiac/carpetaciudadana/buzonnotificaciones_enter.action`.
  - AOC (Cataluña): e-NOTUM.
  - GSede/MOAD: enlaza a DEHú.
  - **Gestiona:** su ruta está en inglés (`enotifications`). `sede.py` la reconoce como página de notificaciones (patrón `enotif`). Aun así, no pulses nada dentro del buzón.
- **No aceptes** invitaciones a "suscribirse a notificaciones" ni a cambiar el canal (p. ej. en GTT o en el Cabildo). Es un cambio de datos.

## 3. Calcular el plazo de 10 días

Base legal: arts. 43.2, 41.5 y 30 de la Ley 39/2015.

- La notificación electrónica se entiende **practicada cuando se accede a su contenido**.
- Si es obligatoria o elegida y nadie la abre en **10 días naturales desde la puesta a disposición**, se entiende **rechazada**. El trámite se da por efectuado y el procedimiento sigue: **a efectos prácticos, cuenta como notificada**.
- Los días naturales incluyen sábados, domingos y festivos. Se cuentan desde el día siguiente a la puesta a disposición.

**Regla para el agente:**

```
último día para abrirla = fecha de puesta a disposición + 10 días naturales (hasta las 23:59)
```

- Ejemplo: puesta a disposición el 5-oct-2026 → último día para abrirla, el 15-oct-2026. Desde el 16-oct se tiene por notificada.
- **Si la sede muestra la fecha**, manda la sede. DEHú da la "Fecha caducidad"; úsala tal cual.
- Si la fecha calculada y la de la sede no coinciden, di las dos y quédate con la **más temprana**.
- **Después** (al abrirla o al vencer los 10 días) empieza el plazo del propio acto: alegar, recurrir, pagar, aportar documentos. Ese plazo se lee **dentro** de la notificación, así que solo la persona lo verá al abrirla. No lo inventes.
- **Estado "Expirada", "Rechazada" o vencida:** el plazo del acto **ya corre**. Avísalo como **urgente**.
- **Las comunicaciones** (AEAT: tipo "Comunicación"; DEHú: pestaña "Comunicaciones") no son notificaciones y no tienen este plazo. Dilo, pero no las abras tampoco.
- **Sin fecha de puesta a disposición** en el listado, no calcules nada. Di "no sé cuándo vence; ábrela tú pronto o mira la fecha en la sede".

## 4. Qué decirle a la persona

Plantilla (sin datos que no hagan falta; enmascara NIF y referencias):

> **Tienes `<N>` notificaciones sin abrir.**
> 1. **`<Organismo emisor>`**: `<concepto>`. Puesta a disposición: `<fecha>`. **Si no la abres, se dará por notificada el `<fecha límite + 1>`** (último día para abrirla: `<fecha límite>`).
> 2. …
>
> No las he abierto: abrirlas hace que empiecen a correr los plazos para responder.
> - **Para leerla:** entra en `<enlace del buzón>` con tu certificado, busca la fila y pulsa `<botón exacto: p. ej. "Aceptar" en "Acciones" de DEHú>`.
> - Cuando la abras, si quieres, te ayudo a entender qué te piden y qué plazo tienes.

Añade, según el caso:

- **Vencida o "Expirada":** "Esta ya cuenta como notificada desde `<fecha>`. Conviene que la abras hoy."
- **Buzón no mirado por un fallo** (DEHú `error=1000`, Carpeta Justicia, guarda): "No he podido revisar `<buzón>` por `<motivo>`. Míralo tú en `<enlace>`."
- **Sin notificaciones:** "No hay notificaciones pendientes en `<buzones revisados>` a fecha `<hoy>`." Di siempre **qué buzones no se han podido revisar**.

## 5. Después

- **Datos de la persona:** no guardes el listado en notas ni memorias sin su permiso (regla dura 8).
  - Si quiere seguimiento, guarda solo organismo, fecha de puesta a disposición y fecha límite.
- **Si la persona abre una notificación y pide ayuda:** puede pasarte el PDF. Léelo y explícaselo; el trámite de respuesta sigue sus propias reglas (firma y presentación de la persona).
- **Frecuencia razonable:** una revisión por buzón cada pocos días. Los plazos son de 10 días naturales y hay WAF.
- **Correos que avisan de una notificación:** no sigas sus enlaces. Entra por la URL oficial. DEHú ofrece un validador público de correos (`sede-dehu.md` §3.2).

## 6. Trampas

- **`sede.py` y las páginas de notificaciones:**
  - Las detecta por "notificaci", "notification", "enotif", "buzón", `SINGLE_NOTIF` o `/dev` en la URL, por "notificaci"/"buzón" en el título, y en DEHú por el host.
  - En esas páginas bloquea "acceder", "abrir", "comparecer", "aceptar", "rechazar", "descargar", "consultar", "leer" y "ver el documento o detalle".
  - La búsqueda de la AEAT, que antes era un falso positivo, ya está permitida: deja pasar el `form.submit` a acciones de consulta (`…Query`).
- **La misma notificación puede estar en dos buzones** (AEAT y DEHú). Cuéntala una vez y no la abras en ninguno.
- **Tokens de DEHú** en `localStorage`: no los leas ni los registres.

## 7. Fuentes

- Ley 39/2015, folleto NEO de la AEAT, ficha ZN01, TGSS (notificaciones obligatorias y Orden ESS/214/2018), DEHú y DGT DEV: ver la cabecera.
- Mapeo en vivo del 15-10-2026: ninguna notificación abierta.
