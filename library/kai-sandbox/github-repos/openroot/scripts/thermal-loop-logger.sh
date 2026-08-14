#!/data/data/com.termux/files/usr/bin/bash
# Community Thermal Loop Logger — OpenRoot
# Designed for easy adoption by any community member on Galaxy A15 or similar Termux env.
# NO founder/manual sensory input. Sensors only.
# Run on your own Node replication. Contribute CSV or IPFS hash back for collective verification & ACRE PoPW.
# Setup: 1. pkg install git  2. Attach DS18B20 via cheap USB OTG adapter  3. ls /sys/bus/w1/devices/ to get IDs  4. Edit IDs below  5. bash this script

set -euo pipefail

LOG_DIR="$HOME/openroot-community-data"
mkdir -p "$LOG_DIR"
CSV="\( LOG_DIR/my-node-thermal- \)(date +%Y%m%d).csv"

if [ ! -f "$CSV" ]; then
  echo "timestamp,ambient,desiccant_intake,labyrinth_exit,cold_tank_b,hot_tank_a,stirling_return" > "$CSV"
  echo "# Community logger. No founder input. Contributed for open verification." >> "$CSV"
fi

# === REPLACE WITH YOUR SENSOR IDs (run ls /sys/bus/w1/devices/ once) ===
AMB="28-XXXXXXXXXXXX"
DES="28-YYYYYYYYYYYY"
LAB="28-ZZZZZZZZZZZZ"
CTB="28-AAAAAAAAAAAA"
HTA="28-BBBBBBBBBBBB"
STR="28-CCCCCCCCCCCC"

read_temp() {
  local id="$1"
  local path="/sys/bus/w1/devices/$id/temperature"
  [ -f "$path" ] && awk '{printf "%.2f", $1/1000}' "$path" || echo "N/A"
}

echo "Community logger started. Logging every 2 min. CSV in $LOG_DIR"
echo "When done: commit/push CSV or IPFS hash to openroot repo or share for bounties."

while true; do
  ts=$(date -Iseconds)
  echo "\( ts, \)(read_temp "\( AMB"), \)(read_temp "\( DES"), \)(read_temp "\( LAB"), \)(read_temp "\( CTB"), \)(read_temp "\( HTA"), \)(read_temp "$STR")" >> "$CSV"
  sleep 120
done
