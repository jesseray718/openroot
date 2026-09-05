#!/data/data/com.termux/files/usr/bin/bash
# Absolute paths. Real sensors only. No estimates.
# Attach: one sensor to solar-black / hot AeroCement face
#         one sensor to radiative / cold / ground side
# Record ΔT = T_hot - T_cold. Airflow if available. Shaft work if Stirling present.
TS=$(date -u +%Y%m%dT%H%M%SZ)
LEDGER=/sdcard/openroot/ledger/eta_ledger.jsonl
echo "Attach sensors now."
echo "When ready, enter T_hot (°C):"
read THOT
echo "Enter T_cold (°C):"
read TCOLD
DT=$(echo "$THOT - $TCOLD" | bc -l)
echo "{\"ts\":\"$TS\",\"type\":\"delta_t_measurement\",\"T_hot\":$THOT,\"T_cold\":$TCOLD,\"delta_T\":$DT,\"η_note\":\"real_joules_only\"}" >> $LEDGER
echo "Recorded ΔT = $DT °C. Ledger updated."
