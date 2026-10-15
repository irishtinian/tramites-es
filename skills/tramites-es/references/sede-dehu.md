---
verificado_el: 2026-10-15
fuentes:
  - https://dehu.redsara.es/es/public
  - https://dehu.redsara.es/es/config/env.json          # catálogo público de la API de la SPA
  - https://dehu.redsara.es/api/v1/faq                  # FAQ oficial (JSON)
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565   # Ley 39/2015, arts. 41 y 43
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3). Login hasta Cl@ve verificado; DEHú rechaza después la sesión con certificado (error=1000, causa desconocida). Listado no obtenido en vivo: estructura sacada del front público."
---

# DEHú: Dirección Electrónica Habilitada única

## 1. Para qué sirve

DEHú es el buzón común de notificaciones de la Administración del Estado y de muchos otros organismos. La Seguridad Social, por ejemplo, también notifica aquí.

El agente **solo lista**: organismo, concepto, fecha de puesta a disposición y fecha de caducidad.

**Abrir, aceptar, rechazar o descargar una notificación es comparecer.** La persona queda notificada y empiezan a correr los plazos. Eso lo hace siempre ella. Procedimiento y cálculo de plazos: `tramite-vigilar-notificaciones.md`.

## 2. Acceso

- **Entrada directa:** `https://dehu.redsara.es/api/login/login-clave-sso?selectedLanguage=es`.
  - Devuelve un `form#claveform` que se envía solo por POST a `pasarela.clave.gob.es/Proxy2/ServiceProvider`.
  - Es el mismo enlace que usa "Mis notificaciones" de Mi Carpeta Ciudadana.
- **Botón de portada:** está en shadow DOM (`dnt-button.access-btn`); con Playwright, `dnt-button.access-btn button`. Hace `GET /api/login/login-clave-form` y envía el SAML.
- **Después:** pasarela Cl@ve → "DNIe / Certificado electrónico" (`sede-clave.md`) → `POST https://dehu.redsara.es/api/login/login-check`.
- **Origins con certificado:** `https://pasarela-ident.clave.gob.es`. `dehu.redsara.es` no pide certificado.
- **Qué certificado:** el de la persona física. Para empresas, ver "Grandes destinatarios" en las trampas.
- **Cómo saber que entró:**
  - `login-check` redirige a `/es/...` con sesión.
  - Si falla, redirige a `/es/login?error=<código>` y la SPA vuelve a `/es/public`.
  - Lee siempre el `error=` de la URL y tradúcelo con esta tabla:

| `error=` | Significado (textos del propio front de DEHú) |
|---|---|
| 1000 | Error genérico en el proceso de autenticación |
| 2000 / 3000 | Error en Cl@ve Permanente / Cl@ve PIN |
| 2001 | Usuario no registrado |
| 4000 | Error con el certificado electrónico |
| 4001 / 4002 / 4003 | Error consultando @Firma / no se envió certificado a @Firma / error interno de @Firma |
| 4004 | Certificado no soportado por @Firma |
| 4005 | Nivel de seguridad (LoA) insuficiente |
| 5000 | Error de autenticación: reintentar |

```bash
uv run scripts/sede.py ejecutar clave_login.py --sede dehu --titular yo   # receta de sede-clave.md
```

### Fallo abierto: login rechazado (`error=1000`)

- **Revalidado** el 15-10-2026 en la validación de la v0.1 (1 intento útil): misma cadena `ServiceRedirect → AuthenticateCitizen → ResponseRedirect → /es/login?error=1000 → /es/public`.
- **Cómo verlo:** la SPA borra el `error=` en menos de un segundo; `pg.url` acaba en `/es/public`. Registra las navegaciones antes de pulsar el botón de Cl@ve:
  ```python
  vistos = []
  pg.on("framenavigated", lambda f: vistos.append(f.url.split("&")[0]) if f == pg.main_frame else None)
  # … receta clave_login.py … y al final: RESULTADO = {"navegaciones": vistos}
  ```
- **Qué pasó** (15-10-2026): Cl@ve autenticó bien (`AuthenticateCitizen` 200 → `ResponseRedirect`), pero `POST /api/login/login-check` respondió `302 → /es/login?error=1000`.
- **Se probó:** las dos entradas, 3 intentos y 1 reintento. Las cookies de sesión (`ID_SESSION`, `SameSite=None`) **sí** llegaban.
- **Descartado:** el mismo certificado entró por Cl@ve en Carpeta Ciudadana, DGT y Justicia, así que el fallo es de DEHú con ese titular o certificado.
- **Causa:** **desconocida**. Hipótesis sin comprobar: alta pendiente en DEHú, o tipo de certificado no admitido.
- **Qué hacer si te pasa:**
  1. No insistas: más de 2 intentos no aportan nada y el WAF puede bloquear.
  2. Dile a la persona que entre ella en `https://dehu.redsara.es` con su certificado.
  3. Si a ella le funciona, apunta en un issue (sin datos personales) el tipo de certificado y el código.
  4. Mientras tanto, usa el **contador de Carpeta Ciudadana** (`sede-carpeta-ciudadana.md` §3.2, verificado: da el nº de notificaciones pendientes en DEHú) y los buzones de cada organismo (AEAT, TGSS, DGT).
- Antes, la guarda de `sede.py` anulaba el autoenvío SAML hacia Cl@ve en `dehu.redsara.es`. **Ya está corregido:** se permite el `form.submit` a acciones de autenticación (Cl@ve, SAML, login).

## 3. Trámites

### 3.1 Listado de notificaciones (`dehu-notificaciones`) · Leer · pendiente

Esta estructura sale del `env.json` público y del bundle de la SPA. **No se ha verificado en vivo.**

| | Pendientes | Realizadas |
|---|---|---|
| Ruta SPA (pestaña) | `https://dehu.redsara.es/es/notifications` | `https://dehu.redsara.es/es/notifications?realized=true` |
| API que usa la SPA | `GET /api/v1/notifications?…&page=<n>&limit=10` | `GET /api/v1/realized_notifications?…&page=<n>&limit=10` |
| Columnas | Identificador, Concepto, Organismo emisor, Organismo raíz, Titular, Vínculo, Fecha disposición, **Fecha caducidad**, Acciones | Las mismas, más **Fecha comparecencia / estado final** y **Estado** (Aceptada, Rechazada, Expirada, Expirada TEU) |

- **Otras pestañas:** comunicaciones (`/es/comunications`) y anuncios del Tablón Edictal Único (`/es/notifications-edictals`).
- **Filtros:**
  - fechas de puesta a disposición (`availabilityDate`), de expiración y de comparecencia, en dd/mm/aaaa;
  - vínculo, organismo emisor, NIF del titular, identificador;
  - tipo de entrega: postal o electrónica.
- **Pasos:**
  1. Login (sección 2).
  2. `nav` a la ruta SPA de pendientes. Espera a que cargue la tabla.
  3. `captura` y `redactar(inner_text)`.
  4. Repite con la de realizadas si hace falta.
  - Pide **ventanas de fechas de 30 días o menos**: los rangos largos dan error (`…date-range-to-long-error`).
- **Dónde para el agente:** en la tabla. **No pulses nada en la columna "Acciones"** ni el identificador.
- **La persona:** para leer una notificación entra ella en DEHú, pestaña "Pendientes", y en "Acciones" elige aceptar o rechazar. Cl@ve le pedirá autenticarse de nuevo para firmar la comparecencia.
- **Éxito:** tabla con filas, o vacía, en la pestaña pedida.
- **Pendiente frente a realizada:**
  - Pendiente = no comparecida, con "Fecha caducidad".
  - Realizada = aceptada, rechazada o expirada. Si está "Expirada", **ya se tiene por notificada**: es urgente decírselo a la persona.

### 3.2 Servicios públicos (`dehu-publico`) · Leer · verificado sin certificado

`https://dehu.redsara.es/es/public` ofrece tres servicios: buscador de organismos, **validador de autenticidad de correos** (útil ante un email sospechoso de "tienes una notificación") y sociedad sucesora.

## 4. Trampas y problemas conocidos

- **Lo que solo hace la persona** (endpoints de comparecencia o con efectos):
  - `/api/v1/notifications/<ref>` y su `/metadata`;
  - `…/appearance-login-form/<ACCEPTING|REJECTING>` (reautenticación);
  - `POST …/voucher` (acuse);
  - `/api/v1/realized_notifications/<ref>/{full_detail,document,voucher,annexe…}`;
  - `…/change-level-clave-login-form`;
  - `PUT /api/v1/notification_center/…/mark-as-read`, que cambia el estado.
  - `sede.py` bloquea en `dehu.redsara.es` los clics de abrir, aceptar, rechazar o descargar, y las rutas de red con `/document`, `acuse` o `comparec`.
  - Ojo: `voucher`, `full_detail` y `appearance-login-form` **no** están en esa lista de red. La protección depende de no pulsar nada en "Acciones".
- **No llames a la API con `fetch`:**
  - Usa la SPA y lee la tabla. Hay un WAF F5 delante: las ráfagas dan "Request Rejected" o 403.
  - Si aparece, para y deja el control a la persona.
  - La SPA también avisa de un **máximo de operaciones diarias**.
- **Tokens:** `access_token` y `refresh_token` viven en `localStorage`. **Nunca** los leas, imprimas ni guardes.
- **Shadow DOM:** toda la interfaz son web components `dnt-*`. Usa selectores que atraviesen el shadow DOM, como `dnt-button.access-btn button`.
- **Una notificación puede estar en varios sitios:** la de la AEAT, por ejemplo, también se ve en la sede de la AEAT. No la abras en ninguno.
- **Grandes destinatarios (LEMA):** el servicio web oficial es para personas jurídicas con volumen y exige alta. **No es para la v0.1.**

## 5. Fuentes

- DEHú (portal público, `env.json` y FAQ) y Ley 39/2015 (art. 43: practicada al acceder; rechazada a los 10 días naturales sin acceso): ver la cabecera.
- Mapeo en vivo del 15-10-2026 (sin ninguna notificación abierta) e historial previo de uso de la API (WAF y ventanas de fechas).
