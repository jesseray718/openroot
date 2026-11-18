#!/bin/bash
# qa_router.sh - front-end to the universal index Q&A system
# Usage: ./qa_router.sh <template_id> <arg1>=<val1> ...
set -eu
DB="/home/jesse/openroot/data/universal_index/universal_index_1794376789.db"
TEMPLATE="$1"; shift || { echo "Usage: $0 <template_id> [args]"; exit 1; }
echo "[router] loading template $TEMPLATE from $DB"
PROMPT=$(sqlite3 "$DB" "SELECT template_prompt FROM qa_templates WHERE template_id='$TEMPLATE'")
MODEL=$(sqlite3 "$DB" "SELECT default_model FROM content_classes LIMIT 1")
echo "[invoke] $MODEL with template=$TEMPLATE"
echo "[placeholder] ollama run $MODEL '$PROMPT' args: $@"
