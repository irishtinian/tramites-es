---
verificado_el: 2026-10-15
estado_mapeo: parcial
municipios_ejemplo: [Madrid]
fuentes:
  - https://sede.madrid.es/portal/site/tramites                # catálogo de la sede
  - https://www.madrid.es/micarpeta                            # Mi Carpeta (redirige a servcla y al CAS)
  - https://servcla.madrid.es/CACIU_FTCARPETA/                 # aplicación de Mi Carpeta
  - https://agenciatributaria.madrid.es                        # Agencia Tributaria Madrid (ATM): fichas de tributos y certificados
---

# Sede propia del Ayuntamiento de Madrid

Riesgo: **Leer** (catálogo, Mi Carpeta) y **Preparar** (registro, actividad, certificados). Firmar, presentar, pagar y abrir notificaciones son **actos** (`firmar`, `presentar`, `pagar`, `comparecer`): los haces según los permisos que te dé tu usuario (`sede.py --permitir …`).

Estado **parcial**: el acceso público está mapeado hasta el selector de identidad; la firma no está confirmada.

## Qué es y dónde se usa

- Sede propia del Ayuntamiento de Madrid (fichas en Vignette). Solo sirve para Madrid capital: los demás municipios de la Comunidad usan otras plataformas (Gestiona, TAO/STA, Aytos…).
- Tributos: **Agencia Tributaria Madrid (ATM)**, organismo propio, con portal en `agenciatributaria.madrid.es`.

## Cómo adaptarla

```text
Sede / catálogo: https://sede.madrid.es/portal/site/tramites
Mi Carpeta:      https://www.madrid.es/micarpeta
Aplicación:      https://servcla.madrid.es/CACIU_FTCARPETA/
Identidad:       https://cas.madrid.es/authenticationendpoint/login.do?...   (parámetros efímeros)
```

- El dominio es fijo. Las fichas usan URLs con `vgnextoid` y `vgnextchannel`: son opacas y pueden cambiar.
- Parte siempre del catálogo y guarda solo el enlace canónico que muestre la propia ficha.
- No guardes la URL del CAS: sus parámetros caducan.

## Acceso

- `www.madrid.es/micarpeta` lleva a `servcla.madrid.es` y de ahí a `cas.madrid.es`.
- Pantalla **SISTEMA DE IDENTIFICACIÓN**:
  - **DNIe / Certificado:** enlace con `onclick` que llama a `handleNoDomain(..., 'IDPCLCTM', 'CLAVE')`. Es el que usa el agente.
  - **IDentifica:** credencial propia de Madrid (contraseña y código por SMS). Es de la persona: el agente no la usa, igual que Cl@ve PIN.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://cas.madrid.es` | `tls-probe`: sin mTLS. `cert-probe` directo: HTTP 403; navegando desde `servcla` sí carga el selector. |
| `https://servcla.madrid.es`, `https://sede.madrid.es` | `tls-probe`: sin mTLS. |

- El `onclick` del certificado lleva el literal `'CLAVE'`. No se pulsó, así que no se sabe si deriva a la pasarela Cl@ve. Si deriva, el certificado lo pide `https://pasarela-ident.clave.gob.es` y en la pasarela solo vale "DNIe / Certificado electrónico". **Pendiente de verificación con certificado.**

## Trámites típicos del autónomo

| Trámite | Entrada | Sin permiso, paras en | Actos (con permiso los haces tú) |
|---|---|---|---|
| Registro / instancia, actividad económica, declaración responsable y licencias urbanísticas | Catálogo `https://sede.madrid.es/portal/site/tramites` → materia | La ficha, con texto y adjuntos preparados | Identificarse, adjuntar, firmar y enviar: `firmar`, `presentar` |
| Certificado de estar al corriente de pago | Portal de la ATM → certificados y justificantes de pago | La ficha, con la solicitud preparada | Presentarla por registro electrónico con identificación y firma: `firmar`, `presentar` |
| Aplazamientos y fraccionamientos | Portal de la ATM | La ficha | Solicitar y firmar: `firmar`, `presentar` |
| Consulta de registros | Mi Carpeta | — (listar asientos es libre) | — |
| Notificaciones | Mi Carpeta | El listado | Abrir: `comparecer` |

- El certificado de la ATM **solo acredita que no hay deudas en vía de apremio**. Para concursos municipales no hace falta pedirlo: el Ayuntamiento lo comprueba de oficio.
- **IAE:** las personas físicas están exentas; las altas y bajas censales van a la AEAT (`sede-aeat.md`).
- Tasa de residuos: la ordenanza fiscal 8/2024 (TGR) se declaró nula. Comprueba su estado en la ATM antes de aconsejar.
- La ATM enlaza una oficina virtual de tributos en `sede2.madrid.es` y una carpeta tributaria en `servcla.madrid.es`. No se abrieron en el mapeo: **pendiente de verificación con certificado**.

## Firma

- **No confirmada:** depende del tramitador y del procedimiento; no se abrió ninguno.
- Firmar y enviar son los actos `firmar` y `presentar`. Con esos permisos, `sede.py` pasa `afirma://` a AutoFirma (`setup-autofirma.md`); sin ellos, captura `afirma://` y bloquea firmar y enviar.
- Éxito esperado: registro presentado en Mi Carpeta (consulta de registros), con número de asiento y justificante descargable. Verifica con `scripts/justificante.py` y en ese listado.

## Trampas

- **WAF Akamai:** `sede.madrid.es`, `www.madrid.es`, `sede2` y `servcla` devuelven 403 "Access Denied" a clientes que no son navegador (curl, WebFetch). Una sesión de navegador limpia sí cargó. Usa sede.py o el navegador de la persona, a ritmo humano, y **no insistas** ante un 403: no es una caída.
- No uses un GET directo a `cas.madrid.es` como prueba de vida: responde 403.
- El portal de la ATM (`agenciatributaria.madrid.es`) sí se lee sin navegador.
- No se observó CAPTCHA ni iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026. Datos de la ATM (certificado de apremio, IAE, TGR): fichas públicas de `agenciatributaria.madrid.es` revisadas el 14/15-oct-2026.
