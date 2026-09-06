#!/usr/bin/env bash
set -euo pipefail

echo "=== MY OPEN ISSUES ==="
gh issue list --assignee @me --state open || true

echo "\n=== PRs NEEDING MY REVIEW ==="
gh pr list --search "review-requested:@me state:open" || true

echo "\n=== MY OPEN PRs ==="
gh pr list --author @me --state open || true

echo "\n=== LATEST ACTION RUNS ==="
gh run list --limit 5 || true

echo "\n=== NEXT ACTION ==="
echo "Choose one task, create/update branch, and ship a small verified PR."
