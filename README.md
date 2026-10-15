# tramites-es

**Tu agente de IA, haciendo de gestor con tu certificado digital. Lo que puede hacer por ti lo decides tú.**

`tramites-es` es un *skill* abierto (licencia MIT) que enseña a cualquier agente de IA (Claude Code, Codex, OpenClaw, Gemini CLI, Cursor, Copilot…) a moverse por las sedes electrónicas españolas en nombre de un **autónomo**: vigilar notificaciones, sacar certificados, consultar deudas y recibos, preparar y presentar trámites, pagar, pedir citas previas y saber qué plataforma usa cada ayuntamiento. Todo **en tu ordenador** y con **tu** certificado.

> ⚠️ **Estado: beta (v0.2.0).**
> - **Las consultas están verificadas en vivo** con un certificado real (AEAT, Seguridad Social, DEHú, Carpeta Ciudadana, DGT, ATC y varias plataformas municipales).
> - **Los actos con efectos** (presentar, pagar, abrir notificaciones, pedir citas) están documentados, pero casi todos siguen **sin probar de punta a punta**: las guías los marcan como "pendiente de verificar en vivo". La renovación del certificado de la FNMT sí se ha completado.
> - Las sedes cambian sin avisar. Si algo no cuadra, abre un issue "sede rota".

## Qué hace

- 📬 **Notificaciones**: lista lo pendiente en DEHú, AEAT, Seguridad Social, DGT y tu ayuntamiento, con el plazo de cada una. Si le das permiso, las abre y te explica qué piden (abrir una notificación hace correr los plazos).
- 📄 **Certificados de estar al corriente** (AEAT, Seguridad Social, ATC Canarias) y otros documentos.
- 💶 **Consultas**: deudas, recibos y bases de autónomo, vida laboral, datos fiscales y censales, declaraciones presentadas, recibos municipales.
- ✍️ **Presentar y pagar**: instancias, declaraciones, solicitudes de ayudas y pagos, firmando con AutoFirma, si tú se lo permites.
- 📅 **Cita previa** para ti: AEAT, Seguridad Social, DGT, DNI, extranjería, Registro Civil, SEPE…
- 🗓️ **Calendario fiscal personal**: AEAT, ATC (Canarias) y haciendas forales, con fuente oficial y fecha de verificación.
- 🏛️ **Tu ayuntamiento**: qué plataforma usa (Gestiona, TAO/STA, GTT, AOC, Sedipualb@…) y cómo presentar una instancia general en cualquier administración (REG/SIR).
- 🎯 **Ayudas abiertas** para autónomos (base de datos nacional de subvenciones).

## Tú decides qué puede hacer tu agente

Consultar no tiene efectos. Lo demás son **actos**, y cada uno es un permiso que das tú:

| Permiso | Qué permite |
|---|---|
| `generar` | pedir certificados, informes y documentos |
| `firmar` | firmar en tu nombre (AutoFirma, firma de la AEAT) |
| `presentar` | enviar, registrar, adjuntar y presentar |
| `pagar` | pagar deudas, recibos y tasas |
| `comparecer` | abrir notificaciones (empiezan los plazos) |
| `cambiar_datos` | domiciliar, dar de baja, cambiar datos de contacto o bancarios |
| `cita` | reservar o confirmar una cita previa a tu nombre |

- Fíjalos una vez en tu terminal: `uv run scripts/permisos.py fijar todo` (o solo los que quieras, p. ej. `fijar generar,cita`).
- O dáselos a tu agente en sus instrucciones o en la conversación: el agente los pasa con `sede.py --permitir …`.
- **Sin permiso**, el agente consulta y prepara, y antes de un acto te pregunta o te deja el enlace y el botón exacto. El navegador del skill bloquea los actos no permitidos para que nada con efectos ocurra sin querer.

## Lo que el skill no hace, aunque le des permiso

- ❌ No usa Cl@ve PIN/Móvil/Permanente ni tus SMS: la AEAT lo considera uso indebido aunque consientas. Solo tu certificado digital.
- ❌ No resuelve CAPTCHAs: los resuelves tú y el agente sigue.
- ❌ No acapara citas: pide **una** para ti, a ritmo humano. Nada de bots que refrescan para cazar huecos.
- ❌ No envía tus datos ni tu certificado a ningún servidor. No hay nube: todo corre en tu equipo.
- ❌ No es asesoramiento fiscal ni legal. Ver [DISCLAIMER.md](DISCLAIMER.md).

## Seguridad

- El certificado y su contraseña solo los toca un módulo (`scripts/cert.py`). Nunca aparecen en el chat, en los logs ni en la línea de comandos.
- El navegador solo presenta tu certificado a **dominios oficiales**. En Linux arranca además con un almacén de certificados aislado. En Windows y macOS el sistema puede ofrecer otros certificados instalados; si aparece un selector, lo eliges tú.
- Los actos que no hayas permitido quedan bloqueados en el navegador (botones, envíos, pasarelas de pago, AutoFirma). Lo que sí permites, el agente lo hace y lo verifica con el justificante oficial.
- Sin hooks, sin servidores MCP y sin binarios: Markdown y scripts Python que puedes leer.
- Ver [SECURITY.md](SECURITY.md) para el modelo de amenazas y cómo reportar problemas.

## Instalación

> Fija una versión (`v0.2.0`) siempre que el instalador lo permita: así sabes exactamente qué instalas.

| Agente | Recomendado | Alternativa |
|---|---|---|
| **Claude Code** | `/plugin marketplace add irishtinian/tramites-es` y luego `/plugin install tramites-es@tramites-es`. Desde el shell, en un comando (Claude Code 2.1.292 o posterior): `claude plugin install tramites-es --marketplace irishtinian/tramites-es` | `npx skills add irishtinian/tramites-es -a claude-code -g --copy` |
| **Codex** | `codex plugin marketplace add irishtinian/tramites-es@v0.2.0` y luego `/plugins` → instalar | `npx skills add irishtinian/tramites-es -a codex -g --copy` (→ `~/.agents/skills`) |
| **OpenClaw** | `openclaw skills install git:irishtinian/tramites-es@v0.2.0 --global` | `git clone` dentro de `<workspace>/skills/` |
| **Hermes** | `hermes skills install irishtinian/tramites-es/skills/tramites-es` | `hermes skills tap add irishtinian/tramites-es` |
| **Gemini CLI** | `gemini skills install https://github.com/irishtinian/tramites-es.git --path skills/tramites-es` | `gemini extensions install https://github.com/irishtinian/tramites-es --ref v0.2.0` |
| **Antigravity** | `agy plugin install https://github.com/irishtinian/tramites-es` | — |
| **Cursor** | Customize → From GitHub Repository | `npx skills add irishtinian/tramites-es -a cursor` |
| **GitHub Copilot** | `gh skill install irishtinian/tramites-es tramites-es@v0.2.0 --agent github-copilot --scope user` | `npx skills add irishtinian/tramites-es -a github-copilot` |
| **Cualquiera** | `npx skills add irishtinian/tramites-es` | `git clone` + `install.ps1` (Windows) o `install.sh` (Linux y macOS) |

Notas:

- `npx skills` usa enlaces simbólicos por defecto: en Windows añade `--copy`. Además envía telemetría anónima, que se desactiva con la variable `DISABLE_TELEMETRY=1`.
- Sin probar todavía: OpenClaw (repo con varias carpetas), Antigravity y Cursor (falta el manifiesto `.cursor-plugin/`). Si te funciona o falla, cuéntalo en un issue.

### Instalación manual: `install.ps1` / `install.sh`

Si prefieres no usar instaladores de terceros, clona el repositorio, revisa lo que vas a instalar y ejecuta el instalador de tu sistema en una terminal normal (sin permisos de administrador):

```powershell
# Windows (PowerShell)
git clone --branch v0.2.0 https://github.com/irishtinian/tramites-es.git
cd tramites-es
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

```sh
# Linux y macOS
git clone --branch v0.2.0 https://github.com/irishtinian/tramites-es.git
cd tramites-es
sh install.sh
```

Los dos hacen lo mismo:

- Copian la carpeta `skills/tramites-es`, sin enlaces simbólicos, en `~/.agents/skills/` y `~/.claude/skills/`, y también en `~/.openclaw/skills/` y `~/.hermes/skills/` si esas carpetas existen.
- Te enseñan qué ficheros van a copiar y adónde, y te piden confirmación antes de tocar nada.
- No descargan nada ni piden permisos de administrador. Si ya había una versión instalada, la sustituyen.

Para actualizar: `git fetch --tags` y `git checkout <versión nueva>` (o `git checkout main && git pull` para lo último sin publicar), y vuelve a ejecutar el instalador. Para desinstalar: borra las carpetas `tramites-es` de esos destinos.

### Después de instalar

1. Reinicia tu agente y pídele *"comprueba el entorno de tramites-es"*: ejecuta `scripts/entorno.py` y te dice qué falta.
2. El certificado lo configuras **tú** en tu terminal, desde la carpeta del skill instalado (el agente no puede hacerlo, a propósito): `uv run scripts/cert.py configurar --alias yo --p12 <ruta al .p12 o .pfx>`. Las guías `references/setup-windows.md`, `setup-macos.md` y `setup-linux.md` lo explican paso a paso.
3. Decide qué puede hacer tu agente: `uv run scripts/permisos.py fijar <permisos>` (o `fijar todo`). Puedes verlos con `permisos.py ver` y quitarlos con `permisos.py quitar`.
4. Para firmar, instala AutoFirma (`references/setup-autofirma.md`).

## Cómo contribuir

Las sedes cambian a menudo. Si una guía no coincide con lo que ves, abre un issue **"sede rota"** (sin datos personales). Para añadir tu ayuntamiento o plataforma, ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

MIT. Ver [LICENSE](LICENSE) y [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Proyecto independiente, sin relación con ninguna Administración pública.
