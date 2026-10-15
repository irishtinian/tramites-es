---
verificado_el: 2026-10-15
fuentes:
  - https://sede.mjusticia.gob.es/es/tramites/certificado-antecedentes
  - https://sede.mjusticia.gob.es/es/tramites/certificado-registro-central
  - https://sede.mjusticia.gob.es/documents/d/guest/solicitud-de-certificado-de-delitos-de-naturaleza-sexual-para-personas-fisicas
  - https://carpeta.justicia.es/group/guest/home
estado_mapeo: "Mapeo en vivo 15-10-2026 con certificado de persona física. Antecedentes penales hasta el paso 1; delitos sexuales: la URL de entrada emite el certificado al abrirla (trampa documentada); Carpeta Justicia en bucle de login (fallo de Justicia)."
---

# Ministerio de Justicia: antecedentes penales, delitos sexuales y Carpeta Justicia

## 1. Para qué sirve

Al autónomo le sirve para pedir dos certificados que exigen contratos, licencias o trabajos con menores:
- el de **antecedentes penales**;
- el del **Registro Central de Delincuentes Sexuales**.

Carpeta Justicia (expedientes judiciales) existe, pero hoy no deja entrar con certificado (ver 3.4).

**Riesgo general: Persona.** Estos certificados los pide y los descarga la persona. El agente informa, prepara los datos y comprueba el estado.

## 2. Acceso

- **Pasarela:** todas las entradas acaban en Cl@ve, opción "DNIe / Certificado" (`sede-clave.md`).
  - `certape` y `redese` hacen `302 → /…/clave/actions/enviarPeticion`, un GET que solo genera la petición SAML y la envía sola a Cl@ve.
- **Origins con certificado:** solo `https://pasarela-ident.clave.gob.es`. Ni `sede.mjusticia.gob.es`, ni `carpeta.justicia.es`, ni `am.justicia.es` piden certificado (verificado con sesión).
- **Qué certificado:** el de la persona física; son certificados personales.
- **Cómo saber que entró:** la página de la aplicación muestra el enlace "Salir" (`/certape/clave/actions/LogoutInit` o `/redese/clave/actions/LogoutInit`).
- **Entrar** (abre el paso 1 de antecedentes, que no envía nada):

```bash
uv run scripts/sede.py ejecutar clave_login.py --sede justicia --titular yo
```

## 3. Trámites

### 3.1 Certificado de antecedentes penales (`justicia-antecedentes-penales`) · Persona · parcial

- **URL:** `https://sede.mjusticia.gob.es/certape/clave/InicioSede?lang=es_es&idtramite=1288778883620&idpagina=1215197884559`.
  - Variante de inhabilitación: añadir `esInhabilitacion=true`.
- **Asistente:** dos pasos, "Datos" y "Confirmar". El paso "Datos" tiene estas secciones:
  - datos personales;
  - contacto: teléfono **obligatorio**, con prefijo de país (`#inputTelefono_2`), y email opcional;
  - **pago (NRC)**;
  - finalidad (`select#cboFinalidad`: Trabajo, Licencia, Concurso público, Interés particular…);
  - apostilla y la casilla "reflejar país y finalidad".
- **Qué hace el agente:** entra, lee el formulario con `probe` y prepara con la persona la finalidad y si necesita apostilla.
- **Dónde para:** antes de "Siguiente" (`#btnSubmit`). No se pulsó en el mapeo.
- **La persona:** rellena el teléfono y el pago, si se lo piden, pulsa **"Siguiente"** y luego confirma.
- **Éxito:** consulta el estado y descarga en `https://sede.mjusticia.gob.es/certape/clave/FormularioConsulta?lang=es_es&idtramite=1288778883620&idpagina=1215197884559` (`justicia-antecedentes-consulta`, **pendiente**: no recorrido). El certificado lleva CSV.

### 3.2 Certificado de delitos de naturaleza sexual (`justicia-delitos-sexuales`) · Persona

> ⚠️ **TRAMPA (comprobada el 15-10-2026): abrir la URL de entrada con sesión EMITE el certificado.**
>
> - **Cómo funciona:**
>   - `https://sede.mjusticia.gob.es/redese/clave/solicitarCertificado?…` es el enlace "Acceder" de la ficha oficial.
>   - Si se abre con sesión iniciada, la sede responde directamente "Solicitud procesada con éxito. El certificado se ha generado correctamente", con los botones "Descargar certificado" (`#butDescargarCertificado`) y "Apostillar".
>   - No hay formulario ni confirmación: **el GET es la solicitud**, y queda registrada a nombre del titular.
> - **Regla:** el agente **nunca** abre `/redese/clave/solicitarCertificado` ni `/redese/clave/solicitarCertificadoMenores`.
>   - `sede.py` las bloquea: corta cualquier navegación cuya URL contenga `solicitar`, `emitir`, `expedir`, `generar`… y la registra como "URL que ejecuta una acción al abrirla".
>   - Si ves ese bloqueo, **no lo esquives**.
> - **Lo emite la persona.**

- **Qué hace el agente:**
  - Explica qué es el certificado y para qué lo piden.
  - Le da el enlace a la ficha: `https://sede.mjusticia.gob.es/es/tramites/certificado-registro-central`.
  - Le advierte de que, nada más pulsar "Acceder" e identificarse, el certificado se genera sin más pasos.
- **La persona:** desde la ficha pulsa "Acceder", entra con su certificado y pulsa **"Descargar certificado"**. "Apostillar" solo si lo necesita para el extranjero.
- **Éxito:** el texto "Solicitud procesada con éxito" y un PDF con CSV. Pásalo por `scripts/justificante.py`.
- **Consulta posterior:** `https://sede.mjusticia.gob.es/redese/clave/FormularioConsulta?lang=es_es&idtramite=1288778560459&idpagina=1215197884559` (`justicia-delitos-sexuales-consulta`, **pendiente**: no recorrido; no lo abras sin comprobar antes con `probe` que no emite nada).

### 3.3 Verificar un certificado por CSV · Persona

- **URL:** `https://sede.mjusticia.gob.es/sedecsvbroker/FormularioVerificacion.action?lang=es_es&idtramite=1288778883620&idpagina=1215197884559`.
- Según la investigación previa, tiene **reCAPTCHA**. Lo hace la persona (regla dura 4).

### 3.4 Carpeta Justicia (`justicia-carpeta`) · Leer · pendiente (no disponible)

- **URL:** `https://carpeta.justicia.es/group/guest/home`.

> **Fallo abierto: bucle de login, causado por un fallo de Justicia.**
>
> - **El ciclo:**
>   1. Cl@ve autentica.
>   2. La respuesta SAML llega a `am.justicia.es/selfservice-ext/saml2/sp/login/clave` por un POST entre sitios. Llega **sin la cookie `SESSION`**, porque esa cookie es `Domain=justicia.es; SameSite=Lax` y el navegador no la manda en un POST entre sitios.
>   3. `am` emite el token y redirige a `/group/guest/home`.
>   4. `/idp/login` → `/selfservice-ext/login` vacía el token y relanza el SAML.
>   5. Cl@ve reautentica por SSO, sin clic, y el ciclo vuelve a empezar (3 vueltas o más).
> - **Descartado:** no es un problema de origins ni de certificado. No hay errores TLS.
> - **No tiene arreglo seguro desde el cliente:** tocar cookies está prohibido.
> - **Qué hacer:**
>   1. Para tras la segunda vuelta.
>   2. Dile a la persona que es un fallo de la sede.
>   3. Puede probar ella en su navegador o volver más adelante.

- **Ruta equivocada:** si caes en una pantalla de usuario y contraseña (`JUxxxxxx` / `MJUxxxxxx`) en `/selfservice-ext/login`, es el **acceso del personal de Justicia**. Vuelve a entrar por `/group/guest/home`.

## 4. Trampas y problemas conocidos

- **URLs que ejecutan al abrirse:** `solicitarCertificado` y `solicitarCertificadoMenores` (3.2). Antes de abrir una URL de Justicia que no esté en esta guía, haz `probe` sin sesión o pregunta.
- **"¿Cómo va lo mío?"** (`https://sede.mjusticia.gob.es/tramites/como`): tiene reCAPTCHA y no hay vía con certificado. Lo hace la persona.
- **"Ingresos CDCJ"** (`/pasarela-de-pago-cdcj`), junto al acceso a Carpeta Justicia: es un pago. No lo toques.
- **Sin certificado** existen el formulario en papel `790` y la verificación por CSV. Las dos las hace la persona.
- **"Redirigiendo al proveedor de identidades…":** a veces se queda ahí. Espera y, si no avanza, para.
- **`sede.justicia.gob.es`** no resuelve en DNS: el host bueno es `sede.mjusticia.gob.es`.

## 5. Fuentes

- Fichas oficiales del Ministerio de Justicia y guía de delitos sexuales: ver la cabecera.
- Mapeo en vivo del 15-10-2026 con certificado de persona física: comportamiento de la URL de solicitud y causa del bucle documentados sin datos personales.
