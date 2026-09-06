#!/data/data/com.termux/files/usr/bin/bash
set -u
THROTTLE=/sdcard/openroot/storage/agape_node/throttle.json
mkdir -p /sdcard/openroot/storage/agape_node

while true; do
  LOAD=$(cat /proc/loadavg | awk '{print $1}')
  # simple policy
  MODE="normal"
  LIMIT=25
  SLEEP_OK=8

  awk "BEGIN {exit !($LOAD > 2.5)}" && MODE="conserve" && LIMIT=10 && SLEEP_OK=18
  awk "BEGIN {exit !($LOAD > 4.0)}" && MODE="cooldown" && LIMIT=5 && SLEEP_OK=30

  cat > "$THROTTLE" <<EOF
{"mode":"$MODE","limit":$LIMIT,"sleep_ok":$SLEEP_OK,"load":$LOAD}
EOF

  sleep 60
done
