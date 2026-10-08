#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
cd ~/openroot
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:sync] pulling lb_loop_v2 from origin"
git pull --ff-only origin main
HEAD_SHORT=$(git rev-parse --short HEAD)
echo "[HEAD] ${HEAD_SHORT}"
if ! git ls-files --error-unmatch bin/lb_loop_v2.py >/dev/null 2>&1; then
  echo "[HALT] lb_loop_v2.py not on origin — A15 push may have failed; run install paste there first"
  exit 1
fi

echo "[STAGE:verify] instrument audit (instrument-before-builder doctrine)"
for f in bin/compound_v1.sh bin/doc_compile.py bin/agent.sh bin/stack_gate.sh bin/team_gate_v2.sh; do
  if [ -f "$f" ]; then
    echo "[OK] $f ($(wc -l < "$f") lines)"
  else
    echo "[MISSING] $f — stage will cache-fail; audit before loop"
  fi
done
echo "[AUDIT] refine_next.sh: $(wc -l < bin/refine_next.sh) lines (stub-held, excluded)"

echo "[STAGE:seed] reseeding mistake ledger on fresh OptiPlex DB (runtime dbs don't travel via git)"
python3 bin/lb_loop_v2.py seed
python3 bin/lb_loop_v2.py show
python3 bin/lb_loop_v2.py stats

echo "[STAGE:loop] cold run on OptiPlex (full compute — local models, real corpus)"
python3 bin/lb_loop_v2.py run
LOOP_RC=$?
echo "[LOOP-RC] ${LOOP_RC}"

echo "[STAGE:proof] immediate rerun must be pure cache — the compounding proof"
python3 bin/lb_loop_v2.py run
PROOF_RC=$?
python3 bin/lb_loop_v2.py stats

echo "[STAGE:handoff] session state seal"
cat <<SEED > context_bridge/session-2026-09-21-optiplex-lbloop.md
# Session: OptiPlex lb_loop deployment — 2026-09-21
- lb_loop_v2 pulled @ ${HEAD_SHORT}; ledger reseeded fresh (dbs are per-node runtime)
- cold pass rc=${LOOP_RC}, cache-proof rc=${PROOF_RC}
- doctrine: OptiPlex = compute node, A15 = lightweight compile node; cache dbs stay per-node, seeds travel via git
SEED
git add context_bridge/session-2026-09-21-optiplex-lbloop.md
git commit -m "[SEED] optiplex lb_loop deployment — cache/ledger state log"
git push origin main && echo "[BANKED] pushed $(git rev-parse --short HEAD)"

echo "[CANARY] optiplex-lbloop-${TS}"
echo "[exit=0]"
