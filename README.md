# tramites-es

**Tu agente de IA, haciendo de gestor con tu certificado digital. Tú siempre pulsas el botón final.**

`tramites-es` es un *skill* abierto (licencia MIT) que enseña a cualquier agente de IA (Claude Code, Codex, OpenClaw, Gemini CLI, Cursor, Copilot…) a moverse por las sedes electrónicas españolas en nombre de un **autónomo**: vigilar notificaciones sin abrirlas, sacar certificados, consultar deudas y recibos, preparar trámites y saber qué plataforma usa cada ayuntamiento. Todo **en tu ordenador**, con **tu** certificado, y sin que el agente pueda firmar, presentar ni pagar por ti.

> ⚠️ **Estado: en desarrollo (v0.1.0-dev). No publicado todavía.** Las guías se están verificando sede a sede.

## Qué hace (v0.1)

- 📬 **Notificaciones**: lista lo pendiente en DEHú, AEAT, Seguridad Social, DGT y tu ayuntamiento **sin abrir nada** (abrir una notificación hace correr los plazos).
- 📄 **Certificados de estar al corriente** (AEAT, Seguridad Social, ATC Canarias): te deja todo preparado.
- 💶 **Consultas**: deudas, recibos y bases de autónomo, vida laboral, datos fiscales y censales, declaraciones presentadas, recibos municipales.
- 🗓️ **Calendario fiscal personal**: AEAT, ATC (Canarias) y haciendas forales, con fuente oficial y fecha de verificación.
- 🏛️ **Tu ayuntamiento**: qué plataforma usa (Gestiona, TAO/STA, GTT, AOC, Sedipualb@…) y cómo presentar una instancia general en cualquier administración (REG/SIR).
- 🎯 **Ayudas abiertas** para autónomos (base de datos nacional de subvenciones).

## Qué NO hace (por diseño)

- ❌ No firma, no presenta, no paga, no da de alta ni de baja. **Eso lo pulsas tú** en la página real o en AutoFirma.
- ❌ No abre notificaciones sin tu OK.
- ❌ No usa Cl@ve PIN/Móvil/Permanente ni tus SMS (la AEAT lo considera uso indebido). Solo tu certificado digital.
- ❌ No resuelve CAPTCHAs ni coge citas previas.
- ❌ No envía tus datos ni tu certificado a ningún servidor. No hay nube: todo corre en tu equipo.
- ❌ No es asesoramiento fiscal ni legal. Ver [DISCLAIMER.md](DISCLAIMER.md).

## Seguridad

- El certificado y su contraseña solo los toca un módulo (`scripts/cert.py`). Nunca aparecen en el chat, en los logs ni en la línea de comandos.
- El navegador solo presenta tu certificado a **dominios oficiales**. En Linux arranca además con un almacén de certificados aislado. En Windows y macOS el sistema puede ofrecer otros certificados instalados; si aparece un selector, lo eliges tú.
- Bloqueos activos en el navegador: los botones de firmar, enviar, presentar, pagar o comparecer quedan bloqueados para el agente. AutoFirma no se lanza sola.
- Sin hooks, sin servidores MCP y sin binarios: Markdown y scripts Python que puedes leer.
- Ver [SECURITY.md](SECURITY.md) para el modelo de amenazas y cómo reportar problemas.

## Instalación

> Sustituye `<owner>` por la cuenta de GitHub que publica el repositorio. Fija una versión (`v0.1.0`) siempre que el instalador lo permita: así sabes exactamente qué instalas.

| Agente | Recomendado | Alternativa |
|---|---|---|
| **Claude Code** | `/plugin marketplace add <owner>/tramites-es` y luego `/plugin install tramites-es@tramites-es`. Desde el shell, en un comando (Claude Code 2.1.292 o posterior): `claude plugin install tramites-es --marketplace <owner>/tramites-es` | `npx skills add <owner>/tramites-es -a claude-code -g --copy` |
| **Codex** | `codex plugin marketplace add <owner>/tramites-es@v0.1.0` y luego `/plugins` → instalar | `npx skills add <owner>/tramites-es -a codex -g --copy` (→ `~/.agents/skills`) |
| **OpenClaw** | `openclaw skills install git:<owner>/tramites-es@v0.1.0 --global` | `git clone` dentro de `<workspace>/skills/` |
| **Hermes** | `hermes skills install <owner>/tramites-es/skills/tramites-es` | `hermes skills tap add <owner>/tramites-es` |
| **Gemini CLI** | `gemini skills install https://github.com/<owner>/tramites-es.git --path skills/tramites-es` | `gemini extensions install https://github.com/<owner>/tramites-es --ref v0.1.0` |
| **Antigravity** | `agy plugin install https://github.com/<owner>/tramites-es` | — |
| **Cursor** | Customize → From GitHub Repository | `npx skills add <owner>/tramites-es -a cursor` |
| **GitHub Copilot** | `gh skill install <owner>/tramites-es tramites-es@v0.1.0 --agent github-copilot --scope user` | `npx skills add <owner>/tramites-es -a github-copilot` |
| **Cualquiera** | `npx skills add <owner>/tramites-es` | `git clone` + `install.ps1` (Windows) o `install.sh` (Linux y macOS) |

Notas:

- `npx skills` usa enlaces simbólicos por defecto: en Windows añade `--copy`. Además envía telemetría anónima, que se desactiva con la variable `DISABLE_TELEMETRY=1`.
- Pendiente de comprobar con el repositorio ya publicado: OpenClaw (repo con varias carpetas), Antigravity y Cursor (falta el manifiesto `.cursor-plugin/`).

### Instalación manual: `install.ps1` / `install.sh`

Si prefieres no usar instaladores de terceros, clona el repositorio, revisa lo que vas a instalar y ejecuta el instalador de tu sistema en una terminal normal (sin permisos de administrador):

```powershell
# Windows (PowerShell)
git clone https://github.com/<owner>/tramites-es.git
cd tramites-es
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

```sh
# Linux y macOS
git clone https://github.com/<owner>/tramites-es.git
cd tramites-es
sh install.sh
```

Los dos hacen lo mismo:

- Copian la carpeta `skills/tramites-es`, sin enlaces simbólicos, en `~/.agents/skills/` y `~/.claude/skills/`, y también en `~/.openclaw/skills/` y `~/.hermes/skills/` si esas carpetas existen.
- Te enseñan qué ficheros van a copiar y adónde, y te piden confirmación antes de tocar nada.
- No descargan nada ni piden permisos de administrador. Si ya había una versión instalada, la sustituyen.

Para actualizar: `git pull` y vuelve a ejecutar el instalador. Para desinstalar: borra las carpetas `tramites-es` de esos destinos.

### Después de instalar

1. Reinicia tu agente y pídele *"comprueba el entorno de tramites-es"*: ejecuta `scripts/entorno.py` y te dice qué falta.
2. El certificado lo configuras **tú** en tu terminal, desde la carpeta del skill instalado (el agente no puede hacerlo, a propósito): `uv run scripts/cert.py configurar --alias yo --p12 <ruta al .p12 o .pfx>`. Las guías `references/setup-windows.md`, `setup-macos.md` y `setup-linux.md` lo explican paso a paso.

## Cómo contribuir

Las sedes cambian a menudo. Si una guía no coincide con lo que ves, abre un issue **"sede rota"** (sin datos personales). Para añadir tu ayuntamiento o plataforma, ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

MIT. Ver [LICENSE](LICENSE) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Proyecto independiente, sin relación con ninguna Administración pública.
