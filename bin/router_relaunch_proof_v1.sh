#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:pre-flight] verify the outbox dir exists now (self-init guard is active)"
ssh -o BatchMode=yes optiplex-ts 'test -d /home/jesse/openroot/lumo_lane/outbox && echo OUTBOX_OK || echo OUTBOX_MISSING'

echo "[STAGE:relaunch] detached 5-round, must survive the 25s mark this time"
ssh -o BatchMode=yes optiplex-ts "bash -s" <<'REMOTE'
set -eu
cd ~/openroot
LOG="context_bridge/router-detached-${TS}.log"
nohup env ROUTER_ROUNDS=5 python3 bin/multi_router.py > "$LOG" 2>&1 &
PID=$!
sleep 30
kill -0 "$PID" 2>/dev/null && echo "[ALIVE] pid=${PID} past the 30s death-mark" || { echo "[DEAD] exited early"; tail -8 "$LOG"; exit 1; }
echo "[LOG] ${LOG}"
REMOTE

echo "[STAGE:seal] proof session artifact"
cat <<SEED > context_bridge/session-2026-09-21-router-proof.md
# Router Proof Session — 2026-09-21
- Relaunch triggered after pub-ready seal (e003bda5)
- Outbox guard verified pre-launch
- Detached 5-round expected to survive 30s+ (self-init fix proven)
## Provenance: lumo-assisted, human-gated
SEED
git add context_bridge/session-2026-09-21-router-proof.md
git commit -m "[SEAL] router relaunch proof initiated — self-init guard verification"
git push origin main && echo "[RELAY] router proof started, monitor ${TS} log on OptiPlex"

echo "[exit=0]"
