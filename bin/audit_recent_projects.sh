# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

ROOT="$HOME/openloom-build"
REPORT="$ROOT/PROJECT_FINALIZATION_REPORT.md"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

cd "$ROOT"

{
  printf '# OpenLoom Recent Project Finalization Audit\n\n'
  printf 'Generated: %s\n\n' "$STAMP"
  printf 'Scope: files modified or created in the last 5 hours.\n\n'

  printf '## Git boundary\n\n'
  printf 'Current branch: `%s`\n\n' "$(git rev-parse --abbrev-ref HEAD)"
  printf 'HEAD: `%s`\n\n' "$(git rev-parse --short HEAD)"

  printf '### Untracked project paths\n\n'
  if git status --porcelain | grep -q '^??'; then
    git status --porcelain | grep '^??' | sed 's/^?? //' | sort
  else
    echo 'None.'
  fi

  printf '\n### Modified tracked files\n\n'
  if git status --porcelain | grep -Eq '^ M|^M '; then
    git status --porcelain | grep -E '^ M|^M ' | sed 's/^...//' | sort
  else
    echo 'None.'
  fi

  printf '\n## Files changed in the last 5 hours\n\n'
  printf '```text\n'
  find . \
    -path './.git' -prune -o \
    -path './.venv' -prune -o \
    -path './demo-pod/*.db-wal' -prune -o \
    -path './demo-pod/*.db-shm' -prune -o \
    -type f -mmin -300 -print | sort
  printf '```\n\n'

  printf '## Suggested finalization groups\n\n'
  printf '### Core OpenLoom source\n\n'
  printf '```text\n'
  find openloom tests -type f -mmin -300 2>/dev/null | sort || true
  printf '```\n\n'

  printf '### Local operator scripts and configuration\n\n'
  printf '```text\n'
  find bin config tasks -type f -mmin -300 2>/dev/null | sort || true
  printf '```\n\n'

  printf '### Evidence artifacts\n\n'
  printf '```text\n'
  find evidence -type f -mmin -300 2>/dev/null | sort || true
  printf '```\n\n'

  printf '### Runtime and generated artifacts\n\n'
  printf '```text\n'
  find runs demo-pod -type f -mmin -300 2>/dev/null | sort || true
  printf '```\n\n'

  printf '## Verification evidence\n\n'
  printf '```json\n'
  python3 -m openloom.cli verify --pod demo-pod
  printf '```\n\n'

  printf '## Manual table extraction summary\n\n'
  if [[ -f evidence/lubuntu-manual/tables/tables_manifest.json ]]; then
    python3 - <<'PY'
import json
from pathlib import Path
p = Path("evidence/lubuntu-manual/tables/tables_manifest.json")
m = json.loads(p.read_text())
print(json.dumps({
    "manifest": str(p),
    "tables": len(m),
    "pdf_pages": sorted({x["pdf_page"] for x in m}),
    "total_rows": sum(x["rows"] for x in m),
}, indent=2))
PY
  else
    echo 'No table manifest found.'
  fi

  printf '\n## Safe finalization recommendation\n\n'
  printf '1. Keep `.venv/`, `demo-pod/`, `runs/`, WAL/SHM files, and bulky generated evidence out of Git.\n'
  printf '2. Review and commit only source, tests, operator scripts, configuration, and selected evidence manifests/receipts.\n'
  printf '3. Do not push until `openloom verify` passes and the staged diff has been reviewed.\n'
} > "$REPORT"

printf 'REPORT_WRITTEN %s\n' "$REPORT"
printf '\n--- REPORT PREVIEW ---\n'
sed -n '1,220p' "$REPORT"
