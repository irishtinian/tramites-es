# Cambios

## [0.1.0-dev] — sin publicar

- Estructura del skill `tramites-es` (un único skill autocontenido) y manifiestos para Claude Code, Codex y Gemini.
- Reglas duras y guía de seguridad.
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
