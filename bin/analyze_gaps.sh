#!/usr/bin/env bash
set -eu
cd /home/jesse/openroot
QUERY="Compare the high-level goals in the founding documents with the current scripts in bin/. What are the top 3 most critical technical modules missing to make the system fully autonomous and verifiable? Provide a concrete 'Gap Matrix' including: Missing Module, Purpose, and the theoretical physics or logic it must satisfy."
PODS="global_brain"

echo "[gate] Analyzing technical gaps via Recursive Loop..."
python3 bin/recursive_dossier_v1.py \
    --question "$QUERY" \
    --pods $PODS \
    --model "openai/gpt-4o-mini" \
    --max-iterations 3 \
    --output "/tmp/gap_analysis.json"

echo "[banked] Gap Analysis complete. Result in /tmp/gap_analysis.json"
cat /tmp/gap_analysis.json | python3 -m json.tool
