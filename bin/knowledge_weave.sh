#!/usr/bin/env bash
set -Eeuo pipefail

# [canary] paste intact
# PURPOSE: Extract local tool registry, prepare for Grok knowledge merge

SCRIPT_DIR="/home/jesse/openroot"
DB_PATH="${HOME}/.local/share/openroot/ledger.db"
OUTPUT_DIR="${SCRIPT_DIR}/data/grok_integration"

mkdir -p "$OUTPUT_DIR"

echo "[stage-1] Scanning all executable scripts..."
find "$SCRIPT_DIR" -type f \( -name "*.py" -o -name "*.sh" \) -executable \
    -exec sh -c 'for f; do echo "$f"; done' _ {} + \
    > "$OUTPUT_DIR/tool_registry.txt"

echo "[stage-2] Computing hashes for all scripts..."
while read -r SCRIPT; do
    HASH=$(sha256sum "$SCRIPT" | cut -d' ' -f1)
    SIZE=$(stat -c%s "$SCRIPT")
    FIRST_LINE=$(head -1 "$SCRIPT" 2>/dev/null || echo "")
    echo "$HASH|$SIZE|$FIRST_LINE|$SCRIPT"
done < "$OUTPUT_DIR/tool_registry.txt" > "$OUTPUT_DIR/tool_manifest.tsv"

echo "[stage-3] Building SQLite tool catalog..."
sqlite3 "$DB_PATH" <<SQL
CREATE TABLE IF NOT EXISTS tool_registry (
    tool_hash TEXT PRIMARY KEY,
    tool_path TEXT NOT NULL,
    tool_size INTEGER,
    first_line TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

DELETE FROM tool_registry;
SQL

while IFS='|' read -r HASH SIZE FIRST LINE PATH; do
    sqlite3 "$DB_PATH" "INSERT INTO tool_registry VALUES('$HASH','$PATH',$SIZE,'$FIRST_LINE',datetime('now'));"
done < "$OUTPUT_DIR/tool_manifest.tsv"

echo "[stage-4] Generating Nomic embeddings for all scripts..."
MODEL="nomic-embed-text"
curl -s http://localhost:11434/api/embeddings -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"$(cat $OUTPUT_DIR/tool_registry.txt | tr '\n' ' ')\"
}" > "$OUTPUT_DIR/script_embeddings.json"

echo "[stage-5] Preparing Grok handoff package..."
cat > "$OUTPUT_DIR/grok_handoff_seed.md" <<HANDOFF
# GROK KNOWLEDGE MERGE SEED

## Local State Verified
- Tool Count: $(wc -l < "$OUTPUT_DIR/tool_registry.txt")
- Total Hashes: $(wc -l < "$OUTPUT_DIR/tool_manifest.tsv")
- DB Path: $DB_PATH
- Generated: $(date -Iseconds)

## Pending Grok Data Sections
[A] Script Headers
[B] SQLite Schemas  
[C] Nomic Patterns
[D] Handoff Templates
[E] Bottleneck Fixes

## Instruction for Grok
Merge your extracted patterns into this structure. Output ONLY merged
data, no explanations. Preserve local hashes and paths unchanged.
HANDOFF

echo "[stage-6] Sealing handoff with SHA256..."
cd "$OUTPUT_DIR"
SEED_HASH=$(sha256sum grok_handoff_seed.md | cut -d' ' -f1)
echo "$SEED_HASH|grok_handoff_seed.md" >> seed_master.log

echo "[DONE] Handoff ready at $OUTPUT_DIR/grok_handoff_seed.md"
echo "[NEXT] Copy this file to Grok and await structured response"
echo "[NEXT] Forward Grok's response back to Lumo for synthesis"
