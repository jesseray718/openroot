#!/usr/bin/env bash
# lumo_bridge_run.sh - bound multi-cycle bridge driver. BRIDGEV1 canary.
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
N=${1:-5}
echo "[BRIDGEV1] running $N cycles, 60s apart"
for i in $(seq 1 "$N"); do
  echo "=== cycle $i/$N ==="
  python3 bin/lumo_bridge_bot_v1.py cycle || echo "[cycle $i soft-failed - continuing]"
  [ "$i" -lt "$N" ] && sleep 60
done
python3 bin/lumo_bridge_bot_v1.py status
echo "[BANKED] [exit=0]"
