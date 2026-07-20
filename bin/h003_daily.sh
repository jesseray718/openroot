#!/data/data/com.termux/files/usr/bin/bash
set -e

AREA="${1:-12}"
OPENROOT="$HOME/projects/openroot"
H003_LOG="$OPENROOT/research/h003_ledger.log"
LEDGER="$OPENROOT/acre/ledger.jsonl"

echo "=== H-003 Daily PoPW ==="
bash "$OPENROOT/bin/h003_integrate.sh" "$AREA"

# Parse latest entry from h003 log
LATEST=$(tail -1 "$H003_LOG")
IFS='|' read -r _ AREA_KWH NIGHTLY _7N ACRE_KWH TS <<< "$LATEST"

# Extract numeric values
NIGHTLY_KWH=$(echo "$NIGHTLY" | sed 's/[^0-9.]//g')
WEEKLY_KWH=$(echo "$_7N" | sed 's/[^0-9.]//g')
ACRE=$(echo "$ACRE_KWH" | sed 's/[^0-9.]//g')
JOULES=$(echo "$WEEKLY_KWH * 3600000" | bc)

# Previous hash from ACRE ledger
PREV=$(tail -1 "$LEDGER" | grep -o '"hash":"[^"]*' | cut -d'"' -f4 || echo "0000000000000000")

# Build entry
ENTRY='{"entry_id":"h003_'$(date -u +%Y%m%d)'_weekly","timestamp":"'$TS'","work_type":"thermal_generation_h003","energy_joules":'$JOULES',"acre_minted":'$ACRE',"previous_hash":"'$PREV'","validators":["ND00","ND01"],"une_code":"DV.GEN.TH.AE01","area_m2":'$AREA',"nightly_kwh":'$NIGHTLY_KWH',"7n_kwh":'$WEEKLY_KWH',"source":"h003_daily.sh"}'

echo "$ENTRY" >> "$LEDGER"
echo ""
echo "✅ Appended to acre/ledger.jsonl"
echo "$ENTRY" | python3 -m json.tool

echo ""
echo "=== Git commit (copy/paste) ==="
echo "cd $HOME/projects/openroot && git add acre/ledger.jsonl research/h003_ledger.log && git commit -m \"feat(h003): $(date -u +%Y-%m-%d) nightly ${NIGHTLY_KWH} kWh → ${ACRE} ACRE (DV.GEN.TH.AE01)\" && git push origin main"
