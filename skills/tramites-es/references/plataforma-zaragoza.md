---
verificado_el: 2026-10-15
estado_mapeo: parcial
municipios_ejemplo: [Zaragoza]
fuentes:
  - https://www.zaragoza.es/sede/                                   # sede
  - https://www.zaragoza.es/sede/portal/tramites-servicios/         # catálogo
  - https://www.zaragoza.es/sede/servicio/tramite/11901             # Registro General (ficha)
  - https://www.zaragoza.es/sede/servicio/tramite/148               # comunicación previa de apertura
  - https://www.zaragoza.es/sede/servicio/tramite/27120             # certificado de estar al corriente
  - https://tributos.zaragoza.es/info.0                             # oficina virtual tributaria
---

# Sede propia del Ayuntamiento de Zaragoza

Riesgo: **Leer** (catálogo, fichas) y **Preparar** (registro, actividad, certificados). Firmar, presentar, pagar y abrir notificaciones lo hace la persona.

Estado **parcial**: la entrada del registro (`/procedimiento/11901`) agotó el tiempo y no se vio el selector final; la firma no está confirmada.

## Qué es y dónde se usa

- Sede propia en `www.zaragoza.es/sede/`. Solo sirve para Zaragoza ciudad.
- Tributos: propios (Área de Hacienda). La oficina virtual tributaria está en `tributos.zaragoza.es` y tiene huella de Gestiona (`/info.0`).

## Cómo adaptarla

```text
Sede:       https://www.zaragoza.es/sede/
Catálogo:   https://www.zaragoza.es/sede/portal/tramites-servicios/
Búsqueda:   https://www.zaragoza.es/sede/servicio/tramite/
Ficha:      https://www.zaragoza.es/sede/servicio/tramite/{ID}
Categoría:  https://www.zaragoza.es/sede/servicio/tramite/tipo/{ID}
Ejecución:  https://www.zaragoza.es/procedimiento/{ID}
OVT:        https://tributos.zaragoza.es/info.0
```

- El dominio es fijo; cambia el ID del trámite. La ficha está en `/sede/servicio/tramite/{ID}` y el inicio electrónico en `/procedimiento/{ID}`.
- Categorías útiles: tributos `143`, urbanismo `144`.
- El catálogo se publica también en JSON, XML y CSV.

## Acceso

- La ficha del Registro General (`11901`) muestra **"Iniciar trámite con certificado o Cl@ve"**, que lleva a `/procedimiento/11901`.
- Esa ejecución **agotó 60 segundos sin cargar** en el mapeo y no se insistió. El acceso público está confirmado; **el selector final está pendiente de verificación con certificado**.
- Si la identificación pasa por Cl@ve, en la pasarela solo vale "DNIe / Certificado electrónico". La sede admite firmar con Cl@ve Permanente: eso es de la persona.
- La **Zona personal** de `/sede/acceso` usa una cuenta local (correo y contraseña). No es la identificación del registro electrónico y el agente no la usa.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://www.zaragoza.es` | `tls-probe`/`cert-probe`: sin mTLS. Dónde se pide el certificado: **pendiente**. |
| `https://pasarela-ident.clave.gob.es` | Pide el certificado en la rama "DNIe / Certificado" de Cl@ve (`sede-clave.md`). |

## Trámites típicos del autónomo

| Trámite | ID de ficha | Dónde para el agente | Qué hace la persona |
|---|---|---|---|
| Registro General (instancia) | `11901` | En la ficha, con texto y adjuntos preparados | "Iniciar trámite", se identifica, adjunta, firma y envía |
| Comunicación previa de apertura | `148` | Ídem | Ídem |
| Inicio de actividad | `13038` | Ídem | Ídem |
| Autoliquidación de la tasa de licencia de actividad | `13401` | Explica el importe y el modelo | Autoliquida y **paga** |
| Veladores y sombrillas | `196` | Ídem que la instancia | Ídem |
| Basura: incorporación / baja | `215` / `23401` | Ídem | Ídem |
| Certificado de estar al corriente | `27120` (o la OVT) | Ídem | Lo solicita y firma |
| Ayuda al autónomo | `41838` | Lee requisitos y plazos | La solicita (`ayudas.md`) |
| Actividad ocasional en vía pública | `29120` | Ídem que la instancia | Ídem |
| Autoliquidación del IAE, aplazamientos, certificado tributario | OVT `https://tributos.zaragoza.es/info.0` | Consulta | Paga, aplaza o firma |

- Las personas jurídicas solo pueden hacer los trámites de actividad por vía electrónica.
- **OVT tributaria:** solo ofrece Cl@ve como entrada (el certificado, por la rama "DNIe / Certificado"). Con sesión: **pendiente de verificación con certificado**.
- Los IDs `148`, `13038`, `13401`, `196`, `215`, `23401` y `27120` salen de fichas públicas revisadas el 14/15-oct-2026; `11901`, `41838`, `29120`, `143` y `144`, del mapeo del 15-oct-2026. Abre la ficha antes de usarla.

## Firma

- **Pendiente.** La sede publica una ayuda del componente de firma y un verificador de documentos, pero el mecanismo concreto no se vio.
- La firma la hace la persona; sede.py captura `afirma://` y bloquea firmar, enviar y pagar.
- Éxito esperado: asiento y justificante del registro, y consulta posterior en la carpeta enlazada por la sede. Verifica con `scripts/justificante.py` y con el verificador de documentos.

## Trampas

- **Ejecución lenta:** `/procedimiento/11901` agotó 60 s. Es un quirk observado, no un WAF confirmado. Espera; no reintentes en bucle.
- **Bucle de redirecciones en la OVT** sin cookies: usa navegador real.
- No confundas la Zona personal (cuenta local) con el acceso con certificado.
- No se observó CAPTCHA ni iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026. IDs de actividad, veladores, basura y certificado: fichas públicas revisadas el 14/15-oct-2026.
