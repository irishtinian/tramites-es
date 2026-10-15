---
verificado_el: 2026-10-15
estado_mapeo: parcial   # Adeje: acceso con certificado y recibos privados verificados; el resto de entidades, solo por huella pública
fuentes:
  - https://adeje.tributoslocales.es/380015/AADEJE/
  - https://soria.tributoslocales.es/425000/DSORIA
  - https://laspalmasgc.tributoslocales.es/350163/APALMASGC
  - https://aytoburgos.tributoslocales.es/090591/ABURGOS
---

# Receta GTT: oficinas virtuales tributarias `*.tributoslocales.es`

## Para qué sirve

Muchas oficinas virtuales de **tributos locales** (de ayuntamientos y de servicios de recaudación de diputaciones y cabildos) usan la misma aplicación web de la empresa GTT. La investigación del proyecto contó unas 18 instalaciones. Entre ellas:
- diputaciones de Ávila, León, Palencia, Soria, Valladolid, Segovia, Ciudad Real y Guadalajara;
- ayuntamientos como Almería, Burgos, León, Segovia, Palma, Lleida, Tarragona y Girona;
- en Canarias, **Adeje**, **Arucas** y **Las Palmas de Gran Canaria**, y la Red Tributaria de Lanzarote (con otra versión de la aplicación).

Con ella el agente puede:
- **leer** los recibos pendientes, próximos y pagados y las solicitudes presentadas;
- con los permisos de su usuario, hacer los **actos**: pagar (`pagar`), domiciliar (`cambiar_datos`) o pedir un certificado (`generar`). Sin ellos, explicarle cómo hacerlo.

No es la sede del ayuntamiento: es su oficina tributaria. La instancia general y las licencias suelen estar en otra plataforma (`plataforma-gestiona.md`, `plataforma-tao-sta.md`…).

**Cómo reconocerla:** título «Oficina Virtual Tributaria», aplicación de una sola página (Nuxt) con clases CSS `gtt-*`, y rutas `/<CODIGO>/<SERVICIO>/…`.

## Parámetros y rutas

```text
ORIGIN   = https://<entidad>.tributoslocales.es    (o un dominio propio de la entidad)
CODIGO   = código de la entidad (6 cifras)
SERVICIO = identificador de la entidad en mayúsculas

Portada:       {ORIGIN}/{CODIGO}/{SERVICIO}/
Certificado:   https://certifica.gtt.es/OficinaVirtual/oficina.asp?servicio={SERVICIO}&entidad={CODIGO}
```

- En los ayuntamientos, `CODIGO` es el código INE del municipio más su dígito de control, y `SERVICIO` es «A» + nombre: Adeje es `380015/AADEJE`; Las Palmas de GC, `350163/APALMASGC`. Las diputaciones usan «D» + nombre (Soria, `425000/DSORIA`). Es un patrón observado: compruébalo siempre en la URL real.
- En Adeje, el par de la portada y el del botón de certificado coinciden (`380015` / `AADEJE`).
- **Variantes:**
  - instalaciones catalanas con prefijo de idioma: `{ORIGIN}/ct/{CODIGO}/{SERVICIO}`;
  - versión anterior con `…/ovt/EXP?/{CODIGO}/{SERVICIO}/homenoauth/pag3` (Red Tributaria de Lanzarote, Lugo). Esta versión **no está mapeada**.

Rutas funcionales de la portada (Adeje, verificadas sin certificado). Pueden variar por entidad:

| Ruta | Qué es | Riesgo o acto |
|---|---|---|
| `{ORIGIN}/{CODIGO}/{SERVICIO}/consultar-recibo` | Detalle de un recibo domiciliado | leer |
| `…/csv` | Verificar un documento por CSV | leer (puede tener CAPTCHA) |
| `…/calendario-fiscal` | Calendario de cobros | leer |
| `…/plusvalia` | Plusvalía | `presentar` si presenta |
| `…/pagar`, `…/tasas`, `…/obtener-documento` | Pagar impuestos y tasas u obtener el documento de pago | `pagar` |
| `…/recibos/pendientes` | **Recibos privados** (pendientes, próximos y pagados) | leer, con sesión |

Con sesión aparecen además, según la entidad: domiciliaciones, fraccionamientos y plan personalizado de pago, bienes, solicitudes presentadas y aportación de documentos, notificaciones, apoderamientos y «Obtener certificado» (de no deuda). Sin sesión salen como «Opción bloqueada. Inicia sesión…».

## Acceso

| Dato | Valor |
|---|---|
| Botón | Portada → **Certificado digital** |
| Login | `https://certifica.gtt.es/OficinaVirtual/oficina.asp?servicio={SERVICIO}&entidad={CODIGO}` |
| Certificado por TLS | **Sí, por ruta** en `certifica.gtt.es/OficinaVirtual/oficina.asp` (`cert-probe`). No en el *handshake* ni en `{ORIGIN}` |
| Origins | `{ORIGIN}`, `https://certifica.gtt.es` |
| `sede.py` | `--sede adeje-tributos` |

- Otras entidades ofrecen DNIe y Cl@ve en el modal «Identifícate». La rama Cl@ve **no está mapeada**: si la usas, solo «DNIe / Certificado electrónico» (`sede-clave.md`). Algunas ofrecen NIF + contraseña («clave segura de usuario»): **nunca** la uses en nombre de la persona.
- **Dominio del proveedor:** `certifica.gtt.es` y `*.tributoslocales.es` son de la empresa que presta el servicio, no de la Administración. Úsalos solo cuando los enlace la web oficial de la entidad (ayuntamiento, diputación o cabildo). Si no estás seguro, pregunta a la persona («Solo sedes oficiales» en `SKILL.md`).
- **Cómo saber que entró:** saludo autenticado en la portada y opciones antes bloqueadas ya disponibles (verificado en Adeje; la identidad no se copió).

La aplicación **tarda unos 12 segundos en cargar** (antes solo hay un spinner). `sede.py abrir` espera menos: usa una receta. Ejemplo de solo lectura para Adeje. El acceso y el listado están verificados el 15-10-2026; la receta en sí no se ha ejecutado tal cual.

```python
# gtt_recibos.py — solo lectura. Cambia BASE por {ORIGIN}/{CODIGO}/{SERVICIO}/ de tu entidad.
BASE = "https://adeje.tributoslocales.es/380015/AADEJE/"
pg.wait_for_timeout(12000)
nav(BASE + "recibos/pendientes", espera=15000)
captura("recibos")
RESULTADO = {"url": pg.url.split("?")[0], "titulo": pg.title(), "probe": probe(pg)}
```

```bash
uv run scripts/sede.py ejecutar gtt_recibos.py --sede adeje-tributos --titular <ALIAS>
```

La salida y las capturas locales pueden contener importes y referencias de la persona: no los copies fuera de la conversación y enmascara en los informes («Datos personales enmascarados» en `SKILL.md`).

## Trámites

- **Recibos privados** (riesgo: leer).
  - Lista pendientes, próximos y pagados y avisa de plazos.
  - Verificar un pago: el recibo pasa a «pagados».
- **Solicitudes presentadas** (riesgo: leer). Opción «Solicitudes y seguimiento». **No mapeada con sesión.**
- **Pagar u obtener documento de pago** (acto `pagar`).
  - Con el permiso: confirma con tu usuario recibo, importe y medio de pago, y paga (`sede.py --permitir pagar`).
  - Sin él: `sede.py` bloquea abrir `…/pagar`. Explica dónde está y qué datos pide, y dale el enlace.
  - Verificar: justificante y estado «pagado».
- **Domiciliación** (acto `cambiar_datos`). Lleva el IBAN: confirma con tu usuario la cuenta exacta y no la copies a ningún otro sitio.
- **Certificado de no deuda** (acto `generar`). Solo en algunas entidades; **no mapeado**.
- **Alta en notificaciones** (acto `cambiar_datos`). Aparece como invitación en la portada, con datos de contacto y aceptación de condiciones. Acéptala solo si tu usuario quiere recibir ahí las notificaciones: desde entonces le llegarán por esa vía.

## Cómo adaptarla a tu ayuntamiento

1. **¿Quién cobra tus tributos?** Puede ser el ayuntamiento o su diputación, consorcio o cabildo.
   ```bash
   uv run scripts/buscar.py --municipio "Nombre del municipio"
   ```
   El censo puede no traer el recaudador. En Canarias, usa `canarias-recaudacion.md`. En el resto, busca en la web municipal el enlace «Tributos», «Oficina virtual tributaria» o «Pago de recibos».
2. **Saca el ORIGIN, el CODIGO y el SERVICIO** de la URL a la que lleva ese enlace: `https://<host>/<CODIGO>/<SERVICIO>/`. Ábrela sin certificado para confirmarlo:
   ```bash
   uv run scripts/sede.py abrir --url "https://<host>/<CODIGO>/<SERVICIO>/"
   ```
   Si solo ves un spinner, es la carga lenta. Reintenta con una receta que espere 12-15 segundos.
3. **Login:** sustituye el par en `certifica.gtt.es/OficinaVirtual/oficina.asp?servicio=<SERVICIO>&entidad=<CODIGO>`. Comprueba en la portada que el botón «Certificado digital» lleva a esa URL.
4. **Origins:** `https://<host>` y `https://certifica.gtt.es`. Si la entidad no está en `assets/sedes.yaml`, confirma con la persona que el enlace sale de la web oficial antes de usar el certificado.
5. **Menú:** cambia según la entidad. Usa `sede.py probe` para ver qué opciones tiene.

## Trampas

- **Carga lenta:** no concluyas que la página está vacía mientras haya spinner. `curl` y WebFetch solo ven el título.
- **Banner de cookies** modal que tapa los botones: elige **Rechazar** (o la opción más restrictiva) antes de seguir.
- **Invitación a notificaciones** en la portada: acto `cambiar_datos` (ver «Trámites»). Si solo estás consultando, ciérrala sin aceptar.
- **CAPTCHA de imagen** en la verificación por CSV y en el formulario de contacto (visto en el código, no en pantalla). Si aparece, lo resuelve la persona y tú sigues.
- **Pagos públicos:** algunas entidades piden el NIF del titular y una referencia del recibo. Úsalos solo con los datos de la propia persona.
- **Versión antigua** (`…/homenoauth/pag3`): otra interfaz, sin receta.

## Fuentes

- Mapeo en vivo de tramites-es del 15-10-2026 en la oficina virtual tributaria de Adeje: portada y rutas públicas sin certificado, acceso con certificado y listado de recibos privados. Sin copiar importes ni referencias; sin pagos, domiciliaciones ni aceptación de condiciones.
- Investigación del proyecto (R2 §2.2, §5 y §6, 14-15/10/2026): huella, patrón de URL e instalaciones por GET público.
