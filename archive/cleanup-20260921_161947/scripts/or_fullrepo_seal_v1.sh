#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
CONFIRM=${CONFIRM:-0}
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:preflight] $(hostname) at $(pwd) — FULL REPO SEAL WORKFLOW"
echo "This will: merge PRs, create milestones/releases/issues/discussions, update profile/landing"
echo "Run once to DRY-RUN, review output, then run again with CONFIRM=1 to execute"

echo "[STAGE:audit] enumerate current state"
OPEN_PRS=$(gh pr list --repo jesseray718/openroot --state open --json number,title --jq '.[] | "\(.number) \(.title)"')
OPEN_ISSUES=$(gh issue list --repo jesseray718/openroot --state open --json number,title --jq '.[] | "\(.number) \(.title)"')
EXISTING_MILESTONES=$(gh api repos/jesseray718/openroot/milestones --jq '.[] | "\(.number) \(.title) \(.state)"' 2>/dev/null || echo "NONE")
EXISTING_RELEASES=$(gh release list --repo jesseray718/openroot --json tagName,name --jq '.[] | "\(.tagName) \(.name)"' 2>/dev/null || echo "NONE")

echo "[AUDIT] Open PRs:"
echo "$OPEN_PRS" | head -10
echo "[AUDIT] Open Issues:"
echo "$OPEN_ISSUES" | head -10
echo "[AUDIT] Existing Milestones:"
echo "$EXISTING_MILESTONES"
echo "[AUDIT] Existing Releases:"
echo "$EXISTING_RELEASES"

echo "[STAGE:profile-audit] check profile page state"
PROFILE_README=$(gh api /user --jq '.login' 2>/dev/null || echo "UNKNOWN")
echo "[AUDIT] Profile login: $PROFILE_README"
PROFILESIZE=$(curl -sL "https://github.com/$PROFILE_README.md" 2>/dev/null | wc -l || echo "0")
echo "[AUDIT] Profile README size: ${PROFILESIZE} lines"

echo "[STAGE:landing-audit] check GitHub Pages status"
PAGES_STATUS=$(gh api repos/jesseray718/openroot/pages --jq '.source.branch + "/" + .source.path' 2>/dev/null || echo "NOT_CONFIGURED")
echo "[AUDIT] GitHub Pages: $PAGES_STATUS"

echo "=========================================="
echo "DRY-RUN SUMMARY — nothing executed yet"
echo "=========================================="
echo ""
echo "[ACTION 1] MERGE PRs (count: $(echo "$OPEN_PRS" | wc -l))"
echo "$OPEN_PRS" | head -5
echo ""
echo "[ACTION 2] CREATE MILESTONE v1.0 — 'Public Launch'"
echo "[ACTION 3] CREATE RELEASE v1.0.0 — tag: v1.0.0"
echo "[ACTION 4] CREATE ISSUES (from MASTER_TODO.md)"
echo "[ACTION 5] CREATE DISCUSSION — 'Welcome Contributors'"
echo "[ACTION 6] UPDATE PROFILE README — add OpenRoot pin slot"
echo "[ACTION 7] UPDATE LANDING PAGE — sync with README"
echo ""
echo "=========================================="
echo "TO EXECUTE: export CONFIRM=1 && bash /home/jesse/openroot/or_fullrepo_seal_v1.sh"
echo "=========================================="
echo "[CANARY] FULLREPOSEAL-V1-${TS}-DRY-RUN-COMPLETE"
echo "[exit=0]"
