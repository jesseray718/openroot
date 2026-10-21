#!/usr/bin/env bash
# doctrine_v1.sh — untrack runtime derivatives, codify config-vs-runtime law
# SPDX-License-Identifier: GPL-3.0-only
# Usage: CONFIRM=1 bash bin/doctrine_v1.sh
set -euo pipefail
export GIT_PAGER=cat

cd /home/jesse/openroot
CANARY="DOCTRINEV1"
STAMP="$(date +%Y%m%d_%H%M%S)"
echo "[$CANARY] $(date -u +%FT%TZ) | stamp=$STAMP"

echo "[gate 0] tracked-state check:"
git ls-files --error-unmatch data/superloop_chains.json >/dev/null 2>&1 \
  && echo "  chains.json: TRACKED (expectation met)" || echo "  chains.json: already untracked"
git ls-files --error-unmatch context_bridge/superloop_DASHBOARD.md >/dev/null 2>&1 \
  && echo "  DASHBOARD.md: TRACKED (expectation met)" || echo "  DASHBOARD.md: already untracked"

echo "[stage 1] untracking runtime derivatives (disk copies preserved)..."
git rm --cached data/superloop_chains.json context_bridge/superloop_DASHBOARD.md
echo "[banked] both untracked; disk copies preserved"

echo "[stage 2] gitignore hardening (idempotent)..."
grep -q '^data/superloop_chains.json$' .gitignore 2>/dev/null || echo 'data/superloop_chains.json' >> .gitignore
grep -q '^context_bridge/superloop_DASHBOARD.md$' .gitignore 2>/dev/null || echo 'context_bridge/superloop_DASHBOARD.md' >> .gitignore
echo "[banked] .gitignore rules appended"

echo "[stage 3] codify law in PIPELINE.md..."
if ! grep -q 'DATA DOCTRINE' PIPELINE.md; then
  cat >> PIPELINE.md <<'DOCEOF'

## Data Doctrine (config vs runtime)

Tracked = config, rewritten only by deliberate human-gated commits:

- `data/model_registry.json` — routing weights, provenance-worthy. Tooling READS
  this file; only the human gate WRITES it. Auto-rewrites land in
  `data/operator_holds/` for review instead.

Untracked = runtime derivatives, regenerated freely on disk:

- `data/superloop_chains.json` — analytics VIEW re-derived from command history
  each pulse. Immutable source is the SQLite ledger + mistake_solutions/.
- `context_bridge/superloop_DASHBOARD.md` — cron-pulsed dashboard (15 min).
  Regen templates must re-add the SPDX header before any future re-tracking.

Rule: a file is tracked XOR machine-written. Never both.
DOCEOF
  echo "[banked] PIPELINE.md doctrine section appended"
else
  echo "[gate] PIPELINE.md already has DATA DOCTRINE — skipped"
fi

echo "[stage 4] commit..."
git add .gitignore PIPELINE.md bin/doctrine_v1.sh
git diff --cached --quiet && { echo "[gate] nothing staged — aborting"; exit 0; }
git commit -m "[FIX] doctrine: untrack runtime derivatives (chains.json, DASHBOARD.md), codify config-vs-runtime law

- chains.json is a regenerated analytics view, not provenance
- DASHBOARD.md pulses via cron every 15min; latest regen dropped SPDX header
- model_registry.json stays tracked as config: tooling reads, human gate writes
- .gitignore hardened so regeneration never dirties the tree
- doctrine_v1.sh itself banked to bin/

AI-assisted, human-gated."
echo "[banked] doctrine commit sealed: $(git rev-parse --short HEAD)"

echo "[$CANARY] done stamp=$STAMP"
echo "[exit=0]"
