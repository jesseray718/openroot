#!/data/data/com.termux/files/usr/bin/bash
set -u
ROOT=/sdcard/openroot
LOG=$ROOT/logs
STORE=$ROOT/storage/agape_node
PY=python
command -v python >/dev/null 2>&1 || PY=python3
mkdir -p "$LOG" "$STORE"

start_one () {
  NAME="$1"; CMD="$2"; OUT="$3"
  if pgrep -f "$NAME" >/dev/null 2>&1; then
    echo "[ok] $NAME already running"
  else
    nohup bash -lc "$CMD" >"$OUT" 2>&1 &
    echo "[ok] started $NAME"
  fi
}
stop_all () {
  pkill -f agape-autopilot.sh || true
  pkill -f agape-health.sh || true
  pkill -f agape-keeper.sh || true
  echo "[ok] stopped all"
}
mode_set () {
  MODE="$1"
  case "$MODE" in
    boost) LIMIT=40; SLEEP_OK=4;;
    normal) LIMIT=25; SLEEP_OK=8;;
    conserve) LIMIT=10; SLEEP_OK=18;;
    cooldown) LIMIT=5; SLEEP_OK=30;;
    *) echo "bad mode"; exit 1;;
  esac
  cat > "$STORE/throttle.json" <<EOF
{"mode":"$MODE","limit":$LIMIT,"sleep_ok":$SLEEP_OK,"manual_override":true}
EOF
  echo "[ok] mode=$MODE limit=$LIMIT sleep_ok=$SLEEP_OK"
}
status_all () {
  echo "=== PROCS ==="
  pgrep -af "agape-autopilot.sh|agape-health.sh|agape-keeper.sh" || echo "none"
  echo "=== THROTTLE ==="
  [ -f "$STORE/throttle.json" ] && cat "$STORE/throttle.json" || echo "none"
  echo "=== NODE ==="
  $PY "$ROOT/src/nodes/agape-node/agape_node.py" status || true
  echo "=== LOG ==="
  tail -n 20 "$ROOT/logs/agape-autopilot.log" 2>/dev/null || true
}
enqueue_one () {
  TASK="${1:-passenger micro-task}"
  U="${2:-2}"
  I="${3:-2}"
  $PY "$ROOT/src/nodes/agape-node/agape_node.py" enqueue --payload "{\"task\":\"$TASK\",\"urgency\":$U,\"impact\":$I}"
}

case "${1:-}" in
  start)
    start_one "agape-health.sh" "$ROOT/scripts/agape-health.sh" "$LOG/health.out"
    start_one "agape-keeper.sh" "$ROOT/scripts/agape-keeper.sh" "$LOG/keeper.out"
    start_one "agape-autopilot.sh" "$ROOT/scripts/agape-autopilot.sh" "$LOG/nohup.out"
    ;;
  stop) stop_all ;;
  restart) stop_all; sleep 1; "$0" start ;;
  status) status_all ;;
  boost|normal|conserve|cooldown) mode_set "$1" ;;
  enqueue) enqueue_one "${2:-}" "${3:-}" "${4:-}" ;;
  *) echo "usage: start|stop|restart|status|boost|normal|conserve|cooldown|enqueue \"task\" [u] [i]" ;;
esac
