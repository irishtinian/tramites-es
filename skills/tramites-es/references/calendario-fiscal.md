---
verificado_el: 2026-10-15
fuentes:
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/calendario-contribuyente/calendario-contribuyente-2026/plazos-presentacion-autoliquidaciones-domiciliacion-bancaria.html
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/calendario-contribuyente/calendario-contribuyente-2026/calendario-anual/octubre/hasta-20-octubre.html
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/calendario-contribuyente/calendario-contribuyente-2026/calendario-anual/diciembre/hasta-31-diciembre.html
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/contenidos-lectura-facil/calendario-contribuyente-2026-simplificado-personas-fisicas.html
  - https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740      # Ley del IVA, art. 3 (Canarias, Ceuta y Melilla fuera del IVA)
  - https://www.boe.es/buscar/act.php?id=BOE-A-1992-28925      # Reglamento del IVA, arts. 71.4 y 81
  - https://www.boe.es/buscar/act.php?id=BOE-A-2007-6820       # Reglamento del IRPF, arts. 108.1, 109.2 y 111.1
  - https://www.boe.es/eli/es/o/2009/11/05/eha3111/con         # modelo 390, art. 8
  - https://www.boe.es/eli/es/o/2009/11/10/eha3127/con         # modelo 190, art. 5
  - https://www.boe.es/eli/es/o/2008/10/20/eha3012/con         # modelo 347, art. 10
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565      # Ley 39/2015, arts. 30 y 31
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-420
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-425
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-415
  - https://www.gobiernodecanarias.org/boc/2026/066/1094.html  # Decreto ley 3/2026 (REPEP)
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Colectivos/Trabajo+Autonomo/guia
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Categorias/Altas,+bajas+y+modificaciones/Bajas+y+modificaciones/BCRendimientos
  - https://www.navarra.es/es/hacienda/calendario-fiscal
  - https://www.boe.es/buscar/act.php?id=BOE-A-2023-24840      # RD 1007/2023 (VeriFactu)
  - https://www.hacienda.gob.es/sgt/gabsehacienda/nota-informativa-verifactu.pdf
  - https://www.boe.es/eli/es/rd/2026/03/25/238                # RD 238/2026 (factura electrónica)
  - https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20587  # Orden HAC/1028/2026
---

# Calendario fiscal del autónomo (octubre de 2026 a diciembre de 2027)

**La única fuente de fechas es `assets/calendario.yaml`.** Esta guía y `scripts/calendario.py` derivan de él. Si una fecha de aquí no coincide con el YAML, manda el YAML: avisa y abre un issue.

Riesgo: **Leer.** Un calendario no presenta nada. Cuando des una fecha a la persona, di siempre el **modelo**, el **organismo**, la **fecha límite de domiciliación** (si existe), la **fuente** y la fecha `verificado_el`. Si han pasado más de 60 días desde esa fecha, dilo y recomienda comprobarla en la fuente (regla 9 de `SKILL.md`).

## Uso del script

```bash
uv run scripts/calendario.py proximos --territorio comun --dias 45
uv run scripts/calendario.py proximos --territorio canarias --dias 45 --obligaciones 420,130,111,cuota_reta
uv run scripts/calendario.py proximos --territorio comun --dias 30 --desde 2027-01-10   # simular otra fecha
uv run scripts/calendario.py obligaciones --territorio canarias                        # códigos disponibles
uv run scripts/calendario.py validar                                                   # integridad del YAML
```

- `--territorio`: `comun`, `canarias`, `ceuta`, `melilla`, `navarra`, `bizkaia`, `gipuzkoa` o `alava`. Sale de `perfil-autonomo.md`.
- `--obligaciones`: los códigos del perfil (p. ej. `303,130,111,115,349,390,190,180,347,cuota_reta,base_reta`). Sin filtro, salen todos los del territorio.
- Cada fila trae `fecha`, `modelo`, `organismo`, `domiciliacion.hasta`, `estado`, `fuentes` y, si procede, `regla` y `nota`. Los avisos van en `avisos`.
- Las entradas `no_verificado` salen **aparte**, en `no_verificados`, con `fecha_orientativa`. **Nunca las presentes como plazo.**

## Estados de cada fecha

| Estado | Qué significa | Cómo decírselo a la persona |
|---|---|---|
| `verificado` | La fecha aparece literalmente en la fuente oficial citada | "Vence el X (fuente, verificado el ...)" |
| `regla` | Calculada con la regla literal de la norma u organismo más la regla de días inhábiles. El calendario oficial de ese año aún no estaba publicado | "Vence el X según la norma; la AEAT/ATC aún no ha publicado su calendario de 2027" |
| `no_verificado` | Sin fuente primaria comprobada | No es un plazo. "Hay que comprobarlo en ..." |

Recuento a 15-10-2026: **71 entradas, 85 filas por modelo** (31 verificadas, 48 por regla, 6 no verificadas).

## Regla de días inhábiles

- **AEAT:** si el último día es sábado, domingo o fiesta nacional, el plazo acaba el primer día hábil siguiente, y la domiciliación se amplía los mismos días. Entre el fin de la domiciliación y el del plazo hay "un mínimo de tres días hábiles o cinco naturales" (calendario de domiciliación 2026).
- **ATC:** misma regla para el 420 y el 425; la domiciliación "quedará ampliada en el mismo número de días".
- **Ley 39/2015:** art. 30 (cómputo de plazos) y art. 31.2.b (lo presentado en día inhábil se entiende presentado el primer día hábil siguiente). Por eso las **solicitudes** que acaban en fin de semana (p. ej. el cambio de base del 31-10-2026) conviene hacerlas el viernes anterior.
- **Festivos autonómicos y locales:** el art. 30.6 de la Ley 39/2015 los tiene en cuenta, pero no está verificado cómo lo aplica la AEAT a sus plazos. No cuentes con ellos: presenta antes.
- **2027:** la resolución de fiestas laborales de 2027 no se ha comprobado. Ninguna fecha calculada cae en fin de semana ni en 1 y 6 de enero, Viernes Santo (26 de marzo), 1 de mayo, 15 de agosto, 12 de octubre, 1 de noviembre o 6, 8 y 25 de diciembre.

## AEAT: declaraciones trimestrales

Común, Canarias, Ceuta y Melilla. El **303** y el **349** son solo del territorio común: en Canarias no hay IVA (IGIC en la ATC) y en Ceuta y Melilla tampoco (IPSI).

| Periodo | Plazo | Domiciliación hasta | Modelos | Estado | Base |
|---|---|---|---|---|---|
| 3T 2026 | **mar 20-10-2026** | 15-10-2026 | 303, 130, 131, 111, 115 | verificado | Calendario AEAT 2026 |
| 3T 2026 | mar 20-10-2026 | (sin ingreso) | 349 | verificado | Calendario AEAT 2026 |
| 4T 2026 | **mié 20-01-2027** | 15-01-2027 (regla) | 111, 115 | regla | RIRPF art. 108.1 |
| 4T 2026 | **lun 01-02-2027** | **no publicada** (en 2026 fue el 27-01) | 303 | verificado | AEAT: "Hasta el 1 de febrero de 2027" |
| 4T 2026 | lun 01-02-2027 | **no publicada** | 130, 131 | regla | RIRPF art. 111.1 (1-30 de enero; el 30 es sábado) |
| 4T 2026 | lun 01-02-2027 | (sin ingreso) | 349 | regla | RIVA art. 81 |
| 1T 2027 | mar 20-04-2027 | 15-04-2027 | 303, 130, 131, 111, 115 (+349) | regla | RIVA 71.4; RIRPF 108.1 y 111.1 |
| 2T 2027 | mar 20-07-2027 | 15-07-2027 | 303, 130, 131, 111, 115 (+349) | regla | ídem |
| 3T 2027 | mié 20-10-2027 | 15-10-2027 | 303, 130, 131, 111, 115 (+349) | regla | ídem |

- La domiciliación de 2027 sigue el patrón publicado para 2026 (del 1 al 15 cuando el plazo acaba el 20): es `regla`, no fecha publicada.
- Si la persona está en **REDEME o SII**, su 303 (y el 111 si es gran empresa) es **mensual**: no está cubierto aquí.
- Exención del 130: los profesionales no lo presentan si en el año anterior al menos el 70 % de sus ingresos tuvo retención (RIRPF art. 109.2).
- El 4T de 2027 vence en enero de 2028, fuera de la cobertura.

## AEAT: anuales, opciones y Renta

| Fecha | Qué | Territorio | Estado | Base |
|---|---|---|---|---|
| jue 05-11-2026 | Renta 2025: cargo del segundo plazo (solo si se fraccionó) | común, Canarias, Ceuta, Melilla | verificado | Calendario simplificado AEAT 2026 |
| jue 31-12-2026 | 036: renuncia o revocación de estimación directa simplificada y de módulos para 2027 | común, Canarias, Ceuta, Melilla | verificado | AEAT "Hasta el 31 de diciembre" |
| jue 31-12-2026 | 036: IVA simplificado y agricultura; opción o renuncia al criterio de caja para 2027 | común | verificado | ídem |
| lun 01-02-2027 | 390 resumen anual de IVA 2026 | común | regla | Orden EHA/3111/2009 art. 8 |
| lun 01-02-2027 | 190 resumen anual de retenciones 2026 | común, Canarias, Ceuta, Melilla | regla | Orden EHA/3127/2009 art. 5 |
| lun 01-02-2027 | 180 resumen anual de retenciones de alquileres 2026 | común, Canarias, Ceuta, Melilla | regla | RIRPF art. 108.1 |
| lun 01-03-2027 | 347 operaciones con terceros 2026 | común, Ceuta, Melilla | regla | Orden EHA/3012/2008 art. 10 ("mes de febrero"); en Baleares el 1-03 es festivo autonómico: presenta antes |

## Canarias: Agencia Tributaria Canaria (ATC)

En Canarias el IGIC va a la ATC y el IRPF, las retenciones y la Renta siguen en la AEAT (tablas de arriba). El 420 y el 425 se generan con el **programa de ayuda de la ATC** (fichero `.dec`), que luego se sube a la sede: no hay formulario web ni API pública. El agente prepara los datos; la persona genera el `.dec`, firma y presenta.

| Fecha | Qué | Domiciliación hasta | Estado | Base |
|---|---|---|---|---|
| mar 20-10-2026 | 420, 3T 2026 | 15-10-2026 | verificado | ATC modelo 420; SICAC 4015 |
| vie 01-01-2027 | **REPEP con umbral general de 50.000 €**: inclusión automática, salvo renuncia, si el volumen de 2026 no supera 50.000 € | — | verificado (hito) | Decreto ley 3/2026, BOC nº 66 |
| lun 01-02-2027 | 420, 4T 2026 ("todo el mes de enero"; el 31 es domingo) | 20-01-2027 (podría ser el 21: la ATC amplía la domiciliación los mismos días; usa el 20) | regla | ATC modelo 420 |
| lun 01-02-2027 | 425, resumen anual de 2026 (también los del REPEP, solo con las casillas informativas) | — | regla | ATC modelo 425; SICAC 4018 |
| lun 01-03-2027 | 415, operaciones con terceros de 2026 (más de 3.005,06 € con un mismo cliente o proveedor; hay exenciones) | — | regla | ATC modelo 415 ("mes de febrero") |
| mar 20-04-2027 | 420, 1T 2027 | 15-04-2027 | regla | ATC: 20 primeros días; domiciliación, 15 |
| mar 20-07-2027 | 420, 2T 2027 | 15-07-2027 | regla | ídem |
| mié 20-10-2027 | 420, 3T 2027 | 15-10-2027 | regla | ídem |

- **Quien está en el REPEP no presenta el 420** (solo es para el régimen general), pero **sí el 425**. Antes de preparar un 420 de 2027, comprueba el régimen (ver `perfil-autonomo.md`).
- La "declaración anual única" para el REPEP desde 2027 es un anuncio de prensa, no una norma.

## Seguridad Social (TGSS, igual en todo el Estado)

**Cuota mensual:** "se cargará en tu cuenta el último día hábil de cada mes" (guía de Import@ss). Fechas calculadas (estado `regla`):

| 2026 | 2027 (ene-jun) | 2027 (jul-dic) |
|---|---|---|
| oct: vie 30 | ene: vie 29 · feb: vie 26 · mar: mié 31 | jul: vie 30 · ago: mar 31 · sep: jue 30 |
| nov: lun 30 | abr: vie 30 · may: lun 31 | oct: vie 29 · nov: mar 30 |
| dic: jue 31 | jun: mié 30 | dic: vie 31 |

**Cambio de base de cotización** (hasta 6 veces al año; fechas literales de la TGSS, `verificado`):

| Último día para pedirlo | Efectos | Nota |
|---|---|---|
| 31-10-2026 (sábado) | 1-11-2026 | Por prudencia, el viernes 30 |
| 31-12-2026 | 1-01-2027 | |
| 28-02-2027 (domingo) | 1-03-2027 | Por prudencia, el viernes 26 |
| 30-04-2027 | 1-05-2027 | |
| 30-06-2027 | 1-07-2027 | |
| 31-08-2027 | 1-09-2027 | |
| 31-10-2027 (domingo) | 1-11-2027 | Por prudencia, el viernes 29 |
| 31-12-2027 | 1-01-2028 | |

- **Cambio de mutua:** antes del 1 de octubre, con efectos el 1 de enero. Para 2028: hasta el **30-09-2027** (`verificado`).
- **Regularización anual** (sin fecha fija): si sale a ingresar, hasta el último día del mes siguiente a la notificación; después, recargo del 10 % y luego del 20 %. Si sale a devolver, la TGSS devuelve de oficio antes del 30 de abril.
- **Cambio de cuenta de cargo:** del 1 al 13, efectos ese mes; desde el 14, el mes siguiente.

## Territorios forales, Ceuta y Melilla

En los forales los impuestos van a la Hacienda Foral, pero **la Seguridad Social es la TGSS**: la tabla de arriba vale también allí.

**Navarra** (calendario fiscal 2026 de Hacienda Foral, `verificado`; el resto, no verificado):

| Plazo | Modelo | Qué |
|---|---|---|
| 20-10-2026 | F69 | IVA, régimen simplificado, 3T 2026 |
| 20-10-2026 | 759 | Retenciones por alquiler de inmuebles urbanos (IRPF), 3T 2026 |
| 30-10-2026 | F69 | IVA, régimen general, 3T 2026 |
| 30-10-2026 | 715 | Retenciones de trabajo y actividades profesionales (IRPF), 3T 2026 |
| 03-11-2026 | 130 | Pago fraccionado del IRPF (empresarios y profesionales), 3T 2026 |

**Bizkaia, Gipuzkoa y Álava:** calendario **no verificado**. Consulta la fuente oficial: Gipuzkoa `https://www.gipuzkoa.eus/es/web/ogasuna/calendario-fiscal` (se carga dinámicamente); Bizkaia `https://www.batuz.eus/es/inicio` (calendario no localizado); Álava `https://egoitza.araba.eus` (calendario no localizado).

**Ceuta y Melilla:** valen las tablas de la AEAT salvo 303, 349 y 390. El **IPSI** lo gestiona cada ciudad autónoma y **no está cubierto**.

## Hitos normativos

| Fecha | Hito | Estado | Base |
|---|---|---|---|
| 01-01-2027 | VeriFactu: límite para contribuyentes del Impuesto sobre Sociedades (no autónomos en IRPF) | verificado | RD 1007/2023, DF 4ª (RDL 15/2025) |
| 01-01-2027 | REPEP a 50.000 € en Canarias | verificado | Decreto ley 3/2026 |
| **01-07-2027** | **VeriFactu para el resto, autónomos incluidos**: el software de facturación debe estar adaptado antes de esa fecha | verificado | RD 1007/2023, DF 4ª |
| 06-10-2027 | Factura electrónica obligatoria para quien factura más de 8 M€ | verificado | RD 238/2026 + Orden HAC/1028/2026 |
| 06-10-2028 | Factura electrónica obligatoria para el resto (autónomos incluidos) | verificado | ídem |
| 06-10-2029 | Personas físicas: informar del estado y pago de las facturas | verificado | RD 238/2026, DT 3ª |

> **VeriFactu y 2028:** el 5-10-2026 Hacienda anunció una **previsión** de aplazar VeriFactu a octubre de 2028. **No hay norma publicada**: hasta que salga en el BOE, la fecha legal es el **1-07-2027**. Dilo así y comprueba el BOE antes de afirmar otra cosa. VeriFactu no aplica en el País Vasco ni en Navarra (sistemas propios); la factura electrónica en territorio foral no está verificada.

## No verificado (no son plazos)

- **Renta 2026** (campaña previsiblemente de abril a junio de 2027) y su segundo plazo: los fija una orden ministerial cada primavera.
- **Domiciliación del 303 y del 130/131 del 4T de 2026**: la AEAT aún no la ha publicado.
- **184** (comunidades de bienes): en 2026 venció el 2-02; la norma del plazo no se ha comprobado.
- **347 en Canarias**: no verificado si se presenta además del 415 de la ATC.
- **Renuncia al REPEP y opciones de IGIC para 2027 (modelo 400)**: plazo y duración mínima de la renuncia sin verificar.
- **Opciones y renuncias del 036 para 2028** (en 2026 fue hasta el 31 de diciembre).
- **Calendarios forales** salvo el 3T de 2026 de Navarra; **IPSI** de Ceuta y Melilla.

## Cómo actualizar este calendario cada año

1. **Cuándo.** En cuanto la AEAT publique el "Calendario del contribuyente" del año siguiente (suele hacerlo en diciembre), el BOE publique la resolución de fiestas laborales y la ATC, la TGSS y las haciendas forales actualicen sus páginas. Repite la comprobación antes de cada versión del skill.
2. **Confirma las fechas `regla`.** Compara cada entrada `regla` del año con el calendario oficial. Si coincide, pásala a `verificado` y cambia la fuente al calendario nuevo. Si no coincide, corrige la fecha y anota la diferencia en el PR. Rellena las domiciliaciones que falten.
3. **Añade el año siguiente.** Copia el patrón trimestral (20 de abril, julio y octubre; enero para el 4T) con estado `regla` y la regla literal de la norma. Calcula los días inhábiles. Nada pasa a `verificado` sin la fecha publicada.
4. **Revisa los cambios normativos:** VeriFactu (texto consolidado del RD 1007/2023 en el BOE), factura electrónica (RD 238/2026), REPEP y modelos de la ATC (BOC), orden de cotización de autónomos (BOE), orden de la campaña de Renta, cambios de modelos o de plazos.
5. **Actualiza la cabecera del YAML:** `verificado_el`, `cobertura` y fuentes nuevas. Retira las entradas anteriores a la nueva cobertura.
6. **Valida:** `uv run scripts/calendario.py validar` debe salir con `"ok": true`. Después actualiza las tablas de esta guía (mismas fechas que el YAML) y su `verificado_el`.
7. **PR sin datos personales**, citando cada fuente (BOE, BOC, AEAT, ATC, Seguridad Social, hacienda foral).
