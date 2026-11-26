#!/usr/bin/env bash
# Actualiza `_identidad/` a la última etiqueta `identidad-v*` del paquete.
# Uso: scripts/actualizar-identidad.sh [--check]
#   sin argumentos: descarga la última versión si hay una nueva.
#   --check: no descarga; sale 1 si la copia no es la última etiqueta.
# Sale 0 si está al día; 1 si hay que actualizar, no hay etiquetas o falla.

set -euo pipefail

modo="${1:-}"

REPO_URL="https://github.com/lanuzalorenzo/lanuzalorenzo.github.io"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="$RAIZ/_identidad"
FICHEROS=(identidad.css plantilla.tpl shell.py menu.js marca-tile.svg SHA256SUMS VERSION LEEME.md)

ultima="$(git ls-remote --tags --refs "$REPO_URL" 'identidad-v*' \
  | sed 's#.*refs/tags/##' | sort -V | tail -1)"
if [ -z "$ultima" ]; then
  echo "sin etiquetas identidad-v* en $REPO_URL" >&2
  exit 1
fi

actual="$(cat "$DESTINO/VERSION")"
nueva="${ultima#identidad-v}"
if [ "$actual" = "$nueva" ]; then
  echo "al día: $actual"
  exit 0
fi
if [ "$modo" = "--check" ]; then
  echo "atrasado: $actual; la última etiqueta es identidad-v$nueva" >&2
  echo "ejecuta scripts/actualizar-identidad.sh" >&2
  exit 1
fi

# Se descarga por el commit de la etiqueta y no por su nombre: raw.github
# cachea el 404 de una etiqueta recién creada para rutas sueltas.
commit="$(git ls-remote --tags --refs "$REPO_URL" "$ultima" | cut -f1)"
base="https://raw.githubusercontent.com/lanuzalorenzo/lanuzalorenzo.github.io/$commit/identidad"
for fichero in "${FICHEROS[@]}"; do
  curl -sSfL "$base/$fichero" -o "$DESTINO/$fichero"
done
(cd "$DESTINO" && sha256sum -c SHA256SUMS --quiet)
echo "actualizado: $actual → $nueva"
