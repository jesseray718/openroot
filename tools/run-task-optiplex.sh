#!/usr/bin/env bash
set -Eeuo pipefail

DB_PATH="${HOME}/.local/share/openroot/ledger.db"

if [ ! -f "TASK.md" ]; then
    echo "Error: TASK.md not found in $(pwd)" >&2
    exit 1
fi

python3 tools/task-loop.py init

TASK_ID="TASK-$(date +%Y%m%d-%H%M%S)"
BRANCH="ai/${TASK_ID}"
REPO="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || echo "openroot")")"
GOAL=$(grep -A 1 "## Goal" TASK.md | tail -n 1 | xargs)

python3 tools/task-loop.py record "$TASK_ID" "$REPO" "$BRANCH" "$GOAL"

git checkout -b "$BRANCH"

RECENT_CONTEXT=$(python3 tools/context_injector.py)
PROMPT_TEXT=$(cat TASK.md)
SYSTEM_PROMPT="You are an expert C++20 and Python developer.
Past System Context:
${RECENT_CONTEXT}

Task Description:
${PROMPT_TEXT}

Generate ONLY a valid unified diff git patch. No commentary."

PAYLOAD=$(jq -n --arg prompt "$SYSTEM_PROMPT" '{model: "qwen2.5-coder", prompt: $prompt, stream: false}')

echo "==> Querying Qwen 2.5 Coder on local Ollama..."
curl -s http://localhost:11434/api/generate -d "$PAYLOAD" \
  | jq -r .response \
  | sed '/^```/d' > /tmp/ai.patch

if git apply --check /tmp/ai.patch 2>/dev/null; then
    echo "==> Applying patch..."
    git apply /tmp/ai.patch
    python3 -m compileall -q . || true
    
    git add .
    git commit -m "feat: ${GOAL}"
    COMMIT_SHA=$(git rev-parse HEAD)
    
    git push origin "$BRANCH"
    PR_URL=$(gh pr create --title "feat: ${GOAL}" --body "Automated task ${TASK_ID} via Qwen 2.5 Coder." --fill)
    PR_NUM=$(echo "$PR_URL" | awk -F'/' '{print $NF}')
    
    python3 tools/task-loop.py update "$TASK_ID" "committed" "$COMMIT_SHA" "$PR_NUM"
    python3 enable_vector_embeddings.py --db "$DB_PATH" --model nomic-embed-text
    echo "==> Success! PR #${PR_NUM} created and vectorized."
else
    echo "==> Error: Patch check failed." >&2
    python3 tools/task-loop.py update "$TASK_ID" "rejected"
    exit 1
fi
