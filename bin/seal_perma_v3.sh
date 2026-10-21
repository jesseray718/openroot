#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Seal v3: [PERMA-V3] commit — CONFIRM gated, human review first
set -euo pipefail
export GIT_PAGER=cat
cd /home/jesse/openroot

echo "[SEAL-V3] verdict distribution:"
sqlite3 data/log_feed.db "SELECT verdict, COUNT(*) FROM log_feed GROUP BY verdict;"
echo "[SEAL-V3] debate tail (spot-check 2 unanimous before confirming):"
tail -5 data/debate_ledger.jsonl

if [ "${CONFIRM:-0}" != "1" ]; then
  echo "[SEAL-V3] [held] dry-run"
  echo "[SEAL-V3] review above, then: CONFIRM=1 bash bin/seal_perma_v3.sh"
  exit 0
fi

git add bin/dispatch_court_v6.sh
git add bin/permaculture_orchestrator_v3.sh
git add bin/seal_perma_v3.sh
git add bin/mistake_engine_v1.py
git add deploy/systemd/
git add context_bridge/court-v6-report-*.md
git add context_bridge/permaculture-*.md
git add context_bridge/compost-*.md
git add context_bridge/mistake_solutions/*.md
git commit -m "[PERMA-V3] court v6 + perma orchestrator + compost engine + systemd CI timers"
git log --oneline -1
echo "[SEAL-V3] [banked] sealed - push_guard is yours"
echo "[SEAL-V3] [exit=0]"
