#!/bin/bash
# seal_notes.sh <markdown-file> [title] — harvest old-window insights into the living state
set -eu
SRC=${1:?usage: seal_notes.sh <file> [title]}
TITLE=${2:-window-close}
if [ -d /data/data/com.termux ]; then R="$HOME/src/openroot"; else R="/home/jesse/src/openroot"; fi
TS=$(date -u +%Y%m%dT%H%M%SZ)
DEST="$R/context_bridge/session-notes-$TITLE-$TS.md"
mkdir -p "$R/context_bridge"
cp "$SRC" "$DEST"
H=$(sha256sum "$DEST" | cut -d' ' -f1)
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) | $H | $DEST" >> "$R/context_bridge/synthesis_handoffs.txt"
cd "$R" && git add context_bridge && git -c user.name=jesse -c user.email=j@o \
  commit -m "notes: harvest $TITLE" --quiet --no-verify || true
URL=$(gh gist create "$DEST" --public --desc "OpenRoot session notes $TITLE $TS" | head -1)
echo "[sealed] $DEST"
echo "[hash]   $H"
echo "[gist]   $URL"
echo "[addendum-line] ${URL}raw"
