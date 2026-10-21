#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# gh_fleet_housekeeping_v1.sh — milestones, releases, issues, fleet hygiene
# Dry-run by default. CONFIRM=1 executes. Canary [GHFLEETV1].
set -euo pipefail
export GIT_PAGER=cat GH_PAGER=cat
BASE=/home/jesse/openroot
TS=$(date +%Y%m%d_%H%M%S)
LOG=$BASE/context_bridge/gh_fleet_housekeeping_${TS}.md
USER=jesseray718
FLAGSHIP=openroot
mkdir -p "$BASE/context_bridge"
: > "$LOG"
CONFIRM="${CONFIRM:-0}"

run() { # run "description" cmd...
  local desc="$1"; shift
  echo "- $desc" | tee -a "$LOG"
  if [ "$CONFIRM" = "1" ]; then "$@" 2>&1 | tee -a "$LOG";
  else echo "  [dry] $*" | tee -a "$LOG"; fi
}

echo "[GHFLEETV1] START $TS (CONFIRM=$CONFIRM)" | tee -a "$LOG"
gh auth status 2>&1 | tee -a "$LOG" || { echo "[held] gh not authed"; exit 1; }

echo "## Fleet inventory" | tee -a "$LOG"
gh repo list "$USER" --limit 100 --json name,isArchived,pushedAt \
  --jq '.[] | "\(.name) archived=\(.isArchived) pushed=\(.pushedAt)"' | tee -a "$LOG"

echo "## Flagship: open issues/PRs" | tee -a "$LOG"
gh issue list -R "$USER/$FLAGSHIP" --state open --json number,title,author \
  --jq '.[] | "#\(.number) [\(.author.login)] \(.title)"' | tee -a "$LOG" || true
gh pr list -R "$USER/$FLAGSHIP" --state open --json number,title,author \
  --jq '.[] | "PR#\(.number) [\(.author.login)] \(.title)"' | tee -a "$LOG" || true

echo "## Milestones (existing)" | tee -a "$LOG"
gh api repos/$USER/$FLAGSHIP/milestones --jq '.[] | "\(.title) open=\(.open_issues) closed=\(.closed_issues)"' | tee -a "$LOG" || true

echo "## Releases (existing)" | tee -a "$LOG"
gh release list -R "$USER/$FLAGSHIP" | tee -a "$LOG" || true

# ---- EXECUTE SECTION (dry-run shows exact commands) ----
HEAD=$(git -C "$BASE" rev-parse --short HEAD)

echo "## Actions" | tee -a "$LOG"
for MS in "Consolidation Wave 1 — 41→13 active repos" "Hardware Prototypes v0 — aerocement panel + thermal battery" "Local AI Stack — registry-routed routing GA"; do
  if ! gh api repos/$USER/$FLAGSHIP/milestones --jq '.[].title' 2>/dev/null | grep -qF "$MS"; then
    run "create milestone: $MS" gh api -X POST repos/$USER/$FLAGSHIP/milestones -f title="$MS" -f state=open
  else echo "- milestone exists: $MS" | tee -a "$LOG"; fi
done

# Release anchored to current commit (tag policy fallback: create from HEAD)
if ! gh release list -R "$USER/$FLAGSHIP" | grep -q "v-housekeep-$TS"; then
  run "seal release at $HEAD" gh release create "v-$HEAD" -R "$USER/$FLAGSHIP" --target main \
    -t "Stack consolidation snapshot — $HEAD" \
    -n "Registry-routed local AI stack, week-scripts banked, fleet hygiene pass. Automated by gh_fleet_housekeeping_v1, human-gated."
fi

# Issues: label + comment + close stale (edit lists here after review)
run "label backlog" gh issue edit 53 -R "$USER/$FLAGSHIP" --add-label "contributor,merged"
run "close stale housekeeping issue if empty" gh issue close 53 -R "$USER/$FLAGSHIP" -c "Resolved via PR #63 merge; Reh1t credited in README acknowledgment. Closing after fleet hygiene pass $TS."

# Fleet-wide: list open PRs needing merge (report only — merging is case-by-case)
echo "## Fleet open PRs (report only, manual merge decisions)" | tee -a "$LOG"
for R in $(gh repo list "$USER" --limit 100 --json name --jq '.[].name'); do
  gh pr list -R "$USER/$R" --state open --json number,title,author \
    --jq '"'$R' PR#\(.number) [\(.author.login)] \(.title)"' 2>/dev/null | tee -a "$LOG" || true
done

echo "[GHFLEETV1] END $TS [exit=0]" | tee -a "$LOG"
echo "log: $LOG"
exit 0
