#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
LOG=$(ls -t /home/jesse/openroot/logs/universal_index_overhaul_v*.log 2>/dev/null | head -1)
DB=/home/jesse/pods/pod_universal/pod.db

echo "=== [STAGE 0] INDEXER STATUS ==="
tail -5 "$LOG"
if pgrep -f universal_index_overhaul >/dev/null; then
  echo "[held] indexer still running — rerun this script after it exits"
  exit 0
fi
if ! grep -q "run complete" "$LOG"; then
  echo "[gate] indexer exited WITHOUT SEAL — relaunch recommended:"
  echo "  cd /home/jesse/openroot/bin && nohup python3 -u universal_index_overhaul_v1.py > /home/jesse/openroot/logs/universal_index_overhaul_v3_\$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 &"
  exit 1
fi

echo "=== [STAGE 1] SEAL POD ==="
sqlite3 "$DB" "PRAGMA wal_checkpoint(TRUNCATE); PRAGMA integrity_check; PRAGMA optimize;"
echo "--- vacuum (may take minutes) ---"
sqlite3 "$DB" "VACUUM;"
ls -lh "$DB"

echo "=== [STAGE 2] CENSUS ==="
sqlite3 "$DB" "SELECT 'files',COUNT(*) FROM files UNION ALL SELECT 'chunks',COUNT(*) FROM chunks UNION ALL SELECT 'pathways',COUNT(*) FROM pathways UNION ALL SELECT 'dossiers',COUNT(*) FROM dossiers;"

echo "=== [STAGE 3] SHA256 SPOT-CHECK (5 random files) ==="
PASS=0; FAIL=0
for PATH_F in $(sqlite3 "$DB" "SELECT path FROM files ORDER BY RANDOM() LIMIT 5"); do
  [ -f "$PATH_F" ] || { echo "MISSING on disk: $PATH_F"; FAIL=$((FAIL+1)); continue; }
  IDX=$(sqlite3 "$DB" "SELECT file_sha256 FROM files WHERE path='$PATH_F'")
  DISK=$(sha256sum "$PATH_F" | awk '{print $1}')
  if [ "$IDX" = "$DISK" ]; then PASS=$((PASS+1)); echo "[banked] match: $(basename "$PATH_F")"; else FAIL=$((FAIL+1)); echo "[held] MISMATCH: $PATH_F"; fi
done
echo "spot-check: pass=$PASS fail=$FAIL"
[ "$FAIL" -gt 0 ] && { echo "[held] audit failed — do not proceed to bench relaunch"; exit 1; }

echo "=== [STAGE 4] FTS SMOKE ==="
sqlite3 "$DB" "SELECT section_path, snippet(chunks_fts,0,'[',']','…',10) FROM chunks_fts WHERE chunks_fts MATCH 'permaculture' LIMIT 3;"
sqlite3 "$DB" "SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH 'dossier';"

echo "=== [STAGE 5] RELAUNCH BENCH (resumes at q15) ==="
cd /home/jesse/openroot/bin
nohup python3 -u run_dossier_agent_bench_v1.py > /home/jesse/openroot/logs/dossier_agent_bench_v4_$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 &
echo "[banked] bench relaunched pid=$!"

echo "=== [STAGE 6] COUNTERS ==="
echo "dry-runs=0 completed=$(sqlite3 "$DB" 'SELECT COUNT(*) FROM pathways')"
echo "[exit=0]"
