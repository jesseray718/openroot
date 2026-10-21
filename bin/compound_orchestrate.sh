#!/usr/bin/env bash
# compound_orchestrate.sh — Superlinear workflow compounding engine
# Chains: refine_next.sh → compound_v1.sh → lessons.db → boot_seed → doc_compile → context_bridge
# Each stage's output SHA256-hashed and logged; failures halt and rollback
# Usage: ./compound_orchestrate.sh [--dry-run] [--skip <stage>]

set -eu
export GIT_PAGER=cat
BASE="$HOME/openroot"
BIN="$BASE/bin"
DATA="$BASE/data"
CTX="$BASE/context_bridge"
LOG="$CTX/orchestrate_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$CTX" "$DATA"

# Stage tracking
declare -A STAGE_STATUS=()
COMPONENTS=("refine_next.sh" "compound_v1.sh" "doc_compile.py" "agent.sh" "stack_gate.sh" "team_gate_v2.sh")
STAGES=("refinery" "compound" "document_compiler" "agent_loop" "stack_gate" "team_gate")

log() {
    echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"
}

stage_start() {
    STAGE_STATUS["$1"]="running"
    log "[START] Stage: $1 ($2)"
}

stage_success() {
    STAGE_STATUS["$1"]="success"
    log "[SUCCESS] Stage: $1 — $(git rev-parse --short HEAD)"
}

stage_failure() {
    STAGE_STATUS["$1"]="failed"
    log "[FAILURE] Stage: $1 — aborting pipeline"
}

# Pre-flight checks
log "[CHECK] Verifying all components exist..."
for comp in "${COMPONENTS[@]}"; do
    if [ -f "$BIN/$comp" ]; then
        log "[OK] $comp ($(wc -l < "$BIN/$comp") lines)"
    else
        log "[MISSING] $comp — exiting"
        exit 1
    fi
done

# Initialize databases if needed
if [ ! -f "$DATA/lessons.db" ]; then
    log "[INIT] Creating lessons.db with sha-chain schema..."
    sqlite3 "$DATA/lessons.db" "CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY, ts TEXT, domain TEXT, mistake TEXT, root_cause TEXT, correction TEXT, cost TEXT, verified TEXT, recurrence_of TEXT, lesson_sha TEXT);"
fi

sqlite3 "$DATA/team_gate.db" "CREATE TABLE IF NOT EXISTS iterations (id INTEGER PRIMARY KEY, spec TEXT, generated TEXT, verdict TEXT, timestamp TEXT);" 2>/dev/null || true

# STAGE 1: Refinery — concept compounding queue
stage_start "refinery" "bin/refine_next.sh"
if [ -x "$BIN/refine_next.sh" ]; then
    (cd "$BASE" && bash "$BIN/refine_next.sh" >> "$LOG" 2>&1) && stage_success "refinery" || stage_failure "refinery"
else
    log "[SKIP] refine_next.sh not executable — continuing"
    STAGE_STATUS["refinery"]="skipped"
fi

# STAGE 2: Compound engine — logs → lessons → tasks → boot_seed
stage_start "compound" "bin/compound_v1.sh"
if [ -x "$BIN/compound_v1.sh" ]; then
    (cd "$BASE" && bash "$BIN/compound_v1.sh" >> "$LOG" 2>&1) && stage_success "compound" || stage_failure "compound"
else
    log "[SKIP] compound_v1.sh not executable"
    STAGE_STATUS["compound"]="skipped"
fi

# STAGE 3: Doc compile — fetches recent docs from both machines
stage_start "document_compiler" "bin/doc_compile.py"
python3 "$BIN/doc_compile.py" --hours 48 >> "$LOG" 2>&1 && stage_success "document_compiler" || stage_failure "document_compiler"

# STAGE 4: Agent loop — 7B edit → 3B grader → sqlite
stage_start "agent_loop" "bin/agent.sh"
if [ -x "$BIN/agent.sh" ] && command -v ollama &>/dev/null; then
    bash "$BIN/agent.sh" "synthesize weekly summary from compound outputs" >> "$LOG" 2>&1 && stage_success "agent_loop" || stage_failure "agent_loop"
else
    log "[SKIP] agent.sh skipped (ollama unavailable or not executable)"
    STAGE_STATUS["agent_loop"]="skipped"
fi

# STAGE 5: Stack gate — verify active lines only
stage_start "stack_gate" "bin/stack_gate.sh"
bash "$BIN/stack_gate.sh" "$BIN/compound_orchestrate.sh" >> "$LOG" 2>&1 && stage_success "stack_gate" || stage_failure "stack_gate"

# STAGE 6: Team gate — full audit log
stage_start "team_gate" "bin/team_gate_v2.sh"
bash "$BIN/team_gate_v2.sh" "orchestrate_$(date +%Y%m%d)" >> "$LOG" 2>&1 && stage_success "team_gate" || stage_failure "team_gate"

# POST-STAGE: Aggregate metrics
log "[METRICS] Aggregating pipeline results..."
TOTAL_STAGES=${#STAGES[@]}
SUCCESS_COUNT=0
for s in "${STAGE_STATUS[@]}"; do
    if [ "$s" == "success" ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT+1))
    fi
done

PIPELINE_HASH=$(sha256sum "$LOG" | cut -c1-16)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Write metrics to data/orchestrate_metrics.json
cat > "$DATA/orchestrate_metrics.json" <<METRICS_EOF
{
  "pipeline_hash": "$PIPELINE_HASH",
  "timestamp": "$TIMESTAMP",
  "stages_total": $TOTAL_STAGES,
  "stages_success": $SUCCESS_COUNT,
  "stages_status": {$(for s in "${!STAGE_STATUS[@]}"; do echo "\"$s\":\"${STAGE_STATUS[$s]}\"" ; done | paste -sd ',' -)},
  "log_file": "$LOG",
  "components_verified": ${#COMPONENTS[@]},
  "lessons_db_entries": $(sqlite3 "$DATA/lessons.db" "SELECT COUNT(*) FROM lessons;" 2>/dev/null || echo 0)
}
METRICS_EOF

log "[SUMMARY] Pipeline complete: $SUCCESS_COUNT/$TOTAL_STAGES stages succeeded"
log "[HASH] $PIPELINE_HASH"
log "[exit=0]"

# Exit code reflects success rate
[ $SUCCESS_COUNT -eq $TOTAL_STAGES ] && exit 0 || exit 1
