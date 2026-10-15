---
verificado_el: 2026-10-15
fuentes:
  - https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565   # Ley 39/2015, art. 16.4 (registro en cualquier administración)
  - https://sedipualba.es/entidades-adheridas/               # entidades de Sedipualb@
---

# Plataformas municipales: índice

Muchos ayuntamientos comparten la misma plataforma de sede. Una **receta de plataforma** sirve para todos ellos cambiando el dominio y los códigos locales. Las grandes ciudades tienen sede propia y guía propia.

## Tabla

Municipios: estimaciones de nuestra investigación de octubre de 2026 (sondeo de ~1.050 municipios más revisión regional), no un censo oficial.

| Plataforma | Slug | Municipios (aprox.) | Acceso para el agente | Firma | Estado de la receta | Guía |
|---|---|---|---|---|---|---|
| Gestiona (esPublico) | `gestiona` | ~4.300 | Cl@ve → DNIe/Certificado (en Cataluña, también VÀLid) | Certificado o firma no criptográfica, según el trámite | Parcial (lectura verificada con certificado) | `plataforma-gestiona.md` |
| TAO / STA (T-Systems) | `tao-sta` | ~80–100 | Certificado directo o Cl@ve | AutoFirma | Parcial (lectura verificada con certificado) | `plataforma-tao-sta.md` |
| Oficina tributaria GTT (`*.tributoslocales.es`) | `gtt` | ~18 oficinas supramunicipales y las de muchas ciudades | Certificado (`certifica.gtt.es`); según la entidad, Cl@ve o DNI/NIF | — (consulta y pago) | Parcial (lectura verificada con certificado) | `plataforma-gtt.md` |
| AOC (Seu-e, e-TRAM, VÀLid) | `aoc` | ~800–1.000 con algún servicio; ~383 sedes Seu-e | VÀLid → certificado/DNIe | Deducida, sin verificar | Verificada sin certificado | `plataforma-aoc.md` |
| Sedipualb@ | `sedipualba` | ~400 (900 entidades) | Certificado directo o Cl@ve (iframe) | AutoFirma / SEFYCU | Verificada sin certificado | `plataforma-sedipualba.md` |
| GSede / MOAD | `gsede-moad` | ~80–100 | Certificado directo o Cl@ve | AutoFirma | Verificada sin certificado | `plataforma-gsede-moad.md` |
| Aytos | `aytos` | ~65–80 | Cl@ve → certificado (el acceso "firmando" necesita el permiso `firmar`) | AutoFirma trifásica | Verificada sin certificado | `plataforma-aytos.md` |
| eXperta / PAEMUR | `experta-paemur` | ~60–100 | Certificado o Cl@ve | AutoFirma | Parcial (un ejemplo degradado) | `plataforma-experta-paemur.md` |
| eAdmin / GestDoc | `eadmin-gestdoc` | ~20–30 | Cl@ve → certificado | AutoFirma | Verificada sin certificado | `plataforma-eadmin-gestdoc.md` |
| OpenSIAC (gtt) | `opensiac` | ~35–60 | Cl@ve → certificado | Pendiente | Parcial | `plataforma-opensiac.md` |
| Madrid (propia) | `madrid` | 1 | CAS municipal → DNIe/Certificado | Pendiente | Parcial | `plataforma-madrid.md` |
| Barcelona (propia) | `barcelona` | 1 | VÀLid → certificado/DNIe | Pendiente | Parcial | `plataforma-barcelona.md` |
| València (propia) | `valencia` | 1 | Certificado directo o Cl@ve | Pendiente | Parcial | `plataforma-valencia.md` |
| Zaragoza (propia) | `zaragoza` | 1 | Certificado o Cl@ve | Pendiente | Parcial | `plataforma-zaragoza.md` |
| **REG + SIR (vía universal)** | — | Cualquier administración integrada en SIR | Cl@ve → DNIe/Certificado | Pendiente | Verificada sin certificado | `registro-reg-sir.md` |

"Verificada sin certificado" = rutas, selectores y origins comprobados en la parte pública; lo de dentro de la sesión está marcado en cada guía como **pendiente de verificación con certificado**.

## ¿Qué plataforma usa mi ayuntamiento?

```bash
uv run scripts/buscar.py --municipio "Sort"
```

Devuelve JSON con:
- `plataforma`: el slug de la tabla. Si no hay guía para ese slug, `guia` apunta a `registro-reg-sir.md` y `nota` lo explica.
- `sede_url`: la sede detectada. Es la que se usa en las rutas de la receta.
- `confianza`: `alta`, `media` o `baja`. Con `baja`, confirma la plataforma con las huellas de abajo antes de seguir la receta.
- `recaudador`: quién cobra los tributos, si se sabe. Los recibos a menudo no están en la sede municipal.

Huellas rápidas en la URL de la sede:

| Slug | Huella |
|---|---|
| `gestiona` | `*.sedelectronica.es` / `.gal`, `*.eadministracio.cat`, `*.egoitzaelektronikoa.eus`, ruta `/info.0` |
| `tao-sta` | `/sta/CarpetaPublic/`, `APP_CODE=STA` |
| `gtt` | `*.tributoslocales.es/<código>/<ENTIDAD>` |
| `aoc` | `seu-e.cat/<idioma>/web/<slug>`, `etram.seu-e.cat` |
| `sedipualba` | `*.sedipualba.es` |
| `gsede-moad` | `/opencms/system/modules/sede/` |
| `aytos` | `/portal/entidades.do?ent_id=`, `*.blcloud.es/portal/` |
| `experta-paemur` | `/web/inicioWebc.do?...entidad=`, `/3webc/`, `sede.<municipio>.regiondemurcia.es` |
| `eadmin-gestdoc` | `/eAdmin/*.do`, `/GDCarpetaCiudadano/` |
| `opensiac` | `/opensiac/...main.action`, `*.sede.e-ayuntamiento.es` |

Una huella solo en el HTML (no en la URL) puede ser un enlace a otra plataforma: por ejemplo, registro en una y tributos en otra.

## Reglas comunes a todas las recetas

- **Los códigos son locales.** IDs de trámite, entidad o asunto de un municipio no valen en otro. Sácalos del catálogo vigente.
- **Cl@ve:** el agente solo pulsa "Acceso DNIe / Certificado electrónico". El certificado lo pide `https://pasarela-ident.clave.gob.es`, que debe estar en los origins.
- **CAPTCHA:** lo resuelve la persona y tú sigues.
- **Notificaciones:** listar es libre. Abrir es comparecer (acto `comparecer`).
- **Actos:** firmar, presentar, pagar y cambiar datos los haces según los permisos de tu usuario (`SKILL.md`). Con el permiso, `sede.py` pasa `afirma://` a AutoFirma; sin él, lo bloquea.
- **Éxito:** número de registro o CSV con `scripts/justificante.py` y el asiento en el listado oficial de la sede.

## Si no hay receta

1. **Instancia general:** REG + SIR (`registro-reg-sir.md`) llega a cualquier ayuntamiento integrado en SIR.
2. **Tributos y recibos:** pide a la persona un recibo de IBI o basura. El emisor, el logo y la URL impresa dicen quién cobra.
3. **Explora en solo lectura** con `sede.py probe`, que por defecto no usa certificado:

   ```bash
   uv run scripts/sede.py probe --url "<sede_url>"
   uv run scripts/sede.py probe --url "<sede_url>" --clic "Catálogo"
   ```

   Devuelve el inventario de campos, botones y encabezados, sin valores. En `probe` sin titular no pulses botones de certificado: el sistema puede mostrar su propio selector con los certificados de la persona.
4. **Documenta** lo encontrado (rutas, parámetros que cambian, acceso, origins) y, si la persona quiere, abre un issue "nueva sede" en el repo, **sin datos personales**.
