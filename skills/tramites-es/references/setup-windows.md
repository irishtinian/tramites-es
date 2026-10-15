---
verificado_el: 2026-10-15
fuentes:
  - https://docs.astral.sh/uv/getting-started/installation/     # instalar uv (winget e instalador oficial)
  - https://docs.astral.sh/uv/guides/install-python/            # uv descarga Python si hace falta
  - https://www.python.org/downloads/
  - https://www.google.com/chrome/
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/obtener-certificado-software
  - https://www.sede.fnmt.gob.es/preguntas-frecuentes/exp-imp-y-elim-de-certificados   # exportar/importar en Windows
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar
  - https://learn.microsoft.com/powershell/module/pki/export-pfxcertificate             # -CryptoAlgorithmOption AES256_SHA256
---

# Preparar Windows para tramites-es

Guía para que **el agente acompañe a una persona no técnica**, paso a paso, en Windows 10 u 11.

## Antes de empezar (para el agente)

- Un paso cada vez. Frases cortas. Espera a que la persona diga "hecho" o te cuente qué ve.
- **Tú no tocas el certificado ni su contraseña.** No pidas el `.pfx`, no lo leas, no lo copies, no pidas la contraseña. Los pasos marcados con 🔑 los hace la persona en **su** terminal y tú solo le das el comando para copiar.
- No ejecutes tú comandos que listen el almacén de certificados: muestran nombre y NIF.
- Si la persona pega su contraseña en el chat: dile que no lo repita y que exporte de nuevo con **otra** contraseña (paso 3) y vuelva a configurar (paso 5).
- Al final, comprueba con `uv run scripts/entorno.py` (paso 6).

## 1. Abrir una terminal

1. Pulsa la tecla **Windows**, escribe `Terminal` (o `PowerShell`) y pulsa **Intro**.
2. Los comandos de esta guía son para **PowerShell**. Para pegar: clic derecho o `Ctrl+V`.
3. Importante: los pasos 🔑 se hacen en **esta ventana**, fuera del chat del agente. Si se lanzan desde el agente, `cert.py` se niega a propósito.

## 2. Instalar uv y Google Chrome

**uv** (recomendado) instala Python y las dependencias por ti.

1. Escribe:
   ```powershell
   winget install --id=astral-sh.uv -e
   ```
   Si `winget` no existe, usa el instalador oficial de uv:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
2. **Cierra la terminal y abre otra** (para que Windows encuentre `uv`).
3. Comprueba: `uv --version`. Debe salir un número de versión.
4. No hace falta instalar Python aparte: uv descarga uno si falta. Las dependencias (Playwright, etc.) vienen declaradas en cada script y `uv run` las instala la primera vez. Esa primera vez tarda un poco.

**Google Chrome** (obligatorio; no vale Edge ni Chromium):

1. `winget install -e --id Google.Chrome`, o descárgalo de https://www.google.com/chrome/.
2. No hace falta `playwright install`: el skill usa el Google Chrome instalado.

**Sin uv (alternativa).** Instala Python 3.11 o superior desde https://www.python.org/downloads/ y sigue su asistente (si te ofrece añadir Python al PATH, márcalo). Ojo: si al escribir `python` se abre la Microsoft Store, es un acceso directo vacío de Windows; usa `py`. Instala las dependencias con las versiones que figuran en la cabecera `# /// script` de los scripts, por ejemplo:
```powershell
py -m pip install --user playwright==1.58.0 pyyaml==6.0.3 cryptography==44.0.2 keyring==25.6.0
```
y en esta guía cambia `uv run` por `py`.

## 3. Conseguir el certificado como fichero `.pfx` / `.p12`

El skill necesita el certificado **con su clave privada** en un fichero `.pfx` o `.p12`. Hay tres casos:

- **A. Ya tienes el fichero.** Por ejemplo, la copia de seguridad que la FNMT recomienda hacer al descargar el certificado. Ve a "Dónde guardarlo". Si el fichero es antiguo o te lo dio una gestoría, haz también el paso 4.
- **B. Está instalado en Windows** (lo usas en el navegador). Expórtalo (abajo).
- **C. No tienes certificado.** Solicítalo en la FNMT (u otro emisor). La FNMT pide: configuración previa, solicitud por internet, acreditar tu identidad y descarga. Ver https://www.sede.fnmt.gob.es/certificados/persona-fisica/obtener-certificado-software. Al descargarlo, haz la copia de seguridad que te propone.

### Dónde guardarlo

1. Crea una carpeta privada:
   ```powershell
   New-Item -ItemType Directory -Force "$env:APPDATA\tramites-es"
   ```
2. Guarda ahí el fichero, por ejemplo como `yo.pfx`. Para abrir esa carpeta en el Explorador: `explorer "$env:APPDATA\tramites-es"`.
3. **Seguridad:**
   - No lo dejes en el Escritorio, en Descargas ni en Documentos (OneDrive puede subirlos a la nube).
   - No lo envíes por WhatsApp, Telegram, email ni lo subas a ningún chat (tampoco al del agente).
   - Quien tenga el fichero y la contraseña puede actuar como tú ante la Administración.

### B. Exportarlo desde Windows (asistente) 🔑

1. Pulsa `Windows + R`, escribe `certmgr.msc` y pulsa **Aceptar**.
   También se llega desde Chrome: Configuración → Privacidad y seguridad → Seguridad → Gestionar certificados.
2. Abre **Personal → Certificados**. Busca el tuyo (columna "Emitido por", por ejemplo una autoridad de la FNMT).
3. Doble clic en él. Debe decir **"Tiene una clave privada correspondiente a este certificado"**. Si no lo dice, no sirve.
4. Clic derecho → **Todas las tareas → Exportar...**
5. Elige **"Exportar la clave privada"**. Si esa opción sale en gris, mira "Si no deja exportar" más abajo.
6. Formato: **Intercambio de información personal: PKCS #12 (.PFX)**. Marca "Incluir todos los certificados en la ruta de acceso de certificación (si es posible)". **No** marques "Eliminar la clave privada si la exportación es correcta".
7. Marca **Contraseña** y escribe una contraseña larga. En **Cifrado**, elige **AES256-SHA256** (no TripleDES-SHA1). Así evitas el problema del paso 4.
8. Nombre de archivo: guárdalo en la carpeta privada, por ejemplo `yo.pfx`. Pulsa **Finalizar**.

Los textos exactos pueden variar un poco según la versión de Windows.

**Alternativa en PowerShell** (también 🔑; pide la contraseña sin mostrarla):
```powershell
Get-ChildItem Cert:\CurrentUser\My | Where-Object HasPrivateKey | Format-List Subject, NotAfter, Thumbprint
$huella = "<pega aquí el Thumbprint de tu certificado>"
$pw = Read-Host "Contraseña para el fichero" -AsSecureString
Export-PfxCertificate -Cert "Cert:\CurrentUser\My\$huella" -FilePath "$env:APPDATA\tramites-es\yo.pfx" -Password $pw -CryptoAlgorithmOption AES256_SHA256
```
La primera línea muestra tu nombre y NIF: no la pegues en el chat.

### Si no deja exportar la clave privada

La clave se instaló como **no exportable** y Windows no la deja salir. Opciones:

1. Busca la copia de seguridad que hiciste al descargar el certificado.
2. Si no la tienes, pide un certificado nuevo (o renuévalo, ver paso 7) y esta vez guarda la copia.

## 4. Ficheros antiguos (cifrado RC2 o 3DES)

Algunos `.pfx` antiguos, de gestorías o exportados con "TripleDES-SHA1" usan un cifrado que Playwright (OpenSSL 3) ya no lee.

**Síntoma:** `cert.py configurar` dice `"ok": true`, pero al abrir una sede el agente ve un error con `Unsupported PKCS12 PFX data` o `unsupported`.

**Solución en Windows, sin instalar nada** 🔑:

1. Doble clic en el `.pfx` → **Usuario actual** → Siguiente → escribe su contraseña.
2. Marca **"Marcar esta clave como exportable"**. Deja que elija el almacén automáticamente → Finalizar.
3. Expórtalo otra vez como en el paso 3B, **eligiendo AES256-SHA256**, con otro nombre (por ejemplo `yo-aes.pfx`).
4. Vuelve a configurar (paso 5) con el fichero nuevo. Cuando todo funcione, borra el fichero antiguo.

Ventaja extra: el certificado queda instalado en Windows, que es lo que necesita AutoFirma (`setup-autofirma.md`).

Si tienes `openssl` (por ejemplo, el que trae Git para Windows), puedes comprobar el cifrado con los comandos de `setup-linux.md`, paso 4.

## 5. Configurar el certificado en tramites-es 🔑

Lo hace **la persona**, en su terminal. El agente le dice cuál es la carpeta del skill (la que contiene `SKILL.md`).

1. Entra en la carpeta del skill:
   ```powershell
   cd "<carpeta del skill>"
   ```
2. Ejecuta:
   ```powershell
   uv run scripts/cert.py configurar --alias yo --p12 "$env:APPDATA\tramites-es\yo.pfx"
   ```
3. Escribe la contraseña del fichero. **No se ve nada al escribir: es normal.** Pulsa Intro.
4. La contraseña se guarda en el **Administrador de credenciales de Windows** (entrada `tramites-es`). No queda en ningún fichero ni en el historial.
5. Sale un resultado con `"ok": true`, el tipo de certificado, la caducidad y el NIF enmascarado. Ese resultado **sí** se puede pegar al agente: no tiene secretos.

Notas:
- **No muevas ni renombres el `.pfx`** después: `cert.py` guarda su ruta. Si lo mueves, repite este paso.
- ¿Certificado de representante de una sociedad? Configúralo con otro alias, por ejemplo `--alias empresa`.
- Para quitarlo: `uv run scripts/cert.py olvidar --alias yo`.

## 6. Comprobar que todo está listo

1. Ejecuta (esto ya lo puede hacer el agente):
   ```powershell
   uv run scripts/entorno.py
   ```
2. Debe salir `"ok": true`. Si no, la lista `pasos` dice qué falta.
3. AutoFirma no es obligatorio: solo hace falta para que **tú** firmes en algunas sedes (`setup-autofirma.md`).
4. Para revisar un certificado concreto: `uv run scripts/cert.py comprobar --alias yo`.

## 7. Problemas típicos

**`uv` no se reconoce como comando.** Cierra la terminal y abre otra. Si sigue, repite la instalación del paso 2.

**Al escribir `python` se abre la Microsoft Store.** Es el acceso directo de Windows. Usa `uv run` (o `py`).

**`entorno.py` dice que falta Chrome** o Chrome no abre. Instala **Google Chrome** (paso 2). El skill lo busca en Archivos de programa y en tu carpeta de usuario (`AppData\Local`).

**En la ventana del agente aparece "Seleccionar un certificado".** **No elijas nada:** pulsa Cancelar y avisa al agente. Suele ser una web que no está en la lista de dominios del skill o un dominio que falta.

**Certificado caducado o a punto de caducar.** `entorno.py` muestra `CADUCADO` o `caduca en menos de 30 días`.
- La FNMT deja renovar por internet durante los **60 días previos** a la caducidad, con condiciones (https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar). Si ya caducó, hay que pedir uno nuevo.
- Con el certificado nuevo: expórtalo (paso 3) y repite el paso 5 con el **mismo alias** (se sobrescribe).

**"No se ha enviado/seleccionado ningún certificado"**, error 4002 de Cl@ve o una página de error de la sede justo al entrar con certificado. Casi siempre falta un *origin*: la sede saltó a un subdominio que no recibe el certificado.
- El agente revisa `hosts_con_error` y `url_final` en la salida de `sede.py`.
- Si el dominio es oficial, propón añadirlo a `assets/sedes.yaml` y abrir un issue "sede rota". Si no es oficial, para y pregunta.
- En Windows, `sede.py cert-probe` no detecta bien si una ruta pide certificado (lo avisa en su salida).

**Antivirus.** Algunos antivirus con "análisis de HTTPS" o "de conexiones cifradas" interfieren con el certificado de cliente: la sede falla solo en la ventana del agente. Prueba a excluir las sedes oficiales de ese análisis (consulta la ayuda de tu antivirus). No desactives el antivirus entero. Si bloquea `uv` o Playwright, compruébalo antes: permítelo solo si lo instalaste desde la web oficial.
