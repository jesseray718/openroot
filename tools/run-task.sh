#!/usr/bin/env bash
set -Eeuo pipefail

if [ ! -f "TASK.md" ]; then
    echo "Error: TASK.md not found in $(pwd)" >&2
    exit 1
fi

TASK_ID="TASK-$(date +%Y%m%d-%H%M%S)"
BRANCH="ai/${TASK_ID}"
REPO="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || echo "openroot")")"
GOAL=$(grep -A 1 "## Goal" TASK.md | tail -n 1 | xargs)

mkdir -p tools
python3 tools/task-loop.py record "$TASK_ID" "$REPO" "$BRANCH" "$GOAL"

git checkout -b "$BRANCH"

PROMPT_TEXT=$(cat TASK.md)
PAYLOAD=$(jq -n --arg prompt "Generate ONLY a valid unified diff git patch for the following task:\n$PROMPT_TEXT" '{model: "qwen2.5-coder", prompt: $prompt, stream: false}')

# Clean markdown code blocks from model response
curl -s http://localhost:11434/api/generate -d "$PAYLOAD" \
  | jq -r .response \
  | sed '/^```/d' > /tmp/ai.patch

if git apply --check /tmp/ai.patch 2>/dev/null; then
    echo "==> Applying patch..."
    git apply /tmp/ai.patch
    python3 -m compileall -q .
    
    git add .
    git commit -m "feat: ${GOAL}"
    COMMIT_SHA=$(git rev-parse HEAD)
    
    git push origin "$BRANCH"
    PR_URL=$(gh pr create --title "feat: ${GOAL}" --body "Automated task ${TASK_ID} via Qwen 2.5 Coder." --fill)
    PR_NUM=$(echo "$PR_URL" | awk -F'/' '{print $NF}')
    
    python3 tools/task-loop.py update "$TASK_ID" "committed" "$COMMIT_SHA" "$PR_NUM"
    echo "==> Success! PR #${PR_NUM} created."
else
    echo "==> Error: Generated patch failed validation check." >&2
    python3 tools/task-loop.py update "$TASK_ID" "rejected"
    exit 1
fi
