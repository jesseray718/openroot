#!/data/data/com.termux/files/usr/bin/bash
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LEDGER=/sdcard/openroot/ledger/eta_ledger.jsonl
mkdir -p /sdcard/openroot/ledger
echo "Scanning thermal_zone* ..."
for z in /sys/class/thermal/thermal_zone*/temp; do
  if [ -r "$z" ]; then
    T=$(cat "$z" 2>/dev/null)
    ZONE=$(basename $(dirname "$z") | sed 's/thermal_zone//')
    echo "zone$ZONE = $T m°C"
    echo "{\"ts\":\"$TS\",\"type\":\"a15_thermal\",\"zone\":\"$ZONE\",\"temp_mC\":$T,\"source\":\"thermal_zone\"}" >> $LEDGER
  fi
done
echo "Ledger updated."
tail -8 $LEDGER
