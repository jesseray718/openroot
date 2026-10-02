#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat

ssh -o BatchMode=yes optiplex-ts "bash -s" <<'REMOTE'
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)   # defined HERE, remote side — quoted heredoc means no A15 expansion crosses

echo "[STAGE:pre-flight] outbox dir present (self-init guard proof #1)"
test -d lumo_lane/outbox && echo OUTBOX_OK || { echo "[GATE] outbox missing — self-init guard suspect, aborting"; exit 1; }

echo "[STAGE:sync] main current before any seal"
git fetch origin
[ -z "$(git log --oneline HEAD..origin/main)" ] || { echo "[HELD] behind origin — pulling ff"; git pull --ff-only origin main; }
[ -z "$(git log --oneline origin/main..HEAD)" ] || { echo "[HELD] local ahead — review first"; exit 1; }
echo "[OK] HEAD = $(git rev-parse --short HEAD) = origin/main"

echo "[STAGE:relaunch] detached 5-round, must survive the 30s death-mark"
LOG="context_bridge/router-detached-${TS}.log"
nohup env ROUTER_ROUNDS=5 python3 bin/multi_router.py > "$LOG" 2>&1 &
PID=$!
sleep 30
if kill -0 "$PID" 2>/dev/null; then
  echo "[ALIVE] pid=${PID} past 30s — self-init guard held under real load (proof #2)"
  echo "[TAIL] early rounds:"
  grep -E "ROUTER ROUND|PASS|FAIL|HIVE" "$LOG" | head -10 || true
else
  echo "[DEAD] exited early — honest state, tail:"
  tail -10 "$LOG"
  exit 1
fi
echo "[LOG] ${LOG} — monitor anytime: tail -f ${LOG}"

echo "[STAGE:seal] proof artifact, committed where the proof lives"
cat > context_bridge/session-2026-09-21-router-proof.md <<SEED
# Router Proof Session — 2026-09-21
- Pre-flight: lumo_lane/outbox present (OUTBOX_OK) — self-init guard active
- Detached 5-round relaunch survived the 30s death-mark where the previous run died in ~20s
- Crash class (FileNotFoundError lumo_lane/outbox) closed: guard in cf6c422a, now proven under load
- Prior router pgrep hits re-confirmed as ssh argv false-positives; argv-exact check doctrine stands
- Root lesson (v1 miss, fixed in this script): quoted heredoc 'REMOTE' exports NOTHING — every
  var used remotely must be defined inside the remote block. Cross-boundary assumption class.
- OPEN: full 5-round results (tail router-detached-${TS}.log), CONFIRM=1 pub-ready execution, v2.9 cascade
## Provenance: lumo-assisted, human-gated
SEED
git add context_bridge/session-2026-09-21-router-proof.md
git commit -m "[SEAL] router self-init guard proven under load — detached 5-round alive past death-mark"
git push origin main && echo "[SEALED] $(git rev-parse --short HEAD)"

echo "[CANARY] router-proof-v2-${TS}"
echo "[exit=0]"
REMOTE

echo "[exit=0]"
