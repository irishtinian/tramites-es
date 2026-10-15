---
verificado_el: 2026-10-15
fuentes:
  - https://pasarela.clave.gob.es/Proxy2/ServiceProvider   # pantalla de selección (se llega por POST SAML desde la sede)
  - https://sede.agenciatributaria.gob.es/Sede/identificacion-electronica/clave-movil/uso-personal-clave-prevencion-practicas-autorizadas.html
estado_mapeo: "Mapeo en vivo 15-10-2026: selector y flujo con certificado verificados al entrar en Carpeta Ciudadana, DGT, Justicia y DEHú (en DEHú, la propia sede rechaza después el login)."
---

# Pasarela Cl@ve (identificación compartida del Estado)

## 1. Para qué sirve

Cl@ve **no es una sede**: es la pasarela por la que te identificas en muchas sedes. Esta guía explica cómo pasar por ella **solo con certificado**.

- **La usan:** DEHú, la DGT (MiDGT y `sedeclave`), Mi Carpeta Ciudadana (a través de Keycloak `auth-api.redsara.es`), Justicia, el Catastro (opcional) y muchos ayuntamientos (por ejemplo, Gestiona).
- **No la usan para el certificado:**
  - la AEAT, que tiene selector propio (`sede-aeat.md`);
  - la Seguridad Social, que tiene la pasarela `idp.seg-social.es` (`sede-tgss-importass.md`).

## 2. Acceso

- **Entrada:** la sede hace un POST SAML a `https://pasarela.clave.gob.es/Proxy2/ServiceProvider` (título "Página Principal - Clave"). Un GET directo a esa URL da error porque falta el SAML. **No es que Cl@ve esté caída.**
- **Botones:** en la versión del 15-10-2026 hay cuatro `button.idp-button`, sin shadow DOM ni iframes.

| Botón | `onclick` | ¿Para el agente? |
|---|---|---|
| Acceso Cl@ve Móvil (incluye Cl@ve PIN) | `selectedIdP('IDP_MOVIL')` | **No** (regla dura 3) |
| **Acceso DNIe / Certificado electrónico** | `selectedIdP('AFIRMA')` | **Sí, el único** |
| Acceso Ciudadanos UE | `selectedIdP('EIDAS')` | No |
| Acceso Cl@ve permanente | `selectedIdP('SEGSOC')` | **No** (regla dura 3) |

- **Flujo con certificado:**
  1. Clic en "DNIe / Certificado".
  2. `POST /Proxy2/ServiceRedirect`.
  3. `POST https://pasarela-ident.clave.gob.es/IdP2/AuthenticateCitizen`: **aquí se pide el certificado**.
  4. Vuelta a la sede (`ResponseRedirect`).
- **Origins con certificado:** `https://pasarela-ident.clave.gob.es`. Ya figura en los `origins` de cada sede de `assets/` que pasa por Cl@ve; si usas `--url` sin `--sede`, no se añade.
  - Lo pide **por renegociación, no en el handshake**: `tls-probe` dice "no" y `cert-probe` dice "sí".
  - `pasarela.clave.gob.es` y `se-pasarela.clave.gob.es` no piden certificado.
  - `pasarela-ident-sistemas.clave.gob.es` ya no existe en DNS.
- **Qué certificado:** Cl@ve solo identifica a **personas físicas**. Para una sociedad hay que usar el certificado de representante directamente en la sede, donde la sede lo permita.
- **Cómo saber que entró:** la URL vuelve al dominio de la sede de origen y esa sede muestra su señal de sesión (nombre o "Salir"). La señal concreta está en la guía de cada sede.

**Receta común** (`clave_login.py`): se ejecuta con la URL de entrada de la sede, que redirige a Cl@ve.

```python
pg.wait_for_selector("button.idp-button", timeout=60000)
pg.click("button.idp-button:has-text('DNIe / Certificado')")
pg.wait_for_url(lambda u: "clave.gob.es" not in u, timeout=90000)
pg.wait_for_timeout(4000)
captura("tras-clave")
RESULTADO = {"url": pg.url.split("?")[0], "titulo": pg.title()}
```

```bash
uv run scripts/sede.py ejecutar clave_login.py --sede <dgt|carpeta-ciudadana|justicia|dehu> --url "<entrada de la sede>" --titular yo
```

Dentro de una misma ejecución, la sesión de Cl@ve se reutiliza por SSO: otra sede o aplicación que vuelva a pasar por Cl@ve entra sin clic. Entre ejecuciones distintas de `sede.py` no se conserva nada.

## 3. Trámites

Cl@ve no tiene trámites propios. Los de cada sede están en `sede-dehu.md`, `sede-dgt.md`, `sede-carpeta-ciudadana.md`, `sede-justicia.md` y `sede-catastro.md`.

## 4. Trampas y problemas conocidos

- **Cl@ve PIN, Cl@ve Móvil y Cl@ve Permanente están prohibidos para el agente**, incluso con el consentimiento de la persona.
  - La AEAT considera uso indebido la automatización de autenticaciones (aviso actualizado el 29-abr-2026).
  - Si una sede solo admite esas opciones, entra la persona.
- **Error 4002** ("no se ha enviado ningún certificado a @Firma"): casi siempre falta el origin `pasarela-ident.clave.gob.es`. Revisa `hosts_con_error` en la salida de `sede.py`.
- **"No se encuentra disponible en estos momentos":** Cl@ve caída o inestable. Reintenta más tarde y no borres cookies (no cambia nada).
- **"Redirigiendo al proveedor de identidades…"** sin avanzar: espera y, si persiste, para y avisa.
- **Versiones anteriores** tenían shadow DOM y hubo que hacer clic por posición. Si el selector deja de encontrar el botón, haz `probe` y abre un issue "sede rota".
- **Los códigos de error** dependen de cada sede. Por ejemplo, DEHú devuelve `?error=<código>` después de Cl@ve (`sede-dehu.md`).

## 5. Fuentes

- Pasarela Cl@ve, observada en vivo el 15-10-2026: ver la cabecera.
- AEAT, "Uso personal de Cl@ve y prevención de prácticas de intermediación no autorizadas" (actualizada el 29-abr-2026): ver la cabecera.
- Historial de uso previo con certificado: error 4002 por falta de origin y caídas puntuales de Cl@ve.
