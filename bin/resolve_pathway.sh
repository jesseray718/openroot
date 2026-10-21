#!/usr/bin/env bash
set -euo pipefail

# 1. Obtain deterministic mistake hash from stack_gate
MISTAKE_HASH=$(bin/stack_gate.sh --hash-failure)

if [ "$MISTAKE_HASH" = "NO_FAIL" ]; then
  echo "✅ No active drift/failure detected. Gate clean."
  exit 0
fi

echo "🔍 Failure signature: ${MISTAKE_HASH}"

# 2. Get repository slug dynamically via GitHub CLI
REPO_SLUG=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [ -z "$REPO_SLUG" ]; then
  echo "⚠️ GitHub CLI not authenticated or not inside a remote repo."
  exit 1
fi

# 3. Lookup pathway in data/pathways.json via GitHub API
if MATCH=$(gh api "repos/${REPO_SLUG}/contents/data/pathways.json" --jq ".nodes[\"${MISTAKE_HASH}\"]" 2>/dev/null); then
  if [ -n "$MATCH" ] && [ "$MATCH" != "null" ]; then
    echo "⚡ CACHE HIT: Recomputation bypassed for hash ${MISTAKE_HASH}"
    echo "$MATCH"
    exit 0
  fi
fi

echo "⚠️ CACHE MISS: Routing compute to starved node for resolution."
