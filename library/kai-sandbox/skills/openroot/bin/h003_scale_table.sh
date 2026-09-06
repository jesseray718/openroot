#!/data/data/com.termux/files/usr/bin/bash
# h003_scale_table.sh — scaling reference with nonlinear cost + power output
# Usage: h003_scale_table.sh [max_area] [base_cost_per_m2] [effective_nights]

MAX=${1:-500}
BASE_COST=${2:-250}
EFF_NIGHTS=${3:-290}
CAPTURE_RATE=12.91
STIRLING_EFF=0.25
STORAGE_LOSS=0.08
TRANSPORT_EFF=0.85
ELEC_RATE=0.12
STIRLING_POWER_DENSITY=0.311

printf "%-6s %8s %9s %8s %8s %8s %8s %10s %10s %9s %7s %10s\n" \
  "Area" "Nightly" "7n(kWh)" "Mech" "Therm" "Out" "Peak(kW)" "ACRE" "Cost($)" "Save$/yr" "PB(y)" "Label"

for a in 1 5 10 25 50 100 250 500; do
  [ "$a" -gt "$MAX" ] && break
  CAPTURE=$(awk "BEGIN{printf \"%.1f\", $a * $CAPTURE_RATE}")
  SEVEN=$(awk "BEGIN{printf \"%.1f\", $CAPTURE * 7}")
  MECH=$(awk "BEGIN{printf \"%.1f\", $CAPTURE * $STIRLING_EFF}")
  REMAIN=$(awk "BEGIN{printf \"%.1f\", $CAPTURE * (1 - $STIRLING_EFF)}")
  THERM=$(awk "BEGIN{printf \"%.1f\", $REMAIN * (1 - $STORAGE_LOSS) * $TRANSPORT_EFF}")
  OUT=$(awk "BEGIN{printf \"%.1f\", $MECH + $THERM}")
  PEAK=$(awk "BEGIN{printf \"%.2f\", $a * $STIRLING_POWER_DENSITY}")
  ACRE=$(awk "BEGIN{printf \"%.0f\", $SEVEN * 3600000 / 1000}")
  DISCOUNT=$(awk "BEGIN{d=1-0.15*(log($a)/log(10)); if(d<0.55) d=0.55; printf \"%.3f\", d}")
  COST=$(awk "BEGIN{printf \"%.0f\", $a * $BASE_COST * $DISCOUNT}")
  YEARLY_SAVE=$(awk "BEGIN{printf \"%.0f\", $OUT * $EFF_NIGHTS * $ELEC_RATE}")
  PAYBACK=$(awk "BEGIN{if($YEARLY_SAVE>0) printf \"%.1f\", $COST/$YEARLY_SAVE; else print \"N/A\"}")

  case $a in
    1) LABEL="tile";;
    5) LABEL="bench";;
    10) LABEL="pilot";;
    25) LABEL="home";;
    50) LABEL="home+";;
    100) LABEL="farm";;
    250) LABEL="community";;
    500) LABEL="village";;
  esac

  printf "%-6s %8s %9s %8s %8s %8s %8s %10s %10s %9s %7s %10s\n" \
    "$a" "$CAPTURE" "$SEVEN" "$MECH" "$THERM" "$OUT" "$PEAK" "$ACRE" "$COST" "$YEARLY_SAVE" "$PAYBACK" "$LABEL"
done

echo ""
echo "Assumptions: capture=${CAPTURE_RATE}kWh/m²/n | stirling=25% | storage_loss=8% | transport=85%"
echo "             base_cost=\$${BASE_COST}/m² (bulk-discounted) | elec=\$${ELEC_RATE}/kWh | nights=${EFF_NIGHTS}/yr"
echo "             Stirling peak=${STIRLING_POWER_DENSITY}kW/m² | nonlinear cost floor=55% of base"
echo "All figures theoretical — pre-physical validation"
echo ""
echo "Re-run: h003_scale_table.sh 500 350 270  (area cost nights)"
