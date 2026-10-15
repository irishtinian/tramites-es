# Cómo contribuir

¡Gracias! Las sedes cambian a menudo y el proyecto vive de que la comunidad avise y corrija.

## Avisar de una sede rota

Abre un issue **"sede rota"** con:
- sede y trámite;
- qué dice la guía y qué ves tú;
- fecha;
- sistema operativo y agente.

**Nunca incluyas datos personales**: NIF, nombres, direcciones, nº de expediente, capturas con datos reales ni tu certificado.

## Añadir una sede, un ayuntamiento o una plataforma

1. Comprueba con `scripts/buscar.py` si tu municipio usa una plataforma que ya tiene receta (Gestiona, TAO/STA, GTT, AOC…). En ese caso, lo normal es que baste con corregir `assets/municipios.csv`.
2. Para una guía nueva, copia la estructura de una existente en `references/`:
   - acceso y origins que piden certificado;
   - ruta de navegación;
   - mecanismo de firma;
   - dónde para el agente;
   - cómo se verifica el éxito;
   - problemas conocidos;
   - `verificado_el` y fuentes oficiales.
3. Los dominios nuevos a los que se presenta el certificado deben ser de una Administración pública, con fuente. Van como `origins` en `assets/_sedes-*.yaml` (`_sedes-estatal.yaml`, `_sedes-canarias.yaml` o `_sedes-plataformas.yaml`) o a `assets/dominios-oficiales.yaml`, y los revisan los CODEOWNERS.
4. Fechas, plazos e importes: solo con fuente primaria (BOE, boletín autonómico, sede del organismo).

## Código

- Python 3.11+, PEP 723 con versiones fijadas, sin prompts interactivos (salvo `cert.py configurar` y `permisos.py fijar`, que son para la persona) y salida JSON por stdout.
- Las guardas de `scripts/sede.py` bloquean los actos que la persona no ha permitido: no hagas que uno pase sin su permiso, y no toques las protecciones de `SKILL.md` (certificado, dominios oficiales, datos personales, Cl@ve, CAPTCHAs). Si crees que una guarda da un falso positivo, explícalo con el caso exacto en el PR.
- Sin red salvo hacia sedes oficiales. Sin `subprocess` de shell arbitrario. Sin secretos en argv ni en logs. Sin Unicode invisible.
- `pytest` y la validación de contenido deben pasar: `uv run --group test pytest` (o `python -m pytest` con las versiones de `pyproject.toml`) y `python .github/scripts/content_guard.py`.

## Revisión

Todo PR que toque `SKILL.md`, `scripts/`, `assets/dominios-oficiales.yaml`, `assets/_sedes-*.yaml`, `assets/municipios.csv` o la CI requiere revisión de CODEOWNERS. Es un repo que maneja certificados digitales: la revisión es estricta a propósito.
