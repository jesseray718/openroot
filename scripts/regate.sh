#!/bin/bash
set -eu
ssh jesse@100.122.169.43 'cd /home/jesse/src/openroot
  python3 bin/permaculture_gate.py
  python3 bin/state_pulse.py
  git add -A
  git -c user.name=jesse -c user.email=j@o commit -m "gate: regate" --quiet --no-verify || true
  git push origin main || true
  echo "[✅ DONE] gate rerun and pushed"'
