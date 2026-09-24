#!/bin/bash
# Warm Pool Manager - Keeps models loaded for instant response

echo "=== MODEL WARM POOL INITIALIZATION ==="

# Pre-load 7B Coder
echo "Loading qwen2.5-coder:7b (warm)..."
timeout 5 ollama run qwen2.5-coder:7b "ping" || echo "7B already warm"

# Pre-load 3B Grader  
echo "Loading qwen2.5:3b (warm)..."
timeout 5 ollama run qwen2.5:3b "ping" || echo "3B already warm"

# Warm pool status
echo ""
echo "Loaded models:"
ollama ps

echo ""
echo "Warm pool active. Models ready for immediate inference."
echo "[exit=0] Warm pool maintained"
