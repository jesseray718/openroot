#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — bank genuine week scripts, declare backup dirs ignored, purge junk
# eta = useful_joules / human_joules
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="BANKWK1"
LOG=/home/jesse/openroot/logs/bank_week_${STAMP}.log
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

# ============================================================
# STAGE A — genuine untracked scripts: gate then stage
# ============================================================
GENUINE=(
  bin/add_contributor_acknowledgment_v1.sh
  bin/compute_marketplace.py
  bin/compute_marketplace_v2.py
  bin/local_stack_status_v1.py
  bin/local_stack_status_v2.py
  bin/merge_ledgers.py
  bin/mobile_sync_tracker_v2.py
  bin/queue_sweep_v1.sh
  bin/reh1t_credit_check_v1.sh
  bin/reh1t_pr53_make_right_v1.sh
  bin/reh1t_reconcile_v2.sh
  bin/routing_weights_v1.py
  bin/specialist_router_v1.py
  bin/stack_test_core_v1.py
  bin/superlinear_strike_v1.py
  bin/todo_tick_v1.sh
  bin/warm_models.sh
  bin/week_sweep_team_review_v1.py
  bin/goals_rebuild_from_remnants_v1.sh
  recovery_minimal_v2026.09.24.sh
  recovery_superlinear_v2026.09.24.sh
  setup_search.py
  context_bridge/solve_backup_20260924_021833.py
  tmp/queue_batch_v1.sh
)

# [gate] syntax-check every script before staging (known defect history: 3 paste manglings this week)
PYFAIL=0; SHFAIL=0
for f in "${GENUINE[@]}"; do
  [[ -f "$f" ]] || { echo "[gate] MISSING: $f — skipped (not present)"; continue; }
  if [[ "$f" == *.py ]]; then
    python3 -m py_compile "$f" || { echo "[gate] PY_COMPILE FAIL: $f"; PYFAIL=1; }
  else
    bash -n "$f" || { echo "[gate] BASH SYNTAX FAIL: $f"; SHFAIL=1; }
  fi
done
if [[ "$PYFAIL" == "1" || "$SHFAIL" == "1" ]]; then
  echo "[gate] syntax failures above — fix or remove from list, rerun. Nothing staged."
  exit 1
fi
echo "[banked] all ${#GENUINE[@]} scripts pass syntax gates"

if [[ "${CONFIRM:-0}" == "1" ]]; then
  git add "${GENUINE[@]}"
  git commit -m "[ADD] bank week's untracked scripts — week_sweep discovery, syntax-gated" \
    -m "reh1t reconciliation trio, model_registry tooling, stack status v1/v2, superlinear strike, recovery scripts, misc bin/" \
    -m "AI-assisted, human-gated; discovered by week_sweep_team_review_v1"
  git log --oneline -1
  echo "[banked] week scripts committed"
else
  echo "[held] CONFIRM=1 to commit ${#GENUINE[@]} scripts"
fi

# ============================================================
# STAGE B — junk files: show, then delete only with CONFIRM
# ============================================================
for j in EOF PYEOF _EOF_SCRIPT_; do
  if [[ -f "$j" ]]; then
    SZ=$(wc -c < "$j")
    echo "[status] junk $j ($SZ bytes): $(head -c 80 "$j" | tr '\n' ' ')"
    if [[ "${CONFIRM:-0}" == "1" ]]; then
      rm "$j"; echo "[banked] deleted $j"
    fi
  fi
done
[[ "${CONFIRM:-0}" == "1" ]] || echo "[held] CONFIRM=1 to delete junk files"

# ============================================================
# STAGE C — README backup prune: keep newest 2
# ============================================================
BAKS=$(ls -t README.md.bak.* 2>/dev/null || true)
if [[ -n "$BAKS" ]]; then
  N=$(echo "$BAKS" | wc -l)
  if [[ "$N" -gt 2 ]]; then
    echo "$BAKS" | tail -n +3 > /tmp/bak_prune_list.txt
    echo "[status] keeping: $(echo "$BAKS" | head -2 | tr '\n' ' ')"
    echo "[status] pruning $(($(wc -l < /tmp/bak_prune_list.txt))) older backups"
    if [[ "${CONFIRM:-0}" == "1" ]]; then
      xargs -a /tmp/bak_prune_list.txt rm
      echo "[banked] README backups pruned"
    else
      echo "[held] CONFIRM=1 to prune (dry-run list: /tmp/bak_prune_list.txt)"
    fi
  fi
fi

# ============================================================
# STAGE D — gitignore declaration for salvage/backup dirs
# ============================================================
GI=.gitignore
touch "$GI"
NEW_RULES=0
while IFS= read -r rule; do
  grep -qxF "$rule" "$GI" || { echo "$rule" >> "$GI"; NEW_RULES=$((NEW_RULES+1)); }
done <<'RULES'
consolidation-backups/
ctx_backup_*/
*.md.bak.*
README.md.bak.*
data/*.db
*.log.tmp
RULES
if [[ "$NEW_RULES" -gt 0 ]]; then
  echo "[held] added $NEW_RULES gitignore rules — future sweeps won't re-flag salvage/backup copies"
  if [[ "${CONFIRM:-0}" == "1" ]]; then
    git add "$GI"
    git commit -m "[FIX] gitignore salvage/backup dirs — stop untracked-noise in week sweeps"
    git log --oneline -1
  fi
else
  echo "[status] gitignore rules already present"
fi

# ============================================================
# STAGE E — handoff
# ============================================================
HANDOFF="$REPO/context_bridge/handoff-bank-week-${STAMP}.md"
{
  echo "# Bank Week Handoff $STAMP"
  echo "- staged ${#GENUINE[@]} scripts (list in logs/bank_week_${STAMP}.log)"
  echo "- junk: EOF/PYEOF/_EOF_SCRIPT_ handled per CONFIRM"
  echo "- untracked INTENTIONALLY kept (salvage evidence): consolidation-backups/, ctx_backup_*, quarantine dirs"
  echo "- numbered bin/05xx-13xx files: TRACKED already, appear new due to recent mtime — bulk-imported library fragments, hygiene review is a separate future task, NOT lost work"
  echo "- next: read context_bridge/team_review_*.md for the 7B profile/landing/consolidation recs (output was cut in paste)"
} > "$HANDOFF"
sha256sum "$HANDOFF"
echo "[$CANARY] END $STAMP [exit=0]"
