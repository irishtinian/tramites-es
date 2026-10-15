---
verificado_el: 2026-10-15
estado_mapeo: parcial
municipios_ejemplo: [Barcelona]
fuentes:
  - https://seuelectronica.ajuntament.barcelona.cat/ca                                   # sede
  - https://seuelectronica.ajuntament.barcelona.cat/oficinavirtual/ca                    # oficina virtual de trámites
  - https://seuelectronica.ajuntament.barcelona.cat/oficinavirtual/ca/all-search-result  # buscador
  - https://seuelectronica.ajuntament.barcelona.cat/oficinavirtual/ca/tramit/20140001157 # factura electrónica
  - https://seuelectronica.ajuntament.barcelona.cat/oficinavirtual/ca/tramit/20180001305 # notificación electrónica
  - https://seuelectronica.ajuntament.barcelona.cat/oficinavirtual/ca/tramit/20200001444 # certificat negatiu de deute
  - https://seuelectronica2.ajuntament.barcelona.cat/APPS/ptbportal/login.do?loginTarget=folder&style=ciudadano&language=ca   # espacio personal
  - https://ajuntament.barcelona.cat/hisenda/ca                                           # Institut Municipal d'Hisenda (IMH)
---

# Sede propia del Ajuntament de Barcelona

Riesgo: **Leer** (buscador, fichas, espacio personal) y **Preparar** (comunicados, solicitudes, certificados). Firmar, presentar, pagar y abrir notificaciones son **actos** (`firmar`, `presentar`, `pagar`, `comparecer`): los haces según los permisos que te dé tu usuario (`sede.py --permitir …`).

Estado **parcial**: el acceso público está mapeado hasta VÀLid; no se llegó a ningún tramitador y la firma no está confirmada.

## Qué es y dónde se usa

- Sede propia (Oficina Virtual, una SPA). Solo sirve para Barcelona ciudad.
- La identificación usa **VÀLid**, del Consorci AOC, como la plataforma AOC (`plataforma-aoc.md`).
- Tributos: **Institut Municipal d'Hisenda (IMH)**, organismo propio. Barcelona no delega en el ORGT.

## Cómo adaptarla

```text
Sede:                https://seuelectronica.ajuntament.barcelona.cat/ca
Oficina virtual:     https://seuelectronica.ajuntament.barcelona.cat/oficinavirtual/ca
Buscador:            .../oficinavirtual/ca/all-search-result
Categoría:           .../oficinavirtual/ca/search-result?idCategory={ID}
Ficha:               .../oficinavirtual/ca/tramit/{TRAMIT_ID}
Espacio personal:    https://seuelectronica2.ajuntament.barcelona.cat/APPS/ptbportal/login.do?loginTarget=folder&style=ciudadano&language=ca
Espacio profesional: https://seuelectronica2.ajuntament.barcelona.cat/APPS/ptbcarpetaprof/?set-locale=ca_ES
```

- El dominio es fijo. Cambian `idCategory` (la `101` agrupa actividades) y `TRAMIT_ID`.
- Los enlaces `.../tramit/{TRAMIT_ID}` son estables y se pueden dar directamente.

## Acceso

- El espacio personal redirige a VÀLid (`valid.aoc.cat`).
- Selectores: `button#btnContinuaCert` (certificado/DNIe, el que usa el agente) y `button#btnContinuaClave` (Cl@ve; en la pasarela solo "DNIe / Certificado").
- idCAT Mòbil (código por SMS) es de la persona: el agente no lo usa.
- El espacio personal del IMH pide certificado digital.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://valid.aoc.cat` | `tls-probe`/`cert-probe`: sin mTLS en el handshake; aloja el botón de certificado. |
| `https://seuelectronica.ajuntament.barcelona.cat`, `https://seuelectronica2.ajuntament.barcelona.cat` | Sin mTLS. |

- Dónde se pide realmente el certificado: **pendiente de verificación con certificado**.

## Trámites típicos del autónomo

| Trámite | `TRAMIT_ID` | Sin permiso, paras en | Actos (con permiso los haces tú) |
|---|---|---|---|
| Comunicat d'activitat (tramitación de expedientes de actividades) | `20220001567` | La ficha, con documentación preparada | Identificarse, adjuntar, firmar y enviar: `firmar`, `presentar` |
| Llicència municipal d'activitats | `20220001573` | Ídem | Ídem |
| Llicència de terrassa (solicitud y modificación) | `20150001188` | Ídem | Ídem |
| Alta en el preu públic de residus comercials | `20100000131` | La ficha, con el orden explicado | Autoliquidar y **pagar** antes de comunicar la actividad: `presentar`, `pagar` |
| Certificat negatiu de deute | `20200001444` | Ídem | Solicitar y firmar: `generar`, `firmar` |
| Fraccionament de pagament | `20250001752` | Ídem | Solicitar y firmar: `presentar`, `firmar` |
| Factura electrònica | `20140001157` | Ídem | Presentarla: `presentar` |
| Notificació electrònica | `20180001305` | El listado del espacio personal | Abrir: `comparecer` |

- Orden para abrir un negocio, según la sede: alta en residus comercials (autoliquidación pagada) → comunicat d'activitat → terrassa, si aplica.
- **IAE:** las personas físicas están exentas; el alta censal va a la AEAT (`sede-aeat.md`).
- Los IDs de esta tabla salen de fichas públicas revisadas el 14/15-oct-2026. Ábrelas antes de usarlas: la ficha manda.
- Contenido del espacio personal y del tramitador: **pendiente de verificación con certificado**.

## Firma

- **Pendiente de confirmar** por trámite. VÀLid admite firma no criptográfica tras identificarse y firma con certificado, pero no se llegó al tramitador.
- Firmar, enviar y pagar son los actos `firmar`, `presentar` y `pagar`. Con esos permisos, `sede.py` pasa `afirma://` a AutoFirma (`setup-autofirma.md`); sin ellos, captura `afirma://` y bloquea firmar, enviar y pagar.
- Éxito esperado: solicitud y estado en **El meu espai** o en la carpeta profesional, con asiento y justificante. Verifica con `scripts/justificante.py` y en ese listado.

## Trampas

- **reCAPTCHA invisible** cargado en la sede. No apareció reto en el mapeo. Si aparece, lo resuelve la persona.
- La Oficina Virtual es una SPA: con curl o WebFetch se ve vacía. Hace falta navegador.
- Hay un script de cookie de F5: ritmo humano, sin reintentos en bucle.
- No se observaron iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026. IDs de actividades, terrazas, residuos, certificado y fraccionamiento: fichas públicas de la Oficina Virtual revisadas el 14/15-oct-2026.
