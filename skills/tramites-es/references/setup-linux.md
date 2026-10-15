---
verificado_el: 2026-10-15
fuentes:
  - https://docs.astral.sh/uv/getting-started/installation/     # instalar uv
  - https://docs.astral.sh/uv/guides/install-python/            # uv descarga Python si hace falta
  - https://www.google.com/chrome/
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/obtener-certificado-software
  - https://www.sede.fnmt.gob.es/preguntas-frecuentes/exp-imp-y-elim-de-certificados   # exportar/importar en Chrome y Firefox (Linux)
  - https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar
  - https://chromium.googlesource.com/chromium/src/+/HEAD/docs/linux/cert_management.md   # Chrome en Linux usa NSS
---

# Preparar Linux para tramites-es

Guía para que **el agente acompañe a una persona**, paso a paso, en Linux (probado sobre todo en Debian/Ubuntu; en Fedora y otras, los comandos de paquetes cambian).

## Antes de empezar (para el agente)

- Un paso cada vez. Frases cortas. Espera a que la persona diga "hecho" o te cuente qué ve.
- **Tú no tocas el certificado ni su contraseña.** No pidas el `.p12`, no lo leas, no lo copies, no pidas la contraseña, no abras el fichero de contraseña. Los pasos marcados con 🔑 los hace la persona en **su** terminal y tú solo le das el comando para copiar.
- Si la persona pega su contraseña en el chat: dile que no lo repita y que exporte de nuevo con **otra** contraseña (paso 3) y vuelva a configurar (paso 6).
- Al final, comprueba con `uv run scripts/entorno.py` (paso 7).

## 1. Abrir una terminal

1. En el escritorio, abre la aplicación **Terminal** (en Ubuntu: `Ctrl + Alt + T`).
2. Para pegar: `Ctrl + Mayús + V`.
3. Importante: los pasos 🔑 se hacen en **esta ventana**, fuera del chat del agente. Si se lanzan desde el agente, `cert.py` se niega a propósito.

## 2. Instalar uv y Google Chrome

**uv** (recomendado) instala Python y las dependencias por ti.

1. Instalador oficial de uv:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. **Cierra la terminal y abre otra.** Comprueba: `uv --version`.
3. No hace falta instalar Python aparte: uv descarga uno si falta. Las dependencias (Playwright, etc.) vienen declaradas en cada script y `uv run` las instala la primera vez.

**Google Chrome** (obligatorio; no vale Chromium, ni en snap ni en flatpak):

1. Descarga el paquete de https://www.google.com/chrome/ (`.deb` para Debian/Ubuntu, `.rpm` para Fedora/openSUSE).
2. Instálalo desde la carpeta de descargas (el nombre del fichero puede variar):
   ```sh
   sudo apt install ./google-chrome-stable_current_amd64.deb      # Debian/Ubuntu
   sudo dnf install ./google-chrome-stable_current_x86_64.rpm     # Fedora
   ```
3. El skill lo busca en `/usr/bin/google-chrome` o `/opt/google/chrome/chrome`. No hace falta `playwright install`.

**Sin uv (alternativa).** Usa Python 3.11+ de tu distribución en un entorno propio (en Debian/Ubuntu puede hacer falta `sudo apt install python3-venv`), con las versiones de la cabecera `# /// script` de los scripts:
```sh
python3 -m venv ~/.venv-tramites
~/.venv-tramites/bin/pip install playwright==1.58.0 pyyaml==6.0.3 cryptography==44.0.2 keyring==25.6.0
```
En esta guía, cambia `uv run` por `~/.venv-tramites/bin/python`.

## 3. Conseguir el certificado como fichero `.p12`

El skill necesita el certificado **con su clave privada** en un fichero `.p12` (o `.pfx`):

- **A. Ya tienes el fichero.** Por ejemplo, la copia de seguridad que la FNMT recomienda hacer al descargar el certificado.
- **B. Está en tu navegador.** Expórtalo 🔑:
  - Firefox: Ajustes → Privacidad & Seguridad → Certificados → Ver certificados → **Sus certificados** → selecciónalo → **Hacer copia...**
  - Chrome: Configuración → Privacidad y seguridad → Seguridad → Gestionar certificados → **Tus certificados** → Exportar.
  - Pon una contraseña larga. Los textos pueden variar según la versión del navegador.
- **C. No tienes certificado.** Solicítalo en la FNMT (u otro emisor): https://www.sede.fnmt.gob.es/certificados/persona-fisica/obtener-certificado-software. Al descargarlo, haz la copia de seguridad que te propone.

**Dónde guardarlo** (carpeta privada, solo para tu usuario):
```sh
mkdir -p ~/.config/tramites-es && chmod 700 ~/.config/tramites-es
mv ~/Descargas/<tu fichero>.p12 ~/.config/tramites-es/yo.p12     # o ~/Downloads, según el idioma
chmod 600 ~/.config/tramites-es/yo.p12
```

**Seguridad:** no lo dejes en el Escritorio ni en Descargas, ni en carpetas sincronizadas con la nube. No lo envíes por WhatsApp, Telegram, email ni lo subas a ningún chat (tampoco al del agente). Quien tenga el fichero y la contraseña puede actuar como tú.

## 4. Ficheros antiguos (cifrado RC2 o 3DES)

Algunos `.p12` (antiguos, de gestorías o de exportaciones viejas) usan un cifrado que Playwright (OpenSSL 3) ya no lee.

**Síntoma si no lo compruebas:** `cert.py configurar` dice `"ok": true`, pero al abrir una sede el agente ve un error con `Unsupported PKCS12 PFX data` o `unsupported`.

**Comprobar** 🔑 (pide la contraseña sin mostrarla; no la escribas en el comando):
```sh
cd ~/.config/tramites-es
openssl pkcs12 -info -noout -in yo.p12
```
- Si ves `AES-256-CBC` en las líneas de "Encrypted data" y "Keybag": está bien. Ve al paso 5.
- Si ves `RC2`, `TripleDES` o un error con `unsupported`: es antiguo. Conviértelo.

**Convertir a AES** 🔑 (con OpenSSL 3; mira `openssl version`. Con OpenSSL 1.1, quita `-legacy`):
```sh
cd ~/.config/tramites-es
printf "Contraseña del certificado: "; read -rs P12PASS; echo; export P12PASS
openssl pkcs12 -legacy -in yo.p12 -passin env:P12PASS -passout env:P12PASS -out tmp.pem
openssl pkcs12 -export -in tmp.pem -passin env:P12PASS -passout env:P12PASS -certpbe AES-256-CBC -keypbe AES-256-CBC -macalg sha256 -out yo-aes.p12
rm tmp.pem; unset P12PASS; chmod 600 yo-aes.p12
openssl pkcs12 -info -noout -in yo-aes.p12
```
- La contraseña se escribe una vez, sin verse, y **no** queda en el historial ni en la línea de comandos (`ps`). El fichero nuevo tiene la misma contraseña.
- `tmp.pem` es intermedio y lleva la clave cifrada; el comando lo borra al terminar.
- La última línea debe mostrar `AES-256-CBC`. Usa `yo-aes.p12` en el paso 6 y, cuando todo funcione, borra `yo.p12`.

## 5. Pantalla y almacén de certificados (lo que hace `sede.py`)

**Pantalla.** Chrome necesita una pantalla, aunque el agente solo consulte.
- Si trabajas en el escritorio, no hay que hacer nada.
- Si el equipo no tiene escritorio o entras por SSH, `entorno.py` muestra `"pantalla": false`. Instala Xvfb (pantalla virtual):
  ```sh
  sudo apt install xvfb          # Debian/Ubuntu
  dnf provides '*/xvfb-run'      # Fedora: te dice qué paquete instalar
  ```
  y pon `xvfb-run -a` delante de los comandos del agente, por ejemplo `xvfb-run -a uv run scripts/sede.py abrir --sede <id> --titular yo`.
- Con Xvfb la ventana no se ve. Lo que tenga que hacer la persona (un CAPTCHA, firmar) lo hará en su propio navegador.

**Almacén aislado.** Chrome en Linux guarda los certificados en una base NSS (`~/.pki/nssdb`). `sede.py` arranca Chrome con un directorio personal temporal, así que:
- El navegador del agente **no ve** los certificados que tengas importados en tu Chrome o Firefox, ni otros (por ejemplo, el de tu empresa).
- El certificado configurado se presenta **solo** a los dominios oficiales de la sede, desde `cert.py`.
- Para el skill **no** hace falta importar nada en NSS ni instalar `libnss3-tools`. Eso solo hace falta para tu navegador y AutoFirma (`setup-autofirma.md`).

## 6. Configurar el certificado en tramites-es 🔑

Lo hace **la persona**, en su terminal. El agente le dice cuál es la carpeta del skill (la que contiene `SKILL.md`).

```sh
cd "<carpeta del skill>"
uv run scripts/cert.py configurar --alias yo --p12 ~/.config/tramites-es/yo.p12
```
1. Escribe la contraseña del fichero. **No se ve nada al escribir: es normal.** Pulsa Intro.
2. La contraseña se guarda en el llavero del escritorio (Secret Service: GNOME Keyring o KWallet).
3. Sale un resultado con `"ok": true`, el tipo de certificado, la caducidad y el NIF enmascarado. Ese resultado **sí** se puede pegar al agente: no tiene secretos.

**Sin llavero** (servidor, SSH, o un error que menciona `keyring`, `No recommended backend` o `Secret Service`): usa un fichero de contraseña con permisos 600.
```sh
touch ~/.config/tramites-es/clave-yo.txt
chmod 600 ~/.config/tramites-es/clave-yo.txt
nano ~/.config/tramites-es/clave-yo.txt
```
En `nano`, escribe la contraseña en la primera línea, guarda con `Ctrl + O`, Intro, y sal con `Ctrl + X`. Después:
```sh
uv run scripts/cert.py configurar --alias yo --p12 ~/.config/tramites-es/yo.p12 --fichero-contrasena ~/.config/tramites-es/clave-yo.txt
```
- `cert.py` rechaza el fichero si no tiene permisos 600.
- **No lo borres:** se lee cada vez. Es menos seguro que el llavero: protege tu usuario y, si puedes, cifra el disco.

Notas:
- **No muevas ni renombres el `.p12`** después: `cert.py` guarda su ruta. Si lo mueves, repite este paso.
- ¿Certificado de representante de una sociedad? Usa otro alias, por ejemplo `--alias empresa`.
- Para quitarlo: `uv run scripts/cert.py olvidar --alias yo`.

## 7. Comprobar que todo está listo

1. Ejecuta (esto ya lo puede hacer el agente; con `xvfb-run -a` delante si no hay escritorio):
   ```sh
   uv run scripts/entorno.py
   ```
2. Debe salir `"ok": true`. Si no, la lista `pasos` dice qué falta.
3. AutoFirma no es obligatorio: solo hace falta para que **tú** firmes en algunas sedes (`setup-autofirma.md`).
4. Para revisar un certificado concreto: `uv run scripts/cert.py comprobar --alias yo`.

## 8. Problemas típicos

**`uv: command not found`.** Cierra la terminal y abre otra. Si sigue, repite el paso 2.

**"no hay pantalla".** Ver paso 5 (`xvfb-run -a`), o ejecuta desde la terminal del escritorio.

**`entorno.py` dice que falta Chrome.** Instala **Google Chrome** con el paquete oficial (paso 2). Chromium de snap o flatpak no sirve.

**Error de llavero al configurar.** Usa `--fichero-contrasena` (paso 6). Si estás en el escritorio, comprueba que el llavero de la sesión está desbloqueado.

**En la ventana del agente aparece "Seleccionar un certificado".** No debería pasar con el almacén aislado. **No elijas nada:** cancela y avisa al agente.

**Certificado caducado o a punto de caducar.** `entorno.py` muestra `CADUCADO` o `caduca en menos de 30 días`.
- La FNMT deja renovar por internet durante los **60 días previos** a la caducidad, con condiciones (https://www.sede.fnmt.gob.es/certificados/persona-fisica/renovar). Si ya caducó, hay que pedir uno nuevo.
- Con el certificado nuevo: expórtalo (paso 3), compruébalo (paso 4) y repite el paso 6 con el **mismo alias** (se sobrescribe).

**"No se ha enviado/seleccionado ningún certificado"**, error 4002 de Cl@ve o una página de error de la sede justo al entrar con certificado. Casi siempre falta un *origin*: la sede saltó a un subdominio que no recibe el certificado.
- El agente revisa `hosts_con_error` y `url_final` en la salida de `sede.py`, y comprueba el host con `uv run scripts/sede.py cert-probe <url>` o `tls-probe <host>` (no usan el certificado).
- Si el dominio es oficial, propón añadirlo a `assets/_sedes-*.yaml` y abrir un issue "sede rota". Si no es oficial, para y pregunta.

**Antivirus o proxy corporativo.** Si inspeccionan HTTPS, pueden romper el certificado de cliente. Excluye las sedes oficiales de esa inspección; no lo desactives entero.
