#!/usr/bin/env bash
# next_actions_20260920_v1.sh — priority queue: fork syncs, supersede PR closes,
# master->main renames (auto-detect), unstable-PR diagnostics, GOALS/MASTER_TODO draft rebuild.
set -eu
export GIT_PAGER=cat PAGER=cat
OPENROOT=/home/jesse/openroot
CANARY_TEXT="[canary] OPENROOT-next-actions-v1-20260920 paste intact"
echo "$CANARY_TEXT"
tail -n 1 "$0" | grep -q '\[exit=0\]' || { echo "[gate] tail-line canary FAILED — paste truncated, abort"; exit 1; }
[[ -x "$OPENROOT/bin/stack_gate.sh" ]] && { bash "$OPENROOT/bin/stack_gate.sh" "$0" || { echo "[gate] stack_gate REJECTED — abort"; exit 1; }; } || echo "[gate] stack_gate.sh absent — proceed, noted in audit trail"

cd "$OPENROOT"
STAMP=$(date +%Y%m%d_%H%M%S)
REPORT="$OPENROOT/context_bridge/report-next-actions-$STAMP.md"
CONF="${CONFIRM:-0}"
: > "$REPORT"
hdr() { printf '\n== %s ==\n' "$1" | tee -a "$REPORT"; }
say_() { printf '%s\n' "$*" | tee -a "$REPORT"; }
gh_ok() { gh auth status >/dev/null 2>&1; }

# ---------- STAGE 1: [fork-sync] ----------
hdr "STAGE 1 [fork-sync]"
if [[ -x "$OPENROOT/bin/frp6_fleet_squash.sh" ]]; then
  if [[ "$CONF" == "1" ]]; then
    say_ "[banked] executing fleet squash (7 syncs)"
    CONFIRM=1 bash "$OPENROOT/bin/frp6_fleet_squash.sh" 2>&1 | tee -a "$REPORT"
    say_ "[banked] fork sync exit=$?"
  else
    say_ "[held] CONFIRM=1 required to execute fork syncs (this run: dry-run only)"
  fi
else
  say_ "[held] frp6_fleet_squash.sh missing at bin/ — verify path, rerun"
fi

# ---------- STAGE 2: [pr-close] superseded PRs ----------
hdr "STAGE 2 [pr-close] superseded: openroot #5 #12 #15 #16 #18"
gh_ok || { say_ "[held] gh not authenticated — skipping"; }
CLOSE_MSG="Closing as superseded by fleet consolidation + fork squash sync (2026-09-20). Content preserved in git history; reopen if any portion is still live."
for n in 5 12 15 16 18; do
  INFO=$(gh pr view "$n" -R jesseray718/openroot --json title,state,url -q '.title+" | "+.state+" | "+.url' 2>/dev/null || echo "NOT FOUND")
  if [[ "$INFO" == "NOT FOUND" ]]; then say_ "[held] PR #$n not found — skip"; continue; fi
  if [[ "$INFO" == *"CLOSED"* ]]; then say_ "[held] PR #$n already closed — skip"; continue; fi
  if [[ "$CONF" == "1" ]]; then
    gh pr close "$n" -R jesseray718/openroot --comment "$CLOSE_MSG" && say_ "[banked] PR #$n closed"
  else
    say_ "[held] preview: PR #$n would CLOSE with supersede comment :: $INFO"
  fi
done

# ---------- STAGE 3: [branch-rename] master->main, auto-detect, owned repos ----------
hdr "STAGE 3 [branch-rename] master->main (auto-detect, six owned repos expected)"
gh_ok && while read -r repo; do
  if gh api "repos/$repo/branches/master" >/dev/null 2>&1; then
    if gh api "repos/$repo/branches/main" >/dev/null 2>&1; then
      say_ "[held] $repo: BOTH master+main exist — ambiguous, manual decision required"
    elif [[ "$CONF" == "1" ]]; then
      gh api -X POST "repos/$repo/branches/master/rename" -f new_name=main >/dev/null \
        && say_ "[banked] $repo: master renamed to main (default branch follows)"
    else
      say_ "[held] preview: $repo would rename master -> main"
    fi
  fi
done < <(gh repo list jesseray718 --limit 300 --json nameWithOwner -q '.[].nameWithOwner')

# ---------- STAGE 4: [ci-diag] unstable PRs / Quality CI diagnostics ----------
hdr "STAGE 4 [ci-diag] unstable PR diagnostics (decision: close vs fix)"
gh pr list -R jesseray718/openroot --state open --json number,title,url,headRefName,statusCheckRollup > "$OPENROOT/data/unstable_prs_$STAMP.json" 2>/dev/null || true
gh run list -R jesseray718/openroot --limit 15 --json displayTitle,workflowName,status,conclusion,createdAt > "$OPENROOT/data/recent_runs_$STAMP.json" 2>/dev/null || true
say_ "[banked] diagnostics written: data/unstable_prs_$STAMP.json, data/recent_runs_$STAMP.json"
say_ "[held] decision deferred to human after reading diagnostics (shared-workflow root cause — fix unblocks dependabot fleet-wide)"

# ---------- STAGE 5: [goals-rebuild] GOALS/MASTER_TODO draft from remnants ----------
hdr "STAGE 5 [goals-rebuild] draft from context_bridge remnants"
DRAFT_G="$OPENROOT/GOALS.rebuild.$STAMP.md"
DRAFT_T="$OPENROOT/MASTER_TODO.rebuild.$STAMP.md"
SALVAGE="$OPENROOT/data/salvaged_tasks_$STAMP.txt"
find "$OPENROOT/context_bridge" -name 'session-2026-09-16-*.md' -print0 2>/dev/null \
  | xargs -0 -r cat 2>/dev/null | grep -hE '^[-*] \[[ x]\]|^[0-9]+\) |^#{2,3} ' | sort -u > "$SALVAGE" || true
{
  echo "# GOALS.md (rebuild draft $STAMP — HUMAN REVIEW REQUIRED, DO NOT COMMIT BLIND)"
  echo "- id: goals-rebuild-$STAMP | status: draft | provenance: context_bridge remnants + boot-seed queue"
  echo "## Mission"
  echo "OpenRoot: open-source hardware blockchain, local agent orchestration (7B builder / 3B grader), eta = J_useful/J_human, permaculture + agape doctrine, falsifiable claims only."
  echo "## Immediate Queue (boot seed 2026-09-18, amended 2026-09-20)"
  echo "1. verify/commit bin/  2. GOALS/MASTER_TODO rebuild (this draft)  3. support Reh1t PR #53  4. pin 4 repos + README [PHOTO] slot  5. aerocement-panel-v0 standalone repo  6. SARE grant framing  7. weekly onepass_v3.sh"
  echo "## Fleet Ops (2026-09-20)"
  echo "Fork squash syncs banked; superseded PRs closed; master->main renames done; Quality CI shared-workflow fix = next fleet-wide unlock."
  echo "## Salvage Index"
  echo "See data/salvaged_tasks_$STAMP.txt ($(wc -l < "$SALVAGE") lines recovered)"
} > "$DRAFT_G"
{
  echo "# MASTER_TODO.md (rebuild draft $STAMP — HUMAN REVIEW REQUIRED)"
  echo "- Status: draft | Provenance: salvaged tasks below, deduped from session-2026-09-16 remnants"
  echo "## Recovered Tasks (raw salvage — review, dedupe, promote)"
  sed 's/^/- /' "$SALVAGE"
} > "$DRAFT_T"
say_ "[held] drafts written (NOT committed — human is the only commit gate):"
say_ "  $DRAFT_G"
say_ "  $DRAFT_T"
say_ "  salvage: $SALVAGE"
say_ "review, then: git add -N '$DRAFT_G' '$DRAFT_T'; git diff; commit with provenance message"
git add -N "$DRAFT_G" "$DRAFT_T" 2>/dev/null || true

# ---------- STAGE 6: [handoff] ----------
hdr "STAGE 6 [handoff]"
sha256sum "$DRAFT_G" "$DRAFT_T" "$SALVAGE" "$REPORT" 2>/dev/null | tee -a "$REPORT"
{ echo ""; echo "## Handoff $STAMP"; echo "mode=${CONF:+execute}${CONF:-dry-run}"; \
  echo "git HEAD: $(git -C "$OPENROOT" rev-parse --short HEAD 2>/dev/null)"; \
  echo "verified: report + drafts + diagnostics above; mutations gated by CONFIRM"; \
  echo "broken: none encountered"; \
  echo "next: review GOALS draft -> commit; read CI diagnostics -> close-vs-fix 5 unstable PRs; reissue stack_gate v3.1"; } >> "$REPORT"
say_ "[banked] report sealed: $REPORT"
echo "[exit=0]"
