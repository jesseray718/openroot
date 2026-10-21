#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# Gate every bin/*.sh pre-run (doctrine). Stub-held instruments are excluded from
# the pipeline, therefore also from gating — a stub cannot block verified instruments.
# Stub exclusion list: context_bridge/.gate_exclude (one basename per line).
# To consciously exempt a REAL script, add its basename there — human is the gate.
set -u
cd "$(dirname "$0")/.." || exit 1
EXCL=$(cat context_bridge/.gate_exclude 2>/dev/null || echo "refine_next.sh")
fails=0
for f in bin/*.sh; do
  base=$(basename "$f")
  skip=0
  while IFS= read -r e; do [ "$base" = "$e" ] && skip=1; done <<< "$EXCL"
  if [ "$skip" = "1" ]; then echo "[SKIP-STUB] $base (stub-held, not gated)"; continue; fi
  if ! bash bin/stack_gate.sh "$f" >/dev/null 2>&1; then
    echo "[GATE-FAIL] $f"; fails=$((fails+1))
  fi
done
[ "$fails" -eq 0 ] || { echo "[RESULT] ${fails} gate failures"; exit 1; }
echo "[RESULT] all gated bin/*.sh pass"
exit 0
