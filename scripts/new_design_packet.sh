#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/templates/design-packet"
DEST_ROOT="$ROOT/designs"

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <slug> <design-name> <maintainer>" >&2
  exit 2
fi

SLUG="$1"
NAME="$2"
MAINTAINER="$3"
DATE="$(date +%F)"
DESIGN_ID="$(printf '%s' "$SLUG" | tr '[:lower:]-' '[:upper:]_' | tr -cd 'A-Z0-9_')"
DEST="$DEST_ROOT/$SLUG"

if ! printf '%s' "$SLUG" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$'; then
  echo "Invalid slug. Use lowercase letters, digits, and single hyphens." >&2
  exit 1
fi

if [ ! -d "$TEMPLATE" ]; then
  echo "Missing template: $TEMPLATE" >&2
  exit 1
fi

if [ -e "$DEST" ]; then
  echo "Destination exists: $DEST" >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"
cp -a "$TEMPLATE" "$DEST"

while IFS= read -r -d '' file; do
  python3 - "$file" "$DESIGN_ID" "$NAME" "$SLUG" "$MAINTAINER" "$DATE" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
replacements = {
    "{{DESIGN_ID}}": sys.argv[2],
    "{{DESIGN_NAME}}": sys.argv[3],
    "{{DESIGN_SLUG}}": sys.argv[4],
    "{{MAINTAINER}}": sys.argv[5],
    "{{DATE}}": sys.argv[6],
}
text = path.read_text(encoding="utf-8")
for source, target in replacements.items():
    text = text.replace(source, target)
path.write_text(text, encoding="utf-8")
PY
done < <(find "$DEST" -type f -print0)

echo "Created: $DEST"
