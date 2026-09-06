#!/data/data/com.termux/files/usr/bin/bash
# UNE-TAG CAPTURE v0.1 | H-003 thermal loop | atomic function 1
# Run after sensor setup. Tags yield for PoPW claim.
TS=$(date +%Y%m%d_%H%M%S)
LOG="\( HOME/openroot/observations/h003_ \){TS}.log"
echo "UNE_TAG: H-003|thermal_cascade|AE-GFRC_labyrinth|desiccant_intake" > "$LOG"
echo "METRICS: kWh_m2_nightly=TARGET_12.91|7night_10m2=TARGET_82.98|stirling_kWh=TARGET_24.89" >> "$LOG"
echo "PROTOCOL: 21d_wet_cure|48h_clear_day_data|IPFS_publish" >> "$LOG"
echo "DEVICE: Samsung_A15|Termux|Kai9000|Shizuku" >> "$LOG"
echo "NEXT: PoPW_CLAIM ready. Attach this + photos + PR to GitHub issue." >> "$LOG"
cat "$LOG"
echo "Captured to $LOG. Ready for function 2 (PoPW claim)."
