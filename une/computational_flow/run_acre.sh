#!/bin/bash
# Permanent η-native ACRE runner — minimal human joules
set -e
cd /home/jesse/openroot
QUERY="${1:-State the definition of η = useful_joules / human_joules and why it is the only allowed performance language in UNE.}"
python3 une/computational_flow/eta_lattice_acre.py "$QUERY" 2>&1 | tee tmp/acre_run_$(date +%Y%m%d-%H%M%S).log
echo
echo "===== LAST ACRE ====="
cat tmp/last_acre.json
echo
echo "===== LEDGER TAIL ====="
tail -n 2 seed-core/ledger/eta_ledger.jsonl
