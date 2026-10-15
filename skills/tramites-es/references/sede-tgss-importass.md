---
verificado_el: 2026-10-15
fuentes:
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Colectivos/Trabajo+Autonomo/guia
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Vida+laboral+e+informes/Informes+sobre+tu+situacion+laboral/Informe+de+tu+vida+laboral
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Consulta+de+pagos+y+deudas/ConsultaRecibos
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Consulta+de+pagos+y+deudas/CCertificado+de+estar+al+corriente+en+las+obligaciones+de+la+Seguridad+Social
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Consulta+de+pagos+y+deudas/PagosDevoluciones_/ConsultaDeudas
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Altas,+bajas+y+modificaciones/Bajas+y+modificaciones/BCRendimientos
  - https://sede.seg-social.gob.es/wps/portal/sede/sede/Ciudadanos/informes+y+certificados/01informes+y+certificados
  - https://sede.seg-social.gob.es/wps/portal/sede/sede/EmpresasyProfesionales/informes+y+certificados/01informes+y+certificados
  - https://www.seg-social.es/wps/portal/wss/internet/HerramientasWeb/51148   # notificaciones electrónicas obligatorias
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3) con certificado de persona física. Vida laboral, recibos, estar al corriente y resoluciones verificados; bases, cuotas y regularización pendientes; alta, baja y cambio de base solo hasta la entrada; notificaciones TGSS sin mapear."
---

# Seguridad Social: Import@ss y sede de la TGSS

## 1. Para qué sirve

La cotización del autónomo (RETA):
- vida laboral;
- recibos de cuota;
- certificado de estar al corriente e informes de deuda;
- bases y cuotas;
- resoluciones de alta y baja;
- regularización anual.

La sede (`sede.seg-social.gob.es`) remite casi todo lo del autónomo a **Import@ss** (`portal.seg-social.gob.es`). Todo autónomo está obligado a recibir las notificaciones de la Seguridad Social por vía electrónica desde el 1-oct-2018 (ver `tramite-vigilar-notificaciones.md`).

## 2. Acceso

- **La Seguridad Social no usa la pasarela Cl@ve para el certificado.** Tiene una pasarela SAML propia: `https://idp.seg-social.es/PGIS/Login` ("Pasarela Seguridad Social").
- **Botones de la pasarela** (DOM normal, sin shadow DOM):
  - `#IPCEIdP` "DNIe o certificado": **el único permitido**.
  - `#IPUCIdP` Cl@ve Permanente, `#CLVMOVILIdP` Cl@ve Móvil e `#IPDCIdP` Vía SMS: **prohibidos** (regla dura 3).
- **Flujo:**
  1. La URL protegida del trámite (`/wps/myportal/...` o `PortalRedirectorN1A|N1P?idApp=<n>`) redirige a la pasarela.
  2. Clic en `#IPCEIdP`.
  3. `POST https://ipce.seg-social.es/IPCE/Login` pide el certificado en el handshake.
  4. Vuelve a la URL pedida.
  - Las aplicaciones antiguas de `sp.seg-social.es/ProsaInternet` reutilizan la sesión: repiten el login solas, sin clic.
- **Origins con certificado:** solo `https://ipce.seg-social.es` (verificado con sesión). `w2.seg-social.es` lo pide en el handshake, pero no apareció en ningún trámite del autónomo: no lo añadas.
- **Qué certificado:**
  - Persona física: el suyo.
  - Sociedad: el de representante, por "Empresas y Profesionales > Informes y certificados" de la sede. Ese camino no se ha recorrido.
- **Cómo saber que entró:** vuelve a la URL protegida y la cabecera muestra el botón "Salir". `sede.py abrir` devuelve `sesion_iniciada: true`.

**Receta de login** (`login_tgss.py`; sirve para cualquier URL protegida):

```python
try:
    pg.wait_for_selector("#IPCEIdP", timeout=30000)   # pasarela PGIS
    pg.click("#IPCEIdP")
except Exception:
    log("sin pasarela: la sesión ya estaba abierta")
pg.wait_for_url(lambda u: "idp.seg-social.es" not in u and "ipce.seg-social.es" not in u, timeout=90000)
pg.wait_for_timeout(4000)
captura("tgss")
RESULTADO = {"url": pg.url.split("?")[0], "titulo": pg.title(),
             "texto": redactar(" ".join(pg.inner_text("body").split()))[:3000]}
```

```bash
uv run scripts/sede.py ejecutar login_tgss.py --sede tgss --url "<URL protegida>" --titular yo
```

**Límite diario:** la TGSS rechaza a partir de unos 3 informes por titular y día. Es una observación del historial y de un proyecto de terceros, no una cifra oficial. Emite **un solo documento por trámite y día** y guarda el PDF en vez de volver a pedirlo.

## 3. Trámites

Las URL que empiezan por `/wps/` cuelgan de `https://portal.seg-social.gob.es`.

### 3.1 Vida laboral (`tgss-vida-laboral`) · Leer · verificado

- **URL:** `/wps/myportal/importass/importass/tramites/datosvidalaboral`, con la receta de login.
- **Qué muestra:** el listado de situaciones en pantalla, con filtro `#control-1` y paginación "Siguiente".
- **Descarga:** botón "Descargar vida laboral" (`#boton-sticky`). Llega como evento `download` de un PDF servido desde `blob:`.
- **Éxito:** el PDF descargado. Pásalo por `scripts/justificante.py`.
- **Dónde para:** "Informar error" es un trámite aparte y lo hace la persona.

### 3.2 Recibos de autónomo (`tgss-recibos-reta`) · Leer · verificado

- **URL:** `/wps/myportal/importass/importass/tramites/historialRecibosRETA`.
- **Éxito:** "Tu historial de recibos", agrupado por año y mes, con conceptos "Cuota autónomos".

### 3.3 Certificado de estar al corriente (`tgss-certificado-corriente`) · Preparar · verificado

Ver `tramite-certificado-corriente.md`.

- **URL:** `/wps/portal/importass/Seguridad/PortalRedirectorN1A?idApp=2265&N1&A`. Lleva a `sp.seg-social.es/ProsaInternet/OnlineAccess` sin clic.
- **Tipos** (radios `certificado_1..9`):
  - Genérico, Licitación, Subvenciones, Artículo 42;
  - Sin deuda a una fecha (y sus variantes de Licitación y Subvenciones);
  - Deuda total, Detalle de deuda.
- **Paso siguiente:** "Continuar" (`#ENVIO_13`) emite el certificado **sin firma**. Sale la pantalla "Información" con "Imprimir" (`#ENVIO_10`), que genera el PDF.
- **Dónde para el agente:** en la elección del tipo. Pulsa "Continuar" solo con el OK explícito de la persona para ese tipo concreto, porque cuenta en el límite diario. Si no, lo hace ella.

### 3.4 Certificados ya emitidos (`tgss-certificados-emitidos`) · Leer · pendiente

- **URL:** `/wps/portal/importass/Seguridad/PortalRedirectorN1A?idApp=2266&N1&A` ("Consultar documentos").
- No recorrido con certificado.

### 3.5 Deudas (`tgss-deudas`) · Leer · parcial

- **URL:** `/wps/portal/importass/Seguridad/PortalRedirectorN1A?idApp=370&N1&A`.
- **Qué es:** la pantalla "AESD - Obtención del documento de ingreso", con tres opciones de búsqueda (CCC/NAF y régimen; nº de referencia; NAF y régimen). No es un listado de deuda, sino el camino a un **documento de pago**.
- **Dónde para:** en esa pantalla. "Continuar" no se pulsó en el mapeo.
- **Para saber cuánto se debe:** el informe "Deuda total" o "Detalle de deuda" del 3.3 (cuenta como informe del día). **No hay consulta de deuda de solo lectura sin generar documento:** ni AESD ni "Tu historial de recibos" (§3.2, que solo lista recibos emitidos, sin estado de pago) dicen si hay deuda.
- **Qué decirle a la persona si no da su OK para el informe:** "En Hacienda no tienes deudas (consultado hoy). En la Seguridad Social veo tus recibos emitidos hasta `<mes>`, pero la TGSS no muestra si hay deuda sin generar un informe. ¿Quieres que pida el informe 'Deuda total' (cuenta como 1 de los ~3 informes del día) o lo pides tú en `<enlace §3.3>` → 'Deuda total' → 'Continuar'?"
- **"Continuar" en AESD:** no se sabe si solo lista o si genera un documento de ingreso. Hasta mapearlo, trátalo como de la persona.
- **Nunca:** "Pago con tarjeta de deudas".

### 3.6 Bases, cuotas y regularización · Leer · pendiente (no recorridos con certificado)

- `tgss-bases-cotizacion`: `/wps/myportal/importass/importass/tramites/informebases` ("Consultar bases").
- `tgss-cuotas-ingresadas`: `/wps/portal/importass/Seguridad/PortalRedirectorN1P?idApp=110&N1&P`.
- `tgss-datos-cotizacion-reta`: `/wps/portal/importass/Seguridad/PortalRedirectorN1P?idApp=762&N1&P`.
- `tgss-regularizacion-reta`: `/wps/myportal/importass/importass/tramites/detalleResultadoRegularizacionAutonomos`.

### 3.7 Resoluciones de alta, baja y modificaciones (`tgss-resoluciones-reta`) · Leer · verificado

- **URL:** `/wps/myportal/importass/importass/tramites/busquedaDocumentos/` ("Archivo de documentos").
- **Pasos:** campo `#BUSQUEDA` y botón `#accionBuscar`. El botón útil es "Consultar documentos", no "Realizar trámite".

### 3.8 Cambio de base y rendimientos previstos (`tgss-cambio-base`) · Persona · solo entrada

- **URL:** `/wps/myportal/importass/importass/tramites/relacionLaboralRETA` ("Relación laboral trabajador autónomo").
- **Qué muestra:** datos del RETA, regularización del año, situación actual y domiciliación.
  - Se puede leer y pulsar "Consultar detalle" y "Descargar resolución".
- **Dónde para:** antes de "Modificar". Ni ese botón ni ningún modal (`#modalModCuota` y `ACC_MOD_CUOTA_COTIZACION`) los toca el agente.
- **La persona:** cambia la base en esa pantalla, con el botón "Modificar".
  - Hay hasta 6 cambios al año, con efectos el 1 de marzo, mayo, julio, septiembre, noviembre y enero (guía TGSS, en Fuentes).
  - Si exige firma o no, **no está verificado**.

### 3.9 Alta en el RETA (`tgss-alta-reta`) · Persona · parcial

- **URL:** `/wps/myportal/importass/importass/tramites/altaAutonomo` ("Alta en trabajo autónomo / Iniciar alta").
- **Dónde para:** antes de "Aceptar y continuar", que inicia el asistente. Lo pulsa la persona.

### 3.10 Baja en el RETA (`tgss-baja-reta`) · Persona · solo entrada

- **URL buena:** `/tramites/relacionLaboralRETA`. La de la tarjeta pública (`relacionLaboralRETAPublica`) da "errorAcceso" con sesión.
- **Dónde está la baja:** es un modal oculto (`#modal-baja-autonomo`, acción `ACC_INICIO_BAJA`), con avisos previos.
- En la misma pantalla están cancelar alta o baja, renovación y renuncia de tarifa (`ACC_*`). **Ninguno lo toca el agente.**

### 3.11 Aplazamiento de deudas (`tgss-aplazamiento`) · Persona · pendiente

- **URL:** `/wps/portal/importass/Seguridad/PortalRedirectorN1P?idApp=2806&N1&P` ("Aplazar pago"). Lo solicita la persona.

### 3.12 Notificaciones de la Seguridad Social (`tgss-notificaciones`) · Leer · pendiente

- **No mapeado.** La ficha de la sede "Notificaciones telemáticas" (`https://sede.seg-social.gob.es/wps/portal/sede/sede/Inicio/NotificacionesTelematicas`) viene de la investigación previa y no se ha recorrido.
- Explora solo con `sede.py probe` y la receta de login, sin `--clic` sobre ninguna notificación. Ver `tramite-vigilar-notificaciones.md`.

## 4. Trampas y problemas conocidos

- **Pagos:** "Pago con tarjeta de deudas" y cualquier "Continuar" hacia un documento de ingreso son de la persona.
- **Modales de acción** en "Relación laboral" (baja, cancelaciones, renovación, renuncia, cambio de base): prohibidos para el agente.
- **Tarjetas de Import@ss:**
  - Las que tienen `accionBoton='window'` abren una ventana nueva (popup).
  - Algunas muestran antes un popup `#form-atria`, cuya opción por defecto es la buena: "Tengo Cl@ve Permanente, Cl@ve Móvil, DNIe, Certificado Electrónico o Vía SMS". Entrar por la URL protegida evita ese popup.
- **Apoderados:** los botones `#boton-lanzamiento-operacion-apoderado` (`seleccionPoderdante`) solo sirven si se actúa como apoderado.
- **Banner de cookies:** pulsa "Rechazar todas".
- **Sin certificado:** la vida laboral y las bases se pueden pedir por correo postal (`/tramites/enviovidalaboraldomicilio`, `/tramites/informebasesdomicilio`). Es una solicitud: la hace la persona.
- **`tls-probe`:** `ipce` da 403 sin certificado, y Akamai está delante. Ritmo humano, sin ráfagas.
- **El NIF sale con prefijo** en AESD (`6-0X…` para NIE, `1-0…` para DNI). El `redactar()` de la v0.1 no lo enmascara: revisa a mano antes de compartir.

## 5. Fuentes

- Fichas y tarjetas oficiales de Import@ss y de la sede: ver la cabecera.
- Mapeo en vivo del 15-10-2026 con certificado de persona física. Se generaron 2 documentos (vida laboral y estar al corriente); nada se firmó, se modificó ni se pagó.
