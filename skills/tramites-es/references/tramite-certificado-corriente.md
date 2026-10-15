---
verificado_el: 2026-10-15
fuentes:
  - https://sede.agenciatributaria.gob.es/Sede/procedimientos/G304.shtml
  - https://sede.agenciatributaria.gob.es/Sede/procedimientoini/G304.shtml
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Consulta+de+pagos+y+deudas/CCertificado+de+estar+al+corriente+en+las+obligaciones+de+la+Seguridad+Social
  - https://sede.seg-social.gob.es/wps/portal/sede/sede/EmpresasyProfesionales/informes+y+certificados/01informes+y+certificados
  - https://sede.gobiernodecanarias.org/tributos/jsf/publico/certificados/certificados_individuales.jsp
  - https://sede.gobiernodecanarias.org/tributos/jsf/publico/validacion/valida.jsp
estado_mapeo: "AEAT G304 recorrido con certificado hasta 'Firmar Enviar' (15-10-2026). TGSS emitido sin firma en el mapeo (15-10-2026). ATC solo en su parte pública: el acceso con certificado pasa por AutoFirma."
---

# Certificado de estar al corriente (AEAT, Seguridad Social y ATC)

**Riesgo: Preparar.** El agente prepara: comprueba antes deudas y declaraciones, elige con la persona el tipo de certificado y la deja ante el botón final.

**Quién da el paso final:**
- **AEAT:** la persona, porque hay que firmar.
- **ATC:** la persona, porque el acceso pasa por AutoFirma.
- **Seguridad Social:** no hay firma. El agente puede emitirlo con el OK explícito de la persona para ese certificado concreto.

## 1. Antes de pedir nada: ¿saldrá positivo?

Un certificado "negativo" (con deudas o declaraciones pendientes) no sirve para una subvención o un contrato. Antes de pedirlo, mira:

1. **Deudas AEAT:** `sede-aeat.md` §3.1.
2. **Deudas TGSS y recibos:** `sede-tgss-importass.md` §3.2 y §3.5.
3. **Declaraciones presentadas** del último año: `sede-aeat.md` §3.5. Comprueba que no falta ningún modelo obligatorio, con `perfil-autonomo.md` y `calendario-fiscal.md`.
4. **En Canarias:** IGIC (420/425) en la ATC (`sede-atc.md`).

Si encuentras algo pendiente, **díselo antes**: pedir el certificado no lo arregla.

Pregunta **para qué lo necesita**. Contratación pública, subvenciones, transporte o uso general son certificados distintos.

## 2. AEAT, G304 (`aeat-certificado-corriente`) · Persona (firma) · verificado hasta la firma

- **URL con certificado:** `https://www1.agenciatributaria.gob.es/wlpl/EMCE-JDIT/ECOTInternetCiudadanosServlet` (acceso en `sede-aeat.md` §2).
- **Formulario:**
  - `fTipoRepresentacion0/1`: en nombre propio o en representación de terceros. En este caso, `fNifT` y `fNombreT`.
  - `fTipoCertificado0..4`: contratar con el sector público / autorizaciones de transporte / subvenciones públicas / … / **General**. Elige según la finalidad.
  - `fMomentoDeterminacionEcot0/1`: en la fecha actual o en una fecha pasada.
  - Botones: "Volver", "Limpiar" y **"Validar solicitud"** (`#validarSolicitud`).
- **Qué hace el agente:**
  1. Rellena las opciones que diga la persona y pulsa "Validar solicitud".
  2. Lee el resumen ("Se ha consignado…") y, sobre todo, el bloque **"Avisos"**. Si todo está bien, "Avisos" dice "Revise los datos introducidos y en caso de estar conforme, firme y envíe la solicitud" y el asistente marca el paso "2. Confirmar la solicitud" (revalidado el 15-10-2026).
  3. Cuéntaselo a la persona.
- **Dónde para:** en el resumen. **"Firmar Enviar"** (`input#FirmayEnvia_<n>`, id dinámico, sin `onclick` en el HTML) es la firma JS de la AEAT y `sede.py` la bloquea **en la página** (su `value` casa con la lista de bloqueo). La guarda de red no la cubre: el envío va al mismo servlet (`ECOTInternetCiudadanosServlet`), así que no hay segunda barrera. No lo pulses "para probar".
- **La persona:**
  - Entra desde la ficha (`https://sede.agenciatributaria.gob.es/Sede/procedimientoini/G304.shtml`) o directamente con el enlace de arriba, en su navegador y con su certificado.
  - Marca **las mismas opciones**, pulsa "Validar solicitud" y después **"Firmar Enviar"**.
  - El navegador del agente se cierra al terminar: la sesión no se puede "pasar".
- **Éxito:**
  - El certificado (PDF con CSV), pasado por `scripts/justificante.py`.
  - Si no sale al momento, la solicitud queda en trámite: la ficha da un plazo de resolución de 20 días hábiles.
  - Estado de la solicitud: `…/wlpl/inwinvoc/es.aeat.dit.adu.emce.recogidaCertInt.RceAcciones?fAccion=1&fTramite=G3042&fTipoPet=2`.
  - Certificados expedidos (G331): `sede-aeat.md` §3.9.
  - Ninguna de las dos consultas se ha recorrido con certificado.

## 3. Seguridad Social (`tgss-certificado-corriente`) · Preparar · verificado

- **URL:** `https://portal.seg-social.gob.es/wps/portal/importass/Seguridad/PortalRedirectorN1A?idApp=2265&N1&A`. Usa la receta de login de `sede-tgss-importass.md` §2. Acaba en `sp.seg-social.es/ProsaInternet/OnlineAccess`, ya identificado.
- **Tipos** (radios `certificado_1..9`):
  - **Genérico**, Licitación de contratos del sector público, **Subvenciones**, Artículo 42;
  - "Sin deuda a una fecha" y sus variantes de licitación y subvenciones;
  - Deuda total, Detalle de deuda (estos dos son **informes de deuda**).
- **Qué hace el agente:** entra, comprueba los tipos y acuerda con la persona cuál necesita.
- **Dónde para:** antes de **"Continuar"** (`#ENVIO_13`).
  - Con el OK explícito de la persona para ese tipo, el agente puede pulsarlo: se emite **sin firma**.
  - En la pantalla "Información", **"Imprimir"** (`#ENVIO_10`) genera el PDF.
  - Si la persona prefiere hacerlo ella: mismo enlace, mismo tipo, "Continuar" e "Imprimir".
  - Con `sede.py` este clic no se ha probado. Si sale "BLOQUEADO", lo hace la persona.
- **Límites:** cuenta para el límite práctico de unos 3 informes por titular y día. Pide **uno**, guarda el PDF y no lo repitas el mismo día.
- **Éxito:** el PDF, pasado por `scripts/justificante.py`. Lleva un código de verificación de la Seguridad Social; el servicio de cotejo no está mapeado.
  - Certificados ya emitidos: `…PortalRedirectorN1A?idApp=2266&N1&A` (pendiente).
- **Sociedad:** con el certificado de representante, por la sede, en "Empresas y Profesionales > Informes y certificados" (en la cabecera). No recorrido.

## 4. ATC, Canarias (`atc-certificado-corriente`) · Preparar · parcial (entra y emite la persona)

Detalle de la sede en `sede-atc.md`.

- **Catálogo público:** `https://sede.gobiernodecanarias.org/tributos/jsf/publico/certificados/certificados_individuales.jsp`.
  - Incluye estar al corriente (subvenciones, contratación pública, transporte, contratistas), situación tributaria, actividades y locales, declaraciones y censo.
  - Telemáticos y **gratuitos**.
- **Acceso:**
  - Hay que identificarse en `https://sede.gobiernodecanarias.org/tributos/jsf/publico/validacion/valida.jsp`.
  - El botón **"Entrar"** lanza **AutoFirma** por websocket. `sede.py` intercepta `afirma://`, así que **el agente no puede entrar**.
- **Qué hace el agente:**
  - Le dice a la persona qué certificado pedir. En la ATC se elige **por finalidad**, p. ej. "Ayudas o subvenciones de las AA.PP.", no por el nombre "estar al corriente".
  - Le da el enlace al catálogo.
- **La persona:** entra con su certificado (AutoFirma; ver `setup-autofirma.md`), elige el certificado por su finalidad y lo descarga.
- **Éxito:** PDF con CSV, de emisión inmediata según la investigación previa.
  - Rutas citadas por esa investigación y **no recorridas** en el mapeo: listado `/tributos/ov/seguro/certificados/individual/listado.jsp`, histórico `miscertificados.jsp` y verificación del CSV `/tributos/jsf/publico/consultacsv/formulario.jsp`.

## 5. Qué decirle a la persona

> Para `<finalidad>` necesitas el certificado de estar al corriente de `<AEAT / Seguridad Social / ATC>`, tipo `<tipo>`.
> - He revisado: `<deudas / declaraciones>` → `<sin pendientes | hay esto pendiente: …>`.
> - **AEAT:** entra en `<enlace>`, marca `<opciones>`, pulsa "Validar solicitud" y luego **"Firmar Enviar"**.
> - **Seguridad Social:** `<lo he emitido y está aquí (CSV …)>` | `<entra en <enlace>, elige "<tipo>", pulsa "Continuar" e "Imprimir">`.
> - **ATC:** entra en `<enlace>` con tu certificado (se abrirá AutoFirma), elige "`<finalidad>`" y descárgalo.

Muchas convocatorias permiten **autorizar la consulta** en vez de aportar el certificado. Míralo en las bases (`ayudas.md`).

## 6. Trampas

- **AEAT:**
  - Elige el tipo que pidan las bases o el contrato. Si no lo dicen, pregunta antes de usar el "General".
  - No pulses "Firmar Enviar" ni busques cómo saltar el bloqueo.
- **Seguridad Social:** junto a los certificados está el documento de ingreso de deudas (`idApp=370`) y el "Pago con tarjeta". Son de la persona.
- **ATC:** no intentes sortear AutoFirma.
- **Repetir pedidos:** no repitas la solicitud si algo falló al final. Comprueba antes en "certificados expedidos" o "emitidos" que no salió (regla de no duplicar).

## 7. Fuentes

- Fichas G304 de la AEAT, tarjeta de Import@ss, catálogo de la sede de la TGSS y certificados individuales y validación de la ATC: ver la cabecera.
- Mapeo en vivo del 15-10-2026 e historial previo: la ATC elige por finalidad y la TGSS rechaza a partir de unos 3 informes por día.
