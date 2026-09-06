#!/data/data/com.termux/files/usr/bin/bash
AREA=${1:-10}
CAPTURE_KWH_PER_M2=12.91          # nightly gross capture
STIRLING_EFF=0.25                 # mechanical conversion
STORAGE_LOSS=0.08                 # daily storage loss (applies to stored thermal)
TRANSPORT_EFF=0.85                # heating/cooling delivery efficiency

CAPTURE=$(awk "BEGIN{printf \"%.2f\", $AREA * $CAPTURE_KWH_PER_M2}")
MECH=$(awk "BEGIN{printf \"%.2f\", $CAPTURE * $STIRLING_EFF}")
REMAINING_THERMAL=$(awk "BEGIN{printf \"%.2f\", $CAPTURE * (1 - $STIRLING_EFF)}")
DELIVERED_THERMAL=$(awk "BEGIN{printf \"%.2f\", $REMAINING_THERMAL * (1 - $STORAGE_LOSS) * $TRANSPORT_EFF}")
TOTAL_OUT=$(awk "BEGIN{printf \"%.2f\", $MECH + $DELIVERED_THERMAL}")
OVERALL=$(awk "BEGIN{printf \"%.1f\", ($TOTAL_OUT / $CAPTURE) * 100}")

printf "H-003-EFF|area=%sm2|capture=%skWh|mech=%skWh|thermal_delivered=%skWh|total_out=%skWh|efficiency=%s%%\n" \
  "$AREA" "$CAPTURE" "$MECH" "$DELIVERED_THERMAL" "$TOTAL_OUT" "$OVERALL"
printf "remaining_thermal=%skWh | after_storage_and_transport=%skWh\n" "$REMAINING_THERMAL" "$DELIVERED_THERMAL"
printf "params: stirling_eff=25%% storage_loss=8%% transport_eff=85%% | theoretical model\n"
