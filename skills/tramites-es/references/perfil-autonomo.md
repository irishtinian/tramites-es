---
verificado_el: 2026-10-15
fuentes:
  - https://sede.agenciatributaria.gob.es/Sede/procedimientoini/G322.shtml   # modelo 036 / Censos WEB (AEAT)
  - https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/folleto-actividades-economicas/11-notificaciones-electronicas/11_2-notificaciones-electronicas-obligatorias-neo.html
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565      # Ley 39/2015, art. 14.2 (obligados a relacionarse electrónicamente)
  - https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740      # Ley del IVA, art. 3 (Canarias, Ceuta y Melilla)
  - https://www.boe.es/buscar/act.php?id=BOE-A-2007-6820       # Reglamento del IRPF, arts. 108, 109.2 y 111
  - https://www.gobiernodecanarias.org/boc/2026/066/1094.html  # Decreto ley 3/2026 (REPEP), BOC nº 66
  - https://sede.gobiernodecanarias.org/sede/procedimientos_servicios/tramites/4015   # 420: solo régimen general
  - https://sede.gobiernodecanarias.org/sede/movil/procedimientos_servicios/tramites/4018  # 425: también el REPEP
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-400
  - https://www3.gobiernodecanarias.org/tributos/atc/w/modelo-415
  - https://sede.gobiernodecanarias.org/tributos/jsf/publico/certificados/certificados_individuales.jsp
  - https://portal.seg-social.gob.es/wps/portal/importass/importass/Colectivos/Trabajo+Autonomo/guia
  - https://www.seg-social.es/wps/portal/wss/internet/HerramientasWeb/51148  # notificaciones electrónicas obligatorias (TGSS)
---

# Perfil del autónomo: deducir sus obligaciones leyendo

Antes de dar plazos o preparar un modelo, el agente necesita el **perfil fiscal** de la persona: territorio, regímenes y qué obligaciones periódicas tiene. **Casi todo se puede leer** en las sedes con su certificado. Pregunta solo lo que no puedas leer.

Riesgo: **Leer.** No cambies datos censales, de cotización ni de contacto (regla 7 de `SKILL.md`). Si ves algo incoherente, explícaselo: la corrección (036, 400, Import@ss) la hace la persona.

Alcance: **persona física** con actividad. Si el titular es una sociedad (Impuesto sobre Sociedades), esta guía no vale: con certificado de representante, actúa solo para esa sociedad y avisa de que sus modelos son otros.

## 1. Orden de lectura

1. **AEAT, "Mis datos censales"** (o el certificado de situación censal): domicilio fiscal, actividades y epígrafes, locales, régimen de IVA, método de IRPF, alta en el ROI o en el REDEME. Es el reflejo del último **036**. Ruta: `sede-aeat.md`.
2. **AEAT, "Declaraciones presentadas"** del último año: qué modelos presentó de verdad. Es la mejor prueba de sus obligaciones reales (y de las que se dejó).
3. **Seguridad Social, Import@ss** (`sede-tgss-importass.md`): acreditación o informe de situación del alta en autónomos, "Base de cotización y rendimientos", recibos y mutua.
4. **Solo en Canarias, ATC** (`sede-atc.md`): certificados de "declaraciones censales presentadas", "actividades y locales" y "situación tributaria" (gratis, con CSV), y los 420 presentados. El acceso con certificado a la ATC puede pasar por AutoFirma: si aparece, lo hace la persona.
5. **Pregunta lo que falte** (§6).

Los nombres exactos de los apartados pueden cambiar: si no coinciden con la pantalla, confía en la pantalla y avisa.

## 2. Territorio fiscal

Es lo primero, porque cambia los modelos, las sedes y el calendario. Se deduce del **domicilio fiscal** de "Mis datos censales" (y de dónde presenta sus declaraciones).

| Territorio | Impuesto indirecto | IRPF y retenciones | Código para `calendario.py` |
|---|---|---|---|
| Común (península y Baleares) | IVA en la AEAT (303, 390, 349) | AEAT | `comun` |
| Canarias | **IGIC en la ATC** (420, 425, 415; censo 400). No hay 303, 390 ni 349 | AEAT (130/131, 111, 115, 190, 180, Renta) | `canarias` |
| Ceuta / Melilla | **IPSI** de la ciudad autónoma (no cubierto). No hay IVA | AEAT | `ceuta` / `melilla` |
| Navarra | IVA foral (F69) en Hacienda Foral | Hacienda Foral (130, 715, 759…) | `navarra` (parcial) |
| Bizkaia / Gipuzkoa / Álava | Hacienda Foral de cada territorio | Hacienda Foral | `bizkaia` / `gipuzkoa` / `alava` (no cubierto) |

- La **Seguridad Social es la TGSS en todo el Estado**, también en los forales.
- Señal de foral: la AEAT no tiene declaraciones de IRPF o IVA de la persona y ella presenta en otra sede. Si opera en varios territorios, el reparto puede ser mixto: no lo deduzcas, pregunta y recomienda un profesional.
- Ceuta, Melilla y Canarias quedan fuera del IVA por el art. 3 de la Ley del IVA.

## 3. Impuesto indirecto y régimen

**Territorio común (IVA):**

| Lo que lees | Obligaciones | Códigos |
|---|---|---|
| Régimen general o simplificado | 303 trimestral + 390 anual | `303`, `390` |
| Criterio de caja (opción) | Igual: 303 + 390 | `303`, `390` |
| Recargo de equivalencia (comercio minorista) | Normalmente sin 303 por esa actividad; compruébalo en sus declaraciones presentadas | — |
| Solo operaciones exentas | Normalmente sin 303 ni 390; compruébalo igual | — |
| Inscrito en el **REDEME** o en el SII | 303 **mensual** (no cubierto por el calendario) | — |
| Alta en el **ROI** / compras o ventas a empresas de la UE | 349 | `349` |

**Canarias (IGIC), con la regla del REPEP corregida** (Decreto ley 3/2026, BOC nº 66 de 7-04-2026):

- **Régimen general:** 420 trimestral y 425 anual. Códigos `420`, `425`.
- **REPEP** (régimen especial del pequeño empresario o profesional): **no presenta el 420** (solo es para el régimen general, SICAC 4015), **pero sí el 425**, solo con las casillas informativas (SICAC 4018). Código `425`.
- **Quién está en el REPEP:**
  - Desde el **1-07-2026**, solo quien ejerció la **opción extraordinaria en julio de 2026** con el modelo 400 y tuvo un volumen de operaciones de 2025 no superior a 50.000 €. Esa ventana **ya está cerrada**.
  - Desde el **1-01-2027**, quedan incluidas **automáticamente, salvo renuncia**, las personas físicas cuyo volumen del año anterior (2026) no supere **50.000 €**.
  - Cómo leerlo: régimen de IGIC en los datos censales de la ATC. Para anticipar 2027, puedes estimar el volumen de 2026 sumando los 420 presentados, pero **la inclusión real se confirma en la ATC**. Si la persona renunció, sigue en régimen general.
  - No verificado: plazo y duración mínima de la renuncia, y la "declaración anual única" anunciada en prensa.
- **415** (operaciones con terceros en la ATC): si supera 3.005,06 € con un mismo cliente o proveedor en el año (hay exenciones). Código `415`.
- Otros regímenes de IGIC (simplificado, comerciante minorista): no cubiertos; deriva a la ATC.

## 4. IRPF, retenciones y Seguridad Social

| Rasgo | Dónde se lee | Obligaciones | Códigos |
|---|---|---|---|
| Estimación directa (normal o simplificada) | Datos censales; 130 presentados | 130 trimestral | `130` |
| Profesional con al menos el 70 % de ingresos con retención el año anterior | Facturas emitidas, retenciones en la Renta | Sin 130 (RIRPF art. 109.2) | — |
| Estimación objetiva (módulos) | Datos censales; 131 presentados | 131 trimestral | `131` |
| Cualquier actividad | — | Renta anual (100) | `100` |
| **Empleados** | 111 y 190 con perceptores de trabajo; la persona conoce su código de cuenta de cotización | 111 trimestral + 190 anual (y cotización de sus trabajadores, fuera de este calendario) | `111`, `190` |
| Paga facturas de **profesionales con retención** | 111 presentados; facturas recibidas | 111 + 190 | `111`, `190` |
| **Local alquilado** (inmueble urbano) | Locales en los datos censales; 115 presentados | 115 trimestral + 180 anual | `115`, `180` |
| Operaciones con un tercero por encima del umbral anual | 347 presentados; libros | 347 (común, Ceuta, Melilla); en Canarias, 415 | `347` / `415` |
| Comunidad de bienes o sociedad civil | Datos censales de la entidad | 184 (fecha no verificada) | `184` |
| Alta en autónomos | Import@ss | Cuota mensual; cambio de base 6 veces al año | `cuota_reta`, `base_reta` |
| **Mutua** colaboradora | Import@ss (resolución de alta) | Cambio antes del 1 de octubre, efectos 1 de enero | `mutua` |
| Opciones de régimen para el año siguiente | Datos censales | 036 en diciembre (y 400 en Canarias) | `036`, `400` |

**Notificaciones** (no son plazos de calendario, pero son parte del perfil):
- Con la **Seguridad Social**, todo autónomo está obligado a la notificación electrónica.
- Con la **AEAT**, están obligados, entre otros, los sujetos del **art. 14.2 de la Ley 39/2015** (por ejemplo, quien ejerce una profesión con **colegiación obligatoria**, en los trámites de esa profesión) y los inscritos en el **REDEME**. El alta en NEO es automática.
- Por eso hay que saber si la persona está **colegiada de forma obligatoria** (no se lee en las sedes: pregúntalo).

## 5. De rasgos a obligaciones: tabla resumen

| Rasgo | Común | Canarias | Ceuta / Melilla |
|---|---|---|---|
| Base (todo autónomo) | `100`, `cuota_reta`, `base_reta`, `mutua` | igual | igual |
| Impuesto indirecto, régimen general | `303`, `390` | `420`, `425` | IPSI (no cubierto) |
| REPEP (Canarias) | — | `425` (sin `420`) | — |
| Intracomunitarias | `349` | — | — |
| Estimación directa | `130` | `130` | `130` |
| Módulos | `131` | `131` | `131` |
| Empleados o profesionales con retención | `111`, `190` | `111`, `190` | `111`, `190` |
| Local alquilado | `115`, `180` | `115`, `180` | `115`, `180` |
| Operaciones con terceros por encima del umbral | `347` | `415` (347 no verificado) | `347` |
| Opciones de régimen | `036` | `036`, `400` | `036` |

Con esa lista, llama a:

```bash
uv run scripts/calendario.py proximos --territorio canarias --dias 45 --obligaciones 420,425,130,111,190,115,180,100,cuota_reta,base_reta
```

## 6. Preguntas mínimas (solo si no se puede leer)

1. ¿En qué comunidad o territorio tienes el domicilio fiscal? (solo el territorio, no la dirección)
2. ¿Tienes trabajadores? ¿Pagas facturas de profesionales con retención de IRPF?
3. ¿Alquilas el local donde trabajas?
4. ¿Compras o vendes a empresas de otros países de la UE?
5. ¿Ejerces una profesión con colegiación obligatoria?
6. En Canarias: ¿estás en el régimen general del IGIC o en el REPEP? ¿Has renunciado al REPEP?
7. ¿Eres comunidad de bienes o sociedad civil?

## 7. Incoherencias que suelen provocar requerimientos

Compruébalas al leer el perfil y antes de preparar cualquier modelo. Avisa a la persona; no corrijas nada tú.

- La suma de los cuatro **303** del año debe cuadrar con el **390** (bases, cuotas, compensaciones). En Canarias: suma de los **420** = **425**.
- **390** frente a **347**: lo declarado con cada tercero debe cuadrar con lo que declaran ellos.
- **349** frente a las casillas de entregas y adquisiciones intracomunitarias del **303**.
- Suma de los **111** = **190**. Suma de los **115** = **180**.
- Ingresos del **130** frente a bases del **303** (ojo con el criterio de caja y las operaciones exentas).
- **130** acumulado del 4T frente al rendimiento de la actividad y los pagos fraccionados en la **Renta**.
- Retenciones soportadas en la **Renta** = las que declaran los clientes en su **190**.
- Epígrafes del **036** = actividad real facturada = **CNAE** de la Seguridad Social.
- **Rendimientos previstos** declarados a la TGSS frente al rendimiento neto que va saliendo en el **130** (si se infraestiman, la regularización llega a ingresar).
- **Domicilio fiscal** coherente entre AEAT, TGSS y ATC; si no, las notificaciones se pierden.
- Otras señales: modelos que "deberían" estar y no están (p. ej. 115 con local alquilado en el censo) o modelos presentados sin el rasgo que los justifica.

## 8. Resultado: el perfil

Devuelve el perfil a la persona para que lo confirme. **Sin NIF, nombres, direcciones ni IBAN.** No lo guardes en notas ni memorias sin su permiso (regla 8).

```yaml
leido_el: AAAA-MM-DD
titular: persona_fisica
territorio: canarias                 # comun | canarias | ceuta | melilla | navarra | bizkaia | gipuzkoa | alava
indirecto: {impuesto: IGIC, regimen: general}   # IVA: general | simplificado | recargo | exento; IGIC: general | repep
irpf: {metodo: estimacion_directa}  # estimacion_directa | estimacion_objetiva
retenedor: {trabajadores: false, profesionales: true, alquiler_local: true}
intracomunitarias: false
colegiacion_obligatoria: false
mutua: "<MUTUA>"
obligaciones: ["420", "425", "130", "111", "190", "115", "180", "100", cuota_reta, base_reta, mutua]
fuentes_leidas: [aeat_datos_censales, aeat_declaraciones_presentadas, tgss_importass, atc_censales]
pendiente_de_confirmar: ["régimen de IGIC en 2027 (REPEP automático si el volumen de 2026 no supera 50.000 €)"]
```

Después: plazos con `calendario-fiscal.md` y `scripts/calendario.py`.
