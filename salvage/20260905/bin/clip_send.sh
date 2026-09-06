#!/data/data/com.termux/files/usr/bin/bash
# Clipboard workaround for Android 10+ — file fallback
CLIP_FILE="/sdcard/openroot/.clip_input"

if [ -t 0 ]; then
  echo "Reading from stdin..."
  cat > "$CLIP_FILE"
else
  cat > "$CLIP_FILE"
fi

echo "Content staged at: $CLIP_FILE"
echo "Run 'clip_read' to retrieve or paste manually into Lumo."
