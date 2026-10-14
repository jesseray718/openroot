#!/usr/bin/env bash
set -eu
D=/home/jesse/openroot/data/device_ledgers
while true; do
  if ! pgrep -f "python3 .*optiplex_fs_scan_v1.py" >/dev/null; then
    if grep -q "SCAN COMPLETE" $D/optiplex_scan_rel2.log 2>/dev/null; then
      echo "$(date -u +%FT%TZ) [banked] scan complete — watchdog exiting" >> $D/watchdog.log
      break
    fi
    echo "$(date -u +%FT%TZ) [gate] scan dead, reviving" >> $D/watchdog.log
    cd $D && nohup python3 optiplex_fs_scan_v1.py optiplex_fs_ledger.db >> optiplex_scan_rel2.log 2>&1 &
  fi
  sleep 300
done
