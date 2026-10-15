# Fuentes de los datos públicos

Los datos de `assets/` son públicos y no contienen datos personales. Aquí se indica de dónde sale cada uno, con qué condiciones se reutiliza y cuándo se consultó. Cada guía de `references/` lleva además sus propias `fuentes` y su `verificado_el`.

## Resumen por fichero

| Fichero | Qué contiene | Fuente | Condiciones | Consultado |
|---|---|---|---|---|
| `_sedes-estatal.yaml`, `_sedes-canarias.yaml`, `_sedes-plataformas.yaml` | Direcciones de acceso, *origins* y nombres de trámites de cada sede | Las propias sedes electrónicas, recorridas en modo solo lectura | Información del sector público (Ley 37/2007). Solo se guardan direcciones y nombres de trámites, no se copian textos | 15-10-2026 |
| `dominios-oficiales.yaml` | Sufijos y hosts de Administraciones públicas a los que se puede presentar el certificado | Sedes oficiales de cada organismo | Ídem | 15-10-2026 |
| `calendario.yaml` | Plazos fiscales y de Seguridad Social | AEAT, Agencia Tributaria Canaria, Seguridad Social, Hacienda Foral de Navarra, BOE y BOC. Cada entrada cita su fuente en la sección `fuentes` del propio fichero | Ídem. Del BOE y los boletines solo se citan fechas y artículos, con su enlace | 15-10-2026 (`verificado_el`) |
| `municipios.csv` | Censo de los 8.132 ayuntamientos: código INE, población, web, sede, plataforma, confianza y organismo recaudador | INE (municipios y padrón) + Wikidata (web oficial) + listados públicos de plataformas provinciales y autonómicas (ver abajo) + 1-2 peticiones GET a la portada pública de cada web y sede, sin iniciar sesión, para identificar la plataforma por su huella. Recaudador: listados públicos de los organismos provinciales de recaudación | Ver cada fuente. Wikidata: CC0. Las URL y plataformas son hechos públicos | 15-10-2026. Plataforma identificada en 4.669 municipios (82 % de la población). El certificado solo se presenta a sedes con confianza alta o media |

`scripts/ayudas.py` no guarda datos en el repositorio: consulta en vivo la BDNS (ver abajo).

## Instituto Nacional de Estadística (INE)

- **Relación de municipios y sus códigos a 1-1-2026** (`diccionario26.xlsx`): códigos INE de los 8.132 municipios.
- **Cifras oficiales de población del Padrón a 1-1-2025** (`pobmun25.xlsx`): para priorizar por población.
- Atribución: *Fuente: Instituto Nacional de Estadística (INE)*, https://www.ine.es
- Condiciones: las del aviso legal del INE para la reutilización de sus datos (citar la fuente y no alterar su sentido).
- Consultado: 14-15/10/2026.

## Wikidata

- Propiedades usadas: P772 (código INE del municipio), P856 (sitio web oficial), P1082 (población) y P576 (fecha de disolución, para descartar municipios extinguidos).
- Consulta SPARQL a https://query.wikidata.org/sparql (14-15/10/2026).
- Licencia: **CC0 1.0** (dominio público). No exige atribución; la damos igualmente: *datos de Wikidata (Wikimedia Foundation)*.
- Aviso: algún P856 apunta a webs que no son del ayuntamiento. Cada dirección se comprueba antes de usarla y la sede nunca se toma solo de Wikidata.

## Fuentes autonómicas y provinciales (para completar `municipios.csv`)

Solo se añadirán si se usan, con su licencia confirmada en este fichero. Candidatas con licencia ya publicada:

- Diputació de Castelló, *Sedes electrónicas de las entidades locales de la provincia de Castellón* (CC BY): dataset abierto de la diputación.
- Generalitat Valenciana, *mapets* (CC BY): portal de datos abiertos de la GVA.
- Gobierno de Navarra, *Guía de entidades locales de Navarra* (CC BY 4.0): portal de datos abiertos de Navarra.

Con licencia por confirmar antes de usarlas: Generalitat de Catalunya (ens locals), Gobierno Vasco (registro de entidades locales), Xunta de Galicia (casas dos concellos), Junta de Comunidades de Castilla-La Mancha y Junta de Andalucía (RAEL).

## Base de Datos Nacional de Subvenciones (BDNS)

- Sistema Nacional de Publicidad de Subvenciones y Ayudas Públicas (IGAE, Ministerio de Hacienda).
- API pública sin autenticación: https://www.infosubvenciones.es/bdnstrans/api (espejo en www.pap.hacienda.gob.es). Verificada el 15-10-2026.
- `scripts/ayudas.py` la consulta en el equipo de la persona, con pausas entre peticiones, y no guarda resultados en el repositorio. Los datos son los publicados por cada órgano convocante; el texto que manda es el extracto publicado en el boletín oficial.

## Sedes electrónicas, BOE y boletines

- Las direcciones, rutas y nombres de trámites salen de recorrer cada sede en modo solo lectura (sin firmar, presentar, pagar ni abrir notificaciones) el 15-10-2026.
- Las fechas y plazos citan la norma (BOE, BOC) o la página oficial del organismo, con su enlace en `calendario.yaml` o en el frontmatter de cada guía.
- Proyecto independiente: los nombres de organismos se usan solo para indicar dónde se hace cada trámite (ver `DISCLAIMER.md` en la raíz del repositorio).
