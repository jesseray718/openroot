#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

printf '\n=== OPENROOT OPEN HARDWARE PREVIEW SUITE ===\n'

printf '\n=== 1. DESIGN PACKET VALIDATION ===\n'
python3 scripts/validate_design_packets.py

printf '\n=== 2. PERMACULTURE ROUTER CONTEXT VALIDATION ===\n'
python3 scripts/validate_permaculture_context.py data/router_examples designs

printf '\n=== 3. PERMACULTURE CI ===\n'
python3 scripts/permaculture_ci.py

printf '\n=== 4. OPEN HARDWARE PREVIEW ===\n'
python3 scripts/preview_open_hardware.py \
  --output-dir reports/open_hardware_preview

printf '\n=== 5. PREVIEW REPORT ===\n'
sed -n '1,360p' reports/open_hardware_preview/open_hardware_preview.md

printf '\n=== 6. GIT STATE ===\n'
git status --short

printf '\n=== 7. PROTECTED STAGING BOUNDARY ===\n'
if git diff --cached --name-only | grep -E \
'^(data/model_registry\.json|data/superloop_chains\.json|context_bridge/superloop_DASHBOARD\.md|bin/quarantine_pyfails_final_v2/)'
then
  printf '\nSTOP: protected local/runtime files are staged.\n'
  exit 1
else
  printf '\nPASS: protected local/runtime files are not staged.\n'
fi

printf '\n=== PREVIEW COMPLETE ===\n'
