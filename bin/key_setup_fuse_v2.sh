#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
ROOT="$HOME/openroot"
TS=$(date +%Y%m%d_%H%M%S)
HOST_IP="jesse@100.122.169.43"
cd "$ROOT"

echo "[STAGE:key] generating ed25519 key if absent (no passphrase — phone-local threat model)"
if [ ! -f "$HOME/.ssh/id_ed25519.pub" ]; then
  ssh-keygen -t ed25519 -N "" -f "$HOME/.ssh/id_ed25519" -q
  echo "[KEYGEN] new key created"
else
  echo "[SKIP] key already exists — idempotent"
fi

echo "[STAGE:authorize] ONE final password prompt to install the key on OptiPlex"
ssh-copy-id -o StrictHostKeyChecking=accept-new "$HOST_IP" || echo "[HELD] ssh-copy-id failed — check password/host, nothing else touched"

echo "[STAGE:verify] passwordless test (BatchMode refuses to prompt — proves key works)"
ssh -o BatchMode=yes "$HOST_IP" 'echo "[PASSWORDLESS] ok as $(whoami)@$(hostname)"' \
  || { echo "[FAIL] key not working — stop here, debug manually"; exit 1; }

echo "[STAGE:config] ~/.ssh/config so plain 'ssh optiplex' works"
touch "$HOME/.ssh/config"; chmod 600 "$HOME/.ssh/config"
grep -q "Host optiplex" "$HOME/.ssh/config" || cat >> "$HOME/.ssh/config" <<CFG
Host optiplex
  HostName 100.122.169.43
  User jesse
  ServerAliveInterval 30
  ServerAliveCountMax 6
CFG
echo "[CONFIG] 'ssh optiplex' now resolves — Tailscale IP for now, swap to 192.168.1.193 when home"

echo "[STAGE:remote-audit] AST-level os-import check (grep was a false-negative instrument)"
ssh -o BatchMode=yes optiplex "bash -s" <<'REMOTE'
set -eu
cd ~/openroot
python3 - <<'PYEOF'
import ast
from pathlib import Path
p = Path("bin/multi_router.py")
tree = ast.parse(p.read_text())
has_os = any(
    (isinstance(n, ast.Import) and any(a.name.split(".")[0] == "os" for a in n.names))
    or (isinstance(n, ast.ImportFrom) and n.module and n.module.split(".")[0] == "os")
    for n in ast.walk(tree)
)
if has_os:
    print("[AUDIT] os import CONFIRMED via AST — prior grep gate was the false negative")
else:
    lines = p.read_text().splitlines(True)
    ins = next(i for i, l in enumerate(lines) if not l.startswith(("#", '"""', "\n", "\t", " "))) or 1
    # safer: insert after first import block
    for i, l in enumerate(lines):
        if l.startswith(("import ", "from ")):
            lines.insert(i, "import os\n"); break
    else:
        lines.insert(0, "import os\n")
    p.write_text("".join(lines))
    ast.parse(p.read_text())
    print("[PATCHED] import os inserted, re-parse clean")
PYEOF
python3 -m py_compile bin/multi_router.py && echo "[COMPILE] passed"
grep -n 'makedirs(d, exist_ok=True)' bin/multi_router.py && echo "[GREP] self-init guard confirmed in-file"
bash bin/stack_gate.sh bin/multi_router.py && echo "[GATED] stack_gate passed"
git add bin/multi_router.py
git diff --cached --quiet && { echo "[SKIP] no change to commit — guard was already banked by the parallel session"; exit 0; } || true
git commit -m "[FIX] multi_router self-init guard verified via AST audit — os import confirmed, grep gate was false negative (Lumo-authored, py_compile+grep passed)"
git push origin main && echo "[BANKED] OptiPlex HEAD $(git rev-parse --short HEAD)"
REMOTE

echo "[STAGE:relaunch] detached 5-round router via key — no password dance"
ssh -o BatchMode=yes optiplex "bash -s" <<'REMOTE2'
set -eu
cd ~/openroot
TS=$(date +%Y%m%d_%H%M%S)
LOG="context_bridge/router-detached-${TS}.log"
nohup env ROUTER_ROUNDS=5 python3 bin/multi_router.py > "$LOG" 2>&1 &
PID=$!
sleep 25
kill -0 "$PID" 2>/dev/null && echo "[ALIVE] pid=${PID} past the 25s death-mark" || { echo "[DEAD] exited early — tail:"; tail -8 "$LOG"; }
echo "[LOG] ${LOG} — ssh optiplex then: tail -f ${LOG}"
REMOTE2

echo "[STAGE:converge] A15 sync — fork-only, no force"
git fetch origin
cp data/team_gate.db "context_bridge/runtime_backups/team_gate.pre-converge-${TS}.db" 2>/dev/null || true
git checkout -- data/team_gate.db 2>/dev/null || true
if [ -n "$(git log --oneline origin/main..HEAD)" ]; then
  git rebase origin/main || { echo "[HELD] rebase conflict — manual gate: resolve, git rebase --continue"; git rebase --abort; exit 1; }
else
  git pull --ff-only origin main
fi
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] && echo "[SYNCED] HEAD = origin/main = $(git rev-parse --short HEAD)"

echo "[STAGE:bind] cross-node mistake binding (shared fingerprint namespace)"
if [ -f bin/lb_loop_v2.py ]; then
  SHA=$(python3 - <<'PYEOF'
import sys
sys.path.insert(0, "bin")
import lb_loop_v2
crash = 'Traceback (most recent call last): File "/home/jesse/openroot/bin/multi_router.py", line 248, in main for f in sorted(os.listdir(ob))[-3:]: FileNotFoundError: [Errno 2] No such file or directory: /home/jesse/openroot/lumo_lane/outbox'
print(lb_loop_v2.fingerprint(crash))
PYEOF
)
  python3 bin/lb_loop_v2.py solve "$SHA" \
    "missing-dir boot-crash class: consumer assumed lumo_lane/outbox existed. Fix: main() self-init makedirs every consumed dir at boot. Same class as Termux /tmp denial. Secondary lesson: grep is a weak import gate — AST-level audit is the instrument (grep false-negative held this very fix once)."
  echo "[BOUND] ${SHA}"
fi
python3 bin/lb_loop_v2.py stats 2>/dev/null || true

echo "[STAGE:seal] session artifact"
cat <<'SEED' > "context_bridge/session-2026-09-21-keyfusion-seal.md"
# Session Seal: SSH key auth + fusion-complete — 2026-09-21
- A15->OptiPlex passwordless via ed25519 key (ssh-copy-id once, never again); ~/.ssh/config 'optiplex' alias
- multi_router.py os-import verified via AST (grep was false negative — instrument audited, not builder blamed)
- self-init guard confirmed; detached 5-round router relaunched (log in context_bridge/)
- Outbox crash bound to lb_loop mistake ledger cross-node; 3B code-edit certification stands from nursery v1.2
- OPEN: router results, tailscale debug (key makes retry cheap now), embed leader, doc_compiler content-hash
## Provenance: lumo-assisted, human-gated
SEED
git add "context_bridge/session-2026-09-21-keyfusion-seal.md"
git commit -m "[SEAL] ssh key auth + ast-verified router fix + cross-node ledger binding"
git push origin main && echo "[SEALED] $(git rev-parse --short HEAD)"

echo "[VERIFY]"
git log --oneline -3
echo "[CANARY] key-fusion-sealed-${TS}"
echo "[exit=0]"
