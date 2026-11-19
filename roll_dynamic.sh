#!/usr/bin/env bash
# =============================================================================
#  OpenRoot Dynamic Rollout Script (Termux → OptiPlex)
#  Usage: TARGET=<ssh-alias> bash roll_dynamic.sh [dry|apply]
# =============================================================================
set -euo pipefail

TARGET="${TARGET:-optiplex}"
SRC_ROOT="/data/data/com.termux/files/home"
DST_ROOT="/home/jesse"
MODE="${1:-dry}"

mkdir -p "$HOME/tmp"
WORK="$(mktemp -d "$HOME/tmp/openroot-rollout.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

echo "[init] Discovering files dynamically..."
cd "$SRC_ROOT"

# Find bin and openroot files automatically without hardcoded lists
find bin openroot .local/bin -type f 2>/dev/null > "$WORK/files.txt"

TOTAL_FILES="$(wc -l < "$WORK/files.txt")"
echo "[init] Found ${TOTAL_FILES} files to synchronize."

# Split into chunks of 250 files
split -l 250 -d "$WORK/files.txt" "$WORK/chunk_"

echo "[sync] Starting chunked transfer to $TARGET (Mode: $MODE)..."

for chunk in "$WORK"/chunk_*; do
    echo "[sync] Processing $(basename "$chunk")..."
    if [ "$MODE" = "apply" ]; then
        rsync -avz --files-from="$chunk" "$SRC_ROOT/" "$TARGET:$DST_ROOT/"
    else
        rsync -avn --files-from="$chunk" "$SRC_ROOT/" "$TARGET:$DST_ROOT/"
    fi
done

echo "============================================================================="
echo " DYNAMIC ROLLOUT COMPLETE"
echo "============================================================================="
