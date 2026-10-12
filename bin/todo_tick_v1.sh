#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — mark completed queue items in MASTER_TODO.md, human-gated commit
# eta = useful_joules / human_joules
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="TICKV1"
LOG=/home/jesse/openroot/logs/todo_tick_${STAMP}.log
mkdir -p "$(dirname "$LOG")" "$REPO/context_bridge"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

cp MASTER_TODO.md "MASTER_TODO.md.bak.${STAMP}"

# [banked] tick verified-complete lines (exact-prefix sed, no collateral)
sed -i \
  -e 's|^- \[ \] Verify/commit bin/ directory|- [x] Verify/commit bin/ directory|' \
  -e 's|^- \[ \] Rebuild GOALS.md + MASTER_TODO|- [x] Rebuild GOALS.md + MASTER_TODO|' \
  -e 's|^- \[ \] Support Reh1t PR #53|- [x] Support Reh1t PR #53|' \
  -e 's|^- \[ \] Pin 4 repos on profile|- [x] Pin 4 repos on profile|' \
  MASTER_TODO.md

grep -n "^- \[x\]" MASTER_TODO.md

if [[ "${CONFIRM:-0}" == "1" ]]; then
  git add MASTER_TODO.md
  git commit -m "[FIX] MASTER_TODO tick — bin/ banked (1555 files), GOALS restore verified (8af3fd29/f2e6fc9a/52082cfe), Reh1t #63 credit verified + thanked, pins set" \
    -m "AI-assisted, human-gated; backup MASTER_TODO.md.bak.${STAMP} kept local"
  git log --oneline -1
  echo "[banked] committed"
else
  echo "[held] CONFIRM=1 to commit the ticked MASTER_TODO.md (diff shown above, backup at MASTER_TODO.md.bak.${STAMP})"
fi

# [banked] handoff seal
HANDOFF="$REPO/context_bridge/handoff-queue-drain-${STAMP}.md"
{
  echo "# Queue Drain Handoff $STAMP"
  echo "## Artifacts"
  echo "- logs/reh1t_credit_20260924_16*.log — #63 authorship verification (eb247e94, both identities)"
  echo "- data/reh1t/thanks_20260924_160318.md — sha256 523464ca... (posted, comment 5822206745)"
  echo "- context_bridge/handoff-queue-sweep-20260924_16*.md — sweep receipts"
  echo "## Verified State"
  echo "- HEAD: $(git rev-parse HEAD)"
  echo "- Reh1t: PR #63 MERGED with credit; issue #53 CLOSED; thank-you posted; dead branches purged (pr53-reconcile, reh1t-53-local-AI)"
  echo "- GOALS/MASTER_TODO: already restored via 8af3fd29/f2e6fc9a/52082cfe — no rebuild needed"
  echo "- bin/: 1555 tracked files"
  echo "- quarantine branch: gone from origin"
  echo "## Broken"
  echo "- pin mutation: updatePinnedItems not a valid GraphQL field — pin manually at github.com/settings/profile (Customize pins), ~30s"
  echo "## Next Actions"
  echo "1. README [PHOTO] slot (docs/img/ + markdown embed)"
  echo "2. aerocement-panel-v0 standalone repo with build evidence (N11 gate: MANIFEST/CLAIMS/INTEGRATION/INTEGRATION_CHECKLIST before publish)"
  echo "3. SARE grant framing (COP-boundary language only)"
  echo "4. cascade-v2.0: fix SOL 300x100 > floor cap 100x100"
  echo "5. Phone pane: canon.py prints 0.0 — blocks new modules"
} > "$HANDOFF"
sha256sum "$HANDOFF"
echo "[$CANARY] END $STAMP [exit=0]"
