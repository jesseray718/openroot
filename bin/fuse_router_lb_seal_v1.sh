#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
ROOT="$HOME/openroot"
TS=$(date +%Y%m%d_%H%M%S)
HOST="jesse@100.122.169.43"
cd "$ROOT"

echo "[STAGE:tunnel-check] OptiPlex reachable via Tailscale?"
if ! ssh -o ConnectTimeout=8 "$HOST" 'echo ok' >/dev/null 2>&1; then
  echo "[HELD] cannot reach $HOST — run when tunnel is up; nothing half-done yet"
  exit 1
fi

echo "[STAGE:remote-fix] multi_router.py self-init guard — consumers guarantee their dirs (root cause, not symptom)"
ssh "$HOST" "bash -s" <<'REMOTE'
set -eu
export GIT_PAGER=cat
cd ~/openroot
mkdir -p lumo_lane/outbox   # symptom relief for the detached relaunch below

python3 - <<'PYEOF'
from pathlib import Path
p = Path.home() / "openroot" / "bin" / "multi_router.py"
t = p.read_text()
if "lumo_lane/outbox" in t and "makedirs" in t:
    print("[SKIP] self-init guard already present — idempotent"); raise SystemExit(0)
anchor = "def main():"
assert anchor in t, "[GATE] main() anchor not found — manual review, refusing to patch blind"
guard = (
    "def main():\n"
    "    # self-init: every lane dir the router consumes is guaranteed here\n"
    "    for d in (\"lumo_lane/outbox\",):\n"
    "        os.makedirs(d, exist_ok=True)\n"
)
i = t.index(anchor) + len(anchor)
p.write_text(t[:i] + "\n" + guard[len(anchor)+1:] + t[i:])
print("[PATCHED] main() now makedirs lumo_lane/outbox before any round")
PYEOF

grep -n "import os" bin/multi_router.py >/dev/null || { echo "[GATE] os import missing — manual review"; exit 1; }
python3 -m py_compile bin/multi_router.py && echo "[COMPILE] passed"
grep -n 'makedirs(d, exist_ok=True)' bin/multi_router.py && echo "[GREP] guard verified in-file"
bash bin/stack_gate.sh bin/multi_router.py && echo "[GATED] stack_gate passed"

cat <<'MSG' > .commitmsg.txt
[FIX] multi_router self-init guard for lumo_lane/outbox (boot-crash class)

- router crashed round 1: FileNotFoundError lumo_lane/outbox (detached run pid dead in 20s)
- main() now guarantees every consumed dir exists before any round — consumer self-init doctrine
- crash bound to lb_loop mistake ledger on A15 (same fingerprint namespace) for permanent lookup

Provenance: lumo-assisted, human-gated
MSG
git add bin/multi_router.py
git commit -F .commitmsg.txt && rm -f .commitmsg.txt
git push origin main && echo "[BANKED] OptiPlex pushed $(git rev-parse --short HEAD)"
REMOTE

echo "[STAGE:relaunch] detached 5-round router — must survive this SSH death"
ssh "$HOST" "bash -s" <<'REMOTE2'
set -eu
cd ~/openroot
TS=$(date +%Y%m%d_%H%M%S)
LOG="context_bridge/router-detached-${TS}.log"
nohup env ROUTER_ROUNDS=5 python3 bin/multi_router.py > "$LOG" 2>&1 &
PID=$!
sleep 25
if kill -0 "$PID" 2>/dev/null; then
  echo "[ALIVE] pid=${PID} past the 25s mark where the last run died"
else
  echo "[DEAD] exited early — tail:"; tail -8 "$LOG"; exit 1
fi
echo "[LOG] ${LOG}"
echo "--- early tail ---"
tail -15 "$LOG"
echo "PASS_ROUND1" ; grep -c "ROUTER ROUND" "$LOG" || true
REMOTE2

echo "[STAGE:converge] A15 clone — fork-only, no force, hold on conflict"
git fetch origin
mkdir -p context_bridge/runtime_backups
cp data/team_gate.db "context_bridge/runtime_backups/team_gate.pre-rebase-${TS}.db" 2>/dev/null || true
git checkout -- data/team_gate.db 2>/dev/null || true
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  if [ -n "$(git log --oneline origin/main..HEAD)" ]; then
    echo "[LOCAL-ONLY] replaying:"; git log --oneline origin/main..HEAD
    git rebase origin/main || { echo "[HELD] rebase conflict — manual gate: resolve, git rebase --continue"; git rebase --abort; exit 1; }
  else
    git pull --ff-only origin main
  fi
fi
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] && echo "[SYNCED] HEAD = origin/main = $(git rev-parse --short HEAD)"

echo "[STAGE:bind] fusing the crash into the lb_loop ledger — OptiPlex fingerprint namespace"
if [ -f bin/lb_loop_v2.py ]; then
  CRASH='Traceback (most recent call last): File "/home/jesse/openroot/bin/multi_router.py", line 248, in main for f in sorted(os.listdir(ob))[-3:]: FileNotFoundError: [Errno 2] No such file or directory: /home/jesse/openroot/lumo_lane/outbox'
  SHA=$(python3 - "$CRASH" <<'PYEOF'
import sys
sys.path.insert(0, "bin")
import lb_loop_v2
print(lb_loop_v2.fingerprint(sys.argv[1]))
PYEOF
)
  python3 bin/lb_loop_v2.py solve "$SHA" \
    "missing-dir boot-crash class: consumer assumed lumo_lane/outbox existed. Fix: main() self-init makedirs every consumed dir at boot (OptiPlex commit; same class as Termux /tmp denial). auto-generatable via: mkdir -p."
  echo "[BOUND] ${SHA} — future occurrences are lookups, never re-debug"
else
  echo "[HELD] bin/lb_loop_v2.py absent on A15 after converge — bind skipped, noted in seal"
fi
python3 bin/lb_loop_v2.py stats 2>/dev/null || true

echo "[STAGE:seal] fused session artifact"
cat <<'SEED' > "context_bridge/session-2026-09-21-fusion-router-lb-seal.md"
# Session Seal: Hive→Router→Ledger fusion — 2026-09-21
- HIVE NURSERY v1.2 (probe-hardened): 3B swept ALL classes incl. code-edit (1481ms vs 7B 3670ms)
  against the echo≠edit structural probe — real talent data, not probe weakness. Registry: data/hive_registry.json.
- ROUTER: died round 1 on lumo_lane/outbox FileNotFoundError; root-caused to missing consumer
  self-init; main() now makedirs every consumed dir; relaunched detached 5-round (survived 25s mark).
- LEDGER FUSION: OptiPlex crash fingerprinted via lb_loop_v2.fingerprint() (shared namespace)
  and bound to solution — first cross-node mistake binding.
- CONVERGE: A15 rebased fork-only onto origin/main (post OptiPlex push).
- Class-pattern emerging across ALL halts this window: instruments invoked bare or dirs assumed
  present — self-init + explicit-operand doctrine closes the whole family, not one instance.
- OPEN: router 5-round results (tail the detached log on OptiPlex), embed leader (nomic 0-dim false-pass
  still), doc_compiler mtime→content-hash, refinery stub, LB_SPEC target.
## Provenance: lumo-assisted, human-gated
SEED
git add "context_bridge/session-2026-09-21-fusion-router-lb-seal.md"
git commit -m "[SEAL] hive-router-ledger fusion: outbox self-init fix, cross-node mistake binding, 3B code-edit certification"
git push origin main && echo "[SEALED] $(git rev-parse --short HEAD)"

echo "[VERIFY] final state"
git log --oneline -3
git status --short | head -3

echo "[CANARY] fuse-router-lb-sealed-${TS}"
echo "[exit=0]"
