#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== Agape Clipboard Float & Receipt Bridge (R=1, c=0) ==="
echo "========================================================"

# 1. Grab raw payload from Android clipboard
CLIP_RAW="$(termux-clipboard-get 2>/dev/null || echo "")"
if [ -z "$CLIP_RAW" ]; then
    echo "[info] Clipboard is currently empty."
    exit 0
fi

echo "[1/3] Captured clipboard payload. Executing..."
echo "------------------------------------------------"

# 2. Execute command/script payload and capture output & exit code
set +e
OUTPUT=$(eval "$CLIP_RAW" 2>&1)
EXIT_CODE=$?
set -e

echo "$OUTPUT"
echo "------------------------------------------------"
echo "[2/3] Execution finished with exit code: $EXIT_CODE"

# 3. Format receipt package and push back to clipboard for instant pasting
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RECEIPT="[OPENROOT-RECEIPT $TIMESTAMP] ExitCode=$EXIT_CODE | Node=A15_Edge | R=1, c=0\nOutput Summary:\n$(echo "$OUTPUT" | tail -n 10)"

echo -e "$RECEIPT" | termux-clipboard-set
echo "[3/3] Formatted execution receipt copied back to clipboard!"
echo "========================================================"
