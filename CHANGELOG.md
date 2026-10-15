# Cambios

## [0.2.0-dev] — sin publicar

### Los permisos los decide la persona usuaria

- El skill ya no prohíbe firmar, presentar ni pagar: cada acto con efectos es un **permiso** que da la persona (`generar`, `firmar`, `presentar`, `pagar`, `comparecer`, `cambiar_datos`, `cita`). Sin permiso, el agente pregunta.
- `scripts/permisos.py` (nuevo): `ver`, `fijar todo|<lista>` y `quitar`. `fijar` y `quitar` solo funcionan en una terminal interactiva.
- `sede.py --permitir <actos>`: las guardas de página, red, diálogos y recetas bloquean solo los actos no permitidos y dicen qué permiso falta (`BLOQUEADO (requiere permiso 'x')` y `como_seguir`).
- AutoFirma: con el permiso `firmar`, `sede.py` pasa `afirma://` al AutoFirma del equipo. `--autofirma-auto N` elige el certificado en Linux sin escritorio (experimental).
- Páginas de cita previa: sin permiso `cita`, un "Confirmar" a secas también se bloquea.
- Guía nueva `tramite-cita-previa.md`: una cita para el titular, a ritmo humano (AEAT, INSS, DGT, DNI, extranjería, Registro Civil, SEPE, ATC, padrón).
- Guías y YAML reescritos con el acto de cada paso (`riesgo: persona` → `riesgo: actuar`). `reglas-y-seguridad.md` explica permisos y protecciones.
- Siguen fuera del alcance aunque haya permiso: automatizar Cl@ve PIN/Móvil/Permanente o SMS, resolver CAPTCHAs y acaparar citas.
- Arreglo: `permisos.py ver` fallaba al mostrar la fecha de `fijado_el`.
- Guía nueva `tramite-renovar-certificado-fnmt.md`: renovar el certificado de persona física o de representante, en modo completo o acompañado. La de representante de administrador único se recorrió de punta a punta el 15-10-2026. Sede `fnmt` en `_sedes-estatal.yaml`.
- `cert.py` avisa cuando faltan 60 días o menos para la caducidad, que es cuando la FNMT abre la renovación.
- `SKILL.md`: las contraseñas y los datos de tarjeta los teclea siempre la persona.

## [0.1.0-dev] — sin publicar

- Estructura del skill `tramites-es` (un único skill autocontenido) y manifiestos para Claude Code, Codex y Gemini.
- Reglas duras y guía de seguridad (sustituidas en la 0.2 por el modelo de permisos).
- Scripts: `cert.py` (único que toca el certificado), `sede.py` (navegador con certificado por origin y bloqueos), `entorno.py`, `buscar.py`, `justificante.py`.
- Bloqueos probados en vivo el 15-oct-2026 contra sedes reales, en modo solo lectura.
- Bloqueo de navegaciones a URLs que ejecutan una acción al abrirlas. Origen: una sede emitía un certificado al cargar la URL.
- Formularios de búsqueda de notificaciones permitidos si no piden abrir ni comparecer.
- `cert.py` re-empaqueta en memoria los `.p12` antiguos (RC2/3DES) con AES-256 para Playwright.
- Salida JSON en UTF-8 en todos los scripts (Windows).
- Scripts nuevos: `calendario.py` (71 vencimientos con fuente) y `ayudas.py` (API pública de la BDNS).
- Pruebas `pytest` sin red ni navegador (`tests/`) y CI: `tests` (Linux y Windows), `content-guard` y `validate`.
- Instaladores `install.ps1` e `install.sh`: copian el skill sin enlaces simbólicos y piden confirmación.
- `CODEOWNERS`, plantillas de PR e issues, y `assets/FUENTES.md` con la atribución de los datos públicos.
- Arreglos: `calendario.py` también escribe JSON en UTF-8 en Windows; `justificante.py` ya distingue la Agencia Tributaria Canaria de la AEAT.

- Censo `assets/municipios.csv`: 8.132 ayuntamientos con plataforma (82 % de la población identificada) y organismo recaudador. `buscar.py --municipio` lleva a la receta de su plataforma o a REG/SIR.
- Validación en vivo de la v0.1 (9 escenarios de solo lectura con certificado real) y aplicación de sus correcciones.

### Cambios de seguridad

- La CI bloquea Unicode invisible, datos personales, URLs acortadas, binarios y certificados, y los dominios nuevos en `assets/` sin revisión de CODEOWNERS.
