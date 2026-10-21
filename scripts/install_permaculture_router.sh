#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

chmod +x \
  scripts/permaculture_router.py \
  scripts/validate_permaculture_context.py \
  scripts/permaculture_ci.py \
  scripts/render_permaculture_report.py \
  scripts/install_permaculture_router.sh

python3 scripts/validate_permaculture_context.py data/router_examples
python3 scripts/permaculture_router.py \
  data/router_examples/thermal-cascade-l0.json \
  --output .ci/permaculture/thermal-cascade-l0.report.json

python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/permaculture_ci.py

printf '\n=== INSTALLATION COMPLETE ===\n'
printf 'Run: python3 scripts/permaculture_ci.py\n'
printf 'Read: docs/PERMACULTURE_ROUTER.md\n'
printf 'Report: .ci/permaculture/thermal-cascade-l0.report.json\n'
