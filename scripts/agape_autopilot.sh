#!/usr/bin/env bash
set -e

OPENROOT_HOME="${OPENROOT_HOME:-$HOME/openroot}"
HEALTH_SCRIPT="$OPENROOT_HOME/scripts/agape_health.py"
LEDGER_SCRIPT="$OPENROOT_HOME/scripts/ledger.py"

echo "=== [Agape Autopilot] Starting Execution Cycle @ $(date -u) ==="

# 1. Ensure virtual environment is active if python is used
if [ -f "$OPENROOT_HOME/venv/bin/activate" ]; then
    source "$OPENROOT_HOME/venv/bin/activate"
fi

# 2. Run Edge Health Check
if [ -f "$HEALTH_SCRIPT" ]; then
    echo "--- Executing Health Monitor ---"
    python3 "$HEALTH_SCRIPT"
else
    echo "Warning: Health script not found at $HEALTH_SCRIPT"
fi

# 3. Perform ledger status check / count entries
if [ -f "$LEDGER_SCRIPT" ]; then
    echo "--- Checking Knowledge Ledger Status ---"
    python3 "$LEDGER_SCRIPT" search "*" | tail -n 5
fi

echo "=== [Agape Autopilot] Cycle Complete ==="
