#!/data/data/com.termux/files/usr/bin/bash
LOG="$HOME/projects/openroot/research/h003_ledger.log"
[ -f "$LOG" ] || { echo "No h003_ledger.log yet"; exit 1; }
if [ "$1" = "--total" ]; then
  awk -F'ACRE=' '{s+=$2; n++} END {printf "runs:%d total_acre:%.4f\n", n, s}' "$LOG"
else
  N=${1:-5}
  tail -n "$N" "$LOG"
fi
termux-clipboard-set "$(tail -n 1 "$LOG" 2>/dev/null)" 2>/dev/null || true
