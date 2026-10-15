#!/bin/sh
# install.sh - instala el skill tramites-es para tus agentes de IA (Linux y macOS).
#
# Copia la carpeta skills/tramites-es de este repositorio, sin enlaces simbolicos, en:
#   ~/.agents/skills/tramites-es     (Codex, Gemini CLI, OpenClaw, Cursor, Copilot... leen ~/.agents/skills)
#   ~/.claude/skills/tramites-es     (Claude Code)
#   ~/.openclaw/skills/tramites-es   (solo si ya existe ~/.openclaw/skills)
#   ~/.hermes/skills/tramites-es     (solo si ya existe ~/.hermes/skills)
#
# Es para personas: muestra lo que va a copiar y pide confirmacion antes de tocar nada.
# No usa la red, no pide permisos de administrador y no escribe fuera de esas carpetas.
# Si ya habia una copia de tramites-es en un destino, la sustituye entera.
#
# Uso (desde la carpeta del repositorio):   sh install.sh
set -eu

SKILL=tramites-es
RAIZ=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd -P)
ORIGEN="$RAIZ/skills/$SKILL"

fallo() {
  printf 'Error: %s\n' "$1" >&2
  exit 1
}

[ -f "$ORIGEN/SKILL.md" ] || fallo "no encuentro $ORIGEN/SKILL.md. Ejecuta install.sh desde la carpeta del repositorio."
[ -n "${HOME:-}" ] && [ -d "$HOME" ] || fallo "la variable HOME no apunta a una carpeta."
[ "$(id -u)" != 0 ] || fallo "no lo ejecutes como root: instala el skill con tu usuario normal."

ENLACES=$(find "$ORIGEN" -type l -print)
[ -z "$ENLACES" ] || fallo "la carpeta del skill contiene enlaces simbolicos y no se copian por seguridad: $ENLACES"

VERSION=$(sed -n '/^[[:space:]]*version:/{s/^[^:]*:[[:space:]]*//;s/"//g;p;q;}' "$ORIGEN/SKILL.md")
N=$(find "$ORIGEN" -type f ! -path '*/__pycache__/*' | wc -l | tr -d ' ')

# Destinos (en los parametros posicionales para no partir rutas con espacios).
set -- "$HOME/.agents/skills" "$HOME/.claude/skills"
AVISOS=""
for AGENTE in .openclaw .hermes; do
  if [ -d "$HOME/$AGENTE/skills" ]; then
    set -- "$@" "$HOME/$AGENTE/skills"
  elif [ -d "$HOME/$AGENTE" ]; then
    AVISOS="$AVISOS
Aviso: existe $HOME/$AGENTE pero no $HOME/$AGENTE/skills. Si quieres instalarlo alli, crea esa carpeta y vuelve a ejecutar install.sh."
  fi
done

echo ""
echo "tramites-es ${VERSION:-?}: se copiaran $N ficheros de"
echo "  $ORIGEN"
echo "a estas carpetas:"
for D in "$@"; do
  if [ -e "$D/$SKILL" ] || [ -L "$D/$SKILL" ]; then
    echo "  $D/$SKILL   (ya existe: se sustituira)"
  else
    echo "  $D/$SKILL"
  fi
done
echo ""
echo "Ficheros:"
(cd "$ORIGEN" && find . -type f ! -path '*/__pycache__/*' | sed 's|^\./|  |' | LC_ALL=C sort)
[ -z "$AVISOS" ] || printf '%s\n' "$AVISOS"
echo ""

[ -t 0 ] || fallo "hace falta una terminal interactiva para confirmar. Ejecuta: sh install.sh"
printf 'Continuar? [s/N] '
read -r RESPUESTA || RESPUESTA=""
case "$RESPUESTA" in
  s|S|si|SI|Si|y|Y|yes|YES) ;;
  *) echo "Cancelado. No se ha copiado nada."; exit 0 ;;
esac

for D in "$@"; do
  mkdir -p "$D"
  TMP="$D/.$SKILL.nuevo.$$"
  rm -rf "$TMP"
  cp -R "$ORIGEN" "$TMP"
  find "$TMP" -name __pycache__ -type d -prune -exec rm -rf {} +
  if [ -e "$D/$SKILL" ] || [ -L "$D/$SKILL" ]; then
    rm -rf "$D/$SKILL"   # si era un enlace, se borra el enlace, no su destino
  fi
  mv "$TMP" "$D/$SKILL"
  echo "OK  $D/$SKILL"
done

echo ""
echo "Hecho. Reinicia tu agente para que cargue el skill."
echo "Despues, pidele: \"comprueba el entorno de tramites-es\" (ejecutara scripts/entorno.py)."
echo "El certificado lo configuras tu en tu terminal: lee skills/$SKILL/references/setup-linux.md o setup-macos.md."
