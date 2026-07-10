#!/data/data/com.termux/files/usr/bin/bash
VOL_L=${1:-100}
# Theoretical starter ratios (edit after physical batches)
CEMENT_KG_PER_L=0.80
SAND_KG_PER_L=0.80
WATER_KG_PER_L=0.28
FIBER_PCT_OF_CEMENT=0.04
ZIRCONIUM_PCT_OF_CEMENT=0.02
XANTHAN_PCT=0.002
CEMENT=$(awk "BEGIN{printf \"%.2f\", $VOL_L * $CEMENT_KG_PER_L}")
SAND=$(awk "BEGIN{printf \"%.2f\", $VOL_L * $SAND_KG_PER_L}")
WATER=$(awk "BEGIN{printf \"%.2f\", $VOL_L * $WATER_KG_PER_L}")
FIBER=$(awk "BEGIN{printf \"%.3f\", $CEMENT * $FIBER_PCT_OF_CEMENT}")
ZIRCONIUM=$(awk "BEGIN{printf \"%.3f\", $CEMENT * $ZIRCONIUM_PCT_OF_CEMENT}")
XANTHAN=$(awk "BEGIN{printf \"%.3f\", $VOL_L * $XANTHAN_PCT}")
printf "AE-GFRC|vol=%sL|cement=%skg|sand=%skg|water=%skg|fiber=%skg|zr=%skg|xanthan=%skg\n" "$VOL_L" "$CEMENT" "$SAND" "$WATER" "$FIBER" "$ZIRCONIUM" "$XANTHAN"
printf "theoretical starter ratios — update from physical batches | target aeration + Zr substitution + xanthan stabilizer\n"
