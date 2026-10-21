#!/bin/bash
# Final Status & Git Cleanup Script
# For Jesse Ray / OpenRoot
# Date: 2026-09-22

echo "============================================================"
echo "OPENROOT FINAL RECOVERY STATUS"
echo "Date: $(date -Iseconds)"
echo "Host: $(uname -n)"
echo "User: $USER"
echo "============================================================"
echo ""

echo "[1] Git Branch & Commit"
echo "------------------------"
git branch --show-current
git rev-parse HEAD | head -c 7; echo ""
echo ""

echo "[2] Git Changes (Uncommitted)"
echo "-----------------------------"
git status --short
if [ -z "$(git status --short)" ]; then
    echo "  (none - working tree clean)"
fi
echo ""

echo "[3] Cycle.sh Location Search"
echo "----------------------------"
for loc in \
    "/data/data/com.termux/files/home/bin/cycle.sh" \
    "/home/jesse/bin/cycle.sh" \
    "~/bin/cycle.sh" \
    "$PWD/bin/cycle.sh"; do
    if [ -f "$loc" ]; then
        echo "FOUND: $loc"
        grep -n "REPO_NAME" "$loc" 2>/dev/null | head -3 || echo "  (REPO_NAME not defined)"
    fi
done
echo ""

echo "[4] Key Services"
echo "----------------"
echo "Syncthing:"
pgrep -x syncthing && echo "  RUNNING" || echo "  NOT RUNNING"
echo ""
echo "SSH Keys:"
ls -la ~/.ssh/black-locust-rmh* 2>/dev/null || echo "  No black-locust-rmh key"
echo ""
echo "Agape Kernel:"
ls -d agape_kb/*/ kernel/ cosmos_engine/ 2>/dev/null || echo "  Not found"
echo ""

echo "[5] Git Status Details"
echo "----------------------"
git status
echo ""

echo "[6] Quick Actions"
echo "-----------------"
echo "To fix git changes:"
echo "  cd ~/openroot"
echo "  git add -A              # Stage all changes"
echo "  git commit -m '[RECOVERY] Post-cycle recovery cleanup'"
echo "  git push origin main    # Push if needed"
echo ""
echo "To fix cycle.sh on Termux (remote):"
echo "  ssh termux"
echo "  cat /data/data/com.termux/files/home/bin/cycle.sh | head -80 | grep -A2 -B2 REPO_NAME"
echo "  # Add: REPO_NAME=\${REPO_NAME:-\$(basename \$(pwd))}"
echo "       # after 'set -eu' line"
echo ""
echo "[exit=0]"
