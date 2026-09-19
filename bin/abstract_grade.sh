#!/usr/bin/env bash
set -eu
export OLLAMA_HOST=http://localhost:11434
FILE="${1:?usage: abstract_grade.sh <manuscript.md>}"
ABSTRACT=$(sed -n '/^## Abstract/,/^## 1\./p' "$FILE" | tail -n +2 | head -20)
printf '%s\n' "$ABSTRACT" | timeout 90 ollama run qwen2.5:3b \
"Grade this research abstract against rubric. Output exactly 2 lines: 'VERDICT: PASS|FAIL' and 'FIRST_FIX: <one concrete improvement>'. Rubric: names a measurable quantity, names an instrument, states an uncertainty or says pending, avoids superlatives, is falsifiable." 2>/dev/null \
|| echo "VERDICT: UNAVAILABLE (3B offline)"
