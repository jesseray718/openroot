#!/usr/bin/env bash
set -eu
DB=/home/jesse/pods/pod_universal/pod.db
BAK=/home/jesse/pods/backups/pod_universal_20261016T071945Z.db

echo "=== [STAGE 1] DIAGNOSE ==="
CHK=$(sqlite3 "$DB" ".timeout 30000" "PRAGMA quick_check;" 2>&1 || echo MALFORMED)
echo "quick_check: $CHK"

if [ "$CHK" = "ok" ]; then
  echo "=== [GATE] DB passes quick_check — trying FTS index rebuild instead ==="
  pgrep -f universal_index_overhaul >/dev/null && { echo "[held] walker running; stop it before rebuild"; exit 1; }
  sqlite3 "$DB" ".timeout 120000" "INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild'); PRAGMA integrity_check;"
  echo "[banked] FTS rebuilt from content"
else
  echo "=== [STAGE 2] CORRUPT — RESTORE FROM VERIFIED BACKUP ==="
  echo "[gate] stopping walker (progress preserved in backup)"
  pkill -f universal_index_overhaul 2>/dev/null && sleep 2 || true
  rm -f "$DB" "$DB-wal" "$DB-shm"
  cp "$BAK" "$DB"
  BAKCHK=$(sha256sum "$BAK" | awk '{print $1}')
  NEWCHK=$(sha256sum "$DB" | awk '{print $1}')
  [ "$BAKCHK" = "$NEWCHK" ] || { echo "[held] restore hash mismatch"; exit 1; }
  echo "[banked] restored backup (sha256 verified: ${NEWCHK:0:16}...)"
  POST=$(sqlite3 "$DB" "PRAGMA quick_check;")
  [ "$POST" = "ok" ] || { echo "[held] restored copy also fails"; exit 1; }
  echo "[banked] integrity ok post-restore"
  echo "=== [STAGE 3] RELAUNCH WALKER (resumes from SD leg) ==="
  cd /home/jesse/openroot/bin
  setsid nohup python3 -u universal_index_overhaul_v1.py > /home/jesse/openroot/logs/universal_index_overhaul_v5_$(date -u +%Y%m%dT%H%M%SZ).log 2>&1 < /dev/null &
  echo "[banked] walker relaunched pid=$!"
fi
echo "[exit=0]"
