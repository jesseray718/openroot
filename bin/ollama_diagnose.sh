#!/usr/bin/env bash
set -Eeuo pipefail

echo "[canary] paste intact"
echo "=== OLLAMA CONNECTIVITY DIAGNOSTICS ==="

# Stage 1: Ollama process check
echo "[stage-1] Checking Ollama daemon..."
if pgrep -x ollama >/dev/null; then
    echo "[PASS] ollama process running"
else
    echo "[FAIL] ollama not running. Start with: ollama serve"
    exit 1
fi

# Stage 2: Health ping
echo "[stage-2] Ping /api/tags..."
TAGS_JSON=$(curl -sf http://localhost:11434/api/tags 2>/dev/null || echo '{}')
MODEL_COUNT=$(echo "$TAGS_JSON" | jq '.models | length' 2>/dev/null || echo "0")
echo "[INFO] Found $MODEL_COUNT models served"
echo "$TAGS_JSON" | jq -r '.models[].name' || echo "[WARN] Could not parse model names"

# Stage 3: Find the correct model tag
echo "[stage-3] Searching for qwen2.5-coder variant..."
CORRECT_TAG=$(echo "$TAGS_JSON" | jq -r '.models[].name' | grep -E 'qwen.*coder' | head -1 || true)
if [ -z "$CORRECT_TAG" ]; then
    echo "[FAIL] No qwen2.5-coder model found. Available:"
    echo "$TAGS_JSON" | jq -r '.models[].name'
    exit 2
fi
echo "[PASS] Correct model tag: $CORRECT_TAG"

# Stage 4: Test a minimal prompt
echo "[stage-4] Testing model response with minimal prompt..."
TEST_PAYLOAD=$(jq -n \
    --arg model "$CORRECT_TAG" \
    --arg prompt "Say hello" \
    '{model: $model, prompt: $prompt, stream: false}')

RESPONSE=$(curl -sf http://localhost:11434/api/generate -d "$TEST_PAYLOAD" 2>/dev/null || echo '{}')
RESPONSE_TEXT=$(echo "$RESPONSE" | jq -r '.response // "NO_RESPONSE"' 2>/dev/null || echo "PARSE_FAIL")
echo "[RESULT] Response: $RESPONSE_TEXT"

if [ "$RESPONSE_TEXT" = "NO_RESPONSE" ] || [ "$RESPONSE_TEXT" = "PARSE_FAIL" ]; then
    echo "[FAIL] Model returned empty or malformed response"
    echo "[DEBUG] Raw response: $RESPONSE"
    exit 3
fi

echo "[PASS] Model responds correctly"
echo "=== DIAGNOSTIC COMPLETE ==="
echo "Use this CORRECT_TAG in your scripts: $CORRECT_TAG"
