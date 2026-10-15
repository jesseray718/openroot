#!/usr/bin/env bash
set -Eeuo pipefail

TASK_FILE="${1:?Usage: run_task.sh TASK.md}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="/home/jesse/openloom-build/runs/${RUN_ID}"
mkdir -p "$RUN_DIR"

cp "$TASK_FILE" "$RUN_DIR/task.md"

ollama run openroot-coder:latest "$(cat "$TASK_FILE")" \
  > "$RUN_DIR/output.md" 2> "$RUN_DIR/stderr.log"

{
  echo "task_file=$TASK_FILE"
  echo "run_id=$RUN_ID"
  echo "model=openroot-coder:latest"
  echo "output=$RUN_DIR/output.md"
  echo "status=complete"
} > "$RUN_DIR/receipt.txt"

cat "$RUN_DIR/receipt.txt"
