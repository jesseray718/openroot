#!/usr/bin/env bash
set -Eeuo pipefail

# [canary] paste intact
if [ ! -f "TASK.md" ]; then
    echo "Error: TASK.md not found in $(pwd)" >&2
    exit 1
fi

echo "==> Syncing TASK.md to OptiPlex..."
scp TASK.md jesse@optiplex:/home/jesse/openroot/TASK.md

echo "==> Running task loop on OptiPlex..."
ssh jesse@optiplex bash -s << 'REMOTE_EXEC'
set -Eeuo pipefail
cd /home/jesse/openroot

DB_PATH="${HOME}/.local/share/openroot/ledger.db"

# [gate-model] resolve tag dynamically - never hardcode
MODEL=$(curl -sf http://localhost:11434/api/tags | jq -r '.models[].name' | grep -E '^qwen2\.5-coder' | head -1 || true)
if [ -z "$MODEL" ]; then
    echo "[held] no qwen2.5-coder model served on localhost:11434" >&2
    exit 2
fi
echo "==> Using model: $MODEL"

GOAL=$(grep -A 1 '^## Goal' /home/jesse/openroot/TASK.md | tail -n 1 | xargs)
PROMPT_TEXT=$(cat /home/jesse/openroot/TASK.md)
RECENT_CONTEXT=$(python3 tools/context_injector.py 2>/dev/null || echo "")

SYS_PROMPT="You are an automated Git patch generation engine. Output ONLY a valid raw unified diff starting with diff --git on the first line. No markdown fences, no explanations, no chat text."

USER_PROMPT="Context:
${RECENT_CONTEXT}

Task Goal: ${GOAL}
Task Requirements:
${PROMPT_TEXT}"

PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --arg sys "$SYS_PROMPT" \
  --arg prompt "$USER_PROMPT" \
  '{
    model: $model,
    system: $sys,
    prompt: $prompt,
    stream: false,
    options: { temperature: 0.2 }
  }')

mkdir -p /home/jesse/openroot/data

echo "==> Requesting patch from ${MODEL}..."
HTTP_RAW=$(curl -s -w '\n%{http_code}' http://localhost:11434/api/generate -d "$PAYLOAD")
HTTP_CODE=$(echo "$HTTP_RAW" | tail -n 1)
BODY=$(echo "$HTTP_RAW" | sed '$d')
echo "$BODY" > /home/jesse/openroot/data/last_raw_response.txt

if [ "$HTTP_CODE" != "200" ]; then
    echo "[held] HTTP ${HTTP_CODE} from Ollama. Body saved to data/last_raw_response.txt" >&2
    exit 3
fi

RAW_OUT=$(echo "$BODY" | jq -r '.response // ""')
if [ -z "$RAW_OUT" ] || [ "$RAW_OUT" = "null" ]; then
    echo "[rejected] empty .response field. Raw body in data/last_raw_response.txt" >&2
    exit 4
fi

echo "$RAW_OUT" | python3 tools/clean_patch.py > /home/jesse/openroot/data/ai.patch
if [ ! -s /home/jesse/openroot/data/ai.patch ]; then
    echo "[rejected] patch extraction empty. Raw response in data/last_raw_response.txt" >&2
    exit 5
fi

# [gate-apply] validate BEFORE touching git - no orphan branches ever
if git apply --check /home/jesse/openroot/data/ai.patch; then
    TASK_ID="TASK-$(date +%Y%m%d-%H%M%S)"
    BRANCH="ai/${TASK_ID}"
    REPO="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || echo openroot)")"
    python3 tools/task-loop.py record "$TASK_ID" "$REPO" "$BRANCH" "$GOAL"
    git checkout -b "$BRANCH"
    git apply /home/jesse/openroot/data/ai.patch
    python3 -m compileall -q . || true
    git add .
    git commit -m "feat: ${GOAL}"
    COMMIT_SHA=$(git rev-parse HEAD)
    git push origin "$BRANCH"
    PR_URL=$(gh pr create --title "feat: ${GOAL}" --body "Automated task ${TASK_ID} via ${MODEL}.")
    PR_NUM=$(echo "$PR_URL" | awk -F'/' '{print $NF}')
    python3 tools/task-loop.py update "$TASK_ID" "committed" "$COMMIT_SHA" "$PR_NUM"
    echo "==> Success! PR #${PR_NUM} on branch ${BRANCH}"
else
    echo "[rejected] git apply dry-run failed. Patch in data/ai.patch" >&2
    exit 6
fi
REMOTE_EXEC
