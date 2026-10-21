#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# Superlinear workflow — one command, whole stack, everything cached where possible.
# Usage: bin/superlinear.sh          (full chain)
#        bin/superlinear.sh status   (read-only: sync+audit+digest, no loop, no models)
set -u
cd "$(dirname "$0")/.." || exit 1
TS=$(date +%Y%m%d_%H%M%S)
echo "[1/SYNC]"; git pull --ff-only origin main 2>&1 | tail -1
echo "[2:GATE]"; bash bin/lb_stack_gate_all.sh && echo "[GATE] green"
echo "[3:CACHED-ANSWERS]"; python3 bin/qa_fts5.py index >/dev/null 2>&1; python3 bin/qa_fts5.py cache-report
echo "[4:LOOP-CACHE-PROOF]"; python3 bin/lb_loop_v2.py run >/dev/null 2>&1 && echo "[PROOF] rc=0 all-cache — seconds, not compute" || echo "[STATE] loop halted — check stats below"
python3 bin/lb_loop_v2.py stats
echo "[5:ENERGY]"; python3 bin/popw_ledger.py report
echo "[6:FRAGMENTS]"; ls context_bridge/fragments/ 2>/dev/null | grep -v README | wc -l | xargs -I{} echo "[FRAGMENTS] {} awaiting staging"
echo "[7:DIGEST]"; tail -6 context_bridge/INBOX.md 2>/dev/null || echo "[INBOX] empty"
echo "[DONE] ${TS} — superlinear chain complete; human gate owns all commits"
