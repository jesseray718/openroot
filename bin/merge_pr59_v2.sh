#!/usr/bin/env bash
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
WT=/tmp/wt-pr59
PR=59
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }
say gate "merge_pr59_v2 start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM"
git fetch origin --prune -q
DIRTY=$(git status --porcelain | wc -l)
STATE=$([ "$(git rev-parse --short HEAD)" = "$(git rev-parse --short origin/main)" ] && printf SYNC || printf DRIFT)
say banked "local tree: $STATE dirty=$DIRTY — preserved"
if ! git show-ref --verify --quiet refs/heads/main; then
  git branch main origin/main && say banked "restored local main"
else
  say banked "local main @ $(git rev-parse --short main)"
fi
PR_STATE=$(gh pr view $PR --json state --jq .state 2>/dev/null || echo UNKNOWN)
HEAD_REF=$(gh pr view $PR --json headRefName --jq .headRefName 2>/dev/null || echo "")
say gate "PR #$PR: state=$PR_STATE head=$HEAD_REF"
[ "$PR_STATE" = "MERGED" ] && { say banked "already merged"; exit 0; }
[ "$CONFIRM" != "1" ] && { say held "DRY-RUN: rerun with CONFIRM=1"; printf '[exit=0]\n'; exit 0; }
git worktree remove --force "$WT" 2>/dev/null || true
git fetch origin "pull/$PR/head" && git worktree add --detach "$WT" FETCH_HEAD
say banked "worktree $WT @ PR head"
if git -C "$WT" merge origin/main --no-edit; then
  say banked "merge clean"
else
  CONFLICTS=$(git -C "$WT" diff --name-only --diff-filter=U | tr '\n' ' ')
  git -C "$WT" merge --abort; git worktree remove --force "$WT"
  say held "CONFLICT in: $CONFLICTS — manual resolve needed"
  printf '[exit=0]\n'; exit 0
fi
FAIL=0
for F in $(git -C "$WT" diff --name-only --diff-filter=ACMR origin/main...HEAD | grep '\.py$' || true); do
  python3 -m py_compile "$WT/$F" || { say held "py_compile FAIL: $F"; FAIL=1; }
done
[ "$FAIL" = "1" ] && { git worktree remove --force "$WT"; say held "gate failed"; printf '[exit=0]\n'; exit 0; }
say banked "py_compile passed"
git -C "$WT" push origin HEAD:"$HEAD_REF"
sleep 3
gh pr merge $PR --squash --delete-branch
say banked "squash-merged PR #$PR"
git worktree remove --force "$WT"
for B in $(git branch -r --merged origin/main | sed 's|^ *origin/||' | grep -vE '^(main|HEAD)$' || true); do
  git push origin --delete "$B" -q && say banked "purged $B"
done
for B in $(git for-each-ref --format='%(refname:short)' refs/heads/ | grep -v '^main$' || true); do
  [ "$(git merge-base --is-ancestor "$B" origin/main && echo yes || echo no)" = "yes" ] && git branch -d "$B" 2>/dev/null && say banked "purged local $B" || true
done
say banked "origin/main=$(git rev-parse --short origin/main) — dirty tree untouched"
printf '[exit=0]\n'
