#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Court v6: adversarial grading — FTS5 body excerpts via direct sha256 join
# Fix vs v5: excerpt now pulled from fts_evidence.body keyed on hash,
# not filename-MATCH which returned the wrong column
set -euo pipefail
export GIT_PAGER=cat
cd /home/jesse/openroot

CANARY="[COURT-V6]"
DB="data/log_feed.db"
DEBATE="data/debate_ledger.jsonl"
DEFENDER="${DEFENDER_MODEL:-qwen2.5-coder:7b}"
PROSECUTOR="${PROSECUTOR_MODEL:-qwen2.5:3b}"
MAX="${MAX:-50}"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="context_bridge/court-v6-report-${STAMP}.md"
LOG="logs/court_v6_${STAMP}.log"
mkdir -p logs context_bridge data
echo "$CANARY boot — defense=$DEFENDER vs prosecution=$PROSECUTOR"

j()  { python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "$1"; }
sq() { printf '%s' "$1" | sed "s/'/''/g"; }
ask() {
  curl -s --max-time 300 http://localhost:11434/api/generate \
    -d "{\"model\":\"$1\",\"prompt\":$(j "$2

$3"),\"stream\":false,\"options\":{\"temperature\":0.2},\"keep_alive\":\"1h\"}" \
    | python3 -c "import json,sys;print(json.load(sys.stdin).get('response','').strip())" 2>/dev/null || echo ""
}
verd() {
  printf '%s' "$1" | head -2 | tr '[:upper:]' '[:lower:]' \
    | grep -oE '(pass|hold|fail)' | head -1 || true
}

[ -f "$DB" ] || { echo "$CANARY [held] $DB missing"; exit 1; }
curl -s --max-time 5 http://localhost:11434/api/tags >/dev/null \
  || { echo "$CANARY [held] ollama down"; exit 1; }

COLS=$(sqlite3 "$DB" "PRAGMA table_info(log_feed);" | cut -d'|' -f2)
for NEED in sha256 path mtime size canaries warns errs dispatch_status; do
  echo "$COLS" | grep -qx "$NEED" \
    || { echo "$CANARY [held] col $NEED absent"; exit 1; }
done
echo "$COLS" | grep -qx verdict \
  || sqlite3 "$DB" "ALTER TABLE log_feed ADD COLUMN verdict TEXT;"
echo "$COLS" | grep -qx graded_at \
  || sqlite3 "$DB" "ALTER TABLE log_feed ADD COLUMN graded_at TEXT;"
sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS hash_profile (
  sha256 TEXT PRIMARY KEY, path TEXT, size INTEGER, mtime TEXT,
  canaries INTEGER, warns INTEGER, errs INTEGER,
  fts_snippet TEXT, graded_count INTEGER DEFAULT 0, updated_at TEXT);"
touch "$DEBATE"

NFTS=$(sqlite3 "$DB" "SELECT COUNT(*) FROM fts_evidence;" 2>/dev/null | head -1 || echo 0)
if [[ "$NFTS" =~ ^[0-9]+$ ]] && [ "$NFTS" -gt 0 ]; then
  FTSMODE=yes
else
  FTSMODE=no
fi
echo "$CANARY FTS5 evidence mode: $FTSMODE ($NFTS excerpts)"

for M in "$DEFENDER" "$PROSECUTOR"; do
  ask "$M" "Reply with one word: ready" "ready?" >/dev/null
done

TOTAL=$(sqlite3 "$DB" "SELECT COUNT(*) FROM log_feed WHERE dispatch_status='pending';")
[ "$TOTAL" -gt "$MAX" ] && TOTAL="$MAX"
echo "$CANARY hearings this session: $TOTAL"

PASS=0; HOLD=0; FAIL=0; UN=0; SP=0; DET=0
mapfile -t HASHES < <(sqlite3 "$DB" "SELECT sha256 FROM log_feed WHERE dispatch_status='pending' LIMIT $MAX;")

DEF_S="You are DEFENSE COUNSEL in a build-evidence court. Argue FOR the evidence only if it earns it. First line EXACTLY 'VERDICT: pass' or 'VERDICT: fail' or 'VERDICT: hold'. Then one short sentence."
PRO_S="You are PROSECUTION from an OPPOSING bench with no stake in this pipeline. Attack the evidence. First line EXACTLY 'VERDICT: fail' or 'VERDICT: hold'; 'VERDICT: pass' only if overwhelming. Then one short sentence."

for H in "${HASHES[@]}"; do
  ROW=$(sqlite3 "$DB" -separator '|' "SELECT path,mtime,size,canaries,warns,errs FROM log_feed WHERE sha256='$(sq "$H")';")
  IFS='|' read -r PATHNAME MTIME SIZE CANARIES WARNS ERRS <<< "$ROW"

  if [[ "${ERRS:-0}" =~ ^[0-9]+$ ]] && [ "${ERRS:-0}" -gt 0 ]; then
    VERDICT=hold
    REASON="errs=${ERRS} deterministic override, court not convened"
    DV=-; PV=-; MODE=det; DET=$((DET+1))
  else
    SNIP=""
    if [ "$FTSMODE" = yes ]; then
      SNIP=$(sqlite3 "$DB" "SELECT substr(replace(body,char(10),' '),1,400) FROM fts_evidence WHERE sha256='$(sq "$H")' LIMIT 1;" 2>/dev/null || true)
    fi
    EV="Evidence: sha256=$H
path=$PATHNAME
mtime=$MTIME size=$SIZE
canaries=$CANARIES warns=$WARNS errs=$ERRS
content_excerpt=${SNIP:-<none>}"

    DRAW=$(ask "$DEFENDER" "$DEF_S" "$EV")
    DV=$(verd "$DRAW"); [ -n "$DV" ] || DV=hold
    PRAW=$(ask "$PROSECUTOR" "$PRO_S" "$EV

Defense argued: $(printf '%s' "$DRAW" | head -3)")
    PV=$(verd "$PRAW"); [ -n "$PV" ] || PV=hold

    if [ "$DV" = "$PV" ]; then
      VERDICT="$DV"; UN=$((UN+1))
      REASON="unanimous ${DV}: $(printf '%s' "$DRAW" | sed -n 2p | cut -c1-110)"
    else
      VERDICT=hold; SP=$((SP+1))
      REASON="split d=$DV p=$PV — human bench"
    fi
    MODE=court
  fi

  sqlite3 "$DB" "UPDATE log_feed SET dispatch_status='graded',verdict='$(sq "$VERDICT")',graded_at=datetime('now') WHERE sha256='$(sq "$H")';"
  sqlite3 "$DB" "INSERT INTO hash_profile (sha256,path,size,mtime,canaries,warns,errs,fts_snippet,graded_count,updated_at) VALUES ('$(sq "$H")','$(sq "$PATHNAME")','${SIZE:-0}','$(sq "$MTIME")','${CANARIES:-0}','${WARNS:-0}','${ERRS:-0}','$(sq "$SNIP")',1,datetime('now')) ON CONFLICT(sha256) DO UPDATE SET graded_count=graded_count+1,fts_snippet=excluded.fts_snippet,updated_at=datetime('now');"
  python3 - "$DEBATE" "$H" "$PATHNAME" "$DV" "$PV" "$VERDICT" "$MODE" "$REASON" <<'PY'
import json,sys,datetime
r={"ts":datetime.datetime.now().isoformat(timespec="seconds"),"sha256":sys.argv[2],
"path":sys.argv[3],"defense":sys.argv[4],"prosecution":sys.argv[5],
"verdict":sys.argv[6],"mode":sys.argv[7],"reason":sys.argv[8]}
open(sys.argv[1],"a").write(json.dumps(r)+"\n")
PY
  case "$VERDICT" in pass) PASS=$((PASS+1));; hold) HOLD=$((HOLD+1));; fail) FAIL=$((FAIL+1));; esac
  echo "[$(echo "$H"|cut -c1-12)] $MODE $VERDICT (d:$DV/p:$PV) $REASON" >> "$LOG"
done

{ echo "# Court v6 — $STAMP"
  echo "- defense=$DEFENDER prosecution=$PROSECUTOR fts=$FTSMODE"
  echo "- heard=$TOTAL pass=$PASS hold=$HOLD fail=$FAIL unanimous=$UN split=$SP det=$DET"
  echo "- verdict dist: $(sqlite3 "$DB" "SELECT verdict,COUNT(*) FROM log_feed GROUP BY verdict;" | tr '\n' ' ')"
} > "$REPORT"
echo "$CANARY done: pass=$PASS hold=$HOLD fail=$FAIL un=$UN split=$SP det=$DET"
sha256sum "$REPORT" "$LOG" | awk '{print "["$2"] "$1}'
echo "$CANARY [exit=0]"
