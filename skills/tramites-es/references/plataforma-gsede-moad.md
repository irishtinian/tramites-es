---
verificado_el: 2026-10-15
estado_mapeo: verificado_sin_certificado
municipios_ejemplo: [Sevilla, Valladolid]
fuentes:
  - https://sede.sevilla.org/opencms/system/modules/sede/index      # portada de la sede de Sevilla
  - https://sede.sevilla.org/opencms/system/modules/gsede/elements/secciones/autenticacion/autenticacion.jsp   # autenticación (Sevilla)
  - https://sede.valladolid.es/opencms/system/modules/sede/index    # portada de la sede de Valladolid
  - https://sede.valladolid.es/opencms/system/modules/gsede/elements/secciones/autenticacion/autenticacion.jsp # autenticación (Valladolid)
  - https://www.sevilla.org/ovweb/                                    # oficina virtual de la Agencia Tributaria de Sevilla
  - https://contribuyente.valladolid.es/                              # Carpeta del Contribuyente de Valladolid
---

# Plataforma GSede / MOAD (OpenCms)

Riesgo: **Leer** (catálogo, carpeta) y **Preparar** (solicitud general, actividad). Firmar, presentar, pagar y abrir notificaciones son **actos** (`firmar`, `presentar`, `pagar`, `comparecer`): los haces según los permisos que te dé tu usuario (`sede.py --permitir …`).

## Qué es y dónde se usa

- Sede sobre OpenCms con módulos `gsede`. Viene del modelo **MOAD** de la Junta de Andalucía y la desarrolla Guadaltel.
- Dónde: **Sevilla** (capital y provincia), Cádiz, **Valladolid**, Mataró (confianza media), Coria del Río, y las Diputaciones de Granada, Huelva y Salamanca.
- Cobertura: ~80–100 sedes vistas en el sondeo. Una fuente secundaria habla de 226 ayuntamientos y 5 diputaciones.

## Cómo adaptarla a tu ayuntamiento

```text
HOST      = dominio de la sede
PROCEDURE = código interno del procedimiento (p. ej. SGE_01)
AREA      = código de área (p. ej. RegistroGeneral_1093)

Portada: https://{HOST}/opencms/system/modules/sede/index
Login:   https://{HOST}/opencms/system/modules/gsede/elements/secciones/autenticacion/autenticacion.jsp
```

- Cambian el dominio y los códigos de procedimiento y área.
- Ojo con la ruta: la portada está en `/modules/sede/` y el login en `/modules/gsede/`.
- **No hay deep links fiables a trámites.** El HTML genera los accesos con JavaScript: `ticket({procedure:'SGE_01'})` (Solicitud General en Sevilla) o `ticket({area:'RegistroGeneral_1093'})`. En Valladolid los enlaces llevan un `ticket=` de sesión que no se puede reutilizar. Navega siempre desde la portada y descubre los códigos en cada sede.

## Acceso

- La página de autenticación ofrece **certificado directo** y Cl@ve.
- Selector del certificado directo: `#autButton` (`onclick="waiting(); chargeClient();"`). Es el que usa el agente.
- Si se usa Cl@ve, en la pasarela solo vale "DNIe / Certificado electrónico". Cl@ve PIN, Móvil o Permanente son de la persona (Valladolid los admite incluso para firmar).
- Origins:

| Origin | Evidencia (15-oct-2026, sin certificado) |
|---|---|
| `https://sede.sevilla.org` | `cert-probe` de `/opencms/system/modules/gsede/.../autenticacion.jsp`: HTTP 200 sin mTLS. |
| `https://sede.valladolid.es` | Ídem. |

- No se sabe si `chargeClient()` pide el certificado por TLS o invoca AutoFirma: **pendiente de verificación con certificado**. Si lanza `afirma://`, sede.py lo bloquea y la identificación la completa la persona.

## Trámites típicos del autónomo

| Trámite | Entrada | Sin permiso, paras en | Actos (con permiso los haces tú) |
|---|---|---|---|
| Solicitud General (instancia) | Portada → "Solicitud General" (`ticket({procedure:'SGE_01'})` en Sevilla) | La ficha generada, con texto y adjuntos preparados | Identificarse, adjuntar, firmar y enviar: `firmar`, `presentar` |
| Actividad, obras, terrazas | Portada → catálogo por materias (urbanismo, vía pública) | El procedimiento | Igual |
| Impuestos, tasas y multas | Portada → área de impuestos (en Sevilla, `ImpuestosTasasMultas_1093`) | La oficina tributaria, que suele ser externa | Pagar: `pagar`; certificados: `generar` |
| Notificaciones | Enlace a DEHú | El listado (`sede-dehu.md`) | Abrir: `comparecer` |
| Mis expedientes y registros | Carpeta de la sede autenticada | — (listar es libre) | — |

- **Sevilla** tiene tres frentes:
  - Tributos: Agencia Tributaria de Sevilla (ATSE), oficina virtual `https://www.sevilla.org/ovweb/`. Con certificado; Cl@ve no aparece.
  - Actividades y veladores: Gerencia de Urbanismo, `https://www.urbanismosevilla.org/oficina-virtual`.
  - Registro general: la sede GSede.
  - El alta y la baja censal del IAE van a la AEAT.
- **Valladolid:** tributos en la Carpeta del Contribuyente (`https://contribuyente.valladolid.es/`, plataforma TAO/STA, `plataforma-tao-sta.md`). Su certificado de deudas es "de no deuda en vía ejecutiva", es decir, solo cubre el apremio.
- Contenido de la carpeta autenticada: **pendiente de verificación con certificado**.

## Firma

- **AutoFirma.** La ayuda pública incluye "Tengo AutoFirma" y la resolución de errores al firmar. No se ejecutó ninguna firma.
- Firmar es el acto `firmar`. Con ese permiso, `sede.py` pasa `afirma://` a AutoFirma (`setup-autofirma.md`); sin él, lo captura y lo bloquea.
- La ayuda menciona la recuperación de trámites no finalizados: no reanudes un borrador sin que tu usuario lo pida.
- Éxito esperado: solicitud en la carpeta, asiento de registro y justificante. Verifica con `scripts/justificante.py` y en el listado de la carpeta.

## Trampas

- **reCAPTCHA:** la sede de Sevilla carga reCAPTCHA. En el mapeo no apareció reto. Si aparece, lo resuelve la persona.
- **F5** delante de Valladolid: ritmo humano, sin reintentos en bucle.
- Los destinos `ticket()` se generan por JavaScript: un `goto` a una URL guardada fallará o caducará.
- No se observaron iframes.

## Fuentes

Ver cabecera. Mapeo público sin certificado del 15-oct-2026 en Sevilla y Valladolid. Datos de tributos de Sevilla y Valladolid: investigación propia del 14/15-oct-2026 sobre las webs municipales citadas.
