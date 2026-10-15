---
verificado_el: 2026-10-15
estado_mapeo: parcial   # Arico: acceso con certificado y «Registros presentados» verificados; Adeje: acceso con certificado sin completar
fuentes:
  - https://ayuntamientodearico.sedelectronica.es/info.0
  - https://adeje.sedelectronica.es/info.0
  - https://adeje.sedelectronica.es/signature-systems
  - https://www.espublicogestiona.com
---

# Receta Gestiona (esPublico): sedes `*.sedelectronica.es`

## Para qué sirve

Gestiona es la plataforma de sede electrónica municipal más extendida de España. La investigación del proyecto estima **unos 4.300 ayuntamientos** (horquilla 3.700-4.800, más de la mitad), sobre todo pequeños y medianos. Es una estimación, no un censo: el censo de `assets/municipios.csv` aún no ha sondeado la mayoría de municipios.

Una misma receta sirve para todos: cambian el dominio y algunos identificadores de trámite. Con ella el agente puede:
- **leer** los registros presentados, los expedientes y el **listado** de notificaciones;
- localizar la ficha de un trámite (instancia general, actividad, licencias) y prepararlo;
- con los permisos de su usuario, hacer los **actos**: iniciar, firmar y presentar (`presentar`, `firmar`) o abrir notificaciones (`comparecer`).

**Los tributos casi nunca están en Gestiona.** Suelen estar en una diputación, un consorcio o una oficina tributaria aparte (por ejemplo, Adeje usa GTT: `plataforma-gtt.md`). En Canarias, mira `canarias-recaudacion.md`.

**Cómo reconocerla:**
- dominio `<tenant>.sedelectronica.es` (también `.sedelectronica.gal`, `*.eadministracio.cat` y `*.egoitzaelektronikoa.eus`), o un dominio propio que redirige a `/info.0`;
- si el tenant no existe, la página dice «Sede Electrónica Indeterminada»: el DNS responde a cualquier subdominio.

## Parámetros y rutas

```text
ORIGIN = https://<tenant>.sedelectronica.es     (cambia por ayuntamiento)
UUID   = identificador estable de un procedimiento

Portada:         {ORIGIN}/info.0
Catálogo:        {ORIGIN}/dossier
Ficha:           {ORIGIN}/catalog/t/{UUID}          pública
Tramitación:     {ORIGIN}/catalog/tw/{UUID}         acto `presentar`: inicia el trámite y puede crear un borrador
Registros:       {ORIGIN}/registro                  registros presentados (listado)
Expedientes:     {ORIGIN}/expedientes
Notificaciones:  {ORIGIN}/enotifications            listar; abrir = acto `comparecer`
Borradores:      {ORIGIN}/solicitudes-en-borrador   listar; crear o seguir uno = acto `presentar`
Identificación:  {ORIGIN}/id-systems                informativa
Firma:           {ORIGIN}/signature-systems         informativa
Validar CSV:     {ORIGIN}/document-validation
```

## Acceso

| Dato | Valor |
|---|---|
| Login | `{ORIGIN}/info.0` → **Identifícate** → **Acceso con sistema Cl@ve** → **DNIe / Certificado electrónico** |
| Origins | `{ORIGIN}`, `https://pasarela.clave.gob.es`, `https://pasarela-ident.clave.gob.es` |
| Certificado por TLS | No en el tenant ni en `pasarela.clave.gob.es`. Lo pide `pasarela-ident.clave.gob.es` por ruta (`sede-clave.md`) |
| `sede.py` | `--sede arico`, `--sede adeje`, o `--url {ORIGIN}/info.0` con los origins de arriba |

- **No hay una URL de login estable** (`/auth` no existe). El enlace **Identifícate** es un *callback* de Apache Wicket (`?x=…`) que caduca: hay que pulsarlo por su texto, no guardarlo.
- En Cataluña Gestiona ofrece además VÀLid/idCAT: no mapeado aquí.
- En la pasarela Cl@ve usa **solo** «DNIe / Certificado electrónico» («Fuera del alcance» en `SKILL.md`). Un GET directo a `pasarela.clave.gob.es/Proxy2/ServiceProvider` da error porque falta el POST SAML: no significa que la sede esté caída.
- **Cómo saber que entró:** la cabecera muestra el área autenticada y la opción **Desconectar** (verificado en Arico). `sede.py abrir` lo marca como `sesion_iniciada: true`.

Cada llamada a `sede.py` abre un navegador nuevo: el login y la consulta deben ir en **una sola receta**. Ejemplo para listar los registros presentados. Los pasos están verificados en Arico el 15-10-2026; la receta en sí no se ha ejecutado tal cual.

```python
# gestiona_registros.py — solo lectura
ORIGIN = re.match(r"https://[^/]+", pg.url).group(0)
for texto in ("Identifícate", "Acceso con sistema Cl@ve"):
    pg.get_by_text(texto, exact=False).first.click(timeout=20000)
    pg.wait_for_timeout(4000)
# En la pasarela Cl@ve, solo la rama de certificado (como en sede-clave.md):
pg.wait_for_selector("button.idp-button", timeout=60000)
pg.click("button.idp-button:has-text('DNIe / Certificado')")
pg.wait_for_url(lambda u: "clave.gob.es" not in u, timeout=90000)
pg.wait_for_timeout(4000)
nav(ORIGIN + "/registro")
captura("registro")
RESULTADO = {"url": pg.url.split("?")[0], "titulo": pg.title(), "probe": probe(pg)}
```

```bash
uv run scripts/sede.py ejecutar gestiona_registros.py --sede arico --titular <ALIAS>
```

El resultado incluye textos de la página, que pueden llevar datos de la persona: no los copies fuera de la conversación y enmascáralos en los informes («Datos personales enmascarados» en `SKILL.md`). Para notificaciones, cambia `/registro` por `/enotifications`: listar no tiene efectos; abrir es el acto `comparecer`, y sin ese permiso `sede.py` lo bloquea.

## Trámites

| Trámite | URL | Riesgo o acto | Notas |
|---|---|---|---|
| Registros presentados | `{ORIGIN}/registro` | leer | Descarga justificantes solo si tu usuario lo pide |
| Expedientes | `{ORIGIN}/expedientes` | leer | No verificado con sesión |
| Notificaciones | `{ORIGIN}/enotifications` | listar: leer; abrir: `comparecer` | Abrir hace correr los plazos |
| Instancia general | `{ORIGIN}/catalog/t/5161fa8d-970e-4b48-a506-b2ac34ceafe5` | `firmar`, `presentar` | Sin permiso, para en la ficha |
| Actividad (comunicación previa, licencia) | `{ORIGIN}/catalog/t/<UUID del tenant>` | `firmar`, `presentar` | Sin permiso, para en la ficha |

- **Instancia general:** el mismo UUID funcionó en Arico y en Adeje. Puede ser común a muchos tenants, pero **compruébalo** en cada sede: si da error, búscala en `/dossier`.
- **Trámites de actividad:** el UUID es propio de cada ayuntamiento. En Arico, la categoría «Actividad Económica» no mostró una licencia o declaración de apertura. Sí había una comunicación urbanística, que no es el mismo trámite. Ejemplos de Adeje en `assets/sedes.yaml`.
- **Presentar:** «Iniciar tramitación electrónica» en la ficha, rellenar, adjuntar, firmar y presentar.
  - Prepara antes el texto (expone, solicita) y la lista de documentos, y confírmalos con tu usuario.
  - **Con los permisos `firmar` y `presentar`** (`sede.py --permitir firmar,presentar`), hazlo tú. **Pendiente de verificar en vivo** de punta a punta.
  - **Sin ellos**, dale a tu usuario el texto, los documentos y el enlace a la ficha.
- **Firma:** según `{ORIGIN}/signature-systems` (Adeje), Gestiona admite certificado y, en trámites de bajo riesgo, firma «no criptográfica» (art. 10.2.c de la Ley 39/2015). Las dos son firma a nombre de tu usuario: acto `firmar`.
- **Cómo verificar una presentación:** que aparezca la entrada nueva en `{ORIGIN}/registro`, con su número y fecha. El acuse a veces solo llega por correo. Antes de reintentar un envío fallido, comprueba ese listado para no duplicar.

## Cómo adaptarla a tu ayuntamiento

1. **Localiza la sede:**
   ```bash
   uv run scripts/buscar.py --municipio "Nombre del municipio"
   ```
   Mira `sede_url` y `plataforma`. El censo puede no tener sondeado el municipio («Sin identificar» o `sede_url` vacía). Entonces abre la web municipal (`web`) y busca el enlace a «Sede electrónica».
2. **Saca el ORIGIN** de `sede_url`:
   - si es `https://<tenant>.sedelectronica.es/…`, el ORIGIN es `https://<tenant>.sedelectronica.es`;
   - si es un dominio propio, ábrelo sin certificado y mira a qué host redirige `/info.0`:
     ```bash
     uv run scripts/sede.py abrir --url "https://<dominio-de-la-sede>/"
     ```
   - el tenant **no siempre es el nombre del municipio**: Arico es `ayuntamientodearico`, Valverde es `aytovalverde`, La Matanza es `matanceros`.
3. **Comprueba que existe:** si la página dice «Sede Electrónica Indeterminada», el tenant no es ese.
4. **UUID de un trámite:** abre `{ORIGIN}/dossier` (o busca en la portada), entra en la ficha y toma el UUID de `/catalog/t/<UUID>`. **No guardes enlaces `?x=`**, que caducan.
5. **Origins para `sede.py`:** el ORIGIN del tenant más las dos pasarelas Cl@ve. Si el ayuntamiento no está en `assets/sedes.yaml`, pasa `--url` y avisa a la persona antes de usar el certificado si el dominio no está en `assets/dominios-oficiales.yaml` ni en el censo («Solo sedes oficiales» en `SKILL.md`).
6. **Tributos:** busca el recaudador del municipio (diputación, consorcio u oficina tributaria). Gestiona no los suele llevar.

## Trampas

- **Enlaces `?x=…`:** caducan con la sesión. Usa solo las rutas de la tabla y los UUID.
- **`/catalog/tw/{UUID}` inicia la tramitación** y puede crear un borrador: acto `presentar`. Sin ese permiso, `sede.py` lo bloquea. Ábrelo solo cuando vayas a presentar de verdad, para no dejar borradores sueltos.
- **Buzón `/enotifications`:** `sede.py` lo trata como página de notificaciones (abrir = `comparecer`).
- **Bucle `ERR_TOO_MANY_REDIRECTS`:** en Adeje apareció tras volver de Cl@ve con certificado. Con una sesión anónima limpia, la portada carga bien. No insistas: cierra, vuelve a empezar una vez y, si se repite, que entre la persona.
- **Sin cookies hay bucle:** `curl` o WebFetch entran en bucle de redirecciones en la portada. Hace falta un navegador.
- **Todo se pinta con JavaScript/AJAX:** espera a que cargue antes de concluir que algo no está.
- **reCAPTCHA:** algunos tenants lo activan (6 de 299 portadas sondeadas). Si aparece, lo resuelve la persona y tú sigues («Fuera del alcance» en `SKILL.md`).
- No se vieron iframes, *shadow DOM* ni WAF en los flujos públicos.

## Instalaciones verificadas

| Ayuntamiento | ORIGIN | Estado el 15-10-2026 |
|---|---|---|
| Villa de Arico | `https://ayuntamientodearico.sedelectronica.es` | Acceso con certificado vía Cl@ve y «Registros presentados» verificados |
| Adeje | `https://adeje.sedelectronica.es` | Fichas públicas verificadas; acceso con certificado no completado (bucle de redirecciones) |

## Fuentes

- Mapeo en vivo de tramites-es del 15-10-2026 en Arico y Adeje, sin datos personales. No se abrieron tramitaciones, borradores ni notificaciones.
- Investigación del proyecto (R1 §3.1, 15-10-2026): huella, cobertura estimada, rutas y firma. Muestra de 389 tenants por huella.
- Pasarela Cl@ve: ver `sede-clave.md`.
