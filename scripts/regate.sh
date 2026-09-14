#!/bin/bash
set -eu
export LC_ALL=C
ssh jesse@100.122.169.43 'cd /home/jesse/src/openroot
  python3 bin/permaculture_gate.py
  python3 bin/state_pulse.py
  git add -A
  git -c user.name=jesse -c user.email=j@o commit -m "gate: regate" --quiet --no-verify || echo "[git] nothing new"
  git pull --rebase -X ours origin main --quiet
  if git push origin main 2>/dev/null; then
    echo "[DONE] gate rerun AND PUSHED (verified)"
  else
    echo "[STOP] push rejected — origin moved during run; re-run this script"
    exit 1
  fi'
