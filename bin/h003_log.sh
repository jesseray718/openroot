#!/data/data/com.termux/files/usr/bin/bash
AREA=${1:-10}
LEDGER="$HOME/projects/openroot/bin/h003_ledger.sh"
if [ ! -x "$LEDGER" ]; then
  echo "h003_ledger.sh missing or not +x" >&2
  exit 1
fi
OUTPUT=$("$LEDGER" "$AREA")
DATE=$(date +%Y-%m-%dT%H:%M:%S)
LOG="$HOME/projects/openroot/research/h003_ledger.log"
printf "%s|%s\n" "$DATE" "$OUTPUT" >> "$LOG"
printf "%s\n" "$OUTPUT"
termux-clipboard-set "$DATE|$OUTPUT" 2>/dev/null || true
