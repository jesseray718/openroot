#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "OpenRoot API stack ready. orq \"H-003 12.91 kWh/m2 Sikeston MO UNE JSON + ACRE delta\""
[ -f "$ROOT/shell/termux-hook.sh" ] && bash "$ROOT/shell/termux-hook.sh" || true
