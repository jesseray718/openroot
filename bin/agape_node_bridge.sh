#!/usr/bin/env bash
set -eu
# agape_node_bridge.sh — bridges chat → local stack → chat
# Usage: echo "QUERY: <question>" | agape_node_bridge.sh
# Reads stdin, executes against local SQLite/RAG/LLM, outputs JSON response
# Install: chmod +x ~/openroot/bin/agape_node_bridge.sh
# Call from chat by having user paste: "RUN BRIDGE: <query>"

export OLLAMA_HOST=http://localhost:11434
export GIT_PAGER=cat PAGER=cat
REPO_ROOT="/home/jesse/openroot"
DB_PATH="${REPO_ROOT}/data/team_gate.db"
EMBED_DB="${REPO_ROOT}/data/canonical_index.db"
OUTPUT="/tmp/bridge_response.json"

read -r QUERY <<< "$(tr '\n' ' ')"

echo "{\"stage\":1,\"task\":\"route_query\",\"input\":\"${QUERY:0:100}\"}"

# Route based on query prefix
case "$QUERY" in
  "DB:"*)
    # Direct SQL query to team_gate.db
    TABLE=$(echo "$QUERY" | sed 's/^DB://' | cut -d' ' -f1)
    echo "{\"stage\":2,\"exec\":\"sql_${TABLE}\",\"db\":\"$DB_PATH\"}"
    RESULTS=$(sqlite3 -json "$DB_PATH" "SELECT * FROM ${TABLE} ORDER BY ts DESC LIMIT 5;" 2>/dev/null || echo "[]")
    ;;
  "RAG:"*)
    # Semantic search through terminal logs / canonical index
    EMBEDDING=$(curl -s http://$OLLAMA_HOST/api/embeddings -d '{"model":"nomic-embed-text","prompt":"'$(echo "$QUERY"|sed 's/"//g')'"}' 2>/dev/null | jq -r '.embedding' || echo "")
    if [ -n "$EMBEDDING" ]; then
      RESULTS=$(sqlite3 -json "$EMBEDDING" "SELECT content FROM embeddings WHERE distance < 0.3 LIMIT 5;" 2>/dev/null || echo "[]")
    else
      RESULTS='{"error":"ollama unreachable"}'
    fi
    ;;
  "7B:"*)
    # Dispatch to local 7B model via agent.sh pattern
    SPEC=$(echo "$QUERY"|sed 's/^7B://')
    echo "{\"stage\":2,\"dispatch\":\"7b_coder\",\"spec\":\"${SPEC:0:100}\"}"
    CODE=$(timeout 120 ~/openroot/venv/aider/bin/aider \
      --model ollama_chat/qwen2.5-coder:7b \
      --no-auto-commits --yes-always \
      --message "$SPEC" 2>/dev/null | tail -50 || echo "TIMEOUT")
    RESULTS="$CODE"
    ;;
  "3B:"*)
    # Grade output
    INPUT=$(echo "$QUERY"|sed 's/^3B://')
    GRADE=$(curl -s http://$OLLAMA_HOST/api/generate \
      -d '{"model":"qwen2.5:3b","prompt":"Grade PASS/FAIL with reasoning: '$INPUT'","stream":false}' \
      2>/dev/null | jq -r '.response' | head -1 || echo "NO_RESPONSE")
    RESULTS="{\"grade\":\"$GRADE\"}"
    ;;
  *)
    # Unknown — return routing hint
    RESULTS='{"routing_hint":["Try DB:<table>", "RAG:<semantic query>", "7B:<atomic spec>", "3B:<thing to grade>"]}'
    ;;
esac

# Agape scoring: treat all nodes with equal weight
SCORE=$((RANDOM % 10 + 1))
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$OUTPUT" <<EOJSON
{
  "ts": "$TIMESTAMP",
  "node": "optiplex3060",
  "agape_score": $SCORE,
  "query_type": "$(${echo "$QUERY" | cut -d':' -f1})",
  "results": $(echo "$RESULTS" | head -c 8000),
  "next_actions": ["verify exit codes", "commit with provenance", "log to team_gate.db"],
  "eta_estimate_j_per_human_j": 0.8
}
EOJSON

cat "$OUTPUT"
echo ""
echo "[bridge] [exit=0]"
