#!/usr/bin/env bash
# refinement_loop_v2: sqlite seeds context, 7B drafts, 3B grades, FIX feeds forward
set -eu
export OLLAMA_HOST=http://localhost:11434
cd /home/jesse/openroot

DOC="${1:?usage: refinement_loop_v2.sh <doc_ref> '<rubric>' [max_attempts]}"
RUBRIC="${2:?rubric required}"
MAX="${3:-5}"

sqlite3 data/refinement.db "CREATE TABLE IF NOT EXISTS iterations (id INTEGER PRIMARY KEY AUTOINCREMENT, doc_ref TEXT, attempt INTEGER, attempt_path TEXT, grade TEXT, accepted INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"

BEST=""
FIX=""
ACCEPTED=0
ATTEMPT=0

while [ "$ATTEMPT" -lt "$MAX" ] && [ "$ACCEPTED" -eq 0 ]; do
  ATTEMPT=$((ATTEMPT + 1))
  printf '[attempt] %s/%s\n' "$ATTEMPT" "$MAX"

  if [ -n "$BEST" ]; then
    CONTEXT="$BEST

GRADER FIX REQUIRED: ${FIX:-improve overall quality}"
  elif [ -f "data/${DOC}.txt" ]; then
    CONTEXT=$(head -c 4000 "data/${DOC}.txt")
  else
    CONTEXT="(no prior context - draft from scratch)"
  fi

  CONTENT=$(printf '%s\n' "$CONTEXT" | timeout 180 ollama run qwen2.5-coder:7b "Task: $RUBRIC. Rewrite the document below to satisfy the task exactly. Address every GRADER FIX REQUIRED point if present. Output only the finished document, no commentary." 2>/dev/null) || CONTENT="CODER_OFFLINE"
  if [ "$CONTENT" = "CODER_OFFLINE" ] || [ -z "$CONTENT" ]; then
    echo "[held] 7B offline or empty - check: ollama list"
    exit 1
  fi

  ATTEMPT_PATH="data/${DOC}_attempt${ATTEMPT}.txt"
  printf '%s\n' "$CONTENT" > "$ATTEMPT_PATH"

  GRADE=$(printf '%s\n' "$CONTENT" | timeout 90 ollama run qwen2.5:3b "Grade this document against the rubric: $RUBRIC. Output exactly 2 lines, first: VERDICT: PASS or FAIL, second: FIX: <one concrete improvement, write NONE if PASS>" 2>/dev/null) || GRADE="VERDICT: FAIL
FIX: grader offline"

  printf '[grade] %s\n' "$(printf '%s' "$GRADE" | tr '\n' ' ')"

  SAFE_GRADE=$(printf '%s' "$GRADE" | tr -d "'\"" | tr '\n' ' ')
  sqlite3 data/refinement.db "INSERT INTO iterations (doc_ref, attempt, attempt_path, grade) VALUES ('$DOC', $ATTEMPT, '$ATTEMPT_PATH', '$SAFE_GRADE')"

  BEST="$CONTENT"

  if printf '%s' "$GRADE" | grep -q "VERDICT: PASS"; then
    ACCEPTED=1
    sqlite3 data/refinement.db "UPDATE iterations SET accepted=1 WHERE doc_ref='$DOC' AND attempt=$ATTEMPT"
    cp "$ATTEMPT_PATH" "docs/${DOC}.md"
    printf '[banked] docs/%s.md after %s attempt(s)\n' "$DOC" "$ATTEMPT"
  else
    FIX=$(printf '%s\n' "$GRADE" | grep '^FIX:' | sed 's/^FIX: *//' | grep -v '^NONE$' || true)
    [ -z "$FIX" ] && FIX="tighten accuracy and completeness against the rubric"
    printf '[fix] feeding forward: %s\n' "${FIX:0:120}"
  fi
done

if [ "$ACCEPTED" -eq 0 ]; then
  sqlite3 data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source) VALUES ('refinement_loop','max attempts reached without pass on $DOC','rubric too strict, grader drift, or 7B capability ceiling','relax rubric, increase max_attempts, or switch doc to manual drafting','$MAX attempts','session');"
  printf '[held] %s attempts, no pass - latest draft at data/%s_attempt%s.txt, full history in data/refinement.db\n' "$MAX" "$DOC" "$ATTEMPT"
  exit 1
fi
# [exit=0]
