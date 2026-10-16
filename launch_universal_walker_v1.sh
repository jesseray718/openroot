#!/usr/bin/env bash
set -eu
if pgrep -f "universal_index_overhaul_v1.py" >/dev/null; then
  echo "[held] walker already running:"; pgrep -af universal_index_overhaul; exit 1
fi
cd /home/jesse/openroot/bin
setsid nohup python3 -u universal_index_overhaul_v1.py > /home/jesse/openroot/logs/universal_index_overhaul_$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 < /dev/null &
echo "[banked] walker launched pid=$!"
