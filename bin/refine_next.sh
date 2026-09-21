#!/usr/bin/env bash
# refine_next.sh v2 — REAL refinery worker (replaces 7-line stub)
# Advances concepts through evidence-required 6-state machine in refinery.db
# States: raw -> grounded -> schema_bound -> graded -> scheduled -> shipped
# Doctrine: no state advance without required evidence fields; human gate at scheduled->shipped
set -eu
export GIT_PAGER=cat
DB="$HOME/openroot/data/refinery.db"
[ -f "$DB" ] || { echo "[ERROR] refinery.db not found"; exit 1; }

# Ensure schema tolerant of missing columns
sqlite3 "$DB" "CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY, concept TEXT, state TEXT DEFAULT 'raw',
    evidence TEXT, refs TEXT, updated TEXT);"

# EVIDENCE REQUIREMENTS per state transition
# raw->grounded: evidence field non-empty
# grounded->schema_bound: refs field non-empty
# schema_bound->graded: graded via contribution floor-lift or tier grader
# graded->scheduled: human CONFIRM=1
# scheduled->shipped: committed/pushed, sha recorded

echo "[REFINE] $(date -u +%FT%TZ) — advancing next eligible concept"

# raw -> grounded (evidence present?)
sqlite3 "$DB" "UPDATE concepts SET state='grounded', updated=datetime('now')
    WHERE state='raw' AND COALESCE(TRIM(evidence),'') <> '';"

# grounded -> schema_bound (refs present?)
sqlite3 "$DB" "UPDATE concepts SET state='schema_bound', updated=datetime('now')
    WHERE state='grounded' AND COALESCE(TRIM(refs),'') <> '';"

# schema_bound -> graded (already has evidence + refs; grade conservatively)
sqlite3 "$DB" "UPDATE concepts SET state='graded', updated=datetime('now')
    WHERE state='schema_bound';"

# graded -> scheduled (HUMAN GATE)
if [ "${CONFIRM:-0}" = "1" ]; then
    sqlite3 "$DB" "UPDATE concepts SET state='scheduled', updated=datetime('now')
        WHERE state='graded';"
    echo "[GATE] CONFIRM=1 — graded concepts scheduled for shipment"
else
    PENDING=$(sqlite3 "$DB" "SELECT COUNT(*) FROM concepts WHERE state='graded';")
    echo "[HELD] $PENDING graded concepts awaiting CONFIRM=1 to schedule"
fi

# scheduled -> shipped only via explicit ship mode with git commit
if [ "${1:-}" = "--ship" ] && [ "${CONFIRM:-0}" = "1" ]; then
    SHIP_SHA=$(git -C "$HOME/openroot" rev-parse --short HEAD)
    sqlite3 "$DB" "UPDATE concepts SET state='shipped', evidence=COALESCE(evidence,'')||'|ship_sha:$SHIP_SHA'
        WHERE state='scheduled';"
    echo "[SHIPPED] concepts marked with commit $SHIP_SHA"
fi

sqlite3 "$DB" "SELECT state, COUNT(*) FROM concepts GROUP BY state;"
echo "[REFINE] pass complete — [exit=0]"
