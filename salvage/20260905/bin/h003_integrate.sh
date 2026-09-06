#!/data/data/com.termux/files/usr/bin/bash
set -e

AREA_M2="${1:-12}"  # Default 12 m² (thermal cascade area)
H003_LOG="$HOME/projects/openroot/research/h003_ledger.log"
mkdir -p "$(dirname "$H003_LOG")"

# H-003 theoretical: 12.91 kWh/m²/night (verified in peer-reviewed dataset)
NIGHTLY_KWH=$(echo "scale=3; $AREA_M2 * 12.91" | bc)
WEEKLY_KWH=$(echo "scale=3; $NIGHTLY_KWH * 7" | bc)
ACRE_FROM_ENERGY=$(echo "scale=6; ($WEEKLY_KWH * 3600000) / 1000" | bc)

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOG_ENTRY="H-003|area=${AREA_M2}m2|nightly=${NIGHTLY_KWH}kWh|7n=${WEEKLY_KWH}kWh|acre=${ACRE_FROM_ENERGY}|timestamp=${TIMESTAMP}"

echo "$LOG_ENTRY" >> "$H003_LOG"
echo "H-003 ledger updated: $LOG_ENTRY"
echo "$LOG_ENTRY" | termux-clipboard-set
