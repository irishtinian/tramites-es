---
verificado_el: 2026-10-15
estado_mapeo: parcial
municipios_ejemplo: [Sabadell, Paterna]
fuentes:
  - https://seu.sabadell.cat/opensiac/main.action                                                          # portada (Sabadell)
  - https://seu.sabadell.cat/opensiac/informacionpublica/tramitesinfo.action?tramitesInfoForm.id=620      # instancia general (Sabadell)
  - https://seu.sabadell.cat/opensiac/certlogin/conectar.action                                            # acceso (Sabadell)
  - https://sede.paterna.es/opensiac/main.action                                                           # portada (Paterna)
  - https://sede.paterna.es/opensiac/informacionpublica/tramites_enter.action                              # catálogo (Paterna)
  - https://web.sabadell.cat/relacioTributs                                                                # reparto de tributos Ajuntament/ORGT (Sabadell)
---

# Plataforma OpenSIAC (gtt, GADD)

Riesgo: **Leer** (catálogo, solicitudes, expedientes) y **Preparar** (instancia, actividad). Firmar, presentar, pagar y abrir notificaciones son **actos** (`firmar`, `presentar`, `pagar`, `comparecer`): los haces según los permisos que te dé tu usuario (`sede.py --permitir …`).

Estado **parcial**: el mecanismo de firma no está confirmado. El falso positivo del buzón está corregido en `sede.py` desde el 15-10-2026.

## Qué es y dónde se usa

- Sede "OpenSIAC" de **gtt** (Gestión Tributaria Territorial), con la marca GADD en el HTML. No confundir con la oficina tributaria GTT de `*.tributoslocales.es` (`plataforma-gtt.md`), que es otro producto de la misma empresa.
- Dónde: Diputación de Palencia (multientidad), Asturias (Llanes, Navia, Valdés…), **Sabadell**, Tona, Pozuelo de Alarcón, **Paterna**, Calvià, Narón, Camargo. También en dominios `*.sede.e-ayuntamiento.es`.
- Cobertura estimada: ~35–60 entidades.

## Cómo adaptarla a tu ayuntamiento

```text
HOST       = dominio de la sede
TRAMITE_ID = identificador local del trámite

Portada:        https://{HOST}/opensiac/main.action
Catálogo:       https://{HOST}/opensiac/informacionpublica/tramites_enter.action
Ficha:          https://{HOST}/opensiac/informacionpublica/tramitesinfo.action?tramitesInfoForm.id={TRAMITE_ID}
Login:          https://{HOST}/opensiac/certlogin/conectar.action
Solicitudes:    https://{HOST}/opensiac/carpetaciudadana/consultasolicitudes_enter.action?script=si
Expedientes:    https://{HOST}/opensiac/carpetaciudadana/consultaexpedientes_enter.action
Notificaciones: https://{HOST}/opensiac/carpetaciudadana/buzonnotificaciones_enter.action
Documentos:     https://{HOST}/opensiac/carpetaciudadana/repositoriodocumentos.action
```

- Cambian el dominio, los IDs de trámite y los módulos activados en cada sede.
- Sabadell: instancia general `tramitesInfoForm.id=620`. Es local: no la copies.
- Hay variantes de ruta: Sabadell también responde en `/opensiac/action/main?method=enter`, y Pozuelo usa `/sede/main.action` en lugar de `/opensiac/`.
- Quita `;jsessionid=...` de cualquier enlace que guardes.

## Acceso

- La ruta se llama `certlogin`, pero **en Paterna solo mostró acceso por Cl@ve**. No supongas certificado directo por el nombre.
- En la pasarela Cl@ve, el agente solo usa **"Acceso DNIe / Certificado electrónico"**.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://seu.sabadell.cat`, `https://sede.paterna.es` | `cert-probe` de `/opensiac/certlogin/conectar.action`: HTTP 200 sin mTLS. |
| `https://pasarela-ident.clave.gob.es` | Pide el certificado en la rama "DNIe / Certificado" de Cl@ve (`sede-clave.md`). |

- Si alguna sede muestra un acceso con certificado directo, dónde se pide: **pendiente de verificación con certificado**.

## Trámites típicos del autónomo

| Trámite | Entrada | Sin permiso, paras en | Actos (con permiso los haces tú) |
|---|---|---|---|
| Instancia general | Ficha `tramitesinfo.action?tramitesInfoForm.id={TRAMITE_ID}` | La ficha, con texto y adjuntos preparados | Identificarse, adjuntar, firmar y enviar: `firmar`, `presentar` |
| Actividad, licencias, urbanismo, certificados | Catálogo `tramites_enter.action` | La ficha, con la documentación preparada | Igual |
| Mis solicitudes, expedientes, documentos | Carpeta autenticada (rutas de arriba) | — (listar es libre) | — |
| Notificaciones | `buzonnotificaciones_enter.action` | El listado | Abrir: `comparecer` |
| Tasas, IAE, recibos | Recaudador | Decir quién cobra | Pagar: `pagar`; certificado: `generar` |

- **Paterna:** tasas, IAE y recibos en `https://paterna.tributoslocales.es` (GTT, `plataforma-gtt.md`).
- **Sabadell:** reparto mixto. El ORGT de la Diputació de Barcelona gestiona y cobra IVTM e IAE; el Ajuntament gestiona IBI, residuos, vados y terrazas, y el ORGT los cobra. Detalle en `https://web.sabadell.cat/relacioTributs`.
- Contenido de la carpeta autenticada: **pendiente de verificación con certificado**.

## Firma

- **Pendiente.** La sede enlaza un portafirmas, pero la parte pública no confirma AutoFirma ni otro cliente. No lo supongas.
- Firmar y enviar son los actos `firmar` y `presentar`. Con esos permisos, `sede.py` pasa `afirma://` a AutoFirma (`setup-autofirma.md`); sin ellos, captura `afirma://` y bloquea firmar y enviar.
- Éxito esperado: la presentación aparece en **Mis solicitudes** con asiento y justificante, y después en Expedientes y Documentos. Verifica con `scripts/justificante.py` y en el listado.

## Trampas

- **Buzón y guarda de `sede.py`** (corregido el 15-10-2026). Antes, la guarda bloqueaba toda ruta del buzón porque `/opensiac/` contiene "open". Ahora "open" solo cuenta como palabra suelta. Si aun así ves BLOQUEADO al listar sin haber pulsado ninguna notificación, no lo esquives: avisa con un issue "sede rota" y cuéntaselo a tu usuario.
- La ruta `certlogin` no implica certificado directo.
- No se observaron CAPTCHA, WAF ni iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en Sabadell y Paterna. No se continuó hasta el selector de la pasarela.
