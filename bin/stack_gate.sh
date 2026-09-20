#!/usr/bin/env bash
# stack_gate.sh v2 — Active-line gate with awk (skips comments/blanks)
# Usage: stack_gate.sh <script_path>
set -eu
SCRIPT="${1:-}"
[ -z "$SCRIPT" ] && { echo "[ERROR] Usage: stack_gate.sh <script>"; exit 1; }
[ ! -f "$SCRIPT" ] && { echo "[ERROR] File not found: $SCRIPT"; exit 1; }

echo "[GATE] stack_gate.sh v2 — scanning active lines"
# Count non-comment, non-blank lines
ACTIVE=$(awk '!/^[[:space:]]*(#|$)/' "$SCRIPT" | wc -l)
TOTAL=$(wc -l < "$SCRIPT")

echo "Active lines: $ACTIVE / $TOTAL"

if [ "$ACTIVE" -lt 1 ]; then
    echo "[GATE] FAIL — no active lines"
    exit 1
fi

# Basic syntax check (bash or python)
if [[ "$SCRIPT" == *.sh ]]; then
    bash -n "$SCRIPT" 2>/dev/null && echo "[GATE] bash syntax OK" || { echo "[GATE] FAIL: bash syntax error"; exit 1; }
elif [[ "$SCRIPT" == *.py ]]; then
    python3 -m py_compile "$SCRIPT" 2>/dev/null && echo "[GATE] python syntax OK" || { echo "[GATE] FAIL: python syntax error"; exit 1; }
fi

echo "[GATE] PASS"
exit 0
