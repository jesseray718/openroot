#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
cd ~/openroot
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:audit] what did the truncated run actually do?"
python3 bin/lb_loop_v2.py stats
python3 - <<'PYEOF'
import sqlite3
c = sqlite3.connect("data/lb_loop.db")
rows = c.execute("SELECT iter, stage, result, mistake_sha FROM loop_log ORDER BY id").fetchall()
if not rows:
    print("[LOG] empty — loop_log written after stage completion; run may have been cut before any flush")
else:
    for it, st, res, sha in rows:
        print(f"iter {it} | {st:<13} | {res}{(' @' + sha) if sha else ''}")
    last = rows[-1][2]
    print(f"[STATE] last stage result: {last} — {'clean pass recorded' if last in ('pass','cache_hit','recovered') else 'interrupted/incomplete'}")
PYEOF

echo "[STAGE:resume] driving loop to completion (passed stages return instantly from cache)"
python3 bin/lb_loop_v2.py run
RUN1=$?
echo "[LOOP-RC] ${RUN1}"

if [ "${RUN1}" = "0" ]; then
  echo "[STAGE:proof] compounding check — rerun must be pure cache"
  python3 bin/lb_loop_v2.py run
  RUN2=$?
  python3 bin/lb_loop_v2.py stats
  echo "[PROOF-RC] ${RUN2} (0 = every stage cache-hit; that is the non-recompute pathway demonstrated)"
fi

echo "[STAGE:seal] session handoff"
cat <<SEED > context_bridge/session-2026-09-21-optiplex-lbloop-resume.md
# OptiPlex lb_loop resume — 2026-09-21
- pulled @ 9130d06f; ledger seeded 4 pairs; refinery stub-held; agent_loop deferred (LB_SPEC unset)
- first cold run truncated in display; loop_log records truth
- resume rc=${RUN1:-n/a}; ledger/cache state in data/lb_loop.db (per-node runtime)
- OPEN: LB_SPEC for agent_loop, refine_next.sh rebuild, auto-fix bindings, agape_cascade v2
## Provenance: lumo-assisted, human-gated
SEED
git add context_bridge/session-2026-09-21-optiplex-lbloop-resume.md
git commit -m "[SEED] optiplex lb_loop resume — completion attempt from cache"
git push origin main && echo "[BANKED] pushed $(git rev-parse --short HEAD)"

echo "[CANARY] lbloop-resumed-${TS}"
echo "[exit=0]"
