#!/data/data/com.termux/files/usr/bin/bash
# OpenRoot Universal Logger
# Tracks every command, captures outcomes as JSON lessons

CONTEXT="/sdcard/openroot/context_bridge/context.json"
LOG_FILE="/sdcard/openroot/output/command_log.jsonl"
mkdir -p /sdcard/openroot/output

# Arguments: logger.sh "command that was run" "exit_code" "stdout snippet" "stderr snippet"
CMD="$1"
EXIT_CODE="$2"
STDOUT_SNIPPET="$3"
STDERR_SNIPPET="$4"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Determine severity
SEVERITY="info"
if [ "$EXIT_CODE" != "0" ]; then
  SEVERITY="warning"
  if echo "$STDERR_SNIPPET" | grep -qiE "denied|cannot|no such|not found|crash"; then
    SEVERITY="critical"
  fi
fi

# Determine category
CATEGORY="general"
if echo "$CMD" | grep -qiE "git|commit|push"; then CATEGORY="git"; fi
if echo "$CMD" | grep -qiE "ollama|llama|model"; then CATEGORY="ai"; fi
if echo "$CMD" | grep -qiE "df|du|rm|clean|storage"; then CATEGORY="storage"; fi
if echo "$CMD" | grep -qiE "jq|context|lesson"; then CATEGORY="context"; fi
if echo "$CMD" | grep -qiE "solana|bitcoin|ots|anchor"; then CATEGORY="blockchain"; fi
if echo "$CMD" | grep -qiE "sensor|battery|cpu|freq|energy"; then CATEGORY="energy"; fi

# Write to JSONL command log (always)
jq -nc \
  --arg ts "$TS" \
  --arg cmd "$CMD" \
  --arg ec "$EXIT_CODE" \
  --arg out "$STDOUT_SNIPPET" \
  --arg err "$STDERR_SNIPPET" \
  --arg sev "$SEVERITY" \
  --arg cat "$CATEGORY" \
  '{timestamp: $ts, command: $cmd, exit_code: ($ec | tonumber), severity: $sev, category: $cat, stdout: $out[:200], stderr: $err[:200]}' \
  >> "$LOG_FILE"

# Only append lesson for discoveries/failures (not every trivial command)
if [ "$SEVERITY" != "info" ] || echo "$STDOUT_SNIPPET" | grep -qiE "installed|created|confirmed|error|warning|recovered|freed|failed"; then
  LESSON_NUM=$(jq '.lessons | length' "$CONTEXT")
  LESSON_NUM=$((LESSON_NUM + 1))
  LESSON_ID=$(printf "L%03d" "$LESSON_NUM")

  TMPFILE="$PREFIX/tmp/ctx.tmp"
  jq \
    --arg id "$LESSON_ID" \
    --arg ts "$TS" \
    --arg cmd "$CMD" \
    --arg ec "$EXIT_CODE" \
    --arg err "$STDERR_SNIPPET" \
    --arg sev "$SEVERITY" \
    --arg cat "$CATEGORY" \
    '.lessons += [{
      "id": $id,
      "timestamp": $ts,
      "title": ($cmd[:80]),
      "body": ("Exit " + $ec + ": " + ($err[:150])),
      "category": $cat,
      "severity": $sev
    }]' \
    "$CONTEXT" > "$TMPFILE" && mv "$TMPFILE" "$CONTEXT"
fi

# Update last_modified timestamp
TMPFILE="$PREFIX/tmp/ctx.tmp"
jq --arg ts "$TS" '.last_modified = $ts' "$CONTEXT" > "$TMPFILE" && mv "$TMPFILE" "$CONTEXT"
