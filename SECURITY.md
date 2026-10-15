# Seguridad

Este skill maneja **certificados digitales** y accede a sedes de la Administración. La seguridad del propio repositorio es parte del producto.

## Quién decide qué

- **Los actos con efectos los autoriza la persona usuaria**, no el skill: `generar`, `firmar`, `presentar`, `pagar`, `comparecer`, `cambiar_datos` y `cita` (tabla en `skills/tramites-es/SKILL.md`). Se fijan con `scripts/permisos.py` (solo en una terminal interactiva) o se pasan con `sede.py --permitir`.
- **Lo que el skill hace siempre**, haya o no permisos, son protecciones: el certificado solo en `cert.py`, solo dominios oficiales, datos personales enmascarados y verificación con el justificante oficial.
- **Fuera del alcance** aunque haya permiso: automatizar Cl@ve PIN/Móvil/Permanente o SMS, resolver CAPTCHAs y acaparar citas.

## Modelo de amenazas (resumen)

| Amenaza | Defensa |
|---|---|
| El agente firma, presenta, paga o abre una notificación sin que la persona lo haya autorizado (por error o por *prompt injection*) | Los actos no permitidos se bloquean en `scripts/sede.py`: botones y envíos de acción, `afirma://`, `confirm()`, rutas de red de pago, presentación y comparecencia, y recetas que los ejecutan. El bloqueo dice qué permiso falta. `SKILL.md` indica al agente que solo su usuario le da instrucciones |
| Una web, un PDF o un correo da instrucciones al agente | `SKILL.md`: el agente las ignora y avisa a su usuario. Los permisos no se amplían por contenido de terceros |
| El certificado o su contraseña acaban en el chat, logs, argv o un servidor | Solo `scripts/cert.py` los toca. Contraseña en el llavero del sistema. Redacción en todo lo que se persiste. Certificado presentado solo a dominios oficiales. Almacén NSS aislado en el navegador |
| Una contribución maliciosa (PR) añade instrucciones o código que exfiltra el certificado | CODEOWNERS y revisión obligatoria, CI que bloquea Unicode invisible, dominios no oficiales y patrones prohibidos, escaneo de skills, dependencias fijadas, sin hooks, MCP ni binarios |
| Suplantación de sedes (phishing) | Lista blanca de dominios oficiales; el agente se detiene ante dominios desconocidos |
| Automatización de Cl@ve, CAPTCHAs o acaparamiento de citas | Fuera del alcance por diseño; se documenta como paso de la persona |

## Límites (léelos)

- **Con permisos, el agente actúa en tu nombre.** Dar `firmar`, `presentar` o `pagar` significa que tu agente puede firmar, presentar o pagar con tu certificado. Dalos solo a un agente en el que confíes, y revisa los justificantes.
- **Las guardas evitan errores y manipulaciones, no a un agente hostil.**
  - `sede.py` bloquea los actos no permitidos y las recetas no pueden tocar las guardas, los secretos ni la red.
  - Pero un agente con **acceso libre a tu terminal** puede ejecutar cualquier otro programa con tus permisos, incluido leer el fichero del certificado o cambiar `permisos.yaml`.
  - La protección de fondo es **el sistema de permisos de tu agente**: qué comandos puede ejecutar sin preguntarte.
- **En Windows y macOS no hay almacén de certificados aislado.** Si el sistema ofrece varios certificados, el selector nativo es tuyo: elige tú.
- **Las guías pueden quedar desactualizadas.** Una sede puede añadir un botón nuevo que ejecute una acción con otro texto que `sede.py` no reconozca. El éxito de cualquier acto se verifica en el listado oficial.

## Reportar una vulnerabilidad

**No abras un issue público.** Usa el informe privado de vulnerabilidades de GitHub del repositorio (Security → Report a vulnerability). Indica la versión, los pasos para reproducir y el impacto. Nunca incluyas tu certificado, contraseñas ni datos personales reales.
