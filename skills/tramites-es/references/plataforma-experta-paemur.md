---
verificado_el: 2026-10-15
estado_mapeo: parcial
municipios_ejemplo: [Mula, Las Palmas de Gran Canaria]
fuentes:
  - https://sede.mula.regiondemurcia.es/web/inicioWebc.do?opcion=noreg&entidad=30029     # portada (Mula)
  - https://sede.mula.regiondemurcia.es/web/catalogoAsuntos.do?opcion=5&entidad=30029    # catálogo (Mula)
  - https://sedeelectronica.laspalmasgc.es/3webc/inicioWebc.do?opcion=noreg              # entrada histórica (Las Palmas GC): HTTP 400 el 15-oct-2026
---

# Plataforma eXperta / PAEMUR (Expert@ Ventanilla Virtual)

Riesgo: **Leer** (catálogo, listados) y **Preparar** (instancias, actividad, certificados). Firmar, presentar, pagar y abrir notificaciones lo hace la persona.

Estado **parcial**: la receta funciona en Mula; la entrada histórica de Las Palmas de Gran Canaria está degradada.

## Qué es y dónde se usa

- "Ventanilla Virtual" eXperta (Expert@). La **Comunidad Autónoma de la Región de Murcia** la da a sus municipios con el nombre **PAEMUR**. Proveedor sin identificar.
- Dónde:
  - Región de Murcia: `sede.<municipio>.regiondemurcia.es` (Mula, Bullas, Cehegín, Fortuna, Abarán, Calasparra, Lorquí, Los Alcázares, Puerto Lumbreras, Fuente Álamo…).
  - Álava (`udalenegoitza.araba.eus`), provincia de Soria (`portaltramitador.dipsoria.es`).
  - Las Palmas de Gran Canaria, Elda, Chiclana y Talavera.
- Cobertura estimada: ~60–100 ayuntamientos.

## Cómo adaptarla a tu ayuntamiento

```text
HOST    = dominio de la sede (puede llevar puerto, p. ej. :20443)
BASE    = web (PAEMUR) o 3webc (despliegues antiguos)
ENTIDAD = código del municipio (5 dígitos)

Portada:   https://{HOST}/{BASE}/inicioWebc.do?opcion=noreg&entidad={ENTIDAD}
Catálogo:  https://{HOST}/{BASE}/catalogoAsuntos.do?opcion=5&entidad={ENTIDAD}
Búsqueda:  https://{HOST}/{BASE}/busquedaAsuntos.do?opcion=0&entidad={ENTIDAD}
Login:     https://{HOST}/{BASE}/inicioWebc.do?opcion=cargar&redirige={BASE64_URL}&entidad={ENTIDAD}&idioma=1
```

- Cambian el host, el prefijo (`web` o `3webc`), la entidad y los códigos de categoría y procedimiento.
- En Mula, `ENTIDAD=30029` y las categorías se abren con `buscarAsuntosSede('<n>')`:

| Código | Categoría (Mula) |
|---|---|
| `10` | Registro / documentos (instancia general) |
| `27` | Licencias de actividad |
| `28` | Actividades |
| `23` | Certificados / justificantes |
| `31` | Certificados / informes |

- Los códigos de categoría son locales: compruébalos en el catálogo de tu municipio.
- El parámetro `redirige` del login es la URL de vuelta en Base64: no lo construyas a mano, entra desde el enlace de la sede.
- Si el host lleva puerto (Elda usa `:20443`), el origin del certificado debe incluirlo: `https://<host>:20443`.

## Acceso

- En Mula, el acceso está en el enlace `#inicoSesion` (sic, mal escrito y duplicado en la página).
- La pantalla **OPCIONES DE ACCESO** ofrece:
  - **Certificado:** botón `ACCEDER` con `onclick=pulsarCertificado()`. Es el que usa el agente.
  - Cl@ve: `pulsarClave()`. En la pasarela, solo "DNIe / Certificado electrónico".
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://sede.mula.regiondemurcia.es` | `tls-probe`/`cert-probe`: HTTP 200 sin mTLS. |
| `https://sedeelectronica.laspalmasgc.es` | Sin mTLS; la entrada histórica devolvió HTTP 400. |

- Dónde se pide el certificado tras `pulsarCertificado()`: **pendiente de verificación con certificado**.

## Trámites típicos del autónomo

| Trámite | Entrada | Dónde para el agente | Qué hace la persona |
|---|---|---|---|
| Instancia / registro general | Catálogo → categoría de registro (`10` en Mula) | En el asunto, con texto y adjuntos preparados | Se identifica, adjunta, firma y envía |
| Licencia o declaración de actividad | Catálogo → `27` / `28` en Mula | Localiza el asunto y prepara la documentación | Igual |
| Certificados municipales | Catálogo → `23` / `31` en Mula | Localiza el asunto | Lo solicita y firma |
| Expedientes y comunicaciones | Ventanilla autenticada | Lista | — |
| Notificaciones | Ventanilla autenticada | **Solo lista** | Abre la que quiera |
| Pagos | Portada → pagos | Localiza el recibo o la liquidación | Paga |

- La oficina tributaria puede ser externa. En la Región de Murcia muchos municipios tienen los tributos en la agencia tributaria regional (ATRM): ver Trampas.
- Contenido de la ventanilla autenticada: **pendiente de verificación con certificado**.

## Firma

- **AutoFirma**: la sede enlaza su descarga. No se ejecutó ninguna firma.
- La firma la hace la persona; sede.py captura `afirma://`.
- Éxito esperado: asiento y justificante en la ventanilla, con el expediente y las comunicaciones en sus listados. Verifica con `scripts/justificante.py` y en el listado.

## Trampas

- **Las Palmas de Gran Canaria:** el 15-oct-2026, `/3webc/inicioWebc.do?opcion=noreg` devolvió HTTP 400 y la raíz agotó el tiempo. No se insistió. Busca la entrada vigente desde la web municipal y, si no aparece, usa REG/SIR (`registro-reg-sir.md`) para la instancia general.
- **Mantenimiento:** Mula mostraba un aviso de mantenimiento durante el mapeo. Si la sede avisa, no reintentes en bucle.
- **ATRM de Murcia** (`agenciatributaria.carm.es`): tiene anti-bot Radware. Navegador real y ritmo humano; si bloquea, la consulta la hace la persona.
- No se observaron CAPTCHA, WAF ni iframes en Mula.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en Mula y Las Palmas de Gran Canaria. No se pulsó ningún botón de acceso.
