#!/data/data/com.termux/files/usr/bin/bash
set -u
while true; do
  if ! pgrep -f "agape-autopilot.sh" >/dev/null 2>&1; then
    nohup bash /sdcard/openroot/scripts/agape-autopilot.sh >/sdcard/openroot/logs/nohup.out 2>&1 &
  fi
  sleep 45
done
