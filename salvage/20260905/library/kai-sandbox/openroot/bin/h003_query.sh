#!/data/data/com.termux/files/usr/bin/bash
# h003_query.sh [N|--total] — query H-003 ledger (deduplicated)
LOG="$HOME/projects/openroot/research/h003_ledger.log"
[ -f "$LOG" ] || { echo "No h003_ledger.log yet"; exit 0; }

# Extract only pipe-delimited data lines (timestamp|H-003|...)
# Dedupe by timestamp+area (cols 1+2 of the H-003 portion)
DEDUPED=$(grep '^20[0-9]' "$LOG" | grep '|H-003|' | awk -F'|' '{key=$1"|"$3; if(!seen[key]++) print}')

if [ "$1" = "--total" ]; then
  RUNS=$(echo "$DEDUPED" | grep -c . 2>/dev/null || echo 0)
  TOTAL=$(echo "$DEDUPED" | grep -oP 'ACRE=\K[0-9.]+' | awk '{s+=$1} END{printf "%.4f", s}')
  echo "runs:$RUNS total_acre:$TOTAL"
elif [ -z "$1" ]; then
  echo "$DEDUPED" | tail -5
else
  echo "$DEDUPED" | tail -"$1"
fi
