#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# merge_pr59_v3.sh — Path A: main-authoritative rebase-merge of PR #59.
# Favors main on conflicts (-X ours). Refuses to push if PR contributes no delta.
# Idempotent, dry-run by default, CONFIRM=1 executes.
# [canary] merge_pr59_v3_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
WT=/tmp/wt-pr59-v3
PR=59
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }

say gate "merge_pr59_v3 start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM"
git fetch origin --prune -q
say banked "dirty=$(git status --porcelain | wc -l) — untouched, work in $WT"

PR_STATE=$(gh pr view $PR --json state --jq .state 2>/dev/null || echo UNKNOWN)
HEAD_REF=$(gh pr view $PR --json headRefName --jq .headRefName 2>/dev/null || echo "")
say gate "PR #$PR: state=$PR_STATE head=$HEAD_REF"
[ "$PR_STATE" = "MERGED" ] && { say banked "already merged"; printf '[exit=0]\n'; exit 0; }
[ "$CONFIRM" != "1" ] && { say held "DRY-RUN: will merge PR head INTO origin/main, -X ours, gates: delta+py_compile+grep. CONFIRM=1 to execute"; printf '[exit=0]\n'; exit 0; }

# fresh worktree from MAIN (authoritative side = ours)
git worktree remove --force "$WT" 2>/dev/null || true
git worktree add --detach "$WT" origin/main
git -C "$WT" fetch origin "pull/$PR/head"
git -C "$WT" merge FETCH_HEAD --no-edit -X ours
say banked "merged PR head into main base @ $(git -C "$WT" rev-parse --short HEAD)"

# GATE 1: delta check — merged tree must differ from origin/main, else PR contributes nothing
DELTA=0
for F in $(git -C "$WT" diff --name-only origin/main HEAD || true); do
  if ! git -C "$WT" diff --quiet origin/main HEAD -- "$F"; then
    DELTA=$((DELTA+1)); say gate "delta retained in: $F"
  fi
done
if [ "$DELTA" -eq 0 ]; then
  git worktree remove --force "$WT"
  say held "ZERO delta survived -X ours — PR #59 adds nothing over current main. Recommend CLOSE (Path B) + let coderabbit regenerate"
  printf '[exit=0]\n'; exit 0
fi
say banked "delta confirmed: $DELTA files changed by merge"

# GATE 2: py_compile every .py that differs from main
FAIL=0
for F in $(git -C "$WT" diff --name-only --diff-filter=ACMR origin/main HEAD | grep '\.py$' || true); do
  python3 -m py_compile "$WT/$F" || { say held "py_compile FAIL: $F"; FAIL=1; }
done
# GATE 3: no conflict markers anywhere
grep -rl '^<<<<<<<\|^>>>>>>>' "$WT/bin" "$WT/docs" 2>/dev/null && FAIL=1
[ "$FAIL" = "1" ] && { git worktree remove --force "$WT"; say held "gates failed — not pushing"; printf '[exit=0]\n'; exit 0; }
say banked "py_compile + conflict-marker gates passed"

# push to PR branch (your repo, you can force-write bot branches), then squash-merge
git -C "$WT" push origin HEAD:"$HEAD_REF"
say banked "pushed merged result to $HEAD_REF"
sleep 3
gh pr merge $PR --squash --delete-branch
say banked "squash-merged PR #$PR, branch deleted"
git worktree remove --force "$WT"
say banked "origin/main=$(git rev-parse --short origin/main) — next: onepass_v3.sh weekly, GOALS/MASTER_TODO rebuild"
printf '[exit=0]\n'
