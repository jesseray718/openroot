#!/bin/bash
# intake.sh — read-only bootstrap for any new window/AI node. Idempotent.
set -u
if [ -d /data/data/com.termux ]; then ROOT="$HOME/src/openroot"; else ROOT="/home/jesse/src/openroot"; fi
LATEST=$(ls -t "$ROOT"/context_bridge/session-*-handoff.md 2>/dev/null | head -1)
if [ -z "$LATEST" ]; then echo "[intake] no handoff found — cold start at $ROOT"; exit 0; fi
echo "[intake] latest handoff: $LATEST"; echo "---"
cat "$LATEST"
echo "---"
if [ -x "$HOME/openroot/bin/../openroot" ]; then :; fi
echo "[intake] rc_circuit seals today:"
grep -c "$(date +%Y-%m-%d)" "$ROOT/circuits/seals/rc_circuit_seals.jsonl" 2>/dev/null || echo 0
