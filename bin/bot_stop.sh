#!/data/data/com.termux/files/usr/bin/sh
PIDFILE="$HOME/openroot/bot_loop.pid"
if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE")
  kill "$PID" 2>/dev/null && echo "[bot] stopped pid=$PID" || echo "[bot] not running"
else
  echo "[bot] no pidfile, not running"
fi
