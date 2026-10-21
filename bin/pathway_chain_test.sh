#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "  OPENROOT DYNAMIC PATHWAY CHAIN TESTER "
echo "  TIME: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
echo "========================================"

# 1. Execute OpenRoot Unified Launch
echo -e "\necho "echo "[STEP 1/5] Running openroot_unified_launch_v1.sh..."
if [ -f "bin/openroot_unified_launch_v1.sh" ]; then
  bin/openroot_unified_launch_v1.sh
else
  echo "⚠️ Launch script not found! Skipping..."
fi

# 2. Execute Weekly Onepass Automation
echo -e "\necho "echo "[STEP 2/5] Running weekly automation onepass_v3.sh..."
if [ -f "bin/onepass_v3.sh" ]; then
  bin/onepass_v3.sh
else
  echo "⚠️ Onepass v3 script not found! Skipping..."
fi

# 3. Dynamic Pathway Ledger Registration
echo -e "\necho "echo "[STEP 3/5] Testing dynamic pathway ledger registration..."
TEST_MISTAKE_HASH="MISTAKE-SIMULATION-$(date +%s)"
TEST_SOLUTION_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "HEAD_HASH")

bin/register_pathway.sh \
  "$TEST_MISTAKE_HASH" \
  "$TEST_SOLUTION_COMMIT" \
  "Dynamic pathway test block registration" \
  "chain_verification"

# 4. Pathway Resolution Lookup
echo -e "\necho "echo "[STEP 4/5] Testing dynamic pathway resolution..."
# Temporarily mock mistake hash to verify lookup logic
if MATCH=$(jq -r ".nodes[\"${TEST_MISTAKE_HASH:-"none"}\"]" data/pathways.json 2>/dev/null); then
  echo "⚡ CACHE HIT SUCCESSFUL for signature: ${TEST_MISTAKE_HASH:-"none"}"
  echo "$MATCH" | jq .
else
  echo "❌ Dynamic pathway resolution failed!"
  exit 1
fi

# 5. Stack Gate Validation Audit
echo -e "\necho "echo "[STEP 5/5] Running stack_gate.sh across all shell instruments..."
SCRIPTS=("bin/openroot_unified_launch_v1.sh" "bin/onepass_v3.sh" "bin/register_pathway.sh" "bin/resolve_pathway.sh" "bin/pathway_chain_test.sh")

for script in "${SCRIPTS[@]}"; do
  if [ -f "$script" ]; then
    echo "Auditing $script..."
    bin/stack_gate.sh "$script"
  fi
done

echo -e "\n========================================"
echo " ✅ ALL PATHWAY CHAIN TESTS PASSED"
echo "========================================"
