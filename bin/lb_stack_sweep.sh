#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
"""lb_stack_sweep.sh — invoke stack_gate.sh with the arg it requires.

Doctrine: 'Stack_gate.sh every script pre-run' (boot seed). lb_loop invoked
stack_gate bare, causing halt a9144496750a70e6 (Usage: stack_gate.sh <script>).
This wrapper supplies the missing operand: every script in bin/ gets gated.
Real file (not bash -c) so lb_loop's stage cache hashes an actual script body.
"""
set -eu
cd "$(dirname "$0")/.."
RC=0
COUNT=0
for f in bin/*.sh bin/*.py; do
  [ -e "$f" ] || continue
  COUNT=$((COUNT+1))
  if bash bin/stack_gate.sh "$f"; then
    echo "[SWEEP-PASS] $f"
  else
    echo "[SWEEP-FAIL] $f"
    RC=1
  fi
done
echo "[SWEEP] gated ${COUNT} scripts, rc=${RC}"
exit $RC
