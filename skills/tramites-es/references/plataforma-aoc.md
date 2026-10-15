---
verificado_el: 2026-10-15
estado_mapeo: verificado_sin_certificado
municipios_ejemplo: [Sort, Baix Pallars]
fuentes:
  - https://seu-e.cat/ca/web/sort                         # Seu-e de Sort (portada pública)
  - https://seu-e.cat/ca/web/sort/tramits-i-gestions      # catálogo público
  - https://seu-e.cat/ca/web/sort/tramits-i-gestions/-/tramits/tramit/14767856   # instancia genérica (Sort)
  - https://seu-e.cat/ca/web/baixpallars/tramits-i-gestions/-/tramits/tramit/14360794   # instancia genérica (Baix Pallars)
  - https://seu-e.cat/mygov/2520940003                    # MyGov de Sort: redirige a VÀLid
  - https://www.aoc.cat/serveis-aoc/valid/                # VÀLid, servicio de identificación del Consorci AOC
  - https://www.aoc.cat/en/blog/2024/e-notum-sintegra-amb-la-dehu/   # e-NOTUM y DEHú (16-dic-2024)
---

# Plataforma AOC (Seu-e, e-TRAM, VÀLid, MyGov, e-NOTUM) — Cataluña

Riesgo: **Leer** (catálogo, seguimiento, listado de notificaciones) y **Preparar** (instancias y comunicaciones). Firmar, presentar, pagar y abrir notificaciones lo hace la persona.

## Qué es y dónde se usa

- El **Consorci AOC** (sector público de la Generalitat) da a los entes locales catalanes varias piezas:
  - **Seu-e**: la sede pública (catálogo, fichas de trámite).
  - **e-TRAM**: el tramitador que ejecuta el trámite.
  - **VÀLid**: la identificación (certificado/DNIe, Cl@ve, idCAT Mòbil).
  - **MyGov / El meu espai**: el seguimiento de trámites.
  - **e-NOTUM**: las notificaciones.
- Casi todos los municipios catalanes usan algún servicio AOC, pero no todos tienen la sede en Seu-e. Los pequeños sí; ciudades como L'Hospitalet, Sabadell (OpenSIAC), Badalona (TAO) o Mataró (GSede) tienen otra sede y solo usan e-NOTUM o e-TAULER.
- Cobertura estimada: ~800–1.000 entes con algún servicio AOC; ~383 sedes registradas en Seu-e según un dato antiguo. Son estimaciones, no un censo.
- Barcelona usa VÀLid, pero su sede es propia: `plataforma-barcelona.md`.

## Cómo adaptarla a tu ayuntamiento

```text
SLUG      = nombre del ente en la URL de Seu-e (sort, baixpallars…)
ENS       = código AOC del ente, de 10 dígitos (NO es el DIR3)
TRAMIT_ID = identificador del trámite en Seu-e

Sede:       https://seu-e.cat/ca/web/{SLUG}
Catálogo:   https://seu-e.cat/ca/web/{SLUG}/tramits-i-gestions
Categoría:  https://seu-e.cat/ca/web/{SLUG}/tramits-i-gestions/-/tramits/classificacio/{CATEGORY_ID}
Ficha:      https://seu-e.cat/ca/web/{SLUG}/tramits-i-gestions/-/tramits/tramit/{TRAMIT_ID}
Ejecución:  https://etram.seu-e.cat/tramits/{ENS}/{TRAMIT}
Mi espacio: https://seu-e.cat/mygov/{ENS}
```

| Municipio | SLUG | ENS | Instancia genérica (TRAMIT_ID) |
|---|---|---|---|
| Sort | `sort` | `2520940003` | `14767856` |
| Baix Pallars | `baixpallars` | `2503900000` | `14360794` |

- Cambian `SLUG`, `ENS` y los IDs de categoría y de trámite. **El mismo trámite tiene IDs distintos en cada ente.**
- El `ENS` no se deduce del dominio: sácalo del enlace a MyGov o a e-TRAM de la propia Seu-e del municipio.
- Busca los IDs siempre en el catálogo vigente del municipio. No copies los del ejemplo.

## Acceso

- `https://seu-e.cat/mygov/{ENS}` redirige a VÀLid (`https://valid.aoc.cat/o/oauth2/auth?...&codi_ens={ENS}`).
- Selectores en VÀLid:
  - **Certificado/DNIe:** `button#btnContinuaCert`. Es el único que usa el agente.
  - Cl@ve: `button#btnContinuaClave` (`onclick=submitLoginForm('clave')`). Si se usa, en la pasarela Cl@ve solo vale "DNIe / Certificado electrónico".
  - **idCAT Mòbil** (código por SMS): es de la persona. El agente no lo usa, igual que Cl@ve PIN.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://valid.aoc.cat` | `tls-probe` y `cert-probe`: no pide certificado en el handshake. Es donde está el botón de certificado. Dónde se pide realmente: **pendiente de verificación con certificado**. |
| `https://seu-e.cat`, `https://etram.seu-e.cat` | Sin mTLS. |

- En otras sedes catalanas el OAuth de VÀLid aparece en otro host de `aoc.cat`. Si la redirección termina en un host distinto de `valid.aoc.cat`, comprueba que es del Consorci AOC y añádelo a los origins antes de usar el certificado.
- No guardes `p_auth`, `state` ni otros parámetros OAuth: caducan con la sesión.

## Trámites típicos del autónomo

| Trámite | Entrada | Dónde para el agente | Qué hace la persona |
|---|---|---|---|
| Instància genèrica (instancia general) | Ficha `.../tramits/tramit/{TRAMIT_ID}` (ver tabla de ejemplo) | En la ficha, con el texto y los adjuntos preparados. Si sede.py bloquea "Tramitar", ese clic es de la persona | Pulsa "Tramitar", se identifica, revisa, adjunta, firma y envía |
| Comunicación o declaración de actividad, licencias | Catálogo → categoría de indústria/comerç o urbanisme | Localiza la ficha y prepara la documentación | Igual que la instancia |
| Tasas, tributos, recibos | Catálogo → categoría de recaptació | Localiza la ficha o el recaudador externo | Paga o pide el certificado |
| Seguimiento de trámites | `https://seu-e.cat/mygov/{ENS}` → "Consulta els teus tràmits" | Lista estado y fechas | — |
| Notificaciones | e-NOTUM, desde MyGov | **Solo lista** remitente, asunto y fechas | Abre la notificación ella, si quiere |

- Los recibos y certificados tributarios dependen del organismo: muchos municipios catalanes los tienen en el ORGT de la Diputació de Barcelona u otro recaudador. Usa `buscar.py` (columna `recaudador`) o pide a la persona un recibo.
- Desde el 16-dic-2024 e-NOTUM está integrado con DEHú, pero **sin la Generalitat ni su sector público**. Las notificaciones municipales pueden verse en los dos sitios.
- Contenido de MyGov y e-NOTUM con sesión iniciada: **pendiente de verificación con certificado**.

## Firma

- **Deducida, no verificada:** e-TRAM combina la identificación VÀLid con la firma del formulario y los documentos según el trámite. VÀLid admite firma no criptográfica tras identificarse y firma con certificado.
- Cualquier firma (VÀLid, AutoFirma, idCAT Mòbil) la hace la persona. sede.py captura `afirma://` y bloquea los botones de firmar y enviar.
- Éxito esperado: asiento o justificante de registro en el trámite y aparición posterior en MyGov. Confírmalo con `scripts/justificante.py` y en el listado de MyGov, no con la pantalla de "correcto".

## Trampas

- **reCAPTCHA invisible** cargado en VÀLid. No apareció reto en el mapeo. Si aparece, para y que lo resuelva la persona.
- Liferay añade `p_auth` a los enlaces: nunca lo uses como deep link.
- Que un municipio tenga e-NOTUM o e-TAULER no significa que su sede sea Seu-e. Confirma que la URL final es `seu-e.cat/<idioma>/web/<slug>` o `etram.seu-e.cat`.
- Hay dominios antiguos de Seu-e caducados que redirigen a webs ajenas. Si la redirección sale de `seu-e.cat` o `aoc.cat`, para.
- No se observaron iframes ni WAF.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en Sort y Baix Pallars: no se pulsó ningún botón de identificación, ni se creó borrador, firma o envío.
