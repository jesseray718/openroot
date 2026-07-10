#!/data/data/com.termux/files/usr/bin/bash
AREA=${1:-10}
NIGHTLY_RATE=12.91
JOULES_PER_KWH=3600000
NIGHTLY_KWH=$(awk "BEGIN{printf \"%.2f\", $AREA * $NIGHTLY_RATE}")
SEVEN_KWH=$(awk "BEGIN{printf \"%.2f\", $NIGHTLY_KWH * 7}")
JOULES=$(awk "BEGIN{printf \"%.0f\", $SEVEN_KWH * $JOULES_PER_KWH}")
ACRE=$(awk "BEGIN{printf \"%.4f\", $JOULES / 1000}")
printf "H-003|area=%sm2|nightly=%skWh|7n=%skWh|ACRE=%s\n" "$AREA" "$NIGHTLY_KWH" "$SEVEN_KWH" "$ACRE"
