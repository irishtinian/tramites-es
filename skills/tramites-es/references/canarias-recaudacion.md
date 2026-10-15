---
verificado_el: 2026-10-15
estado_mapeo: parcial   # tablas y portadas oficiales consultadas por GET (14-15/10/2026); solo el Consorcio de Tenerife está mapeado con certificado
fuentes:
  - https://www.tributostenerife.es/organismos
  - https://www.tributostenerife.es/sites/cttstat/encomiendas.html
  - https://sede.tributostenerife.es/sta/CarpetaPublic/Public?APP_CODE=STA&PAGE_CODE=FRONTAL_OVC
  - https://www.valoragt.com/oficina-virtual
  - https://www.valoragt.com/cuerpo_infmunicipal.xhtml
  - https://www.redtributarialanzarote.es
  - https://tributos.aytolalaguna.es/sta/CarpetaPublic/doEvent?APP_CODE=STA&PAGE_CODE=OVC_HOME
---

# Canarias: quién cobra los tributos locales en cada isla

## Para qué sirve

Los recibos municipales de un autónomo (IBI, IAE, vehículos o IVTM, basura, plusvalía, terrazas y vados) no siempre están en la sede de su ayuntamiento. En Canarias, **tres organismos cobran para unos 55 de los 88 municipios**: el Consorcio de Tributos de Tenerife, Valora (Gran Canaria) y la Red Tributaria de Lanzarote. Esta guía dice dónde mirar. El acceso a cada oficina está en su receta:
- Consorcio y oficinas STA: `plataforma-tao-sta.md`;
- oficinas GTT: `plataforma-gtt.md`.

Riesgo: **leer**. Consultar recibos es de solo lectura. Pagar, domiciliar o fraccionar lo hace la persona.

## Cómo decidirlo

1. Busca el municipio:
   ```bash
   uv run scripts/buscar.py --municipio "Nombre del municipio"
   ```
   El censo da la sede y la plataforma, pero todavía **no trae el recaudador**. Usa las tablas de abajo.
2. Mira la isla y el tributo. Si el municipio está en el Consorcio, comprueba en la tabla de encomiendas si **ese** tributo está encomendado.
3. Si no sale aquí o la fila dice «sin verificar», busca en la web municipal el enlace «Tributos», «Recaudación» o «Pago de recibos», y confirma que el dominio es oficial antes de usar el certificado (regla 6 de `SKILL.md`).

## Tenerife, El Hierro, parte de La Palma y Tuineje: Consorcio de Tributos de la Isla de Tenerife (CTT)

- **Sede (STA):** `https://sede.tributostenerife.es`. Recibos con certificado: `https://sede.tributostenerife.es/sta/CarpetaPrivate/Certificate?APP_CODE=STA&PAGE_CODE=RECIBOS`, verificado con certificado el 15-10-2026. Carta de pago en voluntaria sin acceso: `PAGE_CODE=ACCESO_DEUDA`. En `assets/sedes.yaml`: `--sede consorcio-tenerife`.
- **Miembros** (41 entidades según su web):
  - 28 de los 31 ayuntamientos de Tenerife: todos **salvo Santa Cruz de Tenerife, Adeje y La Guancha**;
  - los 3 de El Hierro (Valverde, La Frontera, El Pinar);
  - 3 de La Palma (Puntallana, Tazacorte, Villa de Mazo);
  - 7 organismos insulares y municipales (Cabildo, Consejo Insular de Aguas, gerencias de urbanismo de La Laguna y Santa Cruz…).
  - Además, **Tuineje** (Fuerteventura) le encomienda varios tributos.
- **Qué cobra:** depende del municipio y del tributo. La tabla oficial está en `https://www.tributostenerife.es/sites/cttstat/encomiendas.html` (G = gestión, Rv = voluntaria, Re = ejecutiva). Lo esencial:
  - **IBI e IAE:** gestión y cobro en el CTT en todos los miembros, **salvo La Laguna**, que solo encomienda la ejecutiva.
  - **Arona:** solo IBI e IAE. El resto se cobra en su oficina STA propia (`https://sta.arona.org`).
  - **Basura:** casi siempre el ayuntamiento lleva el padrón (G) y el CTT cobra (Rv/Re). **El alta o baja de la tasa de un local se pide al ayuntamiento**; el recibo llega del CTT.
  - **IVTM:** en Arico, El Rosario, San Miguel de Abona y Tegueste la gestión es municipal y el cobro del CTT.
  - **Ocupación del dominio público** (terrazas, vados): solo encomendada en algunos municipios. En los demás, la autorización y la liquidación son municipales.
- **La Laguna:** la voluntaria la cobra el ayuntamiento en su OVC STA (`https://tributos.aytolalaguna.es`); la ejecutiva, el CTT (desde noviembre de 2023).
- **Tuineje** encomienda IBI, IAE, IVTM, plusvalía y ocupación del dominio público al CTT. Tiene además una OVT STA propia (`tributos.tuineje.es`); la relación entre las dos no está verificada.

Tenerife fuera del CTT:

| Municipio | Quién cobra | Dónde |
|---|---|---|
| Santa Cruz de Tenerife | Ayuntamiento | OVC STA `https://ovc.santacruzdetenerife.es` (`--sede santa-cruz-tenerife`). Su Gerencia de Urbanismo sí está en el CTT |
| Adeje | Ayuntamiento | OVT GTT `https://adeje.tributoslocales.es/380015/AADEJE/` (`--sede adeje-tributos`) |
| La Guancha | Ayuntamiento | Departamento de Renta y Recaudación; sin oficina virtual mapeada |

## Gran Canaria: Valora Gestión Tributaria (Cabildo)

- **Organismo autónomo del Cabildo de Gran Canaria.** Oficina virtual: `https://www.valoragt.com/oficina-virtual`. **No mapeada con `sede.py`.**
- Con certificado ofrece notificaciones, deudas, fraccionamiento, recibos pagados, domiciliaciones, plan de pago personalizado e **informe de no débitos** (el equivalente al certificado de estar al corriente). Sin identificarse, trámites con CSV o localizador.
- **Municipios en su selector** (15 de 21): Agaete, Artenara, Firgas, Gáldar, Ingenio, La Aldea de San Nicolás, Las Palmas de Gran Canaria, Moya, Santa Brígida, Santa María de Guía, Tejeda, Telde, Teror, Valsequillo y Vega de San Mateo.
- **Ojo con Las Palmas de Gran Canaria:** sale en el selector, pero cobra sus recibos en su OVT GTT propia (`https://laspalmasgc.tributoslocales.es/350163/APALMASGC`). Qué lleva Valora para la capital está sin verificar.
- **Fuera de Valora:**
  - Arucas: propio, OVT GTT `arucas.tributoslocales.es`;
  - Agüimes: propio, oficina STA `oat.aguimes.es`;
  - Mogán: propio, a través de la empresa municipal Gestmogán;
  - Santa Lucía de Tirajana: propio, a través de una empresa municipal;
  - San Bartolomé de Tirajana y Valleseco: propio (sin verificar).

## Lanzarote: Red Tributaria Lanzarote (Cabildo)

- **Organismo autónomo del Cabildo.** Delegan **Arrecife, Haría, San Bartolomé, Teguise y Tinajo**. Gestiona IBI, IAE, IVTM, ICIO, plusvalía, basura, vados y ocupación de la vía pública, entre otros. Tiene plan personalizado de pago.
- Web: `https://www.redtributarialanzarote.es`. Sede en Gestiona: `https://redtributarialanzarote.sedelectronica.es` (`plataforma-gestiona.md`). OVT GTT en versión antigua (`ovtlanzarote.tributoslocales.es/ovt/…`), **sin receta**.
- Tías y Yaiza: propio (sin verificar).

## Resto de islas

| Isla | Situación |
|---|---|
| **Fuerteventura** | No hay organismo insular. Cada ayuntamiento cobra lo suyo, salvo Tuineje (CTT). Antigua y Pájara tienen oficina tributaria propia; Betancuria y Puerto del Rosario usan STA; La Oliva, sin verificar |
| **La Palma** | No hay organismo insular. Puntallana, Tazacorte y Villa de Mazo están en el CTT. Breña Alta, Breña Baja, Puntagorda y San Andrés y Sauces cobran por una pasarela privada de «Recaudación Municipal» (`gestiondetributos.com`). El Paso y Los Llanos de Aridane tienen oficina tributaria propia. El resto, sin verificar |
| **La Gomera** | Sin organismo insular conocido. Alajeró y Valle Gran Rey, propio (sin verificar); Agulo, Hermigua, San Sebastián y Vallehermoso, sin dato |
| **El Hierro** | Los 3 municipios, en el CTT |

**Pasarela privada `gestiondetributos.com`:** no es un dominio de la Administración. No presentes el certificado ahí sin que la persona confirme que es el canal que le indica su ayuntamiento. Mejor: que pague ella.

## Trampas

- **Mismo recibo, dos sitios:** la tasa de basura se gestiona en el ayuntamiento y se cobra en el CTT. Para darla de alta o baja, ayuntamiento; para pagarla o ver el recibo, CTT.
- **La Laguna:** voluntaria en el ayuntamiento, ejecutiva en el CTT. Un recibo puede «cambiar de casa» al pasar a ejecutiva.
- **Arona:** IBI e IAE en el CTT; el resto, en `sta.arona.org`.
- **Granadilla:** su oficina STA tiene recibos propios, pero el IBI, el IAE, el IVTM y la plusvalía están encomendados al CTT, y la basura la cobra el CTT. Ante la duda, mira primero el CTT.
- **Las Palmas de GC** aparece en Valora, pero cobra en su OVT propia.
- **El CTT y la sede de Granadilla** usan la misma plataforma (STA), pero cada una con sus `PAGE_CODE` y trámites.

## Sin verificar

- Recaudador de Fuencaliente, Santa Cruz de La Palma, Agulo, Hermigua, San Sebastián de La Gomera, Vallehermoso y La Oliva.
- «Propio» deducido solo por una página de recaudación: Barlovento, Garafía, Tijarafe, Alajeró, Valle Gran Rey, San Bartolomé de Tirajana, Valleseco, Tías, Yaiza, Betancuria y Puerto del Rosario.
- Qué tributos de cada municipio lleva Valora (y si lleva alguno de Las Palmas de GC).
- Si la ATC tiene convenios de recaudación con ayuntamientos.
- Valora y la Red Tributaria de Lanzarote no están mapeadas con `sede.py`: no hay origins verificados.

## Fuentes

- Investigación del proyecto (R2 §6, 14-15/10/2026): un GET a la portada de los 88 municipios, lista de miembros y tabla de encomiendas del CTT, selector de Valora y portada de la Red Tributaria de Lanzarote.
- Mapeo en vivo de tramites-es del 15-10-2026: Consorcio de Tenerife, Granadilla, Santa Cruz, Arona y Adeje (tributos). Sin datos personales.
- Páginas oficiales citadas en la cabecera.
