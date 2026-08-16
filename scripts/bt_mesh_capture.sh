#!/data/data/com.termux/files/usr/bin/bash
set -e
TS=$(date -u +%Y%m%dT%H%M%SZ)
LOG=/sdcard/openroot/thermo_ledger/bt_$TS.log
{
  echo "=== BT MESH $TS ==="
  echo "device: $(getprop ro.product.model)"
  if command -v rish >/dev/null; then
    rish -c "dumpsys bluetooth_manager" 2>/dev/null | head -50
    echo
    rish -c "dumpsys bluetooth_manager" 2>/dev/null | grep -iE "Connected|Bonded" || true
  else
    echo "rish missing"
  fi
  echo "=== END ==="
} | tee "$LOG"
echo "log written: $LOG"
