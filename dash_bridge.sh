#!/usr/bin/env bash
set -Eeuo pipefail

echo "=== OpenRoot Markor & Termux File Ingestion Bridge ==="
EXPORT_DIR="workareas/dashboard/ingested"
mkdir -p "$EXPORT_DIR"

# Crawl Termux home and Markor storage for raw notes/tidbits
SEARCH_PATHS=(
    "$HOME/openroot"
    "$HOME/storage/shared/Documents/Markor"
    "$HOME/.termux"
)

INDEX_COUNT=0
for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        while IFS= read -r -d '' file; do
            cp "$file" "$EXPORT_DIR/" 2>/dev/null || true
            ((INDEX_COUNT++))
        done < <(find "$path" -type f \( -name "*.md" -o -name "*.json" -o -name "*.txt" \) -print0 2>/dev/null)
    fi
done

echo "[ok] Ingested $INDEX_COUNT files into dashboard optimization buffer."
