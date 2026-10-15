# Seguridad

Este skill maneja **certificados digitales** y accede a sedes de la Administración. La seguridad del propio repositorio es parte del producto.

## Modelo de amenazas (resumen)

| Amenaza | Defensa |
|---|---|
| El agente firma, presenta, paga o abre una notificación por error o por *prompt injection* | Reglas duras en `SKILL.md` + bloqueos en `scripts/sede.py`: bloqueo de botones y submits de acción, `afirma://` capturado, `confirm()` cancelado, rutas de red de pago, presentación y comparecencia abortadas. El clic final siempre es humano |
| El certificado o su contraseña acaban en el chat, logs, argv o un servidor | Solo `scripts/cert.py` los toca. Contraseña en el llavero del sistema. Redacción en todo lo que se persiste. Certificado presentado solo a dominios oficiales. Almacén NSS aislado en el navegador |
| Una contribución maliciosa (PR) añade instrucciones o código que exfiltra el certificado | CODEOWNERS y revisión obligatoria, CI que bloquea Unicode invisible, dominios no oficiales y patrones prohibidos, escaneo de skills, dependencias fijadas, sin hooks, MCP ni binarios |
| Suplantación de sedes (phishing) | Lista blanca de dominios oficiales; el agente se detiene ante dominios desconocidos |
| Automatización de Cl@ve o CAPTCHAs | Prohibido por diseño; se documenta como paso humano |

## Límites (léelos)

- **Las guardas evitan errores y manipulaciones, no a un agente hostil.**
  - `sede.py` bloquea botones, envíos, URLs de acción, AutoFirma y rutas de red peligrosas.
  - Las recetas se ejecutan sin `import`, sin `open` y sin acceso a las rutas de red.
  - Pero un agente con **acceso libre a tu terminal** puede ejecutar cualquier otro programa con tus permisos, incluido leer el fichero del certificado.
  - La protección de fondo es **el sistema de permisos de tu agente**: que te pida aprobación antes de ejecutar comandos. No le des permisos ilimitados ("yolo", "bypass") mientras tenga acceso a tu certificado.
- **En Windows y macOS no hay almacén de certificados aislado.** Si el sistema ofrece varios certificados, el selector nativo es tuyo: elige tú.
- **Las guías pueden quedar desactualizadas.** Una sede puede añadir un botón nuevo que ejecute una acción con otro texto. Por eso el último clic de cualquier acción con efectos lo da siempre la persona, y el éxito se verifica en el listado oficial.

## Reportar una vulnerabilidad

**No abras un issue público.** Usa el informe privado de vulnerabilidades de GitHub del repositorio (Security → Report a vulnerability). Indica la versión, los pasos para reproducir y el impacto. Nunca incluyas tu certificado, contraseñas ni datos personales reales.
