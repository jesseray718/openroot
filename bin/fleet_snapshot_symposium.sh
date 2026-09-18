#!/usr/bin/env bash
# [canary] paste intact
set -Eeuo pipefail

ROOT=/home/jesse/openroot
DB=/home/jesse/.local/share/openroot/ledger.db
OUTDIR=${ROOT}/data/fleet_snapshots
mkdir -p "$OUTDIR"
STAMP=$(date +%Y%m%d-%H%M%S)

echo "[stage-1] Snapshot ledger schema and row counts"
{
  sqlite3 "$DB" ".tables"
  echo "---SCHEMA---"
  sqlite3 "$DB" "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL;"
  echo "---COUNTS---"
  sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table';" | while read -r T; do
    C=$(sqlite3 "$DB" "SELECT COUNT(*) FROM [$T];" 2>/dev/null || echo "?")
    echo "$T: $C rows"
  done
} > "${OUTDIR}/db_structure_${STAMP}.txt"
echo "[stage-1] wrote ${OUTDIR}/db_structure_${STAMP}.txt"

echo "[stage-2] Inventory *.py and *.sh (batched)"
INVENTORY="${OUTDIR}/script_inventory_${STAMP}.tsv"
timeout 300 find "$ROOT" \
  \( -name .git -o -name __pycache__ -o -name node_modules \
     -o -name salvage -o -name attic -o -name venv -o -name .venv \
     -o -name build -o -name .cache -o -name '*.egg-info' \) -prune \
  -o -type f \( -name '*.py' -o -name '*.sh' \) -print0 \
| xargs -0 -r du -b --apparent-size 2>/dev/null \
| while IFS=$'\t' read -r PATHNAME BYTES; do
    printf '%s\t%sB\t-\n' "$PATHNAME" "$BYTES"
  done > "$INVENTORY"
SCRIPT_COUNT=$(wc -l < "$INVENTORY")
echo "[stage-2] wrote $INVENTORY ($SCRIPT_COUNT scripts)"

echo "[stage-3] Model roster"
MODEL_JSON=$(curl -sf http://localhost:11434/api/tags || echo '{}')
MODELS=$(echo "$MODEL_JSON" | jq -r '.models[].name' | tr '\n' ',' | sed 's/,$//')
if [ -z "$MODELS" ]; then
  echo "[held] ollama unreachable or no models"
  exit 2
fi
echo "$MODEL_JSON" > "${OUTDIR}/models_${STAMP}.json"

echo "[stage-4] Composing context packet"
CONTEXT="SYSTEM SNAPSHOT (${STAMP})
Models: ${MODELS}
Scripts indexed: ${SCRIPT_COUNT}
Top-level dirs: $(ls -d ${ROOT}/*/ 2>/dev/null | tr '\n' ' ')
DB tables and counts:
$(head -c 3000 "${OUTDIR}/db_structure_${STAMP}.txt")"

echo "[stage-5] 3B INTAKE - generating interrogation questions"
QUESTIONS=$(jq -n --arg ctx "$CONTEXT" '{
  model: "qwen2.5:3b", stream: false,
  options: {temperature: 0.3},
  prompt: ("You are the intake analyst of a development fleet. Given this system snapshot, generate exactly 5 sharp questions that would reveal inefficiencies, dead code, missing wiring, or unused capacity. Output ONLY the numbered questions, nothing else.\n\n" + $ctx)
}' | curl -s http://localhost:11434/api/generate -d @- | jq -r '.response // empty')
if [ -z "$QUESTIONS" ]; then
  echo "[held] 3B model gave no questions"
  exit 3
fi

echo "[stage-6] 7B SOLVE - answering with directives"
ANSWERS=$(jq -n --arg ctx "$CONTEXT" --arg q "$QUESTIONS" '{
  model: "qwen2.5-coder:7b", stream: false,
  options: {temperature: 0.2},
  prompt: ("You are the senior engineer of this system. Answer each question concretely using the snapshot. For each answer, output one directive line in the form: DIRECTIVE|<exact-path-or-command>|<action>. No prose outside the answers and directives.\n\nSNAPSHOT:\n" + $ctx + "\n\nQUESTIONS:\n" + $q)
}' | curl -s http://localhost:11434/api/generate -d @- | jq -r '.response // empty')
if [ -z "$ANSWERS" ]; then
  echo "[held] 7B model gave no answers"
  exit 4
fi
printf '%s\n' "$ANSWERS" > "${OUTDIR}/last_7b_answer.txt"

echo "[stage-7] Persisting symposium into ledger.db"
python3 - "$DB" "$STAMP" "$(hostname)" "$MODELS" "$SCRIPT_COUNT" \
  "${OUTDIR}/db_structure_${STAMP}.txt" "$QUESTIONS" "$ANSWERS" << 'PYEOF'
import sqlite3, sys
db, stamp, node, models, count, dump_p, questions, answers = sys.argv[1:9]
dump = open(dump_p).read()[:2000]
con = sqlite3.connect(db)
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS fleet_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stamp TEXT, node TEXT, models TEXT, script_count INTEGER,
    db_dump TEXT, questions TEXT, answers TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
cur.execute("""CREATE TABLE IF NOT EXISTS model_findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER, directive TEXT,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(snapshot_id) REFERENCES fleet_snapshots(id))""")
cur.execute("INSERT INTO fleet_snapshots (stamp,node,models,script_count,db_dump,questions,answers) VALUES (?,?,?,?,?,?,?)",
            (stamp, node, models, int(count), dump, questions, answers))
snap_id = cur.lastrowid
import re as _re
_pat = _re.compile(r"^\s*(?:\d+[.)]\s*)?DIRECTIVE\|(.*\S)\s*$")
dirs = [m.group(1) for m in (_pat.match(l) for l in answers.splitlines()) if m]
for d in dirs:
    cur.execute("INSERT INTO model_findings (snapshot_id, directive) VALUES (?,?)", (snap_id, d))
con.commit()
print(f"[stage-7] snapshot {snap_id} persisted, {len(dirs)} directives queued")
PYEOF

echo "[stage-8] Dashboard report"
REPORT="${OUTDIR}/report_${STAMP}.md"
{
  echo "# Fleet Snapshot ${STAMP}"
  echo "- Node: $(hostname), Models: ${MODELS}"
  echo "- Scripts indexed: ${SCRIPT_COUNT}"
  echo "- DB tables: $(sqlite3 "$DB" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';")"
  echo ""
  echo "## 3B Questions"
  echo "$QUESTIONS"
  echo ""
  echo "## 7B Answers + Directives"
  echo "$ANSWERS"
  echo ""
  echo "## Pending directives"
  sqlite3 "$DB" "SELECT id, directive FROM model_findings WHERE status='pending';"
} > "$REPORT"

echo "[DONE] Report: $REPORT"
echo "[NEXT] Review: sqlite3 $DB \"SELECT id,directive,status FROM model_findings WHERE status='pending';\""
