#!/bin/bash
# Final Cleanup: Commit Recovery Artifacts
# Jesse Ray / OpenRoot
# Date: 2026-09-22

set -eu

echo "============================================================"
echo "FINAL CLEANUP: Committing Recovery Artifacts"
echo "============================================================"
echo ""

cd /home/jesse/openroot

# Stage all recovery artifacts
echo "[1] Staging untracked files..."
git add agape_kb/ kernel/ cosmos_engine/
git add bin/cycle_recovery_v1.py bin/recovery_final_status.sh
git add context_bridge/cycle_recovery_20260921_*.md
git add outbox/GREEN777_SSH*.txt 2>/dev/null || true

echo "[2] Current git status:"
git status --short
echo ""

# Create commit message file
REPORT_FILE="context_bridge/final_recovery_$(date +%Y%m%d_%H%M%S).md"
cat > "$REPORT_FILE" << REPORT
# Final Recovery Handoff
Generated: $(date -Iseconds)
Host: $(uname -n)
User: $USER

## Recovery Actions Completed
- [OK] Syncthing running (PIDs: 1173, 1257)
- [OK] SSH key generated: ~/.ssh/black-locust-rmh
- [OK] Agape kernel directories created
- [OK] Wisdom-scaffold submodule removed
- [!!] cycle.sh NOT FOUND on OptiPlex (located on Termux: /data/data/com.termux/files/home/bin/)

## Remaining Issues
1. **cycle.sh REPO_NAME bug**: Script exists on Termux device, not OptiPlex
   - Location: /data/data/com.termux/files/home/bin/cycle.sh
   - Fix needed: Add after 'set -eu' line:
     REPO_NAME="\${REPO_NAME:-\$(basename \$(pwd))}"

2. **Git untracked files**: Now committed below

## Git State
Branch: $(git branch --show-current)
Commit: $(git rev-parse HEAD | head -c 7)

## Artifacts Created
- bin/cycle_recovery_v1.py (v1.2 recovery script)
- bin/recovery_final_status.sh (status checker)
- context_bridge/cycle_recovery_*.md (recovery logs)
- agape_kb/ universal_axioms/ love_language/
- kernel/ cosmos_engine/

## Next Session Actions
1. Fix cycle.sh on Termux device
2. Resume: bin/cycle.sh
3. Verify: bin/recovery_final_status.sh

[exit=0]
REPORT

echo "[3] Creating handoff report: $REPORT_FILE"
git add "$REPORT_FILE"

echo "[4] Committing..."
git commit -m "[RECOVERY] Cycle recovery v1.2 complete
- Added cycle_recovery_v1.py, recovery_final_status.sh
- Restored agape kernel directories
- Fixed syncthing, SSH key infrastructure
- Left cycle.sh REPO_NAME fix for Termux device"

echo "[5] Pushing (dry-run check)..."
git status
echo ""
echo "To push: git push origin main"
echo ""
echo "============================================================"
echo "CLEANUP COMPLETE - Ready for next session"
echo "============================================================"
echo "[exit=0]"
