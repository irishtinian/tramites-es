---
verificado_el: 2026-10-15
estado_mapeo: verificado_sin_certificado
municipios_ejemplo: [Badajoz, Alcorcón]
fuentes:
  - https://sede.aytobadajoz.es/portal/entidades.do?ent_id=1&idioma=1        # portada (Badajoz)
  - https://sede.aytobadajoz.es/sede/catalogoTramites.do?ent_id=1&idioma=1   # catálogo (Badajoz)
  - https://sede.aytobadajoz.es/sede/tramitacionElectronica.do?asu_mod_cod=1&asu_cod=2&asunto=2&aplcorreo=4   # instancia general (Badajoz)
  - https://sede.aytobadajoz.es/sede/miCarpeta.do?ent_id=1&idioma=1          # Mi Carpeta (modal de acceso)
  - https://portalciudadano.ayto-alcorcon.es/portal/entidades.do?ent_id=1&idioma=1   # portada (Alcorcón)
  - https://portalciudadano.ayto-alcorcon.es/sede/tramitacionElectronica.do?asu_mod_cod=3&asu_cod=153   # DR de obra menor (Alcorcón)
  - https://tributos.aytobadajoz.es                                            # portal de tributos de Badajoz
---

# Plataforma Aytos (`portal/entidades.do`)

Riesgo: **Leer** (catálogo, Mi Carpeta) y **Preparar** (instancias, declaraciones responsables). Firmar, presentar, pagar y abrir notificaciones son **actos** (`firmar`, `presentar`, `pagar`, `comparecer`): los haces según los permisos que te dé tu usuario (`sede.py --permitir …`).

## Qué es y dónde se usa

- Sede de **Aytos Soluciones Informáticas** (grupo Berger-Levrault). El certificado TLS de sus instalaciones en la nube es de `*.blcloud.es`.
- Dónde: **Diputación de Badajoz** (plataforma provincial), Badajoz, Mérida, sur y oeste de Madrid (Alcorcón, Torrejón, Coslada, Majadahonda, Pinto, Aranjuez, Collado Villalba), Roquetas de Mar, El Puerto de Santa María, Arcos, Sanlúcar, Cornellà, Sant Boi.
- Cobertura estimada: ~65–80 ayuntamientos.

## Cómo adaptarla a tu ayuntamiento

```text
HOST   = dominio de la sede (propio o *.blcloud.es)
ENT_ID = entidad: suele ser 1, pero no lo asumas
M, C, A = códigos locales del asunto (asu_mod_cod, asu_cod, asunto)

Portada:   https://{HOST}/portal/entidades.do?ent_id={ENT_ID}&idioma=1
Catálogo:  https://{HOST}/sede/catalogoTramites.do?ent_id={ENT_ID}&idioma=1
Ficha:     https://{HOST}/sede/tramitacionElectronica.do?asu_mod_cod={M}&asu_cod={C}&asunto={A}&aplcorreo=4
Carpeta:   https://{HOST}/sede/miCarpeta.do?ent_id={ENT_ID}&idioma=1
```

- Cambian el dominio, `ent_id` y los códigos de asunto.
- Ejemplos: instancia general de Badajoz `asu_mod_cod=1&asu_cod=2&asunto=2`; declaración responsable de obra menor de Alcorcón `asu_mod_cod=3&asu_cod=153`. **No reutilices códigos en otro municipio.** Sácalos del catálogo.
- Si la sede está en un dominio del proveedor (`*.blcloud.es`), comprueba que es la sede que declara el propio ayuntamiento (enlace desde su web o censo de `buscar.py`) antes de usar el certificado.

## Acceso

- Mi Carpeta llama a `abrirLogin(...)` y abre un modal `form#formLogin`.
- Botones vistos:
  - `#firmar` (`onclick=pulsarFirmarIdentificate()`): identificación **firmando con AutoFirma**. Es el acto `firmar`: sin ese permiso, **sede.py lo bloquea**.
  - `#btnClave` (`onclick=pulsarLoginClave()`): pasarela Cl@ve. En la pasarela, el agente solo usa "DNIe / Certificado electrónico"; el certificado lo pide entonces `https://pasarela-ident.clave.gob.es`.
  - Según la instalación, también VÀLid, idCAT o Giltza. idCAT Mòbil y Giltza con contraseña o SMS son de la persona.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://sede.aytobadajoz.es` | `tls-probe`/`cert-probe`: sin mTLS. |
| `https://portalciudadano.ayto-alcorcon.es` | Sin mTLS. |
| `https://pasarela-ident.clave.gob.es` | Pide certificado en la rama Cl@ve "DNIe / Certificado" (`sede-clave.md`). |

- Ruta recomendada para el agente: **Cl@ve → DNIe / Certificado electrónico**, que no necesita firmar. La identificación por `#firmar` necesita el permiso `firmar` y AutoFirma. Retorno de Cl@ve a Mi Carpeta: **pendiente de verificación con certificado**.

## Trámites típicos del autónomo

| Trámite | Entrada | Sin permiso, paras en | Actos (con permiso los haces tú) |
|---|---|---|---|
| Instancia general | Ficha `tramitacionElectronica.do?...` (códigos del catálogo) | La ficha, con texto y adjuntos preparados | Identificarse, adjuntar, firmar y enviar: `firmar`, `presentar` |
| Declaración responsable de actividad u obra | Catálogo → actividades / urbanismo | El asunto, con la documentación preparada | Igual |
| Tributos, autoliquidaciones, pagos | Portada → enlaces de tributos u oficina tributaria | La consulta | Pagar: `pagar`; autoliquidar: `presentar`, `firmar` |
| Mis trámites | Mi Carpeta → Trámites | — (listar asientos y estados es libre) | — |
| Notificaciones | Mi Carpeta → Notificaciones | El listado | Abrir: `comparecer` |
| Cotejo de documentos por CSV | Verificador de documentos | El CSV preparado | El CAPTCHA lo resuelve la persona |

- **Badajoz:** tributos en el portal propio `https://tributos.aytobadajoz.es` (CiudadaNET). Hay pago con tarjeta (acto `pagar`; los datos de la tarjeta los mete la persona).
- **Alcorcón:** autoliquidaciones, tasas y consulta de deuda en el propio portal.
- Contenido de Mi Carpeta con sesión iniciada: **pendiente de verificación con certificado**.

## Firma

- **AutoFirma trifásica**, deducida de `firmaDigital.js`, `autoscript.js` y `pulsarFirmarIdentificate()`. No se ejecutó.
- Firmar es el acto `firmar`. Con ese permiso, `sede.py` pasa `afirma://` a AutoFirma (`setup-autofirma.md`); sin él, lo captura y bloquea `#firmar`.
- Éxito esperado: asiento y justificante en **Mi Carpeta → Trámites**. Los documentos emitidos llevan CSV. Verifica con `scripts/justificante.py` y en el listado.

## Trampas

- **CAPTCHA aritmético escrito en palabras** en el verificador público de documentos. Algunas instalaciones activan CAPTCHA en otros formularios (variable `incluirCaptcha`; visto en Torrejón). No se resuelve: lo hace la persona.
- El login con certificado "directo" es en realidad una firma AutoFirma: sin el permiso `firmar`, no intentes esquivar el bloqueo; entra por Cl@ve.
- El catálogo puede venir en latin-1: si el texto sale con caracteres raros, es la codificación, no un error de la sede.
- No se observó WAF.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en Badajoz y Alcorcón. No se pulsó ningún botón de acceso ni se resolvió el CAPTCHA.
