#!/usr/bin/env bash
# Scan output directory for specific metric files and update token ledger
OUTPUT_DIR=~/volumetric-project/output
LEDGER=~/volumetric-project/tokens_ledger.csv
mkdir -p "$(dirname "$LEDGER")"
# Ensure ledger has header if empty
if [ ! -s "$LEDGER" ]; then
  echo "timestamp,filename,value,units,tokens" > "$LEDGER"
fi
for f in "$OUTPUT_DIR"/* 2>/dev/null; do
  filename=$(basename "$f")
  case "$filename" in
    freeze_dry_kg.txt)
      KG=$(cat "$f" 2>/dev/null || echo 0)
      TOKENS=$(awk "BEGIN {printf \"%.2f\", $KG * 10}")
      echo "$(date '+%Y-%m-%d %H:%M'),$filename,$KG,kg,$TOKENS" >> "$LEDGER"
      ;;
    uptime.txt)
      # Assume uptime file contains seconds of uptime
      SEC=$(cat "$f" 2>/dev/null || echo 0)
      # Example token conversion: 1 token per hour of uptime
      HOURS=$(awk "BEGIN {printf \"%.2f\", $SEC/3600}")
      TOKENS=$(awk "BEGIN {printf \"%.2f\", $HOURS * 1}")
      echo "$(date '+%Y-%m-%d %H:%M'),$filename,$SEC,seconds,$TOKENS" >> "$LEDGER"
      ;;
    *)
      # ignore other files
      ;;
  esac
done
