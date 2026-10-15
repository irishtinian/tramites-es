## Qué cambia y por qué

<!-- Una o dos frases. Si arregla un issue: "Cierra #123". -->

**Tipo:** guía / datos (sedes, municipios, calendario) / script / CI / documentación

## Fuentes

<!-- Enlaces oficiales (BOE, boletín autonómico, sede del organismo) que respaldan cada dato nuevo o cambiado. -->

## Checklist de seguridad

- [ ] No debilita ninguna guarda de `scripts/sede.py` ni ninguna regla dura de `SKILL.md`. Si lo hace, explico abajo el caso exacto (URL sin parámetros, botón, qué pasa).
- [ ] Los dominios nuevos son de una Administración pública y enlazo su fuente oficial. Ningún acortador, IP, `http://` ni dominio parecido a uno oficial.
- [ ] El agente sigue sin poder firmar, presentar, pagar, comparecer ni abrir notificaciones: ese clic sigue siendo de la persona.
- [ ] Sin red nueva salvo hacia sedes oficiales; sin descargas de código o binarios en tiempo de ejecución; sin `subprocess` de shell arbitrario.
- [ ] El certificado y su contraseña solo los toca `scripts/cert.py`; nada de secretos en argv, logs ni capturas.
- [ ] Dependencias con versión exacta (PEP 723 en los scripts, `pyproject.toml` para las pruebas).
- [ ] Sin Unicode invisible, sin URLs acortadas y sin ficheros binarios.

## Checklist de datos personales

- [ ] No hay NIF, NIE, CIF, nombres, direcciones, IBAN, teléfonos, emails, nº de expediente ni referencias de notificaciones reales. Uso marcadores: `<NIF>`, `<TITULAR>`, `<IMPORTE>`…
- [ ] Las capturas y los ejemplos usan datos ficticios o están recortados.
- [ ] Nada sale de un certificado real ni de una sesión real (cookies, tokens, HTML con datos).

## Fechas, plazos e importes

- [ ] Cada fecha, plazo o importe nuevo cita su fuente primaria y actualiza `verificado_el`.
- [ ] Si toco `assets/calendario.yaml`, `calendario.py validar` pasa y la tabla de `references/calendario-fiscal.md` coincide.

## Pruebas

- [ ] `pytest` pasa en local.
- [ ] La CI (`tests`, `content-guard`, `validate`) está en verde.

## Si eres un agente de IA

- [ ] Has leído `AGENTS.md`.
- [ ] Indica el modelo y la herramienta que has usado: <!-- p. ej. "Claude Code + modelo X" -->
- [ ] Una persona ha revisado el diff completo antes de abrir este PR.
