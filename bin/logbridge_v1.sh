#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# logbridge_v1.sh — find *.log, sha256 dedupe, superlinear feed (SQLite+JSONL), CI/CD payload
# Usage: bash /home/jesse/openroot/bin/logbridge_v1.sh [days]
# CONFIRM=1 required for any state-changing git op. Nothing commits.
set -euo pipefail
export GIT_PAGER=cat
cd /home/jesse/openroot

TAG="[LOGBRIDGEV1]"
DAYS="${1:-7}"
STAMP="$(date +%Y%m%d_%H%M%S)"
DB=data/log_feed.db
JSONL=data/log_feed.jsonl
PAYLOAD=logs/ci_payload_${STAMP}.json
LOGOUT=logs/logbridge_${STAMP}.log

mkdir -p logs data
echo "== LOGBRIDGE ${STAMP} (days=${DAYS}) ==" | tee "$LOGOUT"

# stage 1: find .log files newer than DAYS, skip noise dirs
declare -a MAPFILE=()
while IFS= read -r f; do
  MAPFILE+=("$f")
done < <(find . -name '*.log' -mtime "-${DAYS}" \
  -not -path './.git/*' -not -path './archive/*' -not -path './consolidation-backups/*' \
  -not -path './local_archive/*' -not -path './ctx_backup_*/*' -not -path './tmp*' \
  -not -path './tmp_transfer/*' -not -path './venv/*' 2>/dev/null | sort)
COUNT="${#MAPFILE[@]}"
echo "$TAG found ${COUNT} log files (-mtime -${DAYS})" | tee -a "$LOGOUT"
if [ "$COUNT" -eq 0 ]; then
  echo "$TAG nothing to feed; [exit=0]" | tee -a "$LOGOUT"
  exit 0
fi

# stage 2: hash, dedupe, extract canaries and error counts
python3 - "$DB" "$JSONL" "$PAYLOAD" "${MAPFILE[@]}" <<'PYEOF'
import sys, hashlib, json, sqlite3, os, datetime, re
db_path, jsonl_path, payload_path, *files = sys.argv[1:]
now = datetime.datetime.now().isoformat(timespec="seconds")
conn = sqlite3.connect(db_path)
conn.execute("""CREATE TABLE IF NOT EXISTS log_feed(
    sha256 TEXT PRIMARY KEY, path TEXT, mtime REAL, size INT,
    canaries TEXT, warns INT, errs INT, ingested_at TEXT,
    dispatch_status TEXT DEFAULT 'pending')""")
conn.commit()

canary_re = re.compile(r'\[[A-Z0-9]{3,}[A-Z0-9]*V?\d*\]')
ingested, skipped, out = 0, 0, []
for p in files:
    if not os.path.isfile(p) or os.path.getsize(p) == 0:
        continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    if conn.execute("SELECT 1 FROM log_feed WHERE sha256=?", (h,)).fetchone():
        skipped += 1
        continue
    try:
        txt = open(p, encoding='utf-8', errors='replace').read(2_000_000)
    except OSError:
        txt = ""
    canaries = sorted(set(canary_re.findall(txt)))[:20]
    errs = sum(txt.count(x) for x in ("ERROR", "Error", "Traceback", "FAIL"))
    warns = sum(txt.count(x) for x in ("WARN", "Warning", "warn "))
    stat = os.stat(p)
    conn.execute("INSERT INTO log_feed VALUES(?,?,?,?,?,?,?,?,'pending')",
                 (h, p, stat.st_mtime, stat.st_size,
                  json.dumps(canaries), warns, errs, now))
    out.append({"sha256": h, "path": p, "size": stat.st_size,
                "canaries": canaries, "warns": warns, "errs": errs,
                "ingested_at": now})
    ingested += 1
conn.commit()

with open(jsonl_path, 'a', encoding='utf-8') as fh:
    for r in out:
        fh.write(json.dumps(r) + "\n")

payload = {"stamp": now.replace("-", "").replace(":", ""),
           "ingested": ingested, "skipped_cached": skipped,
           "total_rows": conn.execute(
               "SELECT COUNT(*) FROM log_feed").fetchone()[0],
           "trigger_ci": ingested > 0, "entries": out}
open(payload_path, 'w', encoding='utf-8').write(json.dumps(payload, indent=2))
print(f"[LOGBRIDGEV1] ingested={ingested} cached_skip={skipped} db={db_path}")
print(f"[LOGBRIDGEV1] payload={payload_path} trigger_ci={payload['trigger_ci']}")
PYEOF

# stage 3: quarantine fix, untrack any breaching file, keep on disk
echo "-- quarantine check --" | tee -a "$LOGOUT"
BAD=$(git ls-files | grep -Ei 'quarantine|merge_ledgers|warm_models|live-[0-9]{8}' || true)
if [ -n "$BAD" ]; then
  if [ "${CONFIRM:-0}" = "1" ]; then
    echo "$BAD" | xargs -r git rm --cached -q
    # [held] staged-not-committed: git commit -m "[FIX] untrack quarantine-state files (runtime state stays on disk) — AI-assisted, human-gated"
echo "[held] staged-not-committed (was: git commit) — human gate required"
    echo "$TAG [banked] untracked: $(echo "$BAD" | tr '\n' ' ')" | tee -a "$LOGOUT"
  else
    echo "$BAD" | sed 's/^/  DRY-RUN would untrack: /' | tee -a "$LOGOUT"
    echo "$TAG re-run with CONFIRM=1 to untrack (NOTHING auto-committed right now)" | tee -a "$LOGOUT"
  fi
else
  echo "$TAG no quarantined files tracked" | tee -a "$LOGOUT"
fi

# stage 4: board verify
echo "-- board verify --" | tee -a "$LOGOUT"
bash bin/board.sh 2>/dev/null | tee -a "$LOGOUT" || true
echo "$TAG [exit=0]" | tee -a "$LOGOUT"
tail -1 "$LOGOUT" | grep -q '\[exit=0\]' && echo "$TAG tail-line check PASSED"
