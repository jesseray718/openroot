#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# readme_contributors.sh — maintain Contributors section in README.md
# Idempotent: adds section/contributor only if missing. Marker-guarded table.
# USAGE: bin/readme_contributors.sh [handle] [description]
set -eu
cd /home/jesse/openroot
README=README.md
HANDLE="${1:-}"; DESC="${2:-}"
[ -f "$README" ] || { echo "[held] README.md not found"; exit 1; }
if ! grep -q "^## Contributors" "$README"; then
  printf '\n## Contributors\n\nOpenRoot is built by its contributors. Shared credit is the doctrine.\n\n<!-- CONTRIBUTORS-TABLE-START -->\n<!-- CONTRIBUTORS-TABLE-END -->\n' >> "$README"
  echo "[banked] Contributors section created"
fi
insert_row() {
  if grep -q "github.com/$1\b" "$README"; then
    echo "[banked] $1 already listed"
  else
    sed -i "s|<!-- CONTRIBUTORS-TABLE-END -->|[$1](https://github.com/$1) — $2\\\\n<!-- CONTRIBUTORS-TABLE-END -->|" "$README"
    echo "[banked] README contributor added: $1 — $2"
  fi
}
insert_row "jesseray718" "Founder, maintainer, OpenRoot doctrine author"
[ -n "$HANDLE" ] && [ -n "$DESC" ] && insert_row "$HANDLE" "$DESC"
