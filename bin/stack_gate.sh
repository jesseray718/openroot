#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-}"

# Hash-failure signature generator
if [ "$TARGET" = "--hash-failure" ]; then
  # Collect recent error outputs or active state drift to hash
  LAST_ERR=$(git status --short 2>/dev/null; git diff 2>/dev/null)
  if [ -z "$LAST_ERR" ]; then
    echo "NO_FAIL"
  else
    echo -n "$LAST_ERR" | sha256sum | awk '{print $1}'
  fi
  exit 0
fi

if [ -z "$TARGET" ]; then
  echo "[ERROR] Usage: stack_gate.sh <script> | --hash-failure"
  exit 1
fi

echo "[GATE] stack_gate.sh v2 — scanning active lines"
if [ -f "$TARGET" ]; then
  ACTIVE_LINES=$(grep -cvE '^\s*(#|$)' "$TARGET" || true)
  TOTAL_LINES=$(wc -l < "$TARGET")
  echo "Active lines: ${ACTIVE_LINES} / ${TOTAL_LINES}"
  
  if bash -n "$TARGET"; then
    echo "[GATE] bash syntax OK"
    echo "[GATE] PASS"
    exit 0
  else
    echo "[GATE] FAIL: syntax errors detected"
    exit 1
  fi
else
  echo "[ERROR] File not found: $TARGET"
  exit 1
fi
