#!/bin/bash
# OpenRoot USB Hive Bootstrap — offline first
# Assumes the USB is already manually mounted and you have cd'd into it.

set -e

echo "=== OpenRoot USB Hive Bootstrap ==="
echo "Time: $(date -Iseconds)"
echo "Running from: $(pwd)"

# Safety: we must be inside the USB tree
if [ ! -f "./bootstrap.sh" ]; then
  echo "ERROR: bootstrap.sh not found in current directory."
  echo "Mount the USB, cd into its root, then run: bash bootstrap.sh"
  exit 1
fi

TARGET="$HOME/openroot"
echo "Target directory: $TARGET"
mkdir -p "$TARGET"
mkdir -p "$TARGET/ledger"
mkdir -p "$TARGET/session_seeds"
mkdir -p "$TARGET/hive"

echo "--- Copying OpenRoot core ---"
cp -a ./openroot/. "$TARGET/" 2>/dev/null || echo "Note: openroot/ copy had some missing pieces (ok)"

echo "--- Copying ledger ---"
cp -a ./ledger/. "$TARGET/ledger/" 2>/dev/null || echo "Note: ledger/ copy had issues"

echo "--- Copying session seeds ---"
cp -a ./session_seeds/. "$TARGET/session_seeds/" 2>/dev/null || echo "Note: session_seeds/ copy had issues"

echo "--- Copying hive tools ---"
cp -a ./hive/. "$TARGET/hive/" 2>/dev/null || echo "Note: hive/ copy had issues"

echo "--- Kai9000 offline files ---"
if [ -d "./kai9000" ]; then
  mkdir -p "$TARGET/kai9000"
  cp -a ./kai9000/. "$TARGET/kai9000/" 2>/dev/null || echo "Note: kai9000/ copy had issues"
  echo "Kai9000 files copied. Manual model load may still be required."
else
  echo "No kai9000/ directory on stick — skipping."
fi

echo ""
echo "=== Bootstrap finished ==="
echo "Next steps on OptiPlex:"
echo "  1. cd $TARGET"
echo "  2. Check ledger:   ls -la ledger/"
echo "  3. Check seeds:    ls -la session_seeds/"
echo "  4. Launch offline Kai from $TARGET/kai9000/ if present"
echo ""
