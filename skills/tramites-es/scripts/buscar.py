# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""buscar.py — "¿dónde se hace esto?" → sede, plataforma y guía de references/ (salida JSON).

  uv run scripts/buscar.py "certificado de estar al corriente"
  uv run scripts/buscar.py "Granadilla de Abona"          (municipio → sede, plataforma, recaudador)
  uv run scripts/buscar.py --municipio "Adeje"

Fuentes: assets/sedes.yaml (sedes y trámites), assets/municipios.csv (censo de ayuntamientos)
y los nombres de fichero de references/. No usa red.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ASSETS, REFS = RAIZ / "assets", RAIZ / "references"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("-", " ").replace("_", " ").split())


def palabras(s: str) -> set[str]:
    vacias = {"de", "del", "la", "el", "los", "las", "y", "a", "en", "mi", "por", "para", "con", "al"}
    return {w for w in norm(s).split() if w not in vacias and len(w) > 1}


def cargar_sedes() -> dict:
    """assets/sedes.yaml + assets/_sedes-*.yaml (estatal, canarias, plataformas…)."""
    import yaml
    sedes: dict = {}
    for p in [ASSETS / "sedes.yaml", *sorted(ASSETS.glob("_sedes-*.yaml"))]:
        if p.exists():
            sedes.update((yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("sedes", {}) or {})
    return sedes


# Etiquetas del censo (columna plataforma) → sufijo de references/plataforma-<x>.md
PLATAFORMAS = {"gestiona": "gestiona", "tao/sta": "tao-sta", "sedipualb@": "sedipualba", "aoc": "aoc", "aytos": "aytos",
               "gsede/moad": "gsede-moad", "eadmin/gestdoc": "eadmin-gestdoc", "experta": "experta-paemur", "gtt": "gtt",
               "opensiac": "opensiac"}
# Palabras con las que la gente pide una guía cuyo nombre de fichero no las contiene
GUIA_ALIAS = {"calendario-fiscal": "plazos vencimientos calendario fiscal fiscales trimestre trimestral cuando presento",
              "ayudas": "ayudas subvenciones convocatorias cuota cero",
              "canarias-recaudacion": "recaudador recibos municipales ibi iae basura quien cobra",
              "plataformas-municipales": "plataforma ayuntamiento sede municipal",
              "registro-reg-sir": "instancia general escrito registro"}


def nombre_natural(m: str) -> str:
    """El INE pospone el artículo: "Palmas de Gran Canaria, Las" → "Las Palmas de Gran Canaria", "Coruña, A" → "A Coruña"."""
    m2 = re.match(r"^(.+), (El|La|Los|Las|L'|Lo|Els|Les|A|O|As|Os|Es|Sa|Ses|Na)$", m or "")
    if not m2:
        return m or ""
    art = m2.group(2)
    return f"{art}{m2.group(1)}" if art.endswith("'") else f"{art} {m2.group(1)}"


def vocabulario() -> set[str]:
    """Palabras de trámites y guías: un municipio que se llame así ("Ibi", "Fiscal") no se toma por municipio
    dentro de una frase salvo que la persona lo escriba con su mayúscula ("Ibi")."""
    v = set()
    for s in cargar_sedes().values():
        for t in s.get("tramites", []) or []:
            v |= palabras(" ".join([t.get("nombre", ""), " ".join(t.get("alias", []) or [])]))
    for a in GUIA_ALIAS.values():
        v |= palabras(a)
    return v


def buscar_municipio(q: str, limite: int = 5, frase: bool = False) -> list[dict]:
    p = ASSETS / "municipios.csv"
    if not p.exists():
        return []
    nq = norm(q)
    if len(nq) < 2:
        return []
    voc = vocabulario() if frase else set()
    exactos, parciales = [], []
    with p.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            orig = row.get("municipio", "")
            for nombre in dict.fromkeys([orig, nombre_natural(orig)]):
                n = norm(nombre)
                if not n:
                    continue
                if n == nq:
                    exactos.append(row)
                    break
                # coincidencia por palabras completas, nunca por subcadena ("Ea" no casa con "tarea")
                if len(n) >= 3 and re.search(rf"\b{re.escape(n)}\b", nq):
                    # nombres cortos: con sus tildes ("Uña" no es "una"); palabras de trámite: con su mayúscula
                    if len(n) < 5 and not re.search(rf"(?<!\w){re.escape(nombre.casefold())}(?!\w)", q.casefold()):
                        continue
                    if n in voc and nombre not in q:
                        continue
                    parciales.append(row)
                    break
                # "La Laguna" → "San Cristóbal de La Laguna": solo con consultas cortas (en una frase larga, no)
                if (not frase or len(nq.split()) <= 3) and len(nq) >= 4 and re.search(rf"\b{re.escape(nq)}\b", n):
                    parciales.append(row)
                    break
    # a igualdad de coincidencia, primero el más poblado ("La Laguna": San Cristóbal antes que Pajares)
    parciales.sort(key=lambda r: -int((r.get("poblacion") or "0").strip() or 0))
    res = []
    for row in (exactos or parciales)[:limite]:
        etiqueta = (row.get("plataforma") or "").strip() or "desconocida"
        plat = PLATAFORMAS.get(etiqueta.lower(), etiqueta.lower())
        guia = REFS / f"plataforma-{plat}.md"
        nota = None if guia.exists() else "Sin receta para esta plataforma: explora con sede.py probe o usa REG/SIR para la instancia general."
        if etiqueta == "desconocida" and row.get("ccaa") == "Cataluña":
            # Casi todos los ayuntamientos catalanes pequeños tienen sede en seu-e.cat (AOC), aunque el censo no la detectara
            guia = REFS / "plataforma-aoc.md"
            nota = ("Censo sin plataforma. En Cataluña lo probable es la Seu-e del AOC (https://seu-e.cat/ca/web/<slug>): "
                    "compruébalo sin certificado antes de usarla.")
        res.append({
            "tipo": "municipio", "municipio": nombre_natural(row.get("municipio", "")), "provincia": row.get("provincia"),
            "ccaa": row.get("ccaa"), "sede_url": row.get("sede_url") or None, "web": row.get("web") or None,
            "plataforma": etiqueta, "confianza": row.get("confianza"),
            "recaudador": row.get("recaudador") or None,
            "guia": f"references/{guia.name}" if guia.exists() else "references/registro-reg-sir.md",
            "nota": nota,
        })
    return res


def buscar_tramite(q: str, limite: int = 6) -> list[dict]:
    qw = palabras(q)
    cand = []
    for sid, s in cargar_sedes().items():
        for t in s.get("tramites", []) or []:
            texto = " ".join([t.get("nombre", ""), t.get("id", ""), " ".join(t.get("alias", []) or []), s.get("nombre", "")])
            score = len(qw & palabras(texto))
            if score:
                score += 0.3 if s.get("nivel") == "estatal" else 0  # lo general antes que lo local
                cand.append((score, {"tipo": "tramite", "sede": sid, "tramite": t.get("id"), "nombre": t.get("nombre"),
                                     "plataforma": s.get("plataforma"), "url": t.get("url") or s.get("login"),
                                     "riesgo": t.get("riesgo"), "guia": t.get("guia") or s.get("guia"),
                                     "verificado_el": t.get("verificado_el") or s.get("verificado_el")}))
    for f in sorted(REFS.glob("*.md")):
        alias = qw & palabras(GUIA_ALIAS.get(f.stem, ""))
        score = len(qw & palabras(f.stem)) + len(alias)
        if score:
            # los playbooks transversales (tramite-*) y las guías pedidas por sus alias son la mejor puerta de entrada
            cand.append((score + (1 if f.stem.startswith("tramite-") or alias else -0.5), {"tipo": "guia", "guia": f"references/{f.name}"}))
    cand.sort(key=lambda x: -x[0])
    vistos, res = set(), []
    for _, c in cand:
        k = c.get("guia"), c.get("tramite")
        if k not in vistos:
            vistos.add(k)
            res.append(c)
        if len(res) >= limite:
            break
    return res


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # JSON en UTF-8 también en Windows
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("consulta", nargs="?", default="")
    ap.add_argument("--municipio")
    a = ap.parse_args()
    if a.municipio:
        res = buscar_municipio(a.municipio)
    else:
        res = buscar_municipio(a.consulta, frase=True) + buscar_tramite(a.consulta)
    if not res:
        res = [{"tipo": "sin_resultados", "sugerencia": "Reformula (p. ej. 'notificaciones', 'vida laboral', nombre exacto del municipio) "
                "o consulta la tabla de trámites de SKILL.md."}]
    print(json.dumps({"consulta": a.municipio or a.consulta, "resultados": res}, ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
