#!/data/data/com.termux/files/usr/bin/bash
set -u
cd /sdcard/openroot
PY=python; command -v python >/dev/null 2>&1 || PY=python3
LOG=/sdcard/openroot/logs/agape-autopilot.log
TH=/sdcard/openroot/storage/agape_node/throttle.json
mkdir -p /sdcard/openroot/logs /sdcard/openroot/storage/agape_node
echo "[$(date -Is)] autopilot start" >> "$LOG"

while true; do
  LIMIT=25; SOK=8; SIDLE=15; SERR=30
  if [ -f "$TH" ]; then
    L=$(sed -n 's/.*"limit":[[:space:]]*\([0-9]\+\).*/\1/p' "$TH" | head -n1)
    S=$(sed -n 's/.*"sleep_ok":[[:space:]]*\([0-9]\+\).*/\1/p' "$TH" | head -n1)
    [ -n "${L:-}" ] && LIMIT="$L"
    [ -n "${S:-}" ] && SOK="$S"
  fi

  TS=$(date -Is)
  OUT=$($PY src/nodes/agape-node/agape_node.py process --limit "$LIMIT" 2>&1)
  RC=$?
  echo "[$TS] rc=$RC limit=$LIMIT out=$OUT" >> "$LOG"

  if [ $RC -ne 0 ]; then sleep "$SERR"; continue; fi

  REM=$($PY src/nodes/agape-node/agape_node.py status | sed -n 's/.*"queue_size":[[:space:]]*\([0-9]\+\).*/\1/p' | head -n1)
  if [ -n "${REM:-}" ] && [ "$REM" -gt 0 ]; then sleep "$SOK"; else sleep "$SIDLE"; fi
done
