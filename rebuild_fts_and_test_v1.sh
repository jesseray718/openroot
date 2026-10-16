#!/usr/bin/env bash
set -eu
DB=/home/jesse/pods/pod_universal/pod.db
BAK=/home/jesse/pods/backups/pod_universal_20261016T071945Z.db
echo "=== [STAGE 1] STOP WALKER ==="
pkill -f universal_index_overhaul 2>/dev/null && sleep 2 || echo "(already stopped)"
echo "=== [STAGE 2] FRESH RESTORE FROM BACKUP ==="
rm -f "$DB" "$DB-wal" "$DB-shm"
cp "$BAK" "$DB"
echo "=== [STAGE 3] REBUILD EXTERNAL-CONTENT FTS ==="
sqlite3 "$DB" ".timeout 120000" "INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild');"
echo "=== [STAGE 4] INTEGRITY ==="
sqlite3 "$DB" "PRAGMA integrity_check;"
sqlite3 "$DB" "SELECT 'files',COUNT(*) FROM files UNION ALL SELECT 'chunks',COUNT(*) FROM chunks;"
echo "=== [STAGE 5] SNIPPET SMOKE (the failing query) ==="
sqlite3 "$DB" ".timeout 30000" "SELECT rowid, snippet(chunks_fts,0,'[',']','…',10) FROM chunks_fts WHERE chunks_fts MATCH 'merkle' LIMIT 2;"
echo "=== [STAGE 6] RESEAL REPAIRED BACKUP ==="
sqlite3 "$DB" ".backup '/home/jesse/pods/backups/pod_universal_repaired.db'"
sqlite3 /home/jesse/pods/backups/pod_universal_repaired.db "PRAGMA quick_check;"
echo "=== [STAGE 7] RELAUNCH WALKER (singleton guard) ==="
if pgrep -f universal_index_overhaul >/dev/null; then echo "[held] walker already running?!"; exit 1; fi
setsid nohup python3 -u /home/jesse/openroot/bin/universal_index_overhaul_v1.py > /home/jesse/openroot/logs/universal_index_overhaul_v6_$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 < /dev/null &
echo "[banked] walker relaunched pid=$!"
echo "[exit=0]"
