#!/data/data/com.termux/files/usr/bin/env sh
# This script gathers your phone specs for Kai

echo "=== ANDROID DEVICE INFO ==="
getprop ro.product.model
getprop ro.build.version.release
echo ""

echo "=== STORAGE STATUS ==="
df -h ~ /sdcard | head -5
echo ""

echo "=== INSTALLED PACKAGES ==="
pkg list-installed | wc -l
echo "packages above"
echo ""

echo "=== KEY TOOLS ==="
python3 --version
git --version
echo ""

echo "=== CHECKING SENSORS ==="
ls -la /dev/ttyUSB* 2>/dev/null || echo "No USB serial found yet"
