#!/usr/bin/env bash
set -Eeuo pipefail

echo "[canary] paste intact"

KEEP="qwen2.5-coder:7b qwen2.5:3b nomic-embed-text:latest openroot-coder:latest openroot-assistant:latest"

echo "[stage-1] Current models and disk usage:"
ollama list

echo ""
echo "[stage-2] Marking deletions (dry run):"
DELETE_LIST=""
while read -r MODEL; do
    KEEP_FLAG=0
    for K in $KEEP; do
        [ "$MODEL" = "$K" ] && KEEP_FLAG=1
    done
    if [ "$KEEP_FLAG" -eq 0 ]; then
        DELETE_LIST="$DELETE_LIST $MODEL"
        echo "  [prune] $MODEL"
    else
        echo "  [keep] $MODEL"
    fi
done < <(ollama list | tail -n +2 | awk '{print $1}')

if [ -z "${DELETE_LIST// /}" ]; then
    echo "[exit=0] Nothing to prune."
    exit 0
fi

if [ "${CONFIRM:-0}" != "1" ]; then
    echo ""
    echo "[held] Dry run only. Re-run with CONFIRM=1 to delete:$DELETE_LIST"
    echo "[held] Estimated disk freed: run 'ollama list' sizes above"
    exit 0
fi

echo "[stage-3] Deleting:$DELETE_LIST"
for MODEL in $DELETE_LIST; do
    ollama rm "$MODEL" && echo "  [deleted] $MODEL"
done

echo "[stage-4] Final state:"
ollama list
echo "[exit=0] Prune complete"
