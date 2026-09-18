#!/usr/bin/env bash
# [canary] paste intact
set -Eeuo pipefail

LEDGER="/home/jesse/.local/share/openroot/ledger.db"

sqlite3 "${LEDGER}" "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL; PRAGMA cache_size=-8000;" >/dev/null
MODE="$(sqlite3 "${LEDGER}" "PRAGMA journal_mode;")"
MODE="$(printf '%s' "${MODE}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
if [ "${MODE}" != "wal" ]; then
  echo "[held] journal_mode=${MODE}"
  exit 5
fi
echo "[tuned] ledger.db pragmas set"
