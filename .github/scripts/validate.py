#!/usr/bin/env python3
"""validate.py — validación estructural de tramites-es (necesita PyYAML, versión fijada en pyproject.toml).

Comprueba:
  1. Todos los .yaml, .yml y .json del repositorio se pueden leer.
  2. skills/*/SKILL.md: frontmatter con `name` igual al nombre de la carpeta (minúsculas, cifras y
     guiones, máx. 64, sin "claude" ni "anthropic") y `description` de 1 a 1024 caracteres.
  3. skills/*/references/*.md: frontmatter con `verificado_el` (fecha AAAA-MM-DD, no futura).
  4. Las guías enlazadas desde skills/*/assets/*.yaml (claves `guia`) existen.

Uso:  python .github/scripts/validate.py [--raiz RUTA]      (sale con 1 si hay errores)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

import yaml

IGNORAR_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules", ".mypy_cache", ".ruff_cache"}
RE_NOMBRE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RE_FRONTMATTER = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
MAX_DESCRIPCION = 1024


def ficheros(raiz: Path, extensiones: tuple[str, ...]) -> list[Path]:
    res = []
    for dirpath, dirnames, filenames in os.walk(raiz):
        dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIRS]
        res += [Path(dirpath) / f for f in filenames if f.lower().endswith(extensiones)]
    return sorted(res)


def frontmatter(texto: str) -> dict | None:
    m = RE_FRONTMATTER.match(texto.replace("\r\n", "\n"))
    if not m:
        return None
    datos = yaml.safe_load(m.group(1))
    return datos if isinstance(datos, dict) else None


def valores_de_clave(datos, clave: str):
    """Todos los valores de `clave` a cualquier profundidad."""
    if isinstance(datos, dict):
        for k, v in datos.items():
            if k == clave:
                yield v
            yield from valores_de_clave(v, clave)
    elif isinstance(datos, list):
        for v in datos:
            yield from valores_de_clave(v, clave)


def _primera_linea(ex: Exception) -> str:
    texto = str(ex).strip()
    return f"{type(ex).__name__}: {texto.splitlines()[0][:200]}" if texto else type(ex).__name__


def revisar_ficheros_de_datos(raiz: Path) -> list[str]:
    errores = []
    for p in ficheros(raiz, (".yaml", ".yml", ".json")):
        rel = p.relative_to(raiz).as_posix()
        try:
            texto = p.read_text(encoding="utf-8")
            if p.suffix.lower() == ".json":
                json.loads(texto)
            else:
                list(yaml.safe_load_all(texto))
        except Exception as ex:  # noqa: BLE001 - cualquier fallo de lectura es un error de validación
            errores.append(f"{rel}: no se puede leer ({_primera_linea(ex)})")
    return errores


def revisar_skills(raiz: Path) -> list[str]:
    errores = []
    skills = sorted(raiz.glob("skills/*/SKILL.md"))
    if not skills:
        return ["no hay ningún skills/*/SKILL.md"]
    for p in skills:
        rel = p.relative_to(raiz).as_posix()
        try:
            fm = frontmatter(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as ex:
            errores.append(f"{rel}: frontmatter ilegible ({_primera_linea(ex)})")
            continue
        if fm is None:
            errores.append(f"{rel}: falta el frontmatter YAML entre líneas '---'")
            continue
        nombre, carpeta = fm.get("name"), p.parent.name
        if not isinstance(nombre, str) or not RE_NOMBRE.match(nombre) or len(nombre) > 64:
            errores.append(f"{rel}: name '{nombre}' debe tener solo minúsculas, cifras y guiones (máx. 64)")
        elif re.search(r"claude|anthropic", nombre):
            errores.append(f"{rel}: name no puede contener 'claude' ni 'anthropic'")
        if nombre != carpeta:
            errores.append(f"{rel}: name '{nombre}' no coincide con la carpeta '{carpeta}'")
        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errores.append(f"{rel}: falta description")
        elif len(desc) > MAX_DESCRIPCION:
            errores.append(f"{rel}: description tiene {len(desc)} caracteres (máx. {MAX_DESCRIPCION})")
    return errores


def revisar_guias(raiz: Path, hoy: dt.date | None = None) -> list[str]:
    errores = []
    hoy = hoy or dt.date.today()
    for p in sorted(raiz.glob("skills/*/references/*.md")):
        rel = p.relative_to(raiz).as_posix()
        try:
            fm = frontmatter(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as ex:
            errores.append(f"{rel}: frontmatter ilegible ({_primera_linea(ex)})")
            continue
        if not fm or "verificado_el" not in fm:
            errores.append(f"{rel}: falta verificado_el en el frontmatter")
            continue
        v = fm["verificado_el"]
        if isinstance(v, dt.datetime):
            v = v.date()
        try:
            fecha = v if isinstance(v, dt.date) else dt.date.fromisoformat(str(v))
        except ValueError:
            errores.append(f"{rel}: verificado_el '{v}' no es una fecha AAAA-MM-DD")
            continue
        if fecha > hoy + dt.timedelta(days=1):
            errores.append(f"{rel}: verificado_el {fecha} está en el futuro")
    return errores


def revisar_enlaces_a_guias(raiz: Path) -> list[str]:
    errores = []
    for p in sorted(list(raiz.glob("skills/*/assets/*.yaml")) + list(raiz.glob("skills/*/assets/*.yml"))):
        rel = p.relative_to(raiz).as_posix()
        try:
            datos = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue  # ya lo informa revisar_ficheros_de_datos
        for guia in valores_de_clave(datos, "guia"):
            if not isinstance(guia, str) or not guia.startswith("references/"):
                errores.append(f"{rel}: guia '{guia}' debe ser una ruta references/<fichero>.md")
            elif not (p.parent.parent / guia).is_file():
                errores.append(f"{rel}: la guía '{guia}' no existe")
    return errores


def revisar(raiz: Path) -> list[str]:
    raiz = raiz.resolve()
    return (revisar_ficheros_de_datos(raiz) + revisar_skills(raiz)
            + revisar_guias(raiz) + revisar_enlaces_a_guias(raiz))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", default=Path(__file__).resolve().parents[2], type=Path)
    errores = revisar(ap.parse_args().raiz)
    en_actions = os.environ.get("GITHUB_ACTIONS") == "true"
    for e in errores:
        print(f"::error title=validate::{e}" if en_actions else e)
    if errores:
        print(f"validate: {len(errores)} error(es).", file=sys.stderr)
        return 1
    print("validate: todo correcto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
