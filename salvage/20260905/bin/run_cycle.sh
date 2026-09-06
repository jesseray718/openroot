#!/data/data/com.termux/files/usr/bin/bash
CYCLE=$(cat ~/.cycle_count 2>/dev/null || echo 0)
CYCLE=$((CYCLE + 1))
echo $CYCLE > ~/.cycle_count
OUT="/sdcard/openroot/output/cycle_${CYCLE}.txt"
echo "=== CYCLE $CYCLE ===" > $OUT
date >> $OUT
df -h /sdcard >> $OUT
echo "Wrote: $OUT"
