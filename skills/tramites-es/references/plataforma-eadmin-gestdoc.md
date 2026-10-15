---
verificado_el: 2026-10-15
estado_mapeo: verificado_sin_certificado
municipios_ejemplo: [León, Benidorm]
fuentes:
  - https://sede.aytoleon.es/eAdmin/Sede.do                                   # portada (León)
  - https://sede.aytoleon.es/eAdmin/Login.do?action=login                      # acceso (León)
  - https://sede.aytoleon.es/eAdmin/Registrar.do?action=inicioPortalTramites   # catálogo (León)
  - https://sede.benidorm.org/eAdmin/Sede.do                                  # portada (Benidorm)
  - https://aytoleon.tributoslocales.es/240898/ALEON                           # oficina virtual tributaria de León (GTT)
---

# Plataforma eAdmin / GestDoc (Struts `.do`)

Riesgo: **Leer** (carpeta, listados) y **Preparar** (solicitud general, actividad). Firmar, presentar, pagar y abrir notificaciones lo hace la persona.

## Qué es y dónde se usa

- Sede en Java/Struts con rutas `/eAdmin/*.do` y, en algunas instalaciones, `/GDCarpetaCiudadano/*.do` (GestDoc). Proveedor sin identificar.
- Dónde: **León**, Toledo, Cuenca, Ávila, Huesca, **Benidorm**, Úbeda, Martos, Colmenar Viejo, Galapagar, Algemesí, Pájara, Tuineje y el Cabildo de Fuerteventura.
- Cobertura estimada: ~20–30 entidades.

## Cómo adaptarla a tu ayuntamiento

```text
HOST    = dominio de la sede
TIPOREG = código local del procedimiento

Portada:       https://{HOST}/eAdmin/Sede.do
Login:         https://{HOST}/eAdmin/Login.do?action=login
Catálogo:      https://{HOST}/eAdmin/Registrar.do?action=inicioPortalTramites
Procedimiento: https://{HOST}/eAdmin/Registrar.do?action=comenzar&tipoReg={TIPOREG}
Mis datos:     https://{HOST}/eAdmin/DatosPersona.do?action=datosPersona
```

- Cambian el host y `tipoReg`.
- León: solicitud general `tipoReg=2`, transparencia `18`, quejas y sugerencias `3`. **No reutilices estos códigos** sin mirarlos en el catálogo del municipio (Benidorm tiene los suyos).

## Acceso

- `/eAdmin/Login.do?action=login` ofrece Cl@ve mediante `form[name=claveForm]`, que envía un POST SAML a `https://pasarela.clave.gob.es/Proxy2/ServiceProvider`.
- En la pasarela, el agente solo usa **"Acceso DNIe / Certificado electrónico"** (`button.idp-button` con `selectedIdP('AFIRMA')`).
- La propia página avisa: si el procedimiento requiere firma, hace falta AutoFirma y certificado.
- Algunas sedes tienen un **PIN municipal** (PIN24). Es una credencial de la persona: el agente no lo usa.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://sede.aytoleon.es`, `https://sede.benidorm.org` | `tls-probe`/`cert-probe`: sin mTLS. |
| `https://pasarela-ident.clave.gob.es` | Es quien pide el certificado en la rama "DNIe / Certificado" de Cl@ve (`sede-clave.md`). |

- Retorno de Cl@ve a la carpeta: **pendiente de verificación con certificado**.

## Trámites típicos del autónomo

| Trámite | Entrada | Dónde para el agente | Qué hace la persona |
|---|---|---|---|
| Solicitud general | `Registrar.do?action=comenzar&tipoReg={TIPOREG}` | **No la abre** (ver Trampas). Prepara texto y adjuntos y le da el enlace | Abre el enlace, se identifica, adjunta, firma y envía |
| Actividad, licencias | Catálogo `Registrar.do?action=inicioPortalTramites` | Igual: le da el enlace y la documentación preparada | Igual |
| Expedientes, registros, certificados | Carpeta autenticada | Lista | — |
| Notificaciones | Carpeta autenticada | **Solo lista** | Abre la que quiera |
| Mis datos | `DatosPersona.do?action=datosPersona` | Solo lee | Cambia datos ella, si quiere |
| Tasas, recibos, certificado tributario | Oficina tributaria (León: `https://aytoleon.tributoslocales.es/240898/ALEON`, GTT) | `plataforma-gtt.md` | Paga o pide el certificado |

- La oficina tributaria de León (GTT) admite certificado, DNIe, Cl@ve y DNI/NIF, y ofrece fraccionamiento y "Obtener certificado".
- Benidorm enlaza pagos a una entidad bancaria: pagar es de la persona.
- Contenido de la carpeta autenticada: **pendiente de verificación con certificado**.

## Firma

- **AutoFirma**, confirmado por el aviso público de la página de acceso. No se ejecutó.
- La firma la hace la persona; sede.py captura `afirma://`.
- Éxito esperado: entrada en la carpeta (expedientes, registros, notificaciones, certificados). Los justificantes se validan por CSV. Verifica con `scripts/justificante.py` y en el listado.

## Trampas

- **sede.py bloquea `Registrar.do`.** La guarda de red trata como acción toda URL que contiene "registrar", incluso el catálogo (`action=inicioPortalTramites`). No la esquives: el agente prepara y da el enlace, y la persona lo abre. Si el mantenedor afina la guarda, esta guía cambiará.
- `DatosPersona.do` muestra datos personales: no los copies al chat ni a notas, y no cambies nada.
- No se observaron CAPTCHA, WAF ni iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en León y Benidorm. No se envió el formulario Cl@ve.
