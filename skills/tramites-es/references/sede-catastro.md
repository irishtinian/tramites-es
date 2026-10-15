---
verificado_el: 2026-10-15
fuentes:
  - https://www.sedecatastro.gob.es/Accesos/SECAccInmuebles.aspx
  - https://www.sedecatastro.gob.es/Accesos/SECAccExpedientes.aspx
  - https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCBusqueda.aspx
  - https://www1.sedecatastro.gob.es/DocumentosCatalogo/SECValidarCSV.aspx
  - https://www.sedecatastro.gob.es/ValidacionesGraficas/SECValidarGC.aspx
  - https://www.catastro.hacienda.gob.es/ayuda/Guia_Certificacion_Catastral_Descriptiva_Grafica.pdf
estado_mapeo: "Mapeo en vivo 15-10-2026 (fases 1 y 2 y ronda 3) con certificado de persona física. Acceso con certificado y 'accesos a mis inmuebles' verificados; certificación por titular hasta el formulario (no generada)."
---

# Sede Electrónica del Catastro

## 1. Para qué sirve

- Saber qué inmuebles tiene la persona a su nombre.
- Obtener la **certificación catastral** (descriptiva y gráfica), que piden licencias de actividad, alquileres de local o ayudas.
- Ver quién ha consultado o certificado sus inmuebles.
- Consultar datos no protegidos de cualquier finca.

## 2. Acceso

- **Pantalla de elección** (`SECAccDNI.aspx?Dest=<n>`):
  - "Certificado digital: CERES, DNIe, otros." → `SECAccTitular.aspx?Dest=<n>&del=&mun=&final=&RefC=`. Es **mTLS directo, sin Cl@ve**: el que usa el agente.
  - "Cl@ve: PIN24, Cl@ve permanente,…" → `SECAccPIN.aspx`, que lleva a la pasarela Cl@ve. No hace falta.
- **Origin con certificado:** `https://www.sedecatastro.gob.es`, pero **solo en algunas rutas** (`/Accesos/SECAccTitular.aspx` y `/Accesos/SECAccUsuRegCer.aspx`).
  - Lo pide por renegociación, no en el handshake: `tls-probe` dice "no" y `cert-probe` dice "sí".
  - `www1.sedecatastro.gob.es` (buscador, cartografía, cotejo) no lo pide.
- **Entrar:**

```bash
uv run scripts/sede.py abrir --sede catastro --titular yo
# login = https://www.sedecatastro.gob.es/Accesos/SECAccTitular.aspx?Dest=17&del=&mun=&final=&RefC=
```

- **Cómo saber que entró:**
  - Llega a `/CYCBienInmueble/SECGestionCertificados.aspx`.
  - La cabecera muestra `<NIF> - <TITULAR>`: redáctala.
  - Sin certificado sale el aviso "Es necesario un certificado Clase 2 CA para acceder a este servicio" y vuelve a `OVCInicio.aspx`. `sede.py` cancela el aviso: trátalo como "no hay certificado".
- **Qué certificado:** el del titular de los inmuebles (persona física o representante de la sociedad).

## 3. Trámites

### 3.1 Accesos a la información de mis inmuebles (`catastro-accesos-inmuebles`) · Leer · verificado

- **URL:** la de login (`Dest=17`). Lleva a `/CYCBienInmueble/SECGestionCertificados.aspx`, "Accesos a información de inmuebles de un titular".
- **Ojo:** **no es la certificación.** Es el registro de quién ha consultado o certificado tus inmuebles.
  - Tiene un campo "Referencia Catastral" (`ctl00_Contenido_txtRC`) y un botón "Aceptar".
- **Éxito:** título y cabecera con la identidad del titular.

### 3.2 Certificación catastral por titular (`catastro-certificacion-titular`) · Preparar · parcial

- **Ruta:** Inicio > Mis inmuebles > Consulta y certificación de datos catastrales > Búsqueda por NIF/NIE.
  - Con la sesión del paso 3.1, va a `https://www.sedecatastro.gob.es/CYCBienInmueble/OVCBusquedaTitular.aspx` ("Consulta/Certificación de Bienes Inmuebles por Titular").
- **Formulario** (visto con `probe`, no rellenado en el mapeo):
  - **Finalidad**: `ctl00_Contenido_txtFinalidad`, texto libre. Queda registrada en el acceso.
  - Comunidad autónoma, provincia y municipio en cascada (`ddlCCAA` → `ddlProv` → `ddlMun`). Cada select recarga la página (postback ASP.NET): espera a que se rellene el siguiente.
  - Tipo de bien (`TipoBien`): Todos, Urbanos, Rústicos o Especiales.
  - Botones: **DATOS** (`#ctl00_Contenido_btnAceptar`) y **CARTOGRAFÍA** (`#ctl00_Contenido_btnNuevaCartografia`).

```python
# catastro_form.py: solo inventario del formulario, sin rellenar ni pulsar nada
nav("https://www.sedecatastro.gob.es/CYCBienInmueble/OVCBusquedaTitular.aspx")
captura("form-certificacion")
RESULTADO = {"probe": probe(pg)}
```

```bash
uv run scripts/sede.py ejecutar catastro_form.py --sede catastro --titular yo   # entra por Dest=17 y luego va al formulario
```

- **Pasos:** acuerda con tu usuario la finalidad exacta y el ámbito (comunidad, provincia, municipio, tipo de bien), y rellena el formulario.
- **DATOS** genera el listado y la certificación y deja registrado el acceso con la finalidad declarada: es el acto `generar`.
  - Púlsalo solo con ese permiso y la finalidad confirmada. Ojo: `sede.py` **no** lo bloquea (el botón no casa con sus patrones), así que el permiso lo compruebas tú.
  - Como no se pulsó en el mapeo, la salida está **sin verificar**.
- **Salida esperada** (según la guía oficial de la certificación catastral):
  - PDF sellado con un **CSV de 16 caracteres** en el margen y código de barras.
  - Contiene referencia catastral, datos, valores y titulares.
- **Éxito:**
  - El PDF, pasado por `scripts/justificante.py`.
  - Cotejo, sin identificarse, en `https://www1.sedecatastro.gob.es/DocumentosCatalogo/SECValidarCSV.aspx`.
  - El acceso nuevo aparece en 3.1.

### 3.3 Consulta pública de datos no protegidos (`catastro-consulta-publica`) · Leer · verificado sin certificado

- **URL:** `https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCBusqueda.aspx`. Por referencia catastral o por localización, sin titulares ni valores.

### 3.4 Mis expedientes (`catastro-expedientes`) · Leer · pendiente

- **URL:** `https://www.sedecatastro.gob.es/Accesos/SECAccExpedientes.aspx`. Por CSV sin certificado, o con certificado ("Ver todos los expedientes en los que usted ha actuado…").
- **No es del agente:** "Presentación de documentación" y "Requerimientos y alegaciones" los hace la persona.

### 3.5 Valor de referencia (`catastro-valor-referencia`) · Leer · pendiente

- **URL:** `https://www1.sedecatastro.gob.es/Accesos/SECAccvr.aspx`. No recorrido con certificado.

## 4. Trampas y problemas conocidos

- **`Dest=17`** es "accesos a mis inmuebles", **no** la certificación (3.1 frente a 3.2).
- **`Dest=<n>`** indica el servicio de destino tras autenticarse. Solo se ha verificado el 17.
- **Datos personales en URLs:** "Búsqueda por localización" lleva `?Titu=<NIF>`. Redáctalas siempre.
- **Diálogo nativo de Chrome:** si el origin con certificado no está declarado, Chrome puede abrir su selector y la página se cuelga (pasó en el mapeo). Usa siempre `--sede catastro`.
- **Firma:** las declaraciones y la presentación de documentación llevan firma ("icono firma" en el catálogo de trámites). Fuera de alcance: las hace la persona.
- **Banner de cookies:** pulsa "Denegar".
- **WAF:** hay un F5 delante. Navega a ritmo humano.

## 5. Fuentes

- Sede del Catastro, cotejo por CSV y guía oficial de la certificación catastral: ver la cabecera.
- Mapeo en vivo del 15-10-2026 con certificado de persona física: no se generó ninguna certificación.
