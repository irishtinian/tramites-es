---
verificado_el: 2026-10-15
estado_mapeo: parcial
municipios_ejemplo: [València]
fuentes:
  - https://sede.valencia.es/sede/                                       # sede
  - https://sede.valencia.es/sede/registro/procedimiento/HA.GE.45        # ficha de ejemplo (domicilio tributario)
  - https://sede.valencia.es/sede/registro/procedimiento/HA.GT.30        # certificados de situación tributaria
  - https://sede.valencia.es/sede/registro/procedimiento/LA.AS.10        # comunicación de actividad inocua
  - https://sede.valencia.es/sede/carpeta/index.xhtml                    # Carpeta Ciudadana
  - https://sede.valencia.es/sede/authClave.xhtml/carpeta                # pantalla de identificación
---

# Sede propia del Ajuntament de València

Riesgo: **Leer** (catálogo, carpeta) y **Preparar** (comunicaciones, solicitudes, certificados). Firmar, presentar, pagar, domiciliar, cambiar datos y abrir notificaciones lo hace la persona.

Estado **parcial**: el acceso está mapeado hasta la elección de identidad; no se abrió ningún formulario y la firma no está confirmada.

## Qué es y dónde se usa

- Sede propia (aplicación JSF, `.xhtml`). Solo sirve para València ciudad.
- Tributos: propios ("Oficinas de Gestión Tributaria Integral"), dentro de la misma sede.
- Es la sede más cómoda para un agente: **cada procedimiento tiene un código estable**.

## Cómo adaptarla

```text
Sede:           https://sede.valencia.es/sede/
Procedimiento:  https://sede.valencia.es/sede/registro/procedimiento/{CODE}
Por materia:    https://sede.valencia.es/sede/registro/indexM.xhtml?m={MATERIA}&lang=1
Carpeta:        https://sede.valencia.es/sede/carpeta/index.xhtml
Identificación: https://sede.valencia.es/sede/authClave.xhtml/carpeta
```

- El dominio es fijo; cambia el código de procedimiento.
- La sede sale en valenciano por defecto. Añade `?lang=1` para castellano.
- Materias útiles: `HA` (Hacienda), `UA` (licencias urbanísticas y de actividad), `VP` (vía pública), `AE` (actividad económica, empleo y consumo).
- Guarda solo el código de procedimiento, nunca el estado de vista JSF.

## Acceso

- La carpeta redirige a `authClave.xhtml/carpeta`. Dos formularios:
  - `form#formCert`: **certificado directo** mediante submit JSF. Es el que usa el agente.
  - `form#formClave`: POST SAML a `https://pasarela.clave.gob.es/Proxy2/ServiceProvider`, con el botón `#clave-acceso`. En la pasarela, solo "DNIe / Certificado electrónico".
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://sede.valencia.es` | `tls-probe`/`cert-probe` en la raíz: sin mTLS. Dónde se pide tras `formCert`: **pendiente de verificación con certificado**. |
| `https://pasarela-ident.clave.gob.es` | Pide el certificado en la rama "DNIe / Certificado" de Cl@ve (`sede-clave.md`). |

## Trámites típicos del autónomo

| Trámite | Código | Dónde para el agente | Qué hace la persona |
|---|---|---|---|
| Comunicación de actividad inocua | `LA.AS.10` | En la ficha, con documentación preparada | Se identifica, adjunta, firma y envía |
| Declaración responsable de apertura sin obras | `LA.AS.60` | Ídem | Ídem |
| Declaración responsable de comercio minorista | `LA.AS.70` | Ídem | Ídem |
| Despacho profesional en vivienda | `LA.AS.80` | Ídem | Ídem |
| Terraza | `VP.OC.15` | Ídem | Ídem |
| Certificados de situación tributaria (estar al corriente) | `HA.GT.30` | Ídem | Lo solicita y firma |
| Fraccionamientos y aplazamientos | `HA.GT.10` | Ídem | Lo solicita y firma |
| Bonificación del IAE por inicio de actividad | `HA.AE.15` | Ídem | Ídem |
| Tasa de basura: domiciliación / no sujeción / bonificaciones | `HA.TA.20` / `HA.TA.25` / `HA.TA.15` | Explica y prepara | Domiciliar es cambiar datos bancarios: **solo la persona** |
| Domicilio tributario | `HA.GE.45` | Solo explica | Cambiar datos: **solo la persona** |
| Certificado de padrón | `PA.CE.10` | Ídem que los certificados | Lo solicita |
| Instancias, expedientes, cuenta tributaria, padrón, notificaciones | Carpeta | Lista. Notificaciones: **solo lista** | Abre la que quiera |

- La cuenta tributaria ("El meu compte tributari") está en `https://sede.valencia.es/sede/servicios/redirectExterno/3` y redirige a la identificación.
- **Tasa de basura:** la nueva tasa municipal se calcula por consumo de agua y es distinta de la TAMER de la EMTRE.
- **IAE:** las personas físicas están exentas; el alta censal va a la AEAT. `HA.AE.15` solo interesa a quien paga IAE.
- Los códigos `LA.*`, `VP.*`, `HA.GT.*`, `HA.TA.*` y `HA.AE.15` salen de fichas públicas revisadas el 14/15-oct-2026; `PA.CE.10`, `HA.GE.45` y `AD.IS.30` (sugerencias), del mapeo del 15-oct-2026. Abre la ficha antes de usarla.
- Contenido de la carpeta: **pendiente de verificación con certificado**.

## Firma

- **No confirmada:** no se abrió ningún formulario de trámite.
- La firma la hace la persona; sede.py captura `afirma://` y bloquea firmar y enviar.
- Éxito esperado: asiento y justificante; la instancia aparece en la carpeta. Verifica con `scripts/justificante.py` y en el listado.

## Trampas

- `www.valencia.es` devolvió 503 en un primer sondeo y 200 después: si falla, espera y reintenta una vez, no en bucle.
- Aplicación JSF: los botones hacen POST con estado de vista. No reconstruyas formularios a mano.
- No se observaron CAPTCHA, WAF ni iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026, sin elegir identidad.
