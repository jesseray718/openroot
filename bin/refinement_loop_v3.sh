#!/usr/bin/env bash
set -eu
export OLLAMA_HOST=http://localhost:11434
cd /home/jesse/openroot

DOC="${1:?usage: refinement_loop_v3.sh <doc_ref> '<rubric>' [max_attempts]}"
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

GRADER FIX REQUIRED: ${FIX:-none}"
  elif [ -f "data/${DOC}.txt" ]; then
    CONTEXT=$(head -c 4000 "data/${DOC}.txt")
  else
    CONTEXT="(no prior context)"
  fi

  CONTENT=$(printf '%s\n' "$CONTEXT" | timeout 180 ollama run qwen2.5-coder:7b "Task: $RUBRIC. Rewrite to satisfy this exactly. Address FIX points if present. Output ONLY the document, no headers/footers/commentary." 2>/dev/null) || CONTENT="CODER_OFFLINE"
  [ "$CONTENT" = "CODER_OFFLINE" ] || [ -z "$CONTENT" ] && { echo "[held] 7B offline"; exit 1; }

  ATTEMPT_PATH="data/${DOC}_attempt${ATTEMPT}.txt"
  printf '%s\n' "$CONTENT" > "$ATTEMPT_PATH"

  GRADE=$(timeout 90 ollama run qwen2.5:3b "You are an automated grader. Document: ---$CONTENT---. Rubric: $RUBRIC. OUTPUT FORMAT IS MANDATORY. Two lines only. Line1: VERDICT: PASS or Line1: VERDICT: FAIL. Line2: FIX: NONE if PASS, or FIX: one sentence concrete improvement if FAIL. No other words." 2>/dev/null) || GRADE="VERDICT: FAIL
FIX: grader offline"

  printf '[grade] %s\n' "$(echo "$GRADE" | tr '\n' ' ')"

  BEST="$CONTENT"

  if echo "$GRADE" | grep -q "^VERDICT: PASS"; then
    ACCEPTED=1
    sqlite3 data/refinement.db "INSERT INTO iterations (doc_ref, attempt, attempt_path, grade, accepted) VALUES ('$DOC', $ATTEMPT, '$ATTEMPT_PATH', '$(echo "$GRADE" | tr "'" '"')', 1)"
    cp "$ATTEMPT_PATH" "docs/${DOC}.md"
    printf '[banked] docs/%s.md after %s attempt(s)\n' "$DOC" "$ATTEMPT"
    break
  else
    FIX=$(echo "$GRADE" | grep "^FIX:" | sed 's/^FIX: *//' | grep -v "^NONE$" | head -1 || true)
    [ -z "$FIX" ] && FIX="tighten accuracy against rubric"
    printf '[fix] %s\n' "${FIX:0:100}"
    sqlite3 data/refinement.db "INSERT INTO iterations (doc_ref, attempt, attempt_path, grade) VALUES ('$DOC', $ATTEMPT, '$ATTEMPT_PATH', '$(echo "$GRADE" | tr "'" '"')')"
  fi
done

if [ "$ACCEPTED" -eq 0 ]; then
  sqlite3 data/lessons.db "INSERT INTO lessons (domain,mistake,root_cause,correction,cost,source) VALUES ('refinement_loop','max attempts without pass on $DOC','grader format drift or rubric too strict','use stricter output-format constraint in grader prompt, relax rubric or increase MAX','$MAX attempts','session');"
  printf '[held] %s attempts, no pass - latest: data/%s_attempt%s.txt\n' "$MAX" "$DOC" "$ATTEMPT"
  exit 1
fi
# [exit=0]
