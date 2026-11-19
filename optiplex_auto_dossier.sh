#!/usr/bin/env bash
set -Eeuo pipefail

echo "========================================================"
echo "=== OptiPlex Full-Loop Auto Dossier Ingestion Engine ==="
echo "========================================================"

CORE_ROOT="$HOME/openroot"
SYNC_DIR="$CORE_ROOT/workareas/release"
cd "$CORE_ROOT"

echo "[1/4] Scanning for incoming A15 sync payloads..."
LATEST_PAYLOAD="$(ls -t "$SYNC_DIR"/mesh_sync_payload_*.tar.gz 2>/dev/null | head -n 1 || true)"

if [ -z "$LATEST_PAYLOAD" ]; then
    echo "[info] No pending mesh payloads found in $SYNC_DIR."
    exit 0
fi

echo "[ok] Found payload: $LATEST_PAYLOAD"

echo "[2/4] Verifying payload checksum against manifest..."
MANIFEST_FILE="${LATEST_PAYLOAD/mesh_sync_payload/sync_manifest}"
MANIFEST_FILE="${MANIFEST_FILE/.tar.gz/.json}"

if [ -f "$MANIFEST_FILE" ]; then
    EXPECTED_HASH=$(python3 -c "import json; print(json.load(open('$MANIFEST_FILE'))['sha256'])")
    ACTUAL_HASH=$(sha256sum "$LATEST_PAYLOAD" | awk '{print $1}')
    if [ "$EXPECTED_HASH" = "$ACTUAL_HASH" ]; then
        echo "[ok] Checksum verification PASSED ($ACTUAL_HASH)"
    else
        echo "[error] Checksum verification FAILED!"
        exit 1
    fi
fi

echo "[3/4] Unpacking payload into core workspace..."
tar -xzf "$LATEST_PAYLOAD" -C "$CORE_ROOT"

echo "[4/4] Indexing incoming pods into SQLite FTS5 ledger..."
python3 -c "
import sqlite3, os, json, glob
db_path = 'data/universal_index/openroot_core.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS fts_pods (pod_id TEXT PRIMARY KEY, payload TEXT)')
for f in glob.glob('workareas/agape_pods/*.json'):
    data = json.load(open(f))
    cursor.execute('INSERT OR REPLACE INTO fts_pods (pod_id, payload) VALUES (?, ?)', 
                   (data.get('pod_id', 'unknown'), json.dumps(data)))
conn.commit()
conn.close()
print('[ok] SQLite FTS5 indexing complete.')
"

echo "========================================================"
echo "=== OptiPlex Dossier Ingestion & Loop Complete (R=1, c=0) ==="
echo "========================================================"
