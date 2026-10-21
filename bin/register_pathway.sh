#!/usr/bin/env bash
set -euo pipefail

# Usage: bin/register_pathway.sh <MISTAKE_HASH|SPEC_ID> <SOLUTION_COMMIT|ARTIFACT_SHA> <DESCRIPTION> <CATEGORY>

MISTAKE_HASH="${1:-}"
SOLUTION_REF="${2:-}"
DESCRIPTION="${3:-}"
CATEGORY="${4:-hardware_spec}"

if [ -z "$MISTAKE_HASH" ] || [ -z "$SOLUTION_REF" ] || [ -z "$DESCRIPTION" ]; then
  echo "Usage: bin/register_pathway.sh <spec_hash|mistake_hash> <commit|patch|artifact_hash> <description> [category]"
  echo "Example: bin/register_pathway.sh \"M-AEROCEMENT-01\" \"patch-b8f2c\" \"Xanthan gum slurry ratio fix for open-cell matrix\" \"material_spec\""
  exit 1
fi

LEDGER_FILE="data/pathways.json"

if [ ! -f "$LEDGER_FILE" ]; then
  echo '{"pathway_version": "1.0", "nodes": {}}' > "$LEDGER_FILE"
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Compute proof hash tying the entry together
BLOCK_HASH=$(echo -n "${MISTAKE_HASH}:${SOLUTION_REF}:${TIMESTAMP}" | sha256sum | awk '{print $1}')

# Update data/pathways.json using jq
TMP_FILE=$(mktemp)
jq --arg key "$MISTAKE_HASH" \
   --arg sol "$SOLUTION_REF" \
   --arg desc "$DESCRIPTION" \
   --arg cat "$CATEGORY" \
   --arg time "$TIMESTAMP" \
   --arg block "$BLOCK_HASH" \
   '.nodes[$key] = {
      "solution_ref": $sol,
      "description": $desc,
      "category": $cat,
      "registered_at": $time,
      "proof_hash": $block
    }' "$LEDGER_FILE" > "$TMP_FILE"

mv "$TMP_FILE" "$LEDGER_FILE"

echo "✅ Immutable Pathway Node Registered:"
echo "   Key / Signature : ${MISTAKE_HASH}"
echo "   Solution / Ref  : ${SOLUTION_REF}"
echo "   Category        : ${CATEGORY}"
echo "   Proof Hash      : ${BLOCK_HASH}"
