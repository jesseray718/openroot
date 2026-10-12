#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat TERM=dumb
# SPDX-License-Identifier: GPL-3.0-only
LOG=/home/jesse/openroot/data/mistakes/mistake_log.jsonl
PASS=0; FAIL=0; MISSING=0
if [ ! -f "$LOG" ] || [ ! -s "$LOG" ]; then
    echo "[held] no mistake log at $LOG"
    exit 0
fi
while IFS= read -r line; do
    [ -z "$line" ] && continue
    f=$(echo "$line" | python3 -c 'import json,sys;d=json.loads(sys.stdin.read());print(d.get("file","") or "")' 2>/dev/null || true)
    [ -z "$f" ] && continue
    if [ ! -f "$f" ]; then
        MISSING=$((MISSING+1))
        continue
    fi
    case "$f" in
        *.py) python3 -m py_compile "$f" && PASS=$((PASS+1)) || FAIL=$((FAIL+1)) ;;
        *) bash -n "$f" && PASS=$((PASS+1)) || FAIL=$((FAIL+1)) ;;
    esac
done < "$LOG"
echo "[banked] canary CI: pass=$PASS fail=$FAIL missing=$MISSING total=$(wc -l < "$LOG")"
[ "$FAIL" -eq 0 ] || echo "[held] canary CI reported $FAIL failures"
