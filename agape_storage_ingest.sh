#!/usr/bin/env bash
set -Eeuo pipefail
echo "========================================================"
echo "=== OpenRoot Storage Ingestion & Overhaul Engine     ==="
echo "=== Protocol Alignment: R=1, c=0 (Zero Friction)      ==="
echo "========================================================"
TARGET_BUFFER="workareas/storage_overhaul_buffer"
mkdir -p "$TARGET_BUFFER"
SEARCH_PATHS=(
    "$HOME/openroot"
    "$HOME/.termux"
    "$HOME/storage/shared/Documents/Markor"
    "$HOME/storage/downloads"
    "/storage/extSdCard"
    "/storage/emulated/0/Download"
    "/storage/emulated/0/Documents"
)
echo "[1/3] Scanning and ingesting local storage volumes..."
TOTAL_INGESTED=0
for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "  [scan] Traversing: $path"
        while IFS= read -r -d '' file; do
            rel_path="${file#$HOME/}"
            safe_name="$(echo "$rel_path" | tr '/' '_')"
            cp "$file" "$TARGET_BUFFER/$safe_name" 2>/dev/null || true
            ((TOTAL_INGESTED++)) || true
        done < <(find "$path" -type f \( -name "*.md" -o -name "*.json" -o -name "*.txt" -o -name "*.sh" -o -name "*.py" \) -print0 2>/dev/null)
    fi
done
echo "[2/3] Ingestion complete. Total files indexed: $TOTAL_INGESTED"
echo "[3/3] Generating Overhaul Manifest & Inventory..."
MANIFEST_PATH="workareas/release/storage_overhaul_manifest.json"
python3 -c "
import os, json
files = os.listdir('$TARGET_BUFFER')
manifest = {
    'total_files': len(files),
    'file_sample': files[:20],
    'status': 'ingested_and_staged',
    'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
}
json.dump(manifest, open('$MANIFEST_PATH', 'w'), indent=2)
print('[ok] Manifest generated at $MANIFEST_PATH')
"
echo "========================================================"
echo "=== Storage Overhaul Ingestion Complete (R=1, c=0)   ==="
echo "========================================================"
