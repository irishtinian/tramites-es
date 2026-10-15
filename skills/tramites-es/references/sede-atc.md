---
verificado_el: 2026-10-15
estado_mapeo: parcial   # parte pública verificada; con certificado, el acceso se detiene en AutoFirma
fuentes:
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-400
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-420
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-425
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/4015          # 420: solo régimen general
  - https://sede.gobiernodecanarias.org/sede/movil/procedimientos_servicios/tramites/4018   # 425: también el REPEP
  - https://sede.gobiernodecanarias.org/sede/tramites/4006                                  # certificados tributarios
  - https://sede.gobiernodecanarias.org/tributos/jsf/publico/certificados/certificados_individuales.jsp
  - https://sede.gobiernodecanarias.org/tributos/jsf/publico/sede/la_sede/menu_mis_notificaciones.jsp
  - https://sede.gobiernodecanarias.org/tributos/jsf/publico/sede/la_sede/requisitos_tecnicos.jsp
  - https://www3.gobiernodecanarias.org/tributos/atc/web/agencia-tributaria-canaria/modelos-presentacion-telematica
  - https://www3.gobiernodecanarias.org/tributos/atc/entidades-colaboradoras
  - https://www.gobiernodecanarias.org/boc/2026/066/1094.html   # Decreto ley 3/2026 (REPEP), BOC nº 66
  - https://www.gobiernodecanarias.org/boc/2024/064/002.html    # obligación de presentar el 420 por internet
---

# Agencia Tributaria Canaria (ATC)

## Para qué sirve

En Canarias no hay IVA: el autónomo liquida el **IGIC** en la ATC. El IRPF (130/131), las retenciones (111/115) y el censo estatal (036) siguen en la AEAT (`sede-aeat.md`). **No apliques el 303.**

| Modelo o servicio | Qué es | Quién |
|---|---|---|
| **400** | Declaración censal de IGIC (alta, cambios, opción por regímenes) | Casi todos; el alta por DUE (CIRCE) exime del 400 de comienzo |
| **420** | Autoliquidación trimestral del IGIC | Solo **régimen general** (ficha SICAC 4015) |
| **425** | Resumen anual del IGIC | Régimen general **y también el REPEP**, solo con las casillas informativas (SICAC 4018) |
| **415** | Operaciones con terceros | Ver `calendario-fiscal.md` |
| Certificados | Estar al corriente, situación tributaria, actividades y locales, declaraciones, censo | Gratis, con CSV |
| Pago, deudas, notificaciones | Ver abajo | — |

**REPEP** (régimen especial del pequeño empresario; Decreto ley 3/2026, BOC nº 66): quien está en el REPEP **no presenta el 420, pero sí el 425**. Desde el 1-1-2027 entran, salvo renuncia, las personas físicas con volumen del año anterior de hasta 50.000 €. **Antes de preparar un 420, comprueba el régimen** (`perfil-autonomo.md`). Plazos: `calendario-fiscal.md` y `scripts/calendario.py --territorio canarias`.

## Acceso

| Dato | Valor |
|---|---|
| Sede | `https://sede.gobiernodecanarias.org/tributos/` (público en `/tributos/jsf/publico/…`, con sesión en `/tributos/jsf/seguro/…` y `/tributos/ov/seguro/…`) |
| Web informativa | `https://www3.gobiernodecanarias.org/tributos/atc/` (fichas de modelos y programas de ayuda) |
| Login | `https://sede.gobiernodecanarias.org/tributos/jsf/publico/validacion/valida.jsp` |
| Métodos | Certificado o DNIe (vía AutoFirma) y Cl@ve |
| Origins | `https://sede.gobiernodecanarias.org`, `https://www3.gobiernodecanarias.org` |
| `sede.py` | `--sede atc` (ver `assets/_sedes-canarias.yaml`) |

**Cómo entra el certificado.** La ATC **no** pide el certificado por TLS: ni en el *handshake* ni en `valida.jsp` (comprobado con `tls-probe` y `cert-probe` el 15-10-2026). Tras elegir certificado en el menú de validación (`validamenu.jsp`), el botón **Entrar** (`#btnValidar`) lanza **AutoFirma por *websocket*** para firmar el acceso.

- **El acceso a la zona privada de la ATC es una firma** (acto `firmar`).
  - Sin permiso: `sede.py` muestra **BLOQUEADO** y la persona entra en su navegador con AutoFirma.
  - Con permiso: `--permitir firmar` (y `--autofirma-auto N` en Linux sin escritorio). AutoFirma tiene que tener el certificado en el almacén del sistema (`setup-autofirma.md`).
- La rama Cl@ve con «DNIe / Certificado electrónico» (`sede-clave.md`) **no se ha probado en la ATC**. Si la pruebas, añade `https://pasarela-ident.clave.gob.es` a los origins, no uses nunca Cl@ve PIN, Móvil ni Permanente y documenta el resultado.
- **Cómo saber que entró:** no verificado en el mapeo. Pide a la persona que confirme que ve su nombre o NIF en la cabecera antes de seguir.

Peculiaridades técnicas:
- La aplicación es JSF/MyFaces con `jsessionid` efímero: **no guardes enlaces con `;jsessionid=`**.
- No se vio CAPTCHA ni WAF en las páginas públicas.
- El Gobierno de Canarias publica cortes de servicio en `https://sede.gobiernodecanarias.org/sede/la_sede/interrupciones`. Suelen ser **por la tarde**: mejor trabajar por la mañana.

## Trámites

### Certificado de estar al corriente y otros certificados (actos: `firmar` para entrar, `generar`)

- **URL pública del catálogo:** `https://sede.gobiernodecanarias.org/tributos/jsf/publico/certificados/certificados_individuales.jsp`. Tipos: estar al corriente, situación tributaria, actividades y locales, declaraciones presentadas y declaraciones censales. Son gratuitos.
- **El «estar al corriente» depende de la finalidad.** Hay certificados distintos para subvenciones, contratación pública, transporte y contratistas. Pregunta a la persona **para qué lo necesita** antes de nada: en el historial del proyecto, elegir el tipo equivocado obligó a repetirlo.
- Pasos del agente (sin certificado, solo lectura):
  ```bash
  uv run scripts/sede.py abrir --sede atc --url "https://sede.gobiernodecanarias.org/tributos/jsf/publico/certificados/certificados_individuales.jsp"
  ```
- **Con `--permitir firmar,generar`:** entra con AutoFirma, elige la finalidad acordada y emite el certificado.
- **Sin esos permisos:** para en el botón de acceso y prepara la elección («certificado de estar al corriente, finalidad X»). Tu usuario entra, elige la finalidad y lo emite.
- **Cómo verificar** (según la investigación del proyecto; **no recorrido en el mapeo**): la emisión es inmediata, en PDF con CSV, y queda en un histórico «Mis certificados». Comprueba el PDF con `scripts/justificante.py`: titular, finalidad, fecha y CSV.
- El cotejo de CSV (`https://sede.gobiernodecanarias.org/tributos/jsf/publico/consultacsv/formulario.jsp`) **tiene CAPTCHA** (comprobado el 15-10-2026): si hace falta cotejar, lo hace la persona.

### Modelo 420: autoliquidación trimestral (actos: `firmar`, `presentar`, y `pagar` si sale a ingresar)

- **Ficha:** `https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-420`. Telemático obligatorio, con excepciones (ficha y BOC 2024/064).
- **No hay formulario web.** Se usa el **programa de ayuda** de la ATC (Windows, Linux, macOS o paquete multiplataforma). Versión publicada el 15-10-2026: 9.30e26. Comprueba siempre la vigente en la ficha.
- Flujo oficial:
  1. Descargar el programa desde la ficha e instalarlo, **solo desde la ficha oficial**. Instalar software en el equipo de tu usuario requiere su OK y, a menudo, su contraseña de administrador, que escribe él.
  2. Cumplimentar la declaración en el programa.
  3. Elegir «presentación telemática» y guardar el fichero **`.dec`**.
  4. El programa puede abrir la sede con el fichero ya elegido. Si no, se carga en `https://sede.gobiernodecanarias.org/tributos/jsf/seguro/presentacion/carga.jsp?modelo=420&fichero=`.
  5. Acceso con AutoFirma, firma y presentación.
  6. Pago, si sale a ingresar (ver «Pago»).
- **Preparar (sin efectos):**
  - Comprueba antes el régimen de IGIC (REPEP: no hay 420) y el plazo (`calendario-fiscal.md`).
  - Prepara las cifras desde los libros de tu usuario, con un resumen casilla a casilla para teclearlas o revisarlas en el programa.
- **El `.dec` sale del programa de ayuda.** **No generes un `.dec` a mano**: el formato no está publicado. El programa es de escritorio: lo maneja tu usuario, o tú si tienes forma de usar su escritorio.
- **Cargar, firmar y presentar** (`carga.jsp`) son los actos `presentar` + `firmar`; subir el `.dec` desde una receta (`set_input_files`) solo se permite con `presentar`.
  - **Con esos permisos** (`--permitir firmar,presentar[,pagar]`): confirma con tu usuario el resultado (a ingresar, a devolver o cero) antes de firmar, sube el `.dec`, firma con AutoFirma y presenta.
  - **Sin ellos:** dale el enlace de la ficha y el botón de cada paso.
- **Cómo verificar:** justificante de presentación y, mejor, la declaración en «Consultas > declaraciones presentadas» de la sede (ruta del mapeo; no recorrida con sesión). Antes de repetir una presentación que falló, comprueba ese listado para no duplicar.
- **No** se presenta por el Registro General Electrónico: la ATC lo tiene por no presentado.

### Modelo 425: resumen anual (actos: `firmar`, `presentar`)

- **Ficha:** `https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-425`. Carga: `https://sede.gobiernodecanarias.org/tributos/jsf/seguro/presentacion/carga.jsp?modelo=425&fichero=`.
- Mismo flujo que el 420, con su propio programa de ayuda (versión publicada el 15-10-2026: 6.31e25). **No genera pago.**
- **Lo presentan también los del REPEP**, solo con las casillas informativas.
- Prepara el resumen anual (suma de los 420 del año, si los hay). Generar el `.dec`, firmar y presentar: igual que el 420 y con los mismos permisos.

### Modelo 400: declaración censal (actos: `cambiar_datos`, `firmar`, `presentar`)

- **Ficha:** `https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-400`.
- **Es un formulario web**, no un programa de ayuda: `https://sede.gobiernodecanarias.org/tributos/ov/publico/presentacion/modelo400/formulario.jsp` (apartados, «Validar», «Presentar»).
- Cambia datos censales y regímenes (por ejemplo, el REPEP): hazlo **solo si tu usuario lo pide**.
  - Puedes abrir el formulario y explicar los apartados sin ningún permiso.
  - «Validar» y «Presentar» son `cambiar_datos` + `firmar` + `presentar`. Con esos permisos, confirma con tu usuario cada apartado y presenta; sin ellos, se los pulsa él.
- Presentarlo por el Registro General Electrónico equivale a no presentarlo.

### Pago y deudas (acto: `pagar`)

- **Acceso:** `https://sede.gobiernodecanarias.org/tributos/ov/seguro/liquidacion/sinliquidacion.jsp?permiso=true`. Solo se inventarió; no se llegó a ninguna pantalla de pago.
- Formas de pago publicadas por la ATC:
  - cargo en cuenta en el mismo acto de presentación, si la persona es cliente de una entidad adherida;
  - tarjeta de las entidades listadas;
  - pago en una entidad colaboradora, también después de presentar.
  La lista de entidades está en `https://www3.gobiernodecanarias.org/tributos/atc/entidades-colaboradoras`, publicada como imagen.
- **Domiciliación del 420:** solo hasta el día 15 del plazo (`calendario-fiscal.md`).
- Pagar es el acto `pagar`. Sin ese permiso, `sede.py` bloquea pasarelas y botones de pago y le das a tu usuario el enlace. Antes de pagar, confirma importe y cuenta salvo delegación expresa.

### Notificaciones (listar: leer · abrir: acto `comparecer`)

- **La ATC publica sus notificaciones en DEHú.** Para vigilarlas usa `tramite-vigilar-notificaciones.md` y `sede-dehu.md`.
- La sede de la ATC tiene además «Mis notificaciones», de solo consulta. Información pública: `https://sede.gobiernodecanarias.org/tributos/jsf/publico/sede/la_sede/menu_mis_notificaciones.jsp`. El listado está tras el acceso con AutoFirma: **pendiente**, no mapeado con sesión.
- Abrir una notificación cuenta como notificación practicada y **empiezan los plazos**. Es el acto `comparecer`: con permiso de tu usuario, ábrela y dile qué contiene y desde cuándo corre el plazo; sin permiso, lístala.
- Algunos sujetos están obligados a la notificación electrónica de la ATC (Orden de 27-12-2013). La lista exacta no está verificada aquí: si la persona pregunta, remítela a la página de notificaciones de la ATC.

### Otros (riesgo: leer; pendientes)

- **Declaraciones presentadas y datos censales en la ATC:** útiles para el perfil (`perfil-autonomo.md`). Están en la zona privada (AutoFirma). Con el permiso `firmar` entras tú. Sin él, alternativa: que la persona emita el certificado de «declaraciones presentadas» o «declaraciones censales» y te pase el PDF.

## Trampas

- **303 no.** En Canarias es IGIC (420/425) en la ATC. El 130, 111, 115 y la Renta siguen en la AEAT.
- **REPEP:** no presenta 420, sí presenta 425. Comprueba el régimen antes de preparar nada.
- **BLOQUEADO al pulsar Entrar** en `valida.jsp` significa que falta el permiso `firmar`: el acceso con certificado pasa por AutoFirma.
- **AutoFirma desfasada:** la página de requisitos técnicos de la ATC aloja una versión antigua (1.6.5). Instala la oficial vigente (`setup-autofirma.md`). La página de requisitos de la sede del Gobierno de Canarias pide además Java y Acrobat Reader.
- **Programas de ayuda:** cambian de versión. Descárgalos siempre desde la ficha oficial, nunca de terceros.
- **Registro General Electrónico:** no vale para 400, 420 ni 425.
- **Enlace roto en la portada de la ATC:** el botón «Acceder» del alta en notificaciones apuntaba el 14-10-2026 a una dirección de red interna, inaccesible desde fuera. Usa DEHú o la sede.
- **Deep links con `jsessionid`:** caducan. Guarda solo la ruta sin sesión.

## Fuentes

- Mapeo en vivo de tramites-es del 15-10-2026, solo lectura, sin datos personales: fichas de los modelos 400, 420 y 425, programas de ayuda, pantallas de carga, catálogo de certificados, acceso, pago y notificaciones. El acceso con certificado se detuvo en AutoFirma.
- Investigación del proyecto (R4 §3, R6 §4 y verificación cruzada V1, 15-10-2026): REPEP, ausencia de formulario web y de API para el 420/425, certificados y formas de pago.
- Fichas oficiales y BOC citados en la cabecera.
