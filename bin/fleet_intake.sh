#!/bin/bash
# fleet_intake.sh — directions for ANY open AI window, first interaction.
# Covers: what's accomplished, what we're going for, the bigger vision.
if [ -d /data/data/com.termux ]; then ROOT="$HOME/src/openroot"; else ROOT="/home/jesse/src/openroot"; fi
echo "=== OPENROOT SYNTHESIS INTAKE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
SYN_ROOT="$ROOT" python3 "$ROOT/synthesis/synthesis.py" intake
echo; echo "==== SYNTHESIS CARD (concepts + vision) ===="
cat "$ROOT/synthesis/SYNTHESIS_CARD.md"
