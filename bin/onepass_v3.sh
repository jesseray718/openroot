#!/usr/bin/env bash
# onepass_v3.sh — Weekly: env_map, merge janitor, manifest regen, drift report, 7B next-move, session seed, commit
set -eu
export GIT_PAGER=cat
BASE="$HOME/openroot"
CONTEXT="$BASE/context_bridge"
DATA="$BASE/data"

echo "[OP] Weekly Onepass v3 starting"
echo "[OP] Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Phase 1: env_map
echo "[1/7] env_map.py"
python3 "$BASE/bin/env_map.py"

# Phase 2: merge janitor
echo "[2/7] Merge janitor..."
cd "$BASE" && git fetch origin 2>/dev/null || true

# Phase 3: manifest regen
echo "[3/7] Manifest regeneration..."
find "$BASE/bin" -name "*.py" -o -name "*.sh" | sort > "$DATA/manifest.txt"

# Phase 4: drift report
echo "[4/7] Drift report..."
cd "$BASE" && git status --porcelain > "$CONTEXT/drift_report_$(date +%Y%m%d).txt" 2>/dev/null || true

# Phase 5: 7B next-move
echo "[5/7] 7B next-move..."
echo "[NEXT] Analyzing drift... (placeholder for 7B invocation)"

# Phase 6: session seed
echo "[6/7] Session seed..."
SESSION_FILE="$CONTEXT/session-$(date +%Y%m%d)-weekly.md"
echo "# Weekly Session Seed" > "$SESSION_FILE"
echo "**Date:** $(date)" >> "$SESSION_FILE"
echo "**Manifest entries:** $(wc -l < "$DATA/manifest.txt")" >> "$SESSION_FILE"

# Phase 7: commit
echo "[7/7] Committing..."
cd "$BASE" && \
git add "$DATA/manifest.txt" "$DATA/env_map.json" "$CONTEXT/drift_report_"* "$SESSION_FILE" 2>/dev/null && \
git commit -m "[WEEKLY] Onepass v3 orchestration" || echo "[OP] Nothing to commit"

echo "[OP] Onepass v3 complete — [exit=0]"
exit 0
