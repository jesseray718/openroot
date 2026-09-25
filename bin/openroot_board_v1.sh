#!/bin/bash
# [BOARDV1] OpenRoot all-in-one status board — canary marker
# SPDX-License-Identifier: GPL-3.0-only
# READ-ONLY dashboard by default. CONFIRM=1 enables: git push (if ahead).
# Run anywhere in a session to answer "where am I, what's next".
set -u
CANARY="[BOARDV1]"
cd /home/jesse/openroot || { echo "$CANARY not on optiplex repo — abort"; exit 1; }

echo "=============================================================="
echo "  OPENROOT BOARD v1 — $(date -Is)"
echo "=============================================================="

echo ""
echo "--- 1/7 GIT STATE ---"
HEAD=$(git rev-parse --short HEAD)
ORIGIN=$(git rev-parse --short origin/main 2>/dev/null || echo "?")
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
echo "HEAD=$HEAD origin/main=$ORIGIN ahead=$AHEAD behind=$BEHIND"
if [ "$AHEAD" != "0" ] && [ "$AHEAD" != "?" ]; then
  echo "unpushed commits:"
  git log --oneline origin/main..HEAD | head -10
fi
DIRTY=$(git status --short | grep -vc '^??' || true)
UNTRACKED=$(git status --short | grep -c '^??' || true)
echo "tracked changes: ${DIRTY:-0} | untracked: ${UNTRACKED:-0}"
QCOUNT=$(git status --short | grep -cE 'compute_marketplace|merge_ledgers|warm_models|recovery_' || true)
echo "quarantine files present (correct if >0): ${QCOUNT:-0}"

echo ""
echo "--- 2/7 MACHINE ---"
echo "disk: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5")"}') | \
mem: $(free -h | awk '/^Mem:/{print $3"/"$2}') | load: $(uptime | grep -oP 'load average: .*')"
echo "uptime: $(uptime -p | cut -d' ' -f2-)"
TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)
[ -n "$TEMP" ] && echo "cpu temp: $((TEMP/1000))C"

echo ""
echo "--- 3/7 STACK HEALTH ---"
for svc in ollama fail2ban ssh tailscaled; do
  echo "$svc: $(systemctl is-active $svc 2>/dev/null || echo unknown)"
done
if command -v ollama >/dev/null; then
  echo "models resident in RAM: $(ollama ps 2>/dev/null | tail -n +2 | grep -c . || echo 0)"
  ollama list 2>/dev/null | tail -n +2 | awk '{printf "  %s (%s)\n", $1, $3}'
fi

echo ""
echo "--- 4/7 CACHE / FLYWHEEL ---"
python3 /home/jesse/openroot/bin/embed_cache.py stats 2>/dev/null \
  || echo "embed_cache unavailable"

echo ""
echo "--- 5/7 DISK HOTSPOTS ---"
du -xh --max-depth=1 /home/jesse/openroot 2>/dev/null | sort -rh | head -6

echo ""
echo "--- 6/7 QUARANTINE INTEGRITY ---"
BAD=0
git ls-files | grep -qE 'compute_marketplace|merge_ledgers|warm_models|knowledge_base.db|model_weights' \
  && BAD=1
[ "$BAD" = "0" ] && echo "[gate] PASS — quarantine + runtime untracked" \
  || echo "[held] FAIL — quarantined/runtime file is TRACKED, investigate"

echo ""
echo "--- 7/7 OPEN BOARD (priority order) ---"
cat <<'EOF'
1. CONSOLIDATION   — pin 4 / merge 8 / archive-with-redirects (milestone waiting)
2. REH1T_CREDIT    — README ack for PR #63, grep-verify, gentle contact
3. NEW_STACK       — bench newer models into registry (needs your pointer)
4. 114G archive    — consolidation-backups -> /mnt/sdb1 (frees root)
5. Housekeeping    — apt upgrades + autoremove + journal check
6. push_guard fix  — sweep 'guard || action' inversions (must be &&)
7. Lessons chain   — py_compile-before-run entry (3 empirical strikes)
8. aider trial     — venv/aider --no-auto-commits + qwen2.5-coder:7b via ollama
EOF

echo ""
if [ "${CONFIRM:-0}" = "1" ]; then
  if [ "$AHEAD" != "0" ] && [ "$AHEAD" != "?" ]; then
    echo "--- [apply] PUSHING $AHEAD COMMIT(S) ---"
    git push && git log --oneline origin/main -1 && echo "$CANARY [banked] pushed"
  else
    echo "$CANARY nothing to push"
  fi
else
  echo "$CANARY [held] read-only — CONFIRM=1 also pushes if ahead"
fi
echo "$CANARY [exit=0]"
