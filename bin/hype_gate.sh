#!/usr/bin/env bash
set -eu
FILE="${1:?usage: hype_gate.sh <manuscript.md>}"
CODE=0
while IFS= read -r LINE; do
  [ -z "$LINE" ] && continue
  MATCH=$(grep -inE "$LINE" "$FILE" || true)
  if [ -n "$MATCH" ]; then echo "   [FAIL] $LINE"; echo "$MATCH"; CODE=1; fi
done <<'BANNED'
free energy|over.?unity|perpetual
more than 100%|exceeds 100%|breakthrough|revolutionary
unprecedented|miracle|game.?changing.{0,20}efficien
magna.?flux|zero.?point
BANNED
if [ "$CODE" -eq 0 ]; then echo "[PASS] $FILE contains no desk-reject phrases"; else echo "[HELD] revise flagged lines in $FILE"; exit 1; fi
