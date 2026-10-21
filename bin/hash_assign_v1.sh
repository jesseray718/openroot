#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

# ============================================================
# OPENROOT HASH ASSIGN v1 — OPTIPLEX / UBUNTU
# Host-local, resumable SHA-256 manifest generator.
# Uses its own SQLite database:
#   ~/openroot/data/hash_manifest_optiplex.db
# ============================================================

SOURCE_ROOT="${SOURCE_ROOT:-$HOME/openroot}"
DB="${DB:-$HOME/openroot/data/hash_manifest_optiplex.db}"
HOST_TAG="${HOST_TAG:-optiplex}"
LOG_DIR="${LOG_DIR:-$HOME/openroot/logs}"
RUN_DIR="${RUN_DIR:-$HOME/openroot/run}"
BATCH_SIZE="${BATCH_SIZE:-100}"
SQLITE_BUSY_MS="${SQLITE_BUSY_MS:-30000}"

PIDFILE="$RUN_DIR/hash_assign_${HOST_TAG}.pid"
LOCKDIR="$RUN_DIR/hash_assign_${HOST_TAG}.lock"
LOGFILE="$LOG_DIR/hash_assign_${HOST_TAG}.log"

SEEN=0
HASHED=0
SKIPPED=0
ERRORS=0

mkdir -p "$LOG_DIR" "$RUN_DIR" "$(dirname "$DB")"

log() {
  printf '%s host=%s pid=%s %s\n' \
    "$(date -Is)" "$HOST_TAG" "$$" "$*" | tee -a "$LOGFILE"
}

die() {
  log "event=fatal message=$(printf '%q' "$*")"
  exit 1
}

cleanup() {
  rc=$?
  rm -f "$PIDFILE"
  rmdir "$LOCKDIR" 2>/dev/null || true
  log "event=exit code=$rc seen=$SEEN hashed=$HASHED skipped=$SKIPPED errors=$ERRORS"
}

trap cleanup EXIT
trap 'log "event=signal signal=INT"; exit 130' INT
trap 'log "event=signal signal=TERM"; exit 143' TERM

command -v sqlite3 >/dev/null 2>&1 || die "sqlite3 is not installed"
command -v sha256sum >/dev/null 2>&1 || die "sha256sum is not installed"
command -v find >/dev/null 2>&1 || die "find is not installed"
command -v stat >/dev/null 2>&1 || die "stat is not installed"

[[ -d "$SOURCE_ROOT" ]] || die "source root missing: $SOURCE_ROOT"

if ! mkdir "$LOCKDIR" 2>/dev/null; then
  if [[ -f "$PIDFILE" ]]; then
    OLD_PID="$(cat "$PIDFILE" 2>/dev/null || true)"
    if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
      die "another hash job is active: pid=$OLD_PID"
    fi
  fi

  rm -rf "$LOCKDIR"
  mkdir "$LOCKDIR" || die "cannot create lock: $LOCKDIR"
fi

echo "$$" > "$PIDFILE"

sql_quote() {
  local value="$1"
  value=${value//\'/\'\'}
  printf "'%s'" "$value"
}

sqlite_exec() {
  sqlite3 -batch "$DB" <<SQL
PRAGMA busy_timeout=$SQLITE_BUSY_MS;
.output /dev/null
PRAGMA busy_timeout;
.output stdout
$1
SQL
}

file_size() {
  stat -c '%s' "$1" 2>/dev/null \
    || stat -f '%z' "$1" 2>/dev/null \
    || printf '0'
}

file_mtime_ns() {
  stat -c '%Y000000000' "$1" 2>/dev/null \
    || stat -f '%m000000000' "$1" 2>/dev/null \
    || printf '0'
}

init_database() {
  sqlite_exec "
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS manifest (
  path        TEXT PRIMARY KEY,
  sha256      TEXT NOT NULL,
  size_bytes  INTEGER NOT NULL,
  mtime_ns    INTEGER NOT NULL,
  hashed_at   TEXT NOT NULL,
  host        TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'ok',
  error_text  TEXT
);

CREATE INDEX IF NOT EXISTS manifest_sha256_idx
ON manifest(sha256);

CREATE INDEX IF NOT EXISTS manifest_status_idx
ON manifest(status);
"
}

preflight() {
  sqlite3 -batch "$DB" \
    "PRAGMA busy_timeout=$SQLITE_BUSY_MS;
     PRAGMA quick_check;" \
    | tail -n 1 | grep -qx 'ok' \
    || die "SQLite quick_check failed or database remained locked"

  sqlite3 -batch "$DB" \
    "PRAGMA busy_timeout=$SQLITE_BUSY_MS;
     SELECT 1
     FROM pragma_table_info('manifest')
     WHERE name='hashed_at';" \
    | tail -n 1 | grep -qx '1' \
    || die "required manifest field missing"

  sqlite3 -batch "$DB" <<SQL
PRAGMA busy_timeout=$SQLITE_BUSY_MS;
BEGIN IMMEDIATE;
INSERT INTO manifest (
  path, sha256, size_bytes, mtime_ns, hashed_at, host, status, error_text
) VALUES (
  '__OPENROOT_PREFLIGHT__',
  'preflight',
  0,
  0,
  datetime('now'),
  'preflight',
  'preflight',
  NULL
)
ON CONFLICT(path) DO UPDATE SET
  hashed_at=excluded.hashed_at;
ROLLBACK;
SQL
}

is_current() {
  local path="$1"
  local size="$2"
  local mtime="$3"

  sqlite3 -batch -noheader "$DB" \
    "PRAGMA busy_timeout=$SQLITE_BUSY_MS;
     SELECT 1
     FROM manifest
     WHERE path=$(sql_quote "$path")
       AND size_bytes=$size
       AND mtime_ns=$mtime
       AND status='ok'
     LIMIT 1;" \
    | tail -n 1 | grep -qx '1'
}

write_success() {
  local path="$1"
  local sha="$2"
  local size="$3"
  local mtime="$4"
  local now="$5"

  sqlite_exec "
BEGIN IMMEDIATE;
INSERT INTO manifest (
  path, sha256, size_bytes, mtime_ns, hashed_at, host, status, error_text
) VALUES (
  $(sql_quote "$path"),
  $(sql_quote "$sha"),
  $size,
  $mtime,
  $(sql_quote "$now"),
  $(sql_quote "$HOST_TAG"),
  'ok',
  NULL
)
ON CONFLICT(path) DO UPDATE SET
  sha256=excluded.sha256,
  size_bytes=excluded.size_bytes,
  mtime_ns=excluded.mtime_ns,
  hashed_at=excluded.hashed_at,
  host=excluded.host,
  status='ok',
  error_text=NULL;
COMMIT;
"
}

write_error() {
  local path="$1"
  local message="$2"
  local now
  now="$(date -Is)"

  sqlite_exec "
BEGIN IMMEDIATE;
INSERT INTO manifest (
  path, sha256, size_bytes, mtime_ns, hashed_at, host, status, error_text
) VALUES (
  $(sql_quote "$path"),
  '',
  0,
  0,
  $(sql_quote "$now"),
  $(sql_quote "$HOST_TAG"),
  'error',
  $(sql_quote "$message")
)
ON CONFLICT(path) DO UPDATE SET
  hashed_at=excluded.hashed_at,
  host=excluded.host,
  status='error',
  error_text=excluded.error_text;
COMMIT;
"
}

checkpoint() {
  local durable
  durable="$(
    sqlite3 -batch -noheader "$DB" \
      "PRAGMA busy_timeout=$SQLITE_BUSY_MS;
       SELECT COUNT(*) FROM manifest WHERE status='ok';" \
      2>/dev/null | tail -n 1 || printf '?'
  )"

  log "event=checkpoint seen=$SEEN hashed=$HASHED skipped=$SKIPPED errors=$ERRORS durable_rows=$durable"
}

init_database
preflight

log "event=start source_root=$(printf '%q' "$SOURCE_ROOT") db=$(printf '%q' "$DB") batch_size=$BATCH_SIZE"

while IFS= read -r -d '' file; do
  SEEN=$((SEEN + 1))

  if [[ ! -r "$file" ]]; then
    ERRORS=$((ERRORS + 1))
    write_error "$file" "unreadable" || true
    continue
  fi

  size="$(file_size "$file")"
  mtime="$(file_mtime_ns "$file")"

  if is_current "$file" "$size" "$mtime"; then
    SKIPPED=$((SKIPPED + 1))
  else
    if sha="$(sha256sum -- "$file" 2>/dev/null | awk '{print $1}')"; then
      now="$(date -Is)"

      if write_success "$file" "$sha" "$size" "$mtime" "$now"; then
        HASHED=$((HASHED + 1))
      else
        ERRORS=$((ERRORS + 1))
        log "event=write_failed path=$(printf '%q' "$file")"
      fi
    else
      ERRORS=$((ERRORS + 1))
      write_error "$file" "sha256sum_failed" || true
    fi
  fi

  if (( SEEN % BATCH_SIZE == 0 )); then
    checkpoint
  fi
done < <(
  find "$SOURCE_ROOT" \
    -type f \
    ! -path "$DB" \
    ! -path "$DB-wal" \
    ! -path "$DB-shm" \
    ! -path "$LOG_DIR/*" \
    ! -path "$RUN_DIR/*" \
    -print0
)

checkpoint
log "event=complete"
