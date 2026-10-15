---
verificado_el: 2026-10-15
fuentes:
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar                       # ventana de 60 días y casos que obligan a acreditarse en persona
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar/configuracion-previa  # Configurador FNMT 5.1.2; mismo equipo y usuario
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar/descargar-certificado # mismo ordenador y usuario que la solicitud
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica                               # el de persona física es gratuito
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/lista-de-precios              # vídeo-identificación 2,99 € + impuestos
  - https://www.sede.fnmt.gob.es/certificados/certificado-de-representante/administrador-unico-solidario                    # 24 € + impuestos, 2 años, quién puede pedirlo
  - https://www.sede.fnmt.gob.es/certificados/certificado-de-representante/administrador-unico-solidario/renovar-certificado # "no se puede renovar online" (ver §1)
  - https://www.sede.fnmt.gob.es/certificados/certificado-de-representante/administrador-unico-solidario/renovar-certificado-ant # pasos de renovación online
  - https://www.sede.fnmt.gob.es/certificados/certificado-de-representante/administrador-unico-solidario/solicitar-certificado
  - https://www.sede.fnmt.gob.es/certificados/certificado-de-representante/persona-juridica  # 14 € + impuestos; acreditación
estado_mapeo: "Renovación del certificado de representante de administrador único recorrida de punta a punta el 15-10-2026 (solicitud, pago y descarga), con el agente guiando en el escritorio real y la persona tecleando contraseña y tarjeta. Persona física: pasos y requisitos de la sede, sin recorrer."
---

# Renovar el certificado digital de la FNMT

**Actos:** solicitar la renovación y descargar el certificado nuevo = `generar`. En el de representante, pagar = `pagar`. No pasa por AutoFirma: la FNMT usa su propio programa, el **Configurador FNMT**.

**Tu usuario decide hasta dónde llegas.** Dos modos:
- **Completo** (permisos `generar` y, si es de representante, `pagar`): haces tú los pasos de la web y del Configurador. La persona solo teclea lo que es suyo (§4).
- **Acompañado** (sin esos permisos, o si lo prefiere): compruebas si se puede renovar, le das los enlaces y le dices qué pulsar en cada pantalla.

Pregúntale qué modo quiere antes de empezar.

## 1. ¿Se puede renovar por internet?

Mira el certificado con `uv run scripts/cert.py listar`: tipo, `caduca` y `dias_restantes`. Si quedan 60 días o menos, el `aviso` lo dice.

| Certificado | ¿Renovar online? | Si no se puede |
|---|---|---|
| **Persona física** | Sí, en los **60 días previos** a la caducidad, si no está revocado. **No** si se obtuvo identificándose con otro certificado, con DNIe o por vídeo-identificación, ni si ya se renovó antes | Pedir uno nuevo: vídeo-identificación (2,99 € + impuestos), oficina de acreditación (con cita: `tramite-cita-previa.md`) o DNIe. El certificado en sí es gratuito |
| **Representante de administrador único o solidario** | **La sede se contradice** (15-10-2026): su página de renovación dice "no se puede renovar online", pero los pasos de renovación siguen publicados y **funcionaron** ese día de punta a punta. Mismas condiciones: 60 días, se pide con el certificado de **persona física** FNMT (no con el de la empresa) | **Pedir uno nuevo online** con el certificado de persona física o el DNIe (`…/administrador-unico-solidario/solicitar-certificado`). Mismo precio y validez |
| **Representante de persona jurídica** (apoderado, consejero, administrador mancomunado…) | No hay renovación | Pedir uno nuevo (14 € + impuestos). Acreditación online solo para entidades con NIF A, B, C o D; el resto, en una oficina |

- **Representante:** 24 € + impuestos (administrador único) con tarjeta de crédito o débito, validez de 2 años. Pregunta a tu usuario si es administrador **único o solidario** (consta en el Registro Mercantil). Si no lo sabe, la sede lo dice al intentarlo: con otro cargo no le deja.
- **Antes de la ventana de 60 días** no hay renovación. Apunta la fecha en que se abre y avísale entonces.

## 2. Antes de empezar

- **Mismo equipo y mismo usuario del sistema** para solicitar y descargar, y no formatear entre medias (lo exige la FNMT). Por eso esto se hace en el ordenador de tu usuario, en **su escritorio y su navegador normal**, con el certificado de persona física instalado en ese navegador.
  - El navegador de `sede.py` en Linux usa un almacén de certificados aislado y temporal: el certificado nuevo no quedaría instalado en ningún sitio útil. Usar `sede.py` para este trámite está **pendiente de verificar**.
  - En el modo completo necesitas poder manejar ese escritorio (por ejemplo, `xdotool` sobre su pantalla o una herramienta de control del ordenador). Sin escritorio (un servidor por SSH, `xvfb`), solo puedes hacer el modo acompañado.
- **Configurador FNMT** instalado (paso 1 de la sede). Versión publicada el 15-10-2026: 5.1.2, en `https://descargas.cert.fnmt.es/` (Windows `.exe`, macOS `.pkg`, Linux `.deb`; el `.rpm` enlazado era la 5.0.3). Descárgalo **solo** de ahí. Instalarlo pide la contraseña de administrador: la escribe la persona.
- **Correo:** el código de solicitud llega por email. Si tienes acceso a su correo y su permiso para leerlo, búscalo tú. Si no, que te lo pase.

## 3. Pasos

URLs para persona física (`/certificados/persona-fisica/renovar/…`) y para administrador único (`/certificados/certificado-de-representante/administrador-unico-solidario/renovar-certificado/…`), sobre `https://www.sede.fnmt.gob.es`:

| Paso | Persona física | Administrador único |
|---|---|---|
| 1. Configuración previa | `…/renovar/configuracion-previa` | `…/renovar-certificado/configuracion-previa` |
| 2. Solicitud | `…/renovar/solicitar-renovacion` | `…/renovar-certificado/solicitud-de-renovacion` |
| 3. Descarga | `…/renovar/descargar-certificado` | `…/renovar-certificado/descargar-certificado` |

1. **Configuración previa.** Instala o comprueba el Configurador. Si al abrirlo pregunta por un proxy, déjalo en blanco y acepta (lo normal en casa). El Configurador puede cerrarse: la web lo vuelve a lanzar al enviar la petición.
2. **Solicitud** (acto `generar`).
   - Entra con el certificado de **persona física**. En el de representante, la sede rellena sola los datos de la entidad y del representante a partir del certificado y del Registro Mercantil: **compruébalos con tu usuario** (entidad, cargo, titular).
   - El Configurador pide fijar una **contraseña nueva** para la solicitud. La escribe la persona y la guarda ella: se vuelve a pedir al descargar y **no se puede recuperar** (si se pierde, hay que empezar de nuevo).
   - Envía la petición.
3. **Espera** unos 60 minutos. Llegan **dos correos** de la FNMT: un aviso de seguridad (con la opción de anular si no la pidió) y el bueno, con el **código de solicitud** y "ya puede ser descargado". El código es dato personal: no lo copies fuera de la conversación.
4. **Descarga** (acto `generar`; en el de representante, también `pagar`).
   - Mismo equipo, mismo usuario, mismo navegador.
   - Formulario: código de solicitud, NIF o NIE del titular y primer apellido, **exactamente como en la solicitud**, y aceptar las condiciones.
   - **Representante:** pago de 24 € + impuestos con tarjeta. Confirma el importe con tu usuario. Los datos de la tarjeta y la confirmación del banco son suyos (§4).
   - El Configurador pide la contraseña de la solicitud (la teclea la persona) e instala el certificado en el navegador.
5. **Copia de seguridad.** Exporta el certificado nuevo a `.p12` desde el navegador (o con la opción del Configurador) con una contraseña. Guárdalo en una carpeta privada del equipo, con permisos solo para el usuario y nunca en carpetas sincronizadas o compartidas.

## 4. Lo que siempre teclea la persona

Aunque tengas todos los permisos:
- la contraseña de administrador para instalar el Configurador;
- la **contraseña de la solicitud** (al pedir y al descargar);
- la contraseña del `.p12` de la copia de seguridad;
- los **datos de la tarjeta** y la confirmación del pago en la app de su banco.

Tú dejas la ventana delante y esperas. No pidas ninguno de esos datos por el chat ni los guardes en ficheros, notas o memorias.

## 5. Después de renovar

- **El certificado anterior queda revocado** al descargar el nuevo. Pasó así en la renovación de representante del 15-10-2026; en persona física no se ha comprobado. A partir de ahí, todo lo que usaba el viejo deja de funcionar.
- **Actualiza el certificado del agente:** `cert.py configurar` con el `.p12` nuevo. Lo ejecuta la persona en su terminal (`setup-<sistema>.md`). Comprueba con `cert.py listar` que sale la fecha nueva.
- **AutoFirma y otros navegadores:** importa el nuevo donde haga falta (`setup-autofirma.md`, paso 1).
- **El `.p12` viejo:** que la persona lo borre o lo marque como revocado, con la contraseña que lo acompañara, para no confundirlos.
- **Llevarlo a otros equipos:** mejor por USB o red local. Mandárselo por correo deja el certificado y su copia en los servidores del correo; si aun así lo quiere, que la contraseña viaje por otra vía y que borre el correo de enviados y recibidos al terminar.
- **Recordatorio:** apunta la nueva fecha de caducidad y avisa 60 días antes, cuando se abra la siguiente ventana.
- **Prueba:** entra en una consulta con el certificado nuevo (por ejemplo, datos censales de la AEAT, `sede-aeat.md` §3.2).

## 6. Trampas

- **Solicitar y descargar en equipos o usuarios distintos** no funciona: las claves se generan en el equipo de la solicitud.
- **La contraseña de la solicitud no se recupera.** Si se pierde, nueva solicitud.
- **El certificado de la empresa no sirve para pedir su renovación:** se pide con el de persona física (o DNIe).
- **"Renovación" de representante = certificado nuevo en la práctica:** misma validez y mismo precio que pedirlo de cero. Si la ruta de renovación falla, usa la de solicitar.
- **Revocación:** no descargues el nuevo hasta que tu usuario esté listo para cambiar el certificado en todos sus sitios (agente, AutoFirma, gestoría).
- **Ventana de 60 días:** antes no aparece la opción de renovar.
