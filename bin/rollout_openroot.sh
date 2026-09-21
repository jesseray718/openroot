#!/usr/bin/env bash
set -e

echo "[STEP 4/5] Registering rollout pathway resolution block into ledger..."
NEW_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "INIT_ROLLOUT")
MISTAKE_HASH="CONVERGED-BRANCH-OVERHAUL-$(date +%s)"

if [ -f bin/register_pathway.sh ]; then
    bin/register_pathway.sh \
        "$MISTAKE_HASH" \
        "$NEW_COMMIT" \
        "Automated repository branch consolidation and README overhaul" \
        "rollout_automation"
fi

echo "[STEP 5/5] Staging and committing rollout script..."
git add bin/rollout_openroot.sh data/pathways.json 2>/dev/null || true
git commit -m "[FEAT] Add rollout automation script and update pathway ledger" || true
git push origin main

echo "========================================"
echo " ✅ ROLLOUT COMPLETE & COMMITTED TO MAIN"
echo "========================================"
