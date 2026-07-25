#!/data/data/com.termux/files/usr/bin/bash
# AE-GFRC Mix Calculator — corrected: NO SAND
# Composition: cement, water, AR-glass fiber (≥16% ZrO2), xanthan gum
VOL="${1:-50}"
# Per-liter ratios (kg/L) — sandless aerated formulation
CEMENT_PER_L=1.0    # cement carries full binder load
WATER_PER_L=0.28     # ~0.40 w/c ratio
FIBER_PER_L=0.04     # ~4% of cement weight
ZIRCONIA_PER_L=0.02  # ~2% (within fiber, ≥16% ZrO2 by fiber weight)
XANTHAN_PER_L=0.0025 # ~0.25% of cement weight

c=$(awk "BEGIN{printf \"%.2f\", $VOL*$CEMENT_PER_L}")
w=$(awk "BEGIN{printf \"%.2f\", $VOL*$WATER_PER_L}")
f=$(awk "BEGIN{printf \"%.3f\", $VOL*$FIBER_PER_L}")
z=$(awk "BEGIN{printf \"%.3f\", $VOL*$ZIRCONIA_PER_L}")
x=$(awk "BEGIN{printf \"%.3f\", $VOL*$XANTHAN_PER_L}")

out="AE-GFRC|vol=${VOL}L|cement=${c}kg|water=${w}kg|fiber=${f}kg|zr=${z}kg|xanthan=${x}kg"
echo "$out"
echo "$out" | termux-clipboard-set
echo "↳ copied to clipboard"
