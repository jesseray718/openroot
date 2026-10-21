#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — batch the parked queue items, nothing committed without CONFIRM/human gate
# eta = useful_joules / human_joules
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="QSWEEP1"
LOG=/home/jesse/openroot/logs/queue_sweep_${STAMP}.log
mkdir -p "$(dirname "$LOG")" "$REPO/context_bridge"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

# [status] 1. bin/ tracked?
BINCNT=$(git ls-files bin/ | wc -l)
echo "[status] bin/ tracked files: $BINCNT"
if [[ "$BINCNT" -eq 0 ]] && [[ "${CONFIRM:-0}" == "1" ]]; then
  git add bin/ TASK.md analysis/ 2>/dev/null || git add bin/
  git commit -m "[FIX] bank bin/ tooling — 7B-authored, py_compile+grep+smoke lineage notes intact"
  echo "[banked] bin/ committed"
elif [[ "$BINCNT" -eq 0 ]]; then
  echo "[held] bin/ UNTRACKED — CONFIRM=1 to bank"
fi

# [status] 2. GOALS/MASTER_TODO rebuild — stage only, human gates the commit
if [[ -x "$REPO/setup_restore_v1.sh" ]]; then
  bash "$REPO/setup_restore_v1.sh" || echo "[held] setup_restore_v1 exited nonzero — inspect before retry"
  echo "[held] GOALS.rebuild* staged — review, then: git add GOALS.md MASTER_TODO.md && commit"
else
  echo "[status] setup_restore_v1.sh not found — rebuild from context_bridge/session-2026-09-16-*.md remnants"
fi

# [status] 3. quarantine branch purge check
if git ls-remote --heads origin | grep -q quarantine-pulse-20260918; then
  if [[ "${CONFIRM:-0}" == "1" ]]; then
    git push origin --delete quarantine-pulse-20260918
    echo "[banked] quarantine-pulse-20260918 deleted on origin"
  else
    echo "[held] quarantine-pulse-20260918 EXISTS on origin — CONFIRM=1 to delete"
  fi
else
  echo "[status] quarantine branch already gone"
fi

# [status] 4. pin 4 repos on profile (GraphQL updatePinnedItems replaces the pin set)
if [[ "${CONFIRM:-0}" == "1" ]]; then
  IDS=$(gh api graphql -f query='{ viewer { repositories(first: 100, ownerAffiliations: OWNER) { nodes { name id } } } }' \
    --jq '[.data.viewer.repositories.nodes[] | select(.name=="openroot" or .name=="openroot-canon" or .name=="wisdom-scaffold" or .name=="black-locust-rmh")] | map(.id) | join(" ")')
  echo "[status] pin target ids: $IDS"
  gh api graphql -f query="mutation(\$pins:[ID!]!){ updatePinnedItems(input:{pins:\$pins}){ user { pinnedItems(first:6){ totalCount } } } }" -f pins="$(echo $IDS)" \
    && echo "[banked] 4 repos pinned" || echo "[held] pin mutation shape differs — pin manually once via profile UI, then confirm"
else
  echo "[held] profile pins — CONFIRM=1 to run (targets: openroot, openroot-canon, wisdom-scaffold, black-locust-rmh)"
fi

# [banked] 5. structured handoff
HANDOFF="$REPO/context_bridge/handoff-queue-sweep-${STAMP}.md"
{
  echo "# Handoff $STAMP"
  echo "- artifacts: $LOG, $HANDOFF, data/reh1t/pr53_*.patch"
  echo "- bin/ tracked files: $BINCNT"
  echo "- HEAD: $(git rev-parse HEAD)  remote: $(git rev-parse origin/main)"
  echo "- broken: none reported unless [gate]/[held] lines above"
  echo "- next: human-gate pr53-reconcile merge, GOALS.rebuild commit, README [PHOTO] slot, aerocement-panel-v0 repo, SARE framing"
} > "$HANDOFF"
sha256sum "$HANDOFF"
echo "[$CANARY] END $STAMP [exit=0]"
