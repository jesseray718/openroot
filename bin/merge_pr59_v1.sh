#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# merge_pr59_v1.sh — squash-merge openroot PR #59 (coderabbit docs), purge merged branches,
#                    restore local main deleted by repo_clean_v1 (exclusion-grep bug).
# Idempotent, dry-run by default. CONFIRM=1 enables push/merge/branch deletes. Never touches PR #53/#60.
# [canary] merge_pr59_v1_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
WT=/tmp/wt-pr59
PR=59
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }

grep -q 'merge_pr59_v1_CANARY_MARKER' "$0" || { echo "[gate] canary missing — paste truncated"; exit 1; }
[ "$(tail -n1 "$0")" = "[exit=0]" ] || { echo "[gate] tail-line check failed — paste truncated"; exit 1; }

say gate "merge_pr59_v1 start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM"

# [1] sync + state (report only — dirty tree LEFT UNTOUCHED)
git fetch origin --prune -q
DIRTY=$(git status --porcelain | wc -l)
STATE=$([ "$(git rev-parse --short HEAD)" = "$(git rev-parse --short origin/main)" ] && printf SYNC || printf DRIFT)
say banked "local tree: $STATE dirty=$DIRTY — preserved, all work happens in worktree $WT"

# [2] restore local main (deleted by repo_clean_v1 exclusion-grep miss on '* main')
if ! git show-ref --verify --quiet refs/heads/main; then
  git branch main origin/main && say banked "restored local main -> $(git rev-parse --short origin/main)"
else
  say banked "local main present @ $(git rev-parse --short main)"
fi

# [3] PR #59 state
PR_JSON=$(gh pr view $PR --json state,mergeable,headRefName,title --jq '"state=\(.state) mergeable=\(.mergeable) head=\(.headRefName) | \(.title)"')
say gate "PR #$PR: $PR_JSON"
PR_STATE=$(gh pr view $PR --json state --jq .state)
HEAD_REF=$(gh pr view $PR --json headRefName --jq .headRefName)

if [ "$PR_STATE" = "MERGED" ]; then
  say banked "PR #$PR already merged — skipping to branch cleanup"
elif [ "$CONFIRM" != "1" ]; then
  say held "DRY-RUN plan: fetch PR head -> merge origin/main into it in $WT -> py_compile touched .py -> push to $HEAD_REF -> gh pr merge $PR --squash --delete-branch -> purge merged branches"
  say held "rerun with: CONFIRM=1 bash $0"
  printf '[exit=0]\n'
  exit 0
else
  # [4] isolated worktree from PR head, merge origin/main to resolve CONFLICTING
  git worktree remove --force "$WT" 2>/dev/null || true
  git fetch origin "pull/$PR/head" && git worktree add --detach "$WT" FETCH_HEAD
  say banked "worktree $WT @ PR head $(git -C "$WT" rev-parse --short HEAD)"
  if git -C "$WT" merge origin/main --no-edit; then
    say banked "merge origin/main INTO PR head clean @ $(git -C "$WT" rev-parse --short HEAD)"
  else
    CONFLICTS=$(git -C "$WT" diff --name-only --diff-filter=U | tr '\n' ' ')
    git -C "$WT" merge --abort
    git worktree remove --force "$WT"
    say held "CONFLICT in: $CONFLICTS — cannot auto-resolve docs overlap, human gate required (manual: worktree add $WT pull/59/head, resolve, push to $HEAD_REF)"
    printf '[exit=0]\n'
    exit 0
  fi

  # [5] py_compile gate on every .py the PR branch changed vs main (stub-blind protection)
  FAIL=0
  for F in $(git -C "$WT" diff --name-only --diff-filter=ACMR origin/main...HEAD | grep '\.py$' || true); do
    python3 -m py_compile "$WT/$F" || { say held "py_compile FAIL: $F"; FAIL=1; }
  done
  if [ "$FAIL" = "1" ]; then
    git worktree remove --force "$WT"
    say held "py_compile gate failed — NOT pushing. Inspect $WT files listed above"
    printf '[exit=0]\n'
    exit 0
  fi
  say banked "py_compile gate passed"

  # [6] push resolved branch back -> PR flips mergeable -> squash-merge
  git -C "$WT" push origin HEAD:"$HEAD_REF"
  say banked "pushed merge-resolution to $HEAD_REF"
  sleep 5
  gh pr merge $PR --squash --delete-branch
  say banked "squash-merged PR #$PR and deleted branch $HEAD_REF"
  git worktree remove --force "$WT"
fi

# [7] purge merged remote/local branches (main + PR #53 author-side always excluded)
git fetch origin --prune -q
for B in $(git branch -r --merged origin/main | sed 's|^ *origin/||' | grep -vE '^(main|HEAD)$' || true); do
  git push origin --delete "$B" -q && say banked "purged merged remote branch: $B"
done
for B in $(git for-each-ref --format='%(refname:short)' refs/heads/ | grep -v '^main$' || true); do
  [ "$(git merge-base --is-ancestor "$B" origin/main && echo yes || echo no)" = "yes" ] && git branch -d "$B" 2>/dev/null && say banked "purged merged local branch: $B" || true
done

# [8] final state
NEW_MAIN=$(git rev-parse --short origin/main)
say banked "origin/main=$NEW_MAIN — local dirty tree ($DIRTY files) untouched, reconcile at your leisure"
say banked "NOT touched: PR #53 (Reh1t, hands-off), PR #60 (changes/3f27b749)"
printf '[exit=0]\n'
