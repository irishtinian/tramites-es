---
verificado_el: 2026-10-15
fuentes:
  - https://sede.dgt.gob.es/es/mi_dgt/
  - https://sede.dgt.gob.es/es/permisos-de-conducir/permiso-por-puntos/consulta-de-puntos/
  - https://sede.dgt.gob.es/es/permisos-de-conducir/informe-de-conductor/
  - https://sede.dgt.gob.es/es/multas/
  - https://sede.dgt.gob.es/es/multas/direccion-electronica-vial/
  - https://sede.dgt.gob.es/es/multas/consulta-del-tablon-edictal-de-sanciones/
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3) con certificado de persona física. MiDGT, puntos y mis sanciones verificados; DEV verificado solo hasta el acceso (el listado requiere una cuenta con DEV, pendiente); informe de conductor hasta la primera pantalla."
---

# DGT: sede, MiDGT y buzón DEV

## 1. Para qué sirve

- Puntos del carné.
- Multas y sanciones: consulta, nunca pago.
- Buzón de notificaciones de tráfico (DEV, Dirección Electrónica Vial).
- Informe de conductor.
- Vehículos a nombre de la persona.

Para un autónomo con vehículo de trabajo, sobre todo sirve para **vigilar multas y notificaciones de la DEV**.

## 2. Acceso

La DGT tiene **dos maneras de identificarse**:

1. **MiDGT y `sedeclave.dgt.gob.es` usan Cl@ve.**
   - Sin sesión responden `401` con la página "Redirigiendo a Cl@ve para la autenticación".
   - Esa página envía sola un SAML a `pasarela.clave.gob.es`. Después: "DNIe / Certificado" (`sede-clave.md`).
2. **El buzón DEV usa certificado directo.** `https://auth-sedeweb.dgt.gob.es/...` exige mTLS: sin certificado, el handshake se aborta.

- **Origins con certificado** (verificados con sesión):
  - `https://pasarela-ident.clave.gob.es`, para MiDGT;
  - `https://auth-sedeweb.dgt.gob.es`, para la DEV.
  - `sede`, `sedeclave`, `sedeweb` y `sedeapl` no piden certificado.
- **Entrar:**

```bash
uv run scripts/sede.py ejecutar clave_login.py --sede dgt --titular yo   # login = https://sede.dgt.gob.es/es/mi_dgt/
```

- **Cómo saber que entró:** URL `/es/mi_dgt/`, el nombre del titular en la cabecera y el botón "Salir" (`#logout_btn`).
- **Qué certificado:** el de la persona física. "Mis representados" y "Mis representantes" existen, pero no se recorrieron.

## 3. Trámites

Cada ejecución de `sede.py` empieza sin sesión: las recetas hacen primero el paso de Cl@ve y después `nav("<url>")` a cada subpágina, en la misma ejecución. Comando: `uv run scripts/sede.py ejecutar <receta.py> --sede dgt --titular yo`.

### 3.1 Puntos (`dgt-puntos`) · Leer · verificado

- **URL:** `https://sede.dgt.gob.es/es/mi_dgt/mis-puntos/`.
- **Éxito:** bloque "MIS PUNTOS" con el saldo.
- **Otras subpáginas de solo lectura:** `mis-permisos/`, `mis-vehiculos/index.html`, `mis-registros/`, `mis-edictos/`.
- **No es del agente:** `mis-suscripciones/` ("Editar" = cambio de datos).

### 3.2 Multas y sanciones (`dgt-multas`) · Leer · verificado (listado)

- **URL:** `https://sede.dgt.gob.es/es/mi_dgt/mis-sanciones/`.

```python
# dgt_sanciones.py: login por Cl@ve y listado
pg.wait_for_selector("button.idp-button", timeout=60000)
pg.click("button.idp-button:has-text('DNIe / Certificado')")
pg.wait_for_url(re.compile(r"sede\.dgt\.gob\.es/es/mi_dgt/"), timeout=90000)
nav("https://sede.dgt.gob.es/es/mi_dgt/mis-sanciones/")
pg.wait_for_selector("#datatable_sanciones", timeout=60000)
captura("sanciones")
RESULTADO = {"texto": redactar(" ".join(pg.inner_text("body").split()))[:4000]}
```

- **Qué muestra:** la tabla `#datatable_sanciones`.
  - Columnas: número de expediente, estado (p. ej. "TERMINADO POR PAGO"), fecha de la denuncia, provincia, importe y acciones.
  - Los expedientes cerrados van aparte, en el bloque "TERMINADAS".
  - Paginación: 10/25/50/100, más Anterior/Siguiente.
- **Dónde para:** en la tabla. El detalle (`/es/mi_dgt/mis-sanciones/detalle-sancion/?…`) no se abrió en el mapeo.
- **La persona:** pagar ("Paga tu multa", `/es/multas/pago-de-multas/`) y presentar alegación o recurso los hace ella.
  - `sedeclave.dgt.gob.es/WEB_IWPS5_INET/jsp/concertificado/buscarSanciones.jspx` es la **entrada del pago**: solo mirar.
- **Éxito:** el texto "Mostrando X a Y de Z registros". Los números de expediente son datos personales: redáctalos si compartes algo.

### 3.3 Buzón DEV, solo listado (`dgt-dev-notificaciones`) · Leer · parcial

Procedimiento de vigilancia y plazos: `tramite-vigilar-notificaciones.md`.

- **URL con certificado:** `https://auth-sedeweb.dgt.gob.es/WEB_NTRA_CONSULTA/listadoNotificacionesIdiomaPostback.faces?idioma=es`.

```bash
uv run scripts/sede.py abrir --sede dgt --url "https://auth-sedeweb.dgt.gob.es/WEB_NTRA_CONSULTA/listadoNotificacionesIdiomaPostback.faces?idioma=es" --titular yo
```

- **Posibles resultados:**
  - El listado, que **no se ha visto en vivo**: falta verificarlo con una cuenta que tenga DEV.
  - `/WEB_NTRA_CONSULTA/ErrorBuzon.faces`, con el texto "Es necesario disponer de una Dirección Electrónica Vial…". **Es un estado válido:** la persona no tiene DEV. Dilo así; no lo trates como un error técnico. La investigación previa da la DEV por voluntaria para la persona física, pero no está verificado en fuente primaria.
- **Dónde para:** en el listado. Abrir una notificación = notificado.
  - `sede.py` trata la página como de notificaciones (la URL contiene "Notificaciones") y bloquea acceder, abrir, descargar y ver el detalle.
- **La persona:** abre ella la notificación desde el buzón cuando decida.
  - Darse de alta o de baja en la DEV (`WEB_NTRA_CONSULTA-suscripcion`) es un cambio de datos: también lo hace ella.
- **Representantes:** `https://auth-sedeweb.dgt.gob.es/WEB_NTRA_CONSULTA/accesoRepresentantesIdiomaPostback.faces?idioma=es` (no recorrido).

### 3.4 Informe de conductor (`dgt-informe-conductor`) · Preparar · parcial

- **URL:** `https://sedeclave.dgt.gob.es/WEB_HPER/HPER` (datos actuales) o `https://sedeclave.dgt.gob.es/WEB_HPER/HPRO` (últimos 10 años). Entra por Cl@ve; con sesión de MiDGT en la misma ejecución, sin clic.
- **Primera pantalla:** fecha de nacimiento en tres campos (`form1:diaNacimiento`, `form1:mesNacimiento` y `form1:anoNacimiento`) y los botones "Confirmar" y "Limpiar".
- **Dónde para el agente:** antes de "Confirmar". Ese botón llama a `enviar()` y `sede.py` lo bloquea.
- **La persona:** abre el enlace, pone su fecha de nacimiento y pulsa **"Confirmar"**. Según la ficha, sale una pantalla con la descarga del informe en PDF; no se ha verificado.

### 3.5 Tablón Edictal de sanciones (`dgt-tablon-edictal`) · Leer · verificado sin certificado

- **Ficha pública:** `https://sede.dgt.gob.es/es/multas/consulta-del-tablon-edictal-de-sanciones/`. Sirve para multas que no se pudieron notificar.

## 4. Trampas y problemas conocidos

- **Enlaces con rodeo:** los de la sede pasan por stubs `/.galleries/enlaces/...`, que hacen `302` y luego un *meta refresh* a la aplicación real. Espera a la URL final.
- **"El servicio no está disponible"** en un paso de confirmación: no reintentes a ciegas y comprueba que no quedó nada a medias.
- **Selects de localidad en cascada con autocompletado:** pueden elegir otra localidad del mismo municipio. Revisa el valor efectivo.
- **Enlace interno roto:** la página de sanciones contiene uno a un host de preproducción (`consolasedepro01.trafico.es:8080`). Ignóralo: no es un dominio oficial de la lista.
- **Widget de chat:** `chats.dgt.es` da error de certificado del servidor. No afecta.
- **Cita previa:** usa reCAPTCHA y está fuera de alcance (regla dura 4).

## 5. Fuentes

- Fichas oficiales de la DGT: ver la cabecera.
- Mapeo en vivo del 15-10-2026 con certificado de persona física: no se abrió ningún detalle ni notificación, y no se generó ningún informe.
