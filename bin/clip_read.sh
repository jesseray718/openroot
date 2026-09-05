#!/data/data/com.termux/files/usr/bin/bash
CLIP_FILE="/sdcard/openroot/.clip_input"
if [ -f "$CLIP_FILE" ]; then
  cat "$CLIP_FILE"
  rm "$CLIP_FILE"
else
  echo "No staged clip content."
fi
