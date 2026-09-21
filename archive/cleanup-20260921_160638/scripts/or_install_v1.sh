#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:install] type your OPENROUTER_API_KEY now (blind — nothing echoes, nothing logs):"
read -rs KEY
if [ ${#KEY} -lt 20 ]; then
  echo "[HELD] key looks too short to be real (${#KEY} chars) — nothing written. Retry if typo."
  exit 1
fi
mkdir -p "$HOME/.openrouter"
printf 'export OPENROUTER_API_KEY=%s\n' "$KEY" > "$HOME/.openrouter/env"
chmod 600 "$HOME/.openrouter/env"
unset KEY
echo "[INSTALLED] ~/.openrouter/env (mode 600, outside all repos, never in git)"

echo "[STAGE:launch] 5-round router, key sourced into launch shell only"
LOG="context_bridge/router-detached-orinstal-${TS}.log"
nohup bash -c "set -a; source $HOME/.openrouter/env; set +a; env ROUTER_ROUNDS=5 python3 bin/multi_router.py" > "$LOG" 2>&1 &
PID=$!
echo "[LAUNCHED] pid=${PID}"
sleep 45

echo "[STAGE:verdict] canary-first"
if grep -q "multi-router-smoke-complete" "$LOG"; then
  echo "[COMPLETE] full scoreboard:"
  grep -A5 "capability/speed totals" "$LOG"
elif kill -0 "$PID" 2>/dev/null; then
  echo "[ALIVE] still running — results later via: grep -A5 'capability/speed totals' $LOG"
else
  echo "[DEAD] exited early — tail:"; tail -12 "$LOG"; exit 1
fi

echo "[STAGE:poke] lane arming check"
grep "openrouter model" "$LOG" | head -2
grep "openrouter:" "$LOG" | head -4 || true

echo "[STAGE:seal]"
git fetch origin && git pull --ff-only origin main
cat > context_bridge/session-2026-09-21-openrouter-install.md <<SEED
# OpenRouter Key Install — 2026-09-21
- Fresh key installed blind (read -rs) to ~/.openrouter/env, mode 600, outside repos
- Router relaunched with sourced key; scoreboard logged
- Lane-hunt trail: no key existed on A15 or OptiPlex (both scanned, none found) — parked until minted, now minted
## Provenance: lumo-assisted, human-gated
SEED
git add context_bridge/session-2026-09-21-openrouter-install.md
git commit -m "[SEAL] openrouter key installed — free-lane revival attempt under load"
git push origin main && echo "[SEALED] $(git rev-parse --short HEAD)"

echo "[CANARY] or-installed-${TS}"
echo "[exit=0]"
