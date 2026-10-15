---
verificado_el: 2026-10-15
fuentes:
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/consultas-informaticas/otros-servicios-ayuda-tecnica/peticion-cita-previa-traves-internet.html
  - https://www2.agenciatributaria.gob.es/wlpl/TOCP-MUTE/internet/identificacion
  - https://sede.seg-social.gob.es/wps/portal/sede/sede/Ciudadanos/cita+previa+para+pensiones+y+otras+prestaciones/13cita+previa+para+pensiones+y+otras+prestaciones
  - https://sede.seg-social.gob.es/wps/portal/sede/sede/Ciudadanos/cita+previa+para+pensiones+y+otras+prestaciones/202910
  - https://revista.seg-social.es/-/c%C3%B3mo-solicitar-cita-previa-para-pensiones-y-otras-prestaciones-de-la-seguridad-social
  - https://sede.dgt.gob.es/es/otros-tramites/cita-previa/
  - https://sedeclave.dgt.gob.es/WEB_CITE_CONSULTA/paginas/inicio.faces
  - https://www.citapreviadnie.es/citaPreviaDni/
  - https://sede.administracionespublicas.gob.es/pagina/index/directorio/icpplus
  - https://sede.administracionespublicas.gob.es/ayuda/faq/extranjeria
  - https://sede.mjusticia.gob.es/es/tramites/cita-previa-registro-civil
  - https://sede.administracionespublicas.gob.es/icpplustiej/citar?i=es&org=JUS-RC
  - https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763
  - https://sede.sepe.gob.es/portalSede/procedimientos-y-servicios/personas/proteccion-por-desempleo/cita-previa.html
  - https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=sepe&codidioma=es
  - https://sede.gobiernodecanarias.org/sede/tramites/11001
  - https://www3.gobiernodecanarias.org/tributos/atc/es/cita-previa
estado_mapeo: "solo documentación pública; no se ha pedido ninguna cita en vivo"
---

# Cita previa (AEAT, Seguridad Social, DGT, DNI, extranjería, Registro Civil, SEPE…)

**Actos:** reservar o confirmar = `cita`. Anular = `cambiar_datos`. Cambiar una cita = anular la vieja y reservar la nueva (`cita` + `cambiar_datos`).

Con el permiso `cita`, el agente puede pedir una cita **para la persona usuaria**, paso a paso, como lo haría ella. Caso típico: todas las citas de un expediente de nacionalidad (huellas, jura en el Registro Civil, primer DNI).

**Lo que esta guía no permite** (no es cuestión de permisos; ver `SKILL.md`):
- refrescar en bucle para cazar huecos;
- reservar varias citas, o citas para terceros sin relación;
- resolver CAPTCHAs: los resuelve la persona y el agente sigue;
- automatizar Cl@ve PIN o Cl@ve Móvil.

## 1. Reglas de uso

1. **Una cita, del titular.** Es para la persona o para quien ella representa en ese trámite: su sociedad (con certificado de representante), su hijo menor, el familiar que reagrupa o el trabajador al que contrata. Antes de reservar, mira si ya tiene una ("consultar", "gestión de citas"): no dupliques.
2. **Disponibilidad: como mucho una consulta cada 30 minutos** por servicio y oficina, en días laborables de 8:00 a 20:00 y un máximo de 8 al día. Una sola sesión a la vez: ni pestañas en paralelo ni varias provincias a la vez. Por qué 30 minutos:
   - es el ritmo de una persona que vuelve a mirar varias veces al día, y no se parece a un robot (el ICP de extranjería ya rechaza a los clientes que no son un navegador);
   - los huecos salen por tandas (agenda nueva) o sueltos, por anulaciones. Mirar cada pocos segundos solo sirve para quitárselos a otros, que es lo que hacen las redes de reventa;
   - donde hay CAPTCHA, cada consulta necesita a la persona: el ritmo real lo marca ella.
   - Si la sede bloquea (403, "Request Rejected", "demasiadas peticiones", sesión expulsada), **para hasta el día siguiente** y avísala. Si la oficina o el 060 dicen cuándo abren agenda, mira entonces.
3. **CAPTCHA: lo resuelve la persona**, también un reCAPTCHA invisible que rechaza la petición. Nada de servicios de resolución, cambios de User-Agent ni trucos *stealth*: deja la pantalla abierta, ella lo resuelve y tú sigues.
4. **Antes de reservar, confirma con la persona** el trámite, la oficina, la fecha y la hora, y que su nombre está escrito como en su documento. Excepción: que su usuario lo haya delegado con criterios claros ("la primera mañana libre en cualquier oficina de la provincia").
5. **Guarda el justificante:** número o localizador, PDF o captura (`captura()` en la receta) y el correo de confirmación. Es dato personal: guárdalo en local. Dile la fecha, la hora, la dirección y qué tiene que llevar.
6. **Anula lo que no vaya a usar** (`cambiar_datos`, con su OK): así se libera el hueco.
7. **Cl@ve:** en la pasarela, solo "DNIe / Certificado electrónico". Si el servicio solo admite Cl@ve PIN o Móvil, entra ella.
8. **Solo webs oficiales. Las citas son gratuitas:** quien vende citas comete un fraude. La Policía Nacional ha desarticulado redes que acaparaban citas de extranjería con bots y las revendían.

### Con `sede.py`

- Casi todas las citas se piden con datos, sin certificado: ejecuta sin `--titular`. Usa `--titular` solo donde se entra con certificado: anular en la AEAT, INSS con certificado, DGT vía Cl@ve. Para la AEAT usa `--url` con la entrada de §2: con `--sede aeat` el certificado solo va a `www1`.
- Con el permiso de tu usuario: `--permitir cita` (y `cambiar_datos` para anular).
- **La guarda de página** reconoce "Reservar", "Reservar cita" y "Confirmar cita" (acto `cita`) y "Anular" (`cambiar_datos`). En páginas de cita (URL o título con "cita previa", "cita", `icpplus`, `CITE_CONSULTA` o `TOCP-MUTE`) también trata como `cita` un botón que empiece por "Confirmar". **No reconoce** "Aceptar" ni "Siguiente", que en estas webs suelen ser pasos intermedios: sin permiso `cita`, para tú antes del último botón.
- **La guarda de red** puede atribuir un paso de la cita a otro acto, por ejemplo `presentar` o `generar` si la ruta contiene "grabar" o "solicitar". No amplíes permisos por tu cuenta: explícaselo a tu usuario y que decida, o que pulse ella ese botón.

## 2. AEAT: Asistencia y Cita (`cita-aeat`) · pendiente

- **Entrada:** `https://www2.agenciatributaria.gob.es/wlpl/TOCP-MUTE/internet/identificacion`. Sirve para Renta, censos, cartas recibidas, etc.
- **Identificación:** para pedirla, ninguna: NIF y nombre y apellidos. Con "La cita es para otra persona, empresa o entidad" se dan los datos del titular y de quien acude. Anular o modificar exige certificado, DNIe o Cl@ve: usa el certificado.
- **Pasos:**
  1. "Para quién".
  2. "Para qué": "He recibido una carta" con el CSV de 16 caracteres de la carta, u "Otras gestiones" y el servicio.
  3. "Selección cita": provincia o código postal; presencial, telefónica o atención inmediata (llamada o chat); "Seleccionar" un hueco y **"Confirmar cita"**.
  4. "Confirmación": teléfono, correo y motivo, y **"Confirmar"**. Es el botón final y la guarda no lo reconoce.
- **CAPTCHA:** no aparece en el HTML de la identificación.
- **Justificante:** pantalla de resumen (tipo, fecha y hora, lugar, servicio y documentación que llevar) y correo con enlace para modificar o anular. Captura el resumen.
- **Anular o modificar:** "¿Tienes ya una cita? Puedes anular o modificar tu cita" → identificación → "Modificar" o "Anular".
- **Trampas:** si hay carta, usa su CSV: la cita va al servicio exacto. Una cita telefónica resuelve muchas consultas sin desplazarse.

## 3. Seguridad Social

### INSS y CAISS: pensiones y prestaciones (`cita-inss`) · pendiente

- **Ficha:** "Cita previa para prestaciones y otras gestiones" (fuentes 3 y 4).
- **Con certificado:** `https://sede.seg-social.gob.es/wps/portal/sede/Seguridad/PortalRedirectorN2P?idApp=321&idContenido=403c4672-c045-4868-bee5-202e3f37f289&idPagina=com.ss.sede.Ciudadanos&N2&P`. El login es el de `sede-tgss-importass.md`. Consultar o eliminar: la misma ruta con `idApp=322`.
- **Sin certificado:** `https://w6.seg-social.es/ProsaInternetAnonimo/OnlineAccess?ARQ.SPM.ACTION=LOGIN&ARQ.SPM.APPTYPE=SERVICE&ARQ.IDAPP=CPMSWACS&ORGANISMO=I`. Trabajadores del mar (ISM): `ORGANISMO=M`. Consultar o eliminar: `ARQ.IDAPP=CPMSWCCS`.
- **Pasos:** formulario de varios pasos: motivo, centro, día y hora y datos. Elige bien el motivo: el tiempo de la cita depende de él.
- **CAPTCHA:** el acceso sin certificado lleva reCAPTCHA (su clave de sitio está en la página). Con certificado, no comprobado.
- **Justificante:** correo con los datos de la cita. Por teléfono dan un localizador.
- **Trampas:**
  - Si no hay cita en un CAISS, la ficha permite pedirla en otro centro.
  - Cita por teléfono: 901 10 65 70 o 91 541 25 30.
  - Muchos trámites se hacen sin cita en `https://prestaciones.seg-social.es/`.

### TGSS: afiliación, cotización y autónomos

No hay cita previa por internet. Según la guía oficial de la revista de la Seguridad Social, sus oficinas atienden de lunes a viernes de 9 a 14 h sin cita. Antes de ir, mira si se puede hacer en Import@ss (`sede-tgss-importass.md`).

## 4. DGT: Jefaturas y Oficinas de Tráfico (`cita-dgt`) · pendiente

- **Ficha:** `https://sede.dgt.gob.es/es/otros-tramites/cita-previa/`. **Aplicación:** `https://sedeclave.dgt.gob.es/WEB_CITE_CONSULTA/paginas/inicio.faces`. El enlace de la ficha pasa por un stub con *meta refresh*.
- **Identificación:**
  - DNI o NIE del interesado y, si va un representante, también el suyo; correo y teléfono.
  - La portada ofrece "Autenticación en Cl@ve" (con "DNIe / Certificado electrónico"). No se ha comprobado si es obligatoria.
- **Pasos:** centro → área de tramitación → trámite → "Pedir cita" → día y hora → datos → confirmar.
- **CAPTCHA:** reCAPTCHA v3, invisible. Si rechaza la petición, la persona la pide desde su navegador.
- **Justificante:** enlace "Aquí puedes descargarte el justificante" (PDF) y copia por correo.
- **Anular o modificar:** "Consulta o modifica tus citas", con la oficina, la fecha de la cita y el DNI de quien iba a ir.
- **Trampas:**
  - Cada trámite solo se atiende en su área: no reserves en otra área solo porque tenga huecos.
  - Desde el 1-3-2021, las empresas y los obligados a relacionarse electrónicamente no tienen cita presencial.
  - Los mayores de 65 años no necesitan cita en el horario preferente.
  - Si te equivocas de día, anula y pide otra.

## 5. Policía Nacional

### DNI y pasaporte (`cita-dni`) · pendiente

- **URL:** `https://www.citapreviadnie.es/citaPreviaDni/` (enlazada desde dnielectronico.es) → "CONTINUAR".
- **Identificación:**
  - "Acceso con DNI Electrónico": DNIe en un lector. Usa el puerto 38188; no se ha probado con un certificado en software.
  - "Acceso con datos DNI/NIE": número y letra, equipo de expedición, fecha de validez y número de soporte.
  - Quien se ha nacionalizado entra con su NIE para su primer DNI.
- **CAPTCHA:** sí, de imagen (con versión en audio) en el acceso con datos.
- **Pasos:** "Renovar DNI" o "Renovar pasaporte" → provincia, oficina, fecha y hora → confirmar.
- **Justificante:** no verificado. Captura la pantalla final.
- **Anular o cambiar:** "Gestión de citas" → Consultar, Cambiar o Anular (solo en la web y en citas individuales). "Modificar cita" anula la anterior al confirmar ("¿Está usted seguro?"): hacen falta `cita` y `cambiar_datos`.
- **Trampas:** hay que llevar una fotografía reciente. Si el DNI se ha perdido o lo han robado, hay otro acceso ("pérdida o sustracción").

### Extranjería: NIE, TIE, huellas y autorizaciones (`cita-extranjeria`) · pendiente

Es la más difícil.

- **Entrada oficial:** `https://sede.administracionespublicas.gob.es/pagina/index/directorio/icpplus` → "Acceder al procedimiento" → aplicación ICP (`https://icp.administracionelectronica.gob.es/icpplus/index.html`). Ninguna otra web.
- **Quién la pide** (según la sede):
  - autorización inicial de un trabajador: la empleadora;
  - reagrupación: el reagrupante;
  - menores: el padre, la madre o su representante;
  - el resto: el extranjero o su representante.
- **Flujo** (FAQ oficial y guías públicas; no recorrido):
  1. Provincia y trámite. Los de Policía empiezan por "POLICÍA-", como la toma de huellas para la TIE; el resto son de la Oficina de Extranjería.
  2. Información → "Presentación sin Cl@ve". Según guías públicas, también hay acceso con Cl@ve; ahí, certificado.
  3. Datos del documento: tipo y número, nombre como en el documento y, según el trámite, año de nacimiento y nacionalidad.
  4. "Solicitar cita", "Consultar citas confirmadas" o "Anular cita".
  5. Oficina → teléfono y correo → hueco → código de verificación si lo pide → confirmar.
- **CAPTCHA:** en icpplus no se ha podido comprobar: rechaza los clientes que no son un navegador ("Request Rejected"). La misma plataforma en Justicia (icpplustiej, §6) lleva CAPTCHA de imagen y un campo de código de verificación: cuenta con ellos.
- **Sin huecos:** "No hay citas disponibles en este momento" significa que todo está ocupado (FAQ oficial). Lo legítimo:
  - consultar al ritmo de §1: cada consulta es una pasada completa, con la persona delante para el CAPTCHA;
  - mirar otras oficinas de la provincia que admitan el trámite, si a la persona le sirven;
  - preguntar a la oficina o al 060 cuándo abren agenda;
  - nunca bots, nunca intermediarios de pago y nunca otro trámite "porque tiene huecos".
- **Justificante:** número de justificante y correo. Si se pierde, "consultar cita" con el número, o el botón que lo reenvía al correo.
- **Anular:** con los mismos datos con los que se reservó y el número de justificante. El teléfono o el correo de una cita no se cambian por internet: hay que llamar a la oficina.
- **Trampas:**
  - No todas las oficinas están en el sistema.
  - Las huellas suelen pedirse después de la resolución favorable.
  - El nombre, exactamente como en el documento.
  - La sesión caduca rápido: ten los datos listos antes de empezar.

## 6. Registro Civil: jura de nacionalidad e inscripciones (`cita-registro-civil`) · pendiente

- **Ficha:** `https://sede.mjusticia.gob.es/es/tramites/cita-previa-registro-civil` ("Tramitación On-line sin Certificado Digital") → `https://sede.administracionespublicas.gob.es/icpplustiej/citar?i=es&org=JUS-RC`. Es la plataforma ICP.
- **Identificación:** sin certificado, con los datos del documento.
- **Pasos:** ámbito → provincia → registro civil → trámite (cambia según el registro) → datos → hueco → confirmar.
- **CAPTCHA:** sí: CAPTCHA de imagen ("EU CAPTCHA") y campo de código de verificación, vistos en el HTML.
- **Justificante y anulación:** es el mismo sistema que extranjería, pero aquí no se ha verificado.
- **Plazo de la jura:** la concesión por residencia **caduca a los 180 días de su notificación** si la persona no comparece (art. 21.4 del Código Civil). Pide la cita en cuanto llegue la resolución. Si no hay huecos, guarda capturas de los intentos y pregunta al registro. Justicia publica también una instrucción sobre la jura ante notario.
- **Después:** el primer DNI se pide en `citapreviadnie.es` con el NIE (§5).
- **Trampas:** no todos los registros están en la aplicación.

## 7. SEPE y servicios autonómicos de empleo

### SEPE: prestaciones (`cita-sepe`) · pendiente

- **Ficha:** `https://sede.sepe.gob.es/portalSede/procedimientos-y-servicios/personas/proteccion-por-desempleo/cita-previa.html` → "Iniciar Solicitud / Anular Cita" → `https://citaprevia-sede.sepe.gob.es/citapreviasepe/?origen=sepe&codidioma=es`.
- **Pasos (6):** trámite → canal y oficina (empieza por el código postal) → validación → día y hora → datos personales → cita. En la misma aplicación está "Comprobar, modificar o cancelar la reserva".
- **CAPTCHA:** sí, de imagen y con audio.
- **Identificación y justificante:** no verificados.
- **Antes de pedirla:** hay que estar inscrito como demandante de empleo en el servicio autonómico. Muchos trámites se hacen sin cita: con el formulario de presolicitud o en la sede con certificado.

### Servicio Canario de Empleo y otras comunidades

- **SCE (demanda de empleo):** `https://sede.gobiernodecanarias.org/sede/sce/cita_previa`. Es una aplicación JavaScript: pasos no verificados.
- **Otras comunidades:** busca la sede de su servicio de empleo.

## 8. ATC Canarias y ayuntamientos

- **ATC:**
  - Cita: `https://www3.gobiernodecanarias.org/tributos/atc/es/cita-previa`. El formulario valida un reCAPTCHA.
  - Anular: `https://www3.gobiernodecanarias.org/tributos/atc/es/anular-cita-previa`.
  - Identificación y justificante: no verificados.
  - Antes, mira si el trámite se hace en la sede (`sede-atc.md`).
- **Ayuntamientos (padrón):** cada uno tiene su sistema. Localízalo con `scripts/buscar.py --municipio` y la web municipal.
  - Ejemplo: Madrid exige cita para las altas y los cambios del padrón y, según su web, solo da una cita por persona cada 30 días. Su entrada, `www.madrid.es/citaprevia`, no se ha podido descargar: responde 403 a los clientes que no son un navegador.
  - Si el ayuntamiento permite empadronarse en línea con certificado, es mejor que la cita.

## 9. Qué decirle a la persona

- **Antes:** "Para pedir la cita necesito [datos]. Si sale un CAPTCHA, te aviso y lo resuelves tú. Antes de reservar te confirmo la oficina, la fecha y la hora."
- **Si no hay huecos:** "Ahora no hay citas en [oficina]. Vuelvo a mirar como mucho cada 30 minutos en horario de oficina, y como mucho 8 veces hoy. Otras opciones: [otras oficinas], el teléfono [x] o ir sin cita, si se admite."
- **Antes del último clic:** "Hay cita el [día] a las [hora] en [oficina, dirección] para [trámite]. ¿La reservo?"
- **Después:** "Reservada. El justificante [nº] está guardado en [ruta local]. Lleva [documentación]. Si no puedes ir, dímelo y la anulo para liberar el hueco."
- **Siempre:** las citas son gratuitas. Si alguien te pide dinero por una, es un fraude.

## 10. Estado de esta guía

- Se ha leído la documentación pública y el HTML de las páginas de entrada (solo GET, sin rellenar formularios), sin pedir ninguna cita.
- **No verificado:**
  - el flujo completo de cada servicio;
  - los justificantes de DNI, SEPE, ATC y SCE;
  - el CAPTCHA de icpplus (bloqueo del WAF);
  - si la DGT exige Cl@ve;
  - el acceso con certificado en software a citapreviadnie.es.
- Si la pantalla real no coincide, confía en ella y abre un issue "sede rota".
