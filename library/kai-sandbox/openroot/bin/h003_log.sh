#!/data/data/com.termux/files/usr/bin/bash
# h003_log.sh [area] — run ledger calc, append to log, copy to clipboard
mkdir -p "$HOME/projects/openroot/research"
LOG="$HOME/projects/openroot/research/h003_ledger.log"
AREA=${1:-10}
LEDGER="$HOME/projects/openroot/bin/h003_ledger.sh"
[ -x "$LEDGER" ] || { echo "h003_ledger.sh missing"; exit 1; }
OUTPUT=$("$LEDGER" "$AREA")
DATE=$(date +%Y-%m-%dT%H:%M:%S)
ENTRY="${DATE}|${OUTPUT}"
printf "%s\n" "$ENTRY" >> "$LOG"
printf "%s\n" "$ENTRY"
termux-clipboard-set "$ENTRY" 2>/dev/null || true
