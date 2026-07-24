#!/data/data/com.termux/files/usr/bin/bash
# OpenRoot Financial Health Check
# Integrates with cycle monitoring

LOG_DIR="/sdcard/openroot/output/financial"
mkdir -p "$LOG_DIR"

OUTPUT="$LOG_DIR/health_$(date +%Y%m%d_%H%M%S).txt"

{
  echo "========================================"
  echo "  OPENROOT FINANCIAL HEALTH CHECK"
  echo "  $(date)"
  echo "========================================"
  echo ""
  echo "📊 SYSTEM RESOURCES:"
  df -h /sdcard | tail -1
  awk '/MemTotal|MemAvailable/{printf "  %s: %s\n", $1, $2}' /proc/meminfo
  cat /sys/class/power_supply/battery/capacity 2>/dev/null | xargs -I{} echo "  Battery: {}%"
  echo ""
  echo "💰 LLC ACCOUNT STATUS (manual entry required):"
  echo "  Bluebird: ____________"
  echo "  Mercury:  ____________"
  echo ""
  echo "📌 Q3 Tax Reminder:"
  echo "  Due: September 15, 2026"
  echo "  Action: Set aside 25% of profit"
  echo ""
  echo "========================================"
} | tee "$OUTPUT"

echo ""
echo "Saved to: $OUTPUT"
echo "Open in Markor for manual account updates."
