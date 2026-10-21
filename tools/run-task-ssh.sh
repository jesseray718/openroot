#!/usr/bin/env bash
set -Eeuo pipefail

# Host details for your OptiPlex
OPTIPLEX_HOST="user@optiplex.local"
OPTIPLEX_REPO_PATH="~/openroot"

if [ ! -f "TASK.md" ]; then
    echo "Error: TASK.md file not found in current directory." >&2
    exit 1
fi

TASK_ID="TASK-$(date +%Y%m%d-%H%M%S)"
BRANCH="ai/${TASK_ID}"
REPO="$(basename "$(git rev-parse --show-toplevel)")"
GOAL=$(grep -A 1 "## Goal" TASK.md | tail -n 1 | xargs)

echo "==> Registering task $TASK_ID in local SQLite ledger..."
python3 tools/task-loop.py record "$TASK_ID" "$REPO" "$BRANCH" "$GOAL"

echo "==> Sending TASK.md to OptiPlex over SSH..."
scp TASK.md "${OPTIPLEX_HOST}:${OPTIPLEX_REPO_PATH}/TASK.md"

echo "==> Executing build and model patch loop on OptiPlex..."
ssh -t "${OPTIPLEX_HOST}" bash -s << REMOTE_EOF
  set -Eeuo pipefail
  cd "${OPTIPLEX_REPO_PATH}"

  git checkout -b "${BRANCH}"

  # Query OptiPlex local Qwen model via Ollama/llama-server
  PROMPT_TEXT=\$(cat TASK.md)
  PAYLOAD=\$(jq -n --arg prompt "\$PROMPT_TEXT" '{model: "qwen2.5-coder", prompt: \$prompt, stream: false}')
  
  curl -s http://localhost:11434/api/generate -d "\$PAYLOAD" | jq -r .response > /tmp/ai.patch

  if git apply --check /tmp/ai.patch 2>/dev/null; then
      git apply /tmp/ai.patch
      python3 -m compileall -q .
      git diff --check
      
      git add .
      git commit -m "feat: ${GOAL}"
      
      # Push branch to GitHub using OptiPlex gh cli
      git push origin "${BRANCH}"
      gh pr create --title "feat: ${GOAL}" --body "Automated SSH patch for ${TASK_ID} via Qwen." --fill
  else
      echo "Patch validation failed on OptiPlex." >&2
      exit 1
  fi
REMOTE_EOF

if [ $? -eq 0 ]; then
    echo "==> Task ${TASK_ID} successfully executed on OptiPlex and PR created!"
    python3 tools/task-loop.py update "$TASK_ID" "committed"
else
    echo "==> Remote execution failed." >&2
    python3 tools/task-loop.py update "$TASK_ID" "rejected"
    exit 1
fi
