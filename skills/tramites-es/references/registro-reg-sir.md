---
verificado_el: 2026-10-15
estado_mapeo: verificado_sin_certificado
municipios_ejemplo: []
fuentes:
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565                          # Ley 39/2015: art. 16.4 (dónde presentar) y art. 66.6 (modelos específicos)
  - https://sede.administracion.gob.es/servicios-electronicos/registro-electronico-general-age   # ficha oficial del REG
  - https://reg.redsara.es/es/                                                      # aplicación REG
  - https://reg.redsara.es/es/login                                                 # "Nuevo registro" → acceso
  - https://reg.redsara.es/es/media/es/REG-ManualUsuario.pdf                        # manual de usuario oficial
---

# REG + SIR: instancia general a cualquier administración

Riesgo: **Preparar.** El agente prepara el texto y los adjuntos. La persona se identifica, adjunta, firma y envía.

## Qué es y cuándo usarlo

- El **Registro Electrónico General de la AGE (REG)** permite presentar un escrito genérico dirigido a órganos de **cualquier administración pública integrada en el Sistema de Interconexión de Registros (SIR)**: ayuntamientos, diputaciones, comunidades autónomas, organismos estatales.
- Base legal: art. 16.4.a de la Ley 39/2015. Se puede presentar en el registro electrónico de la administración a la que te diriges **o en el de cualquier otra** del art. 2.1, y los registros deben ser interoperables.
- **Úsalo cuando:**
  - `buscar.py` no encuentra receta para la plataforma del ayuntamiento;
  - la sede municipal está caída, bloqueada o no admite certificado;
  - hace falta un escrito libre: alegación, solicitud, aportar documentos a un expediente, una queja.
- **No lo uses cuando:**
  - el procedimiento tiene un **modelo específico obligatorio** (art. 66.6 de la Ley 39/2015). Por ejemplo, autoliquidaciones, modelos tributarios o un formulario de declaración responsable que el ayuntamiento exige. En ese caso, la sede del organismo;
  - hay que **pagar** una tasa o un recibo: eso va por la sede o el recaudador del organismo;
  - la persona quiere seguir el expediente en la carpeta municipal: entrar por la sede del ayuntamiento lo deja todo en un sitio.

## Flujo (público hasta la identificación)

1. Abrir `https://reg.redsara.es/es/` → **Nuevo registro**, que lleva a `https://reg.redsara.es/es/login`.
2. **Accede con tu Cl@ve** → pasarela `https://pasarela.clave.gob.es/Proxy2/ServiceProvider`.
3. En la pasarela, solo **"Acceso DNIe / Certificado electrónico"** (`button.idp-button` con `onclick=selectedIdP('AFIRMA'); idpRedirect.submit()`). Cl@ve PIN, Móvil y Permanente son de la persona.
4. El certificado lo pide `https://pasarela-ident.clave.gob.es/IdP2/AuthenticateCitizen`, y la sesión vuelve al formulario de REG.
5. Formulario: interesado o representante, **organismo destinatario**, asunto, exposición y solicitud, anexos.
6. Firma y envío → **recibo**.

- Los pasos 4 a 6 no se ejecutaron: los campos exactos del formulario autenticado están **pendientes de verificación con certificado**.
- La entrada antigua `/registro/action/are/acceso.do` ya no vale: acaba en "página no encontrada".

Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://reg.redsara.es` | `tls-probe` y `cert-probe`: sin mTLS. |
| `https://pasarela.clave.gob.es` | No pide certificado (`sede-clave.md`). |
| `https://pasarela-ident.clave.gob.es` | **Pide el certificado** por ruta o renegociación, no en el handshake inicial. Si falta en los origins, Cl@ve da el error 4002. |

## Cómo elegir el destino

- El campo **"Código y nombre del organismo o entidad"** autocompleta a partir de **3 caracteres**: nombre del ayuntamiento u órgano, o su **código DIR3**.
- El **Asistente de búsqueda** filtra por nombre o código. Hay que **seleccionar un resultado de la lista**: dejar el texto escrito no basta.
- DIR3 de un ayuntamiento: en los casos comprobados sigue el patrón `L01` + código INE de 5 dígitos + dígito de control (Ayuntamiento de Madrid: `L01280796`). Es una pista: confírmalo siempre en el asistente.
- Un ayuntamiento puede tener varias unidades (registro general, áreas, organismos autónomos). Si la persona no sabe cuál, el ayuntamiento como tal es la opción prudente.
- Antes de presentar, comprueba con la persona:
  - que el nombre y el DIR3 son del ayuntamiento u órgano correcto, y no de un homónimo de otra provincia;
  - que el destinatario aparece en el buscador. Si no aparece, no lo fuerces: usa la sede del ayuntamiento;
  - que el trámite no exige un formulario municipal específico.

## Qué prepara el agente

1. **Destino:** nombre exacto y DIR3 candidato, con la razón de la elección.
2. **Asunto:** una línea concreta. Por ejemplo, "Solicitud de copia del expediente <Nº EXPEDIENTE>" o "Aportación de documentación al expediente <Nº>".
3. **Expone:** hechos, en párrafos cortos y numerados, con las referencias que la persona aporte: expediente, fechas, recibos. Sin opiniones ni datos que no hagan falta.
4. **Solicita:** qué se pide, en una o dos frases.
5. **Adjuntos:** solo lo que el trámite pida, con nombre claro (`01-solicitud.pdf`, `02-plano-local.pdf`), en PDF si es posible y dentro de los límites.
6. **Borrador local** para que la persona lo revise antes de entrar. Usa marcadores (`<NIF>`, `<TITULAR>`) en todo lo que compartas.

Límites del manual oficial: hasta **5 documentos**, **10 MB por fichero** y **15 MB en total**. Revalídalos si la aplicación cambia.

Si la persona lo pide y la sesión es la de sede.py con su certificado, el agente puede escribir los textos en los campos. **Adjuntar ficheros, firmar y enviar no**: sede.py no permite subir archivos desde una receta y bloquea firmar y enviar.

## Qué hace la persona

1. Se identifica: Cl@ve → "DNIe / Certificado electrónico", con su certificado.
2. Revisa el destino, el asunto, el expone y el solicita.
3. Adjunta los ficheros.
4. Firma y envía.
5. Descarga el recibo y lo guarda.

Las alertas por correo o SMS son opcionales: no las actives sin que la persona lo pida.

## El recibo y sus límites

- Según el manual oficial, el éxito es un **recibo firmado electrónicamente** con:
  - número de registro individualizado;
  - fecha y hora de presentación;
  - copia de la solicitud;
  - relación o nombre de los anexos.
- El escrito viaja al organismo destinatario por SIR.
- Verifica el recibo con `scripts/justificante.py` (número de registro y fecha). La pantalla de "correcto" no basta.
- **Lo que el recibo NO prueba:**
  - que el destino haya tramitado el escrito ni que lo haya asignado a un expediente;
  - que el procedimiento admitiera un escrito genérico: si exigía un modelo específico, el ayuntamiento puede requerir subsanación;
  - que el asiento aparezca en la carpeta de la sede municipal. La consulta de registros presentados dentro de REG está **pendiente de verificación con certificado**.
- Antes de repetir una presentación que falló al final, busca el recibo o el asiento para no duplicarla.

## Firma

- La firma final no se ejecutó en el mapeo. Fuentes secundarias indican **AutoFirma o Cl@ve Firma**: **pendiente de verificación con certificado**.
- Cualquier firma la hace la persona; sede.py captura `afirma://`.

## Trampas

- No se observaron CAPTCHA, WAF ni iframes.
- Un GET directo a `Proxy2/ServiceProvider` da error porque falta el POST SAML: no es una caída.
- Cl@ve identifica a personas físicas. Si el escrito es de una sociedad, que REG acepte el certificado de representante está **pendiente de verificación con certificado**; mientras tanto, usa la sede del destino.

## Fuentes

Ver cabecera. Flujo público mapeado sin certificado el 15-oct-2026: `/es/` → `/es/login` → pasarela Cl@ve, sin seleccionar identidad. Elección de destino, límites de anexos y forma del recibo: manual de usuario oficial.
