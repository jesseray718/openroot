#!/usr/bin/env bash
while true; do
  for f in $(ls ~/volumetric-project/output/* 2>/dev/null); do
    if [[ $f == *freeze_dry_kg.txt ]]; then
      KG=$(cat "$f")
      TOKENS=$(echo "scale=2; $KG * 10" | bc)
      echo "$(date '+%Y-%m-%d %H:%M') | ${f##*/} | $KG kg | $TOKENS tokens" >> ~/volumetric-project/tokens_ledger.csv
    elif [[ $f == *uptime.txt ]]; then
      UPTIME=$(cat "$f")
      # Example token calculation: 1 token per hour of uptime
      HOURS=$(echo "$UPTIME" | awk -F: '{print $1}')
      TOKENS=$(echo "scale=2; $HOURS * 1" | bc)
      echo "$(date '+%Y-%m-%d %H:%M') | ${f##*/} | $UPTIME | $TOKENS tokens" >> ~/volumetric-project/tokens_ledger.csv
    fi
  done
  sleep 900
 done
