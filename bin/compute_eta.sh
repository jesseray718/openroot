#!/usr/bin/env bash
set -eu
cd /home/${OPENROOT_USER}/openroot
RECEIPT="/tmp/high_eta_receipt.json"
[ ! -f "$RECEIPT" ] && RECEIPT="/tmp/gap_analysis.json"

TOTAL_TOKENS=$(python3 -c "import json; r=json.load(open('$RECEIPT')); print(r.get('total_tokens', 0))")
LATENCY_S=$(python3 -c "import json; r=json.load(open('$RECEIPT')); print(sum(it.get('latency_ms',0) for it in r.get('iterations', [])) / 1000)")
CLOUD_COST=$(python3 -c "print($TOTAL_TOKENS * 0.0000003)")

python3 bin/coefficient_v1.py --quality 0.8 --value 10.0 --cost $CLOUD_COST --latency $LATENCY_S
