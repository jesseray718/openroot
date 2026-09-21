#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# POPW-instrumented async README draft loop: 7B drafts, 3B grades; every call
# accounts tokens+joules to data/popw_ledger.db; FTS5 corpus; inbox on verdict.
# Usage: bin/readme_draft_loop.sh [max] ; bin/readme_draft_loop.sh query "<terms>"
set -u
cd /home/jesse/openroot || exit 1

if [ "${1:-}" = "query" ]; then
  python3 - "$2" <<'PYQ'
import sqlite3, sys
try:
    rows = sqlite3.connect("data/readme_loop.db").execute(
        "SELECT attempt, verdict, substr(body,1,160) FROM drafts WHERE drafts MATCH ? ORDER BY rank LIMIT 10",
        (sys.argv[1],)).fetchall()
    for r in rows: print(f"[a{r[0]}|{r[1]}] {r[2]}")
except Exception as e: print(f"[FTS5] {e}")
PYQ
  exit 0
fi
MAX="${1:-5}"
mkdir -p data docs context_bridge
python3 - <<'PYDB'
import sqlite3
db = sqlite3.connect("data/readme_loop.db")
db.executescript("""CREATE TABLE IF NOT EXISTS drafts_meta(id INTEGER PRIMARY KEY, attempt INT, ts TEXT, verdict TEXT, fixline TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS drafts USING fts5(attempt UNINDEXED, verdict UNINDEXED, body);""")
db.commit()
PYDB

echo "[warmup] loading coder model into RAM (past stalls were cold loads, not failures)"
timeout 400 python3 bin/popw_ledger.py call warmup qwen2.5-coder:7b "Reply with exactly: READY" 2>&1 | tail -1

README_CTX=$(head -100 README.md 2>/dev/null || echo "[no README]")
PROMPT="Rewrite this README as a professional open-source front page: one-line mission, install (clone + ./bin scripts), architecture (agent loop, gates, mistake ledger, non-recompute cache), contribution workflow (human-gated commits), badges placeholders (CI, GPL-3.0), How-it-works citing the lb_loop 21-cached-passes proof. Keep all existing facts, invent nothing. README follows: ${README_CTX}"

for i in $(seq 1 "$MAX"); do
  echo "[loop] attempt $i/$MAX — draft (popw-accounted)"
  BODY=$(timeout 400 python3 bin/popw_ledger.py call draft qwen2.5-coder:7b "$PROMPT" 2>>context_bridge/popw.tail) || { echo "[loop] draft unavailable — skipped"; sleep 5; continue; }
  echo "[loop] attempt $i/$MAX — grade (popw-accounted)"
  GRADE=$(printf '%s' "$BODY" | timeout 200 python3 bin/popw_ledger.py call grade qwen2.5:3b "Grade: professional, accurate, no invented features? Reply 'PASS' or 'FAIL: <one-line fix>'. Document follows:" --stdin 2>/dev/null | tail -1) || GRADE="FAIL: grader offline"
  python3 - "$i" "$GRADE" "$BODY" <<'PYI'
import sqlite3, sys
db = sqlite3.connect("data/readme_loop.db")
db.execute("INSERT INTO drafts(attempt, verdict, body) VALUES (?,?,?)", (sys.argv[1], sys.argv[2], sys.argv[3]))
db.commit()
PYI
  echo "[loop] attempt $i verdict: ${GRADE}"
  case "$GRADE" in
    PASS*)
      printf '%s' "$BODY" > docs/README.draft.md
      { echo "## $(date +%Y-%m-%dT%H:%M:%S) README draft PASS (attempt $i/$MAX)"; echo "- staged: docs/README.draft.md — review, then commit"; } >> context_bridge/INBOX.md
      python3 bin/popw_ledger.py report >> context_bridge/POPW.report
      echo "[DONE] PASS at attempt $i — POPW report appended to context_bridge/POPW.report"
      exit 0;;
  esac
  sleep 2
done
{ echo "## $(date +%Y-%m-%dT%H:%M:%S) README loop exhausted $MAX attempts"; echo "- corpus: bin/readme_draft_loop.sh query \"terms\""; } >> context_bridge/INBOX.md
python3 bin/popw_ledger.py report >> context_bridge/POPW.report
exit 1
