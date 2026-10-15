---
verificado_el: 2026-10-15
estado_mapeo: verificado_sin_certificado
municipios_ejemplo: [Palma, Cartagena]
fuentes:
  - https://sedipualba.es/entidades-adheridas/                       # listado oficial de entidades adheridas (Diputación de Albacete)
  - https://palma.sedipualba.es/catalogoservicios.aspx              # catálogo de Palma
  - https://palma.sedipualba.es/carpetaciudadana/tramite.aspx?idtramite=13808   # instancia general (Palma)
  - https://palma.sedipualba.es/carpetaciudadana.aspx               # Carpeta Ciudadana (redirige al login)
  - https://cartagena.sedipualba.es/catalogoservicios.aspx          # catálogo de Cartagena
  - https://sede.dipualba.es/firma/documento.aspx                   # módulo de firma (SEFYCU)
---

# Plataforma Sedipualb@ (Diputación de Albacete)

Riesgo: **Leer** (catálogo, carpeta, listados) y **Preparar** (instancias, comunicaciones). Firmar, presentar, pagar y abrir notificaciones son **actos** (`firmar`, `presentar`, `pagar`, `comparecer`): los haces según los permisos que te dé tu usuario (`sede.py --permitir …`).

## Qué es y dónde se usa

- Sede electrónica que la **Diputación de Albacete** ofrece por convenio. El módulo de firma se llama **SEFYCU**.
- El listado oficial tiene ~900 entidades: unos 400 ayuntamientos más mancomunidades, entidades locales menores y organismos.
- Dónde: Albacete, Huesca, Navarra (vía ANIMSA), Valencia, Asturias, Burgos (entidades locales menores), Toledo y Murcia. También **Palma** y **Cartagena**, Sagunto, Sant Vicent del Raspeig, Mislata o Alcantarilla.

## Cómo adaptarla a tu ayuntamiento

```text
TENANT    = subdominio del ente en sedipualba.es
IDTRAMITE = código local del procedimiento

Sede:       https://{TENANT}.sedipualba.es/
Catálogo:   https://{TENANT}.sedipualba.es/catalogoservicios.aspx
Ficha:      https://{TENANT}.sedipualba.es/carpetaciudadana/tramite.aspx?idtramite={IDTRAMITE}
Carpeta:    https://{TENANT}.sedipualba.es/carpetaciudadana.aspx
Registros:  https://{TENANT}.sedipualba.es/carpetaciudadana/buscar_expedientes.aspx?tipo=PUBLICOS&u=int
```

- Cambian el subdominio, el `idtramite`, el idioma y los enlaces externos (oficina tributaria).
- Ejemplos de Palma: instancia general `idtramite=13808`, comunicación previa de obras `14161`. En otros entes la instancia general ha aparecido como `idtramite=39`. **No copies IDs entre entes**: búscalos en el catálogo.
- Truco: `https://sede.dipualba.es/?entidad=<INE5>` redirige a la sede del ente (probado con un municipio de Albacete). Si la entidad no está activa, la respuesta lleva a `noactiva.aspx`.
- Palma tiene además una web de sede en otro dominio (`seuelectronica.palma.cat`), pero el registro va por `palma.sedipualba.es`.

## Acceso

- `/carpetaciudadana.aspx` redirige a `/carpetaciudadana/login.aspx?returnUrl=...`, que abre un **iframe** con `/segex/identificacion_opciones.aspx?idtoken=...`. El `idtoken` es efímero: no lo guardes.
- Opciones vistas en el iframe:
  - **Certificado directo.** Es la que usa el agente.
  - Certificado mediante Cl@ve. En la pasarela, solo "DNIe / Certificado electrónico".
  - Identificación con firma electrónica (AutoFirma 1.9+): es una firma (acto `firmar`). Usa antes el certificado directo.
  - Correo y modalidades Cl@ve PIN/Móvil/Permanente: son de la persona; el agente no las usa.
- Certificados admitidos según la sede: FNMT, DNIe, ACCV, Camerfirma y Firmaprofesional.
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://{TENANT}.sedipualba.es` | `tls-probe`/`cert-probe`: no pide certificado en el handshake. |
| `https://sede.dipualba.es` | `cert-probe` de `/firma/documento.aspx`: HTTP 200 sin mTLS. |

- Dónde se pide el certificado tras pulsar "certificado directo": **pendiente de verificación con certificado**. Si el flujo va por Cl@ve, el certificado lo pide `https://pasarela-ident.clave.gob.es`.

## Trámites típicos del autónomo

| Trámite | Entrada | Sin permiso, paras en | Actos (con permiso los haces tú) |
|---|---|---|---|
| Instancia general | `.../carpetaciudadana/tramite.aspx?idtramite={IDTRAMITE}` | La ficha, con el texto y los adjuntos preparados | "Tramitar", identificarse, adjuntar, firmar y enviar: `presentar`, `firmar` |
| Actividad, obras, urbanismo | Catálogo → actividades / obras / urbanismo | La modalidad exacta, con la documentación preparada | Igual |
| Tasas, IAE, recibos, certificado de estar al corriente | Catálogo → tesorería; suele saltar a la oficina tributaria | El organismo y su web | Pagar: `pagar`; certificado: `generar` |
| Mis trámites y registros presentados | Carpeta → expedientes / registros | — (listar es libre) | — |
| Notificaciones | Carpeta (ecosistema Notific@) | El listado | Abrir: `comparecer` |

- **Tributos fuera de Sedipualb@:**
  - **Palma:** IBI, IAE, IVTM y residuos los lleva la **ATIB** (Govern balear). Autoliquidaciones, tasas y multas, la oficina tributaria municipal en `palma.tributoslocales.es` (GTT, `plataforma-gtt.md`). El 15-oct-2026 esa oficina **no admitía certificado** ("accés amb certificat en breu disponible").
  - **Cartagena:** el Órgano de Gestión Tributaria está en la sede Sedipualb@. Los recibos y la vía ejecutiva los cobra el **OAGRC** (`sede.oagrc.es`).
- Contenido de la carpeta con sesión iniciada: **pendiente de verificación con certificado**.

## Firma

- **AutoFirma / SEFYCU**, deducido de la parte pública: la sede exige AutoFirma 1.9+ y publica el módulo `sede.dipualba.es/firma/documento.aspx`.
- Firmar y enviar son los actos `firmar` y `presentar`. Con esos permisos, `sede.py` pasa `afirma://` a AutoFirma (`setup-autofirma.md`); sin ellos, captura `afirma://` y bloquea firmar y enviar.
- Éxito esperado: el trámite en la carpeta, con asiento registral y justificante o acuse descargable. Verifica con `scripts/justificante.py` y en "registros" de la carpeta.

## Trampas

- **Iframe** de identificación (`/segex/`): los selectores están dentro del frame, no en la página principal.
- **F5** delante de varias sedes. En Palma respondió lento pero funcionó: espera y no reintentes en bucle.
- No se observaron CAPTCHA en el flujo público.
- El ID de un trámite en un ente no sirve en otro.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en Palma y Cartagena. No se eligió ninguna opción de identificación.
