---
verificado_el: 2026-10-15
fuentes:
  - https://dehu.redsara.es/es/public
  - https://dehu.redsara.es/es/config/env.json          # catálogo público de la API de la SPA
  - https://dehu.redsara.es/api/v1/faq                  # FAQ oficial (JSON)
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565   # Ley 39/2015, arts. 41 y 43
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3). Validación v02 (15-10-2026, tarde): login con certificado de persona física OK (sin error=1000) y pestaña de pendientes leída (0 pendientes, 0 realizadas). El error=1000 de la mañana no se reprodujo: tratarlo como intermitente."
---

# DEHú: Dirección Electrónica Habilitada única

## 1. Para qué sirve

DEHú es el buzón común de notificaciones de la Administración del Estado y de muchos otros organismos. La Seguridad Social, por ejemplo, también notifica aquí.

Listar (organismo, concepto, fecha de puesta a disposición y fecha de caducidad) no tiene efectos.

**Abrir, aceptar, rechazar o descargar una notificación es comparecer** (acto `comparecer`): la persona queda notificada y empiezan a correr los plazos. Con ese permiso de tu usuario puedes hacerlo (`sede.py --permitir comparecer`); sin él, lista y dile qué tiene pendiente. Procedimiento y cálculo de plazos: `tramite-vigilar-notificaciones.md`.

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

### Fallo intermitente: login rechazado (`error=1000`)

- **Validación v02 (15-10-2026, ~16:30):** el mismo certificado entró sin error: `ResponseRedirect → /es/login?authData=… → /es/home → /es/home-view` ("DEHú - Inicio"). Si te sale `error=1000`, reintenta **una** vez más tarde antes de dar DEHú por caído.

- **Revalidado** el 15-10-2026 en la validación de la v0.1 (1 intento útil): misma cadena `ServiceRedirect → AuthenticateCitizen → ResponseRedirect → /es/login?error=1000 → /es/public`.
- **Cómo verlo:** la SPA borra el `error=` en menos de un segundo; `pg.url` acaba en `/es/public`. Registra las navegaciones antes de pulsar el botón de Cl@ve:
  ```python
  vistos = []
  # Solo ruta y error=: la URL de vuelta lleva ?authData=<JWT de sesión con el NIF>; nunca la registres entera.
  pg.on("framenavigated", lambda f: vistos.append(f.url.split("?")[0] + (" error=" + f.url.split("error=")[1][:6] if "error=" in f.url else ""))
        if f == pg.main_frame else None)
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

### 3.1 Listado de notificaciones (`dehu-notificaciones`) · Leer · verificado (15-10-2026, pestaña de pendientes)

Verificado en la validación v02 con certificado de persona física: la pestaña de pendientes carga y muestra los dos contadores ("Notificaciones pendientes `<N>`", "Notificaciones realizadas `<N>`"). Con 0 filas no se ha visto la tabla con datos: las columnas de abajo salen del bundle de la SPA.

**Receta** (`dehu_listado.py`; la interfaz son web components, así que `inner_text("body")` no ve el texto del shadow DOM):

```python
pg.wait_for_selector("button.idp-button", timeout=60000)
pg.click("button.idp-button:has-text('DNIe / Certificado')")
pg.wait_for_url(lambda u: "clave.gob.es" not in u, timeout=90000)
pg.wait_for_timeout(6000)
TXT = """() => { const out = []; const walk = (n) => { if (!n) return;
  if (n.nodeType === 3) { const t = n.textContent.trim(); if (t) out.push(t); return; }
  if (n.nodeType !== 1 && n.nodeType !== 11) return;
  if (n.tagName === 'SCRIPT' || n.tagName === 'STYLE') return;
  if (n.shadowRoot) walk(n.shadowRoot); for (const c of n.childNodes) walk(c); };
  walk(document.body); return out.join(' '); }"""
nav("https://dehu.redsara.es/es/notifications", espera=12000)
captura("dehu-pendientes")
RESULTADO = {"url": pg.url.split("?")[0], "texto": redactar(" ".join(pg.evaluate(TXT).split()))[:3000]}
```

```bash
xvfb-run -a uv run scripts/sede.py ejecutar dehu_listado.py --sede dehu --titular yo --json /tmp/dehu.json
```

- **Una sola carga completa por sesión.** En la validación, la tercera `nav()` seguida dentro de DEHú devolvió la página "Playwright client-certificate error: read ECONNRESET" (en `dehu.redsara.es`, que no recibe certificado: lo más probable es el WAF). Para ver otra pestaña, usa el menú de la SPA o lanza otra ejecución más tarde.

| | Pendientes | Realizadas |
|---|---|---|
| Ruta SPA (pestaña) | `https://dehu.redsara.es/es/notifications` | `https://dehu.redsara.es/es/notifications?realized=true` |
| API que usa la SPA | `GET /api/v1/notifications?…&page=<n>&limit=10` | `GET /api/v1/realized_notifications?…&page=<n>&limit=10` |
| Columnas | Identificador, Concepto, Organismo emisor, Organismo raíz, Titular, Vínculo, Fecha disposición, **Fecha caducidad**, Acciones | Las mismas, más **Fecha comparecencia / estado final** y **Estado** (Aceptada, Rechazada, Expirada, Expirada TEU) |

- **Otras pestañas:** comunicaciones (`/es/communications`, con doble "m": `/es/comunications` redirige a la portada) y anuncios del Tablón Edictal Único (`/es/notifications-edictals`).
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
- **Sin el permiso `comparecer`:** el agente para en la tabla, sin pulsar nada en la columna "Acciones" ni en el identificador. Para leer una notificación entra la persona en DEHú, pestaña "Pendientes", y en "Acciones" elige aceptar o rechazar.
- **Con el permiso `comparecer`:** confirma con tu usuario qué notificación abrir (aceptar no es lo mismo que rechazar) y avísale de que desde ese momento corren los plazos. DEHú pide reautenticarse por Cl@ve para firmar la comparecencia (`appearance-login-form`): usa la rama de certificado. Abrir de punta a punta con el agente: **pendiente de verificar en vivo**.
- **Éxito:** tabla con filas, o vacía, en la pestaña pedida.
- **Pendiente frente a realizada:**
  - Pendiente = no comparecida, con "Fecha caducidad".
  - Realizada = aceptada, rechazada o expirada. Si está "Expirada", **ya se tiene por notificada**: es urgente decírselo a la persona.

### 3.2 Servicios públicos (`dehu-publico`) · Leer · verificado sin certificado

`https://dehu.redsara.es/es/public` ofrece tres servicios: buscador de organismos, **validador de autenticidad de correos** (útil ante un email sospechoso de "tienes una notificación") y sociedad sucesora.

## 4. Trampas y problemas conocidos

- **Endpoints de comparecencia o con efectos** (acto `comparecer`):
  - `/api/v1/notifications/<ref>` y su `/metadata`;
  - `…/appearance-login-form/<ACCEPTING|REJECTING>` (reautenticación);
  - `POST …/voucher` (acuse);
  - `/api/v1/realized_notifications/<ref>/{full_detail,document,voucher,annexe…}`;
  - `…/change-level-clave-login-form`;
  - `PUT /api/v1/notification_center/…/mark-as-read`, que cambia el estado.
  - Sin el permiso `comparecer`, `sede.py` bloquea en `dehu.redsara.es` los clics de abrir, aceptar, rechazar o descargar, y las rutas de red con `/document`, `acuse`, `comparec`, `voucher`, `full_detail` y `appearance` (`NOTIF_RED`). Si listas sin ese permiso, no pulses nada en "Acciones".
- **No llames a la API con `fetch`:**
  - Usa la SPA y lee la tabla. Hay un WAF F5 delante: las ráfagas dan "Request Rejected" o 403.
  - Si aparece, para y deja el control a la persona.
  - La SPA también avisa de un **máximo de operaciones diarias**.
- **Tokens:** `access_token` y `refresh_token` viven en `localStorage`. **Nunca** los leas, imprimas ni guardes.
- **Shadow DOM:** toda la interfaz son web components `dnt-*`. Usa selectores que atraviesen el shadow DOM, como `dnt-button.access-btn button`.
- **Una notificación puede estar en varios sitios:** la de la AEAT, por ejemplo, también se ve en la sede de la AEAT. Abrirla en cualquiera de ellos es comparecer.
- **Grandes destinatarios (LEMA):** el servicio web oficial es para personas jurídicas con volumen y exige alta. **No es para la v0.1.**

## 5. Fuentes

- DEHú (portal público, `env.json` y FAQ) y Ley 39/2015 (art. 43: practicada al acceder; rechazada a los 10 días naturales sin acceso): ver la cabecera.
- Mapeo en vivo del 15-10-2026 (sin ninguna notificación abierta) e historial previo de uso de la API (WAF y ventanas de fechas).
