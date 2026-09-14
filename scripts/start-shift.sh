#!/data/data/com.termux/files/usr/bin/bash
set -u
cd /sdcard/openroot

PY=python
command -v python >/dev/null 2>&1 || PY=python3

mkdir -p logs storage/agape_node

echo "=== AGAPE NODE START $(date -Is) ==="
$PY src/nodes/agape-node/agape_node.py status || true

# Seed one lightweight intent each start (idempotent via dedup)
$PY src/nodes/agape-node/agape_node.py enqueue --payload '{"task":"passenger-mode micro-progress","urgency":2,"impact":2}' || true

# Launch autopilot if not already running
if pgrep -f "agape-autopilot.sh" >/dev/null 2>&1; then
  echo "[ok] autopilot already running"
else
  nohup bash /sdcard/openroot/scripts/agape-autopilot.sh >/sdcard/openroot/logs/nohup.out 2>&1 &
  sleep 1
  echo "[ok] autopilot launched"
fi

echo "--- STATUS ---"
$PY src/nodes/agape-node/agape_node.py status || true
echo "--- TAIL LOG ---"
tail -n 20 /sdcard/openroot/logs/agape-autopilot.log 2>/dev/null || echo "no log yet"
echo "=== READY: node oscillating on least resistance ==="
