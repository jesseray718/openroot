#!/data/data/com.termux/files/usr/bin/bash
set -eu
export TERM=dumb

SRC="/storage/emulated/0/Documents/markor/20261005034117_bigplan.txt"
DST_DIR="/storage/emulated/0/Download"
DST="$DST_DIR/20261005034117_bigplan.txt"

echo "[gate] checking source"
if [ ! -f "$SRC" ]; then
  echo "[held] source not found: $SRC"
  exit 1
fi

mkdir -p "$DST_DIR"

SRC_SHA=$(sha256sum "$SRC" | awk '{print $1}')
SRC_SIZE=$(wc -c < "$SRC")
cp "$SRC" "$DST"

DST_SHA=$(sha256sum "$DST" | awk '{print $1}')

if [ "$SRC_SHA" = "$DST_SHA" ]; then
  echo "[banked] copied to: $DST"
  echo "sha256: $SRC_SHA"
  echo "bytes:  $SRC_SIZE"
else
  echo "[held] hash mismatch — copy failed"
  exit 1
fi
echo "[exit=0]"
