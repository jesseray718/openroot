#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — v1.1: removed goals_rebuild_from_remnants_v1.sh (doesn't exist), compute_marketplace.py handled separately
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="BANKWK1v1"
LOG=/home/jesse/openroot/logs/bank_week_${STAMP}.log
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

GENUINE=(
  bin/add_contributor_acknowledgment_v1.sh
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
  recovery_minimal_v2026.09.24.sh
  recovery_superlinear_v2026.09.24.sh
  setup_search.py
  context_bridge/solve_backup_20260924_021833.py
)

PYFAIL=0; SHFAIL=0
for f in "${GENUINE[@]}"; do
  [[ -f "$f" ]] || { echo "[gate] MISSING: $f — skipped"; continue; }
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
  git commit -m "[ADD] bank week's untracked scripts — syntax-gated (v1.1)" \
    -m "reh1t reconciliation trio, model_registry tooling, stack status v1/v2, superlinear strike, recovery scripts, misc bin/" \
    -m "Excluded: compute_marketplace.py (syntax fix pending), goals_rebuild_from_remnants_v1.sh (missing)" \
    -m "AI-assisted, human-gated"
  git log --oneline -1
  echo "[banked] week scripts committed"
else
  echo "[held] CONFIRM=1 to commit ${#GENUINE[@]} scripts"
fi

echo "[$CANARY] END $STAMP [exit=0]"
