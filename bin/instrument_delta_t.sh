#!/data/data/com.termux/files/usr/bin/bash
# Measure ΔT_hot, ΔT_cold, airflow, shaft if present. Write only real joules.
TS=$(date -u +%Y%m%dT%H%M%SZ)
LEDGER=/sdcard/openroot/ledger/eta_ledger.jsonl
echo "{\"ts\":\"$TS\",\"type\":\"delta_t_probe\",\"status\":\"awaiting_sensors\",\"η_target\":\"raise_lowest\"}" >> $LEDGER
echo "Log ready. Attach sensors. Record real ΔT only."
