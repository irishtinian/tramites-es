---
verificado_el: 2026-10-15
fuentes:
  - https://docs.astral.sh/uv/getting-started/installation/     # instalar uv (instalador oficial y Homebrew)
  - https://docs.astral.sh/uv/guides/install-python/            # uv descarga Python si hace falta
  - https://www.python.org/downloads/
  - https://www.google.com/chrome/
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/obtener-certificado-software
  - https://www.sede.fnmt.gob.es/preguntas-frecuentes/exp-imp-y-elim-de-certificados   # exportar desde el Llavero de Mac
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar
---

# Preparar macOS para tramites-es

Guía para que **el agente acompañe a una persona no técnica**, paso a paso, en un Mac.

## Antes de empezar (para el agente)

- Un paso cada vez. Frases cortas. Espera a que la persona diga "hecho" o te cuente qué ve.
- **Tú no tocas el certificado ni su contraseña.** No pidas el `.p12`, no lo leas, no lo copies, no pidas la contraseña. Los pasos marcados con 🔑 los hace la persona en **su** terminal y tú solo le das el comando para copiar.
- Si la persona pega su contraseña en el chat: dile que no lo repita y que exporte de nuevo con **otra** contraseña (paso 3) y vuelva a configurar (paso 5).
- Al final, comprueba con `uv run scripts/entorno.py` (paso 6).

## 1. Abrir el Terminal

1. Pulsa `Cmd + Espacio`, escribe `Terminal` y pulsa **Intro**.
2. Para pegar un comando: `Cmd + V`, y luego **Intro**.
3. Importante: los pasos 🔑 se hacen en **esta ventana**, fuera del chat del agente. Si se lanzan desde el agente, `cert.py` se niega a propósito.

## 2. Instalar uv y Google Chrome

**uv** (recomendado) instala Python y las dependencias por ti.

1. Instalador oficial de uv:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Si ya usas Homebrew, también vale `brew install uv`.
2. **Cierra el Terminal y abre otro** (para que encuentre `uv`).
3. Comprueba: `uv --version`. Debe salir un número de versión.
4. No hace falta instalar Python aparte: uv descarga uno si falta. Las dependencias (Playwright, etc.) vienen declaradas en cada script y `uv run` las instala la primera vez. Esa primera vez tarda un poco.

**Google Chrome** (obligatorio; no vale Safari ni Chromium):

1. Descárgalo de https://www.google.com/chrome/.
2. Abre el `.dmg` y arrastra Chrome a la carpeta **Aplicaciones**. Tiene que quedar en `/Applications/Google Chrome.app`: ahí lo busca el skill.
3. No hace falta `playwright install`: el skill usa el Google Chrome instalado.

**Sin uv (alternativa).** Instala Python 3.11 o superior desde https://www.python.org/downloads/. Ojo: el `python3` que trae el Mac puede pedirte instalar las herramientas de desarrollo de Apple. Crea un entorno propio e instala las dependencias con las versiones de la cabecera `# /// script` de los scripts:
```sh
python3 -m venv ~/.venv-tramites
~/.venv-tramites/bin/pip install playwright==1.58.0 pyyaml==6.0.3 cryptography==44.0.2 keyring==25.6.0
```
En esta guía, cambia `uv run` por `~/.venv-tramites/bin/python`.

## 3. Conseguir el certificado como fichero `.p12`

El skill necesita el certificado **con su clave privada** en un fichero `.p12` (o `.pfx`). Hay tres casos:

- **A. Ya tienes el fichero.** Por ejemplo, la copia de seguridad que la FNMT recomienda hacer al descargar el certificado. Ve a "Dónde guardarlo" y luego al paso 4.
- **B. Está en el Llavero** (lo usas en Safari o Chrome). Expórtalo (abajo).
- **C. No tienes certificado.** Solicítalo en la FNMT (u otro emisor). La FNMT pide: configuración previa, solicitud por internet, acreditar tu identidad y descarga. Ver https://www.sede.fnmt.gob.es/certificados/persona-fisica/obtener-certificado-software. Al descargarlo, haz la copia de seguridad que te propone.

### Dónde guardarlo

1. Crea una carpeta privada:
   ```sh
   mkdir -p "$HOME/Library/Application Support/tramites-es"
   chmod 700 "$HOME/Library/Application Support/tramites-es"
   ```
2. Guarda ahí el fichero, por ejemplo como `yo.p12`. En cualquier ventana de "Guardar" o del Finder, pulsa `Cmd + Mayús + G` y pega `~/Library/Application Support/tramites-es` para llegar a esa carpeta.
3. **Seguridad:**
   - No lo dejes en el Escritorio, en Descargas ni en Documentos (iCloud puede subirlos a la nube).
   - No lo envíes por WhatsApp, Telegram, email ni lo subas a ningún chat (tampoco al del agente).
   - Quien tenga el fichero y la contraseña puede actuar como tú ante la Administración.

### B. Exportarlo desde el Llavero 🔑

1. Abre **Acceso a Llaveros**: `Cmd + Espacio` y escribe "Acceso a Llaveros". En versiones antiguas también está en Aplicaciones → Utilidades.
2. En el llavero **inicio de sesión**, pulsa **Mis certificados**.
3. Busca el tuyo. Al desplegarlo (triángulo) debe verse una **llave** debajo: es la clave privada. Si no hay llave, no sirve.
4. Selecciónalo y elige **Archivo → Exportar ítems...**
5. Formato: **Intercambio de información personal (.p12)**. Guárdalo en la carpeta privada como `yo.p12`.
6. Escribe una contraseña larga para el fichero y confírmala.
7. macOS te pedirá la contraseña de tu usuario del Mac para permitir la exportación. Es normal.

Los textos exactos pueden variar según la versión de macOS.

## 4. Ficheros antiguos (cifrado RC2 o 3DES)

Algunos `.p12` (antiguos, de gestorías o exportados desde el Llavero) usan un cifrado que Playwright (OpenSSL 3) ya no lee. **Compruébalo siempre en Mac.**

**Síntoma si no lo compruebas:** `cert.py configurar` dice `"ok": true`, pero al abrir una sede el agente ve un error con `Unsupported PKCS12 PFX data` o `unsupported`.

**Comprobar** 🔑 (pide la contraseña sin mostrarla; no la escribas en el comando):
```sh
cd "$HOME/Library/Application Support/tramites-es"
openssl pkcs12 -info -noout -in yo.p12
```
- Si ves `AES-256-CBC` en las líneas de "Encrypted data" y "Keybag": está bien. Ve al paso 5.
- Si ves `RC2`, `TripleDES` o un error con `unsupported`: es antiguo. Conviértelo (abajo).

**Convertir a AES** 🔑. Primero mira qué `openssl` tienes: `openssl version`.
- Si dice **LibreSSL** (lo normal en Mac), usa los comandos tal cual.
- Si dice **OpenSSL 3**, añade `-legacy` justo después de `openssl pkcs12` en la **primera** línea de `openssl`.

```sh
cd "$HOME/Library/Application Support/tramites-es"
printf "Contraseña del certificado: "; read -rs P12PASS; echo; export P12PASS
openssl pkcs12 -in yo.p12 -passin env:P12PASS -passout env:P12PASS -out tmp.pem
openssl pkcs12 -export -in tmp.pem -passin env:P12PASS -passout env:P12PASS -certpbe AES-256-CBC -keypbe AES-256-CBC -macalg sha256 -out yo-aes.p12
rm tmp.pem; unset P12PASS
openssl pkcs12 -info -noout -in yo-aes.p12
```

- La contraseña se escribe una vez, sin verse, y **no** queda en el historial ni en la línea de comandos. El fichero nuevo tiene la misma contraseña.
- `tmp.pem` es intermedio y lleva la clave cifrada; el comando lo borra al terminar.
- La última línea debe mostrar `AES-256-CBC`. Si tu `openssl` no acepta alguna opción, instala OpenSSL 3 (por ejemplo `brew install openssl@3`) y usa la variante con `-legacy`, o pide ayuda. Esta variante con LibreSSL no se ha probado en todas las versiones de macOS.
- Usa `yo-aes.p12` en el paso 5. Cuando todo funcione, borra `yo.p12`.

## 5. Configurar el certificado en tramites-es 🔑

Lo hace **la persona**, en su Terminal. El agente le dice cuál es la carpeta del skill (la que contiene `SKILL.md`).

1. Entra en la carpeta del skill:
   ```sh
   cd "<carpeta del skill>"
   ```
2. Ejecuta (cambia `yo.p12` por `yo-aes.p12` si lo convertiste):
   ```sh
   uv run scripts/cert.py configurar --alias yo --p12 "$HOME/Library/Application Support/tramites-es/yo.p12"
   ```
3. Escribe la contraseña del fichero. **No se ve nada al escribir: es normal.** Pulsa Intro.
4. La contraseña se guarda en el **Llavero** de macOS (servicio `tramites-es`). No queda en ningún fichero ni en el historial.
5. Sale un resultado con `"ok": true`, el tipo de certificado, la caducidad y el NIF enmascarado. Ese resultado **sí** se puede pegar al agente: no tiene secretos.

Notas:
- Es posible que macOS pregunte si Python puede usar el Llavero. "Permitir" lo autoriza una vez; "Permitir siempre" no volverá a preguntar. Elige lo que prefieras.
- **No muevas ni renombres el `.p12`** después: `cert.py` guarda su ruta. Si lo mueves, repite este paso.
- ¿Certificado de representante de una sociedad? Configúralo con otro alias, por ejemplo `--alias empresa`.
- Para quitarlo: `uv run scripts/cert.py olvidar --alias yo`.

## 6. Comprobar que todo está listo

1. Ejecuta (esto ya lo puede hacer el agente):
   ```sh
   uv run scripts/entorno.py
   ```
2. Debe salir `"ok": true`. Si no, la lista `pasos` dice qué falta.
3. AutoFirma no es obligatorio: solo hace falta para que **tú** firmes en algunas sedes (`setup-autofirma.md`).
4. Para revisar un certificado concreto: `uv run scripts/cert.py comprobar --alias yo`.

## 7. Problemas típicos

**`uv: command not found`.** Cierra el Terminal y abre otro. Si sigue, repite la instalación del paso 2.

**`entorno.py` dice que falta Chrome.** Comprueba que está en **Aplicaciones** (no en Descargas ni dentro del `.dmg`).

**macOS no deja abrir un instalador.** No desactives las protecciones del sistema. Descarga de nuevo desde la web oficial y, si sigue, consulta su ayuda.

**En la ventana del agente aparece "Seleccionar un certificado".** **No elijas nada:** pulsa Cancelar y avisa al agente. Suele ser una web que no está en la lista de dominios del skill o un dominio que falta.

**Certificado caducado o a punto de caducar.** `entorno.py` muestra `CADUCADO` o `caduca en menos de 30 días`.
- La FNMT deja renovar por internet durante los **60 días previos** a la caducidad, con condiciones (https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar). Si ya caducó, hay que pedir uno nuevo.
- Con el certificado nuevo: expórtalo (paso 3), compruébalo (paso 4) y repite el paso 5 con el **mismo alias** (se sobrescribe).

**"No se ha enviado/seleccionado ningún certificado"**, error 4002 de Cl@ve o una página de error de la sede justo al entrar con certificado. Casi siempre falta un *origin*: la sede saltó a un subdominio que no recibe el certificado.
- El agente revisa `hosts_con_error` y `url_final` en la salida de `sede.py`, y puede comprobar el host con `uv run scripts/sede.py tls-probe <host>` (no usa el certificado).
- Si el dominio es oficial, propón añadirlo a `assets/sedes.yaml` y abrir un issue "sede rota". Si no es oficial, para y pregunta.

**Antivirus.** Algunos antivirus con "análisis de HTTPS" o "de conexiones cifradas" interfieren con el certificado de cliente o con las descargas de Playwright. Prueba a excluir las sedes oficiales de ese análisis (consulta la ayuda de tu antivirus). No desactives el antivirus entero.
