#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — reconcile Reh1t contribution against ISSUE #53 (branch feat/53-local-AI on fork Reh1t/openroot)
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="REH53V2"
LOG=/home/jesse/openroot/logs/reh1t_v2_${STAMP}.log
DATA=/home/jesse/openroot/data/reh1t
mkdir -p "$DATA" "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

# [gate] clean tree
if ! git diff-index --quiet HEAD --; then
  echo "[gate] DIRTY TREE — commit or stash first"; exit 1; fi

git fetch origin --prune
git checkout main && git pull --ff-only

# [status] what is #53 really, and what has Reh1t opened?
echo "[status] issue #53:"
gh issue view 53 --json state,title,assignees,url --jq '"state=" + .state + " | " + .title + " | assignees=" + ([.assignees[].login]|join(",")) + " | " + .url' || echo "[status] issue #53 not viewable"
echo "[status] PRs referencing 53 or authored by Reh1t:"
gh pr list --state all --search "53 in:title" --json number,title,state,headRefName || true
gh pr list --state all --author Reh1t --json number,title,state,headRefName || true

# [banked] fetch their branch straight from the fork (works with or without a PR object)
FORK_URL=https://github.com/Reh1t/openroot.git
BRANCH=feat/53-local-AI
if git fetch "$FORK_URL" "$BRANCH:reh1t-53-local-AI" 2>/dev/null; then
  echo "[banked] fetched Reh1t/${BRANCH}"
elif git fetch origin pull/*/head:reh1t-pr 2>/dev/null && git rev-parse reh1t-pr >/dev/null 2>&1; then
  BRANCH=reh1t-pr; echo "[banked] fell back to pull refs"
else
  echo "[gate] could not fetch fork branch $BRANCH — verify fork/branch name: gh api repos/Reh1t/openroot/branches --jq '.[].name'"
  exit 1
fi

# [status] what commits would we take?
NCOMMITS=$(git rev-list --count origin/main.."reh1t-53-local-AI" 2>/dev/null || echo "?")
echo "[status] commits not in main: $NCOMMITS"
git log --oneline origin/main..reh1t-53-local-AI 2>/dev/null | head -20 || true

# [gate] reconcile preserving authorship via cherry-pick (better than 3-way patch: keeps their commits)
git checkout -B pr53-reconcile origin/main
if git cherry-pick --strategy-option=theirs "origin/main..reh1t-53-local-AI" 2>/dev/null || git cherry-pick -x origin/main..reh1t-53-local-AI; then
  PYFAIL=0
  for f in $(git diff --name-only origin/main HEAD | grep '\.py$' || true); do
    python3 -m py_compile "$f" || PYFAIL=1
  done
  if [[ "$PYFAIL" == "1" ]]; then
    echo "[gate] PY_COMPILE FAIL — branch pr53-reconcile left for inspection, nothing pushed"; exit 1
  fi
  echo "[banked] reconciled on pr53-reconcile:"
  git log --oneline origin/main..HEAD | head -20
  git diff --stat origin/main HEAD | tail -5
else
  echo "[gate] CHERRY-PICK CONFLICT — run: git cherry-pick --abort, then manual merge of reh1t-53-local-AI"; exit 1
fi

# [held] friendly comment on ISSUE #53 — posts only with CONFIRM=1
cat > "$DATA/comment_v2_${STAMP}.md" <<_EOF_CMT_
Hey @Reh1t — checking in on #53. Quick heads-up: main was force-pushed (git filter-repo stripped >50 MB blobs, repo now ~15 MiB), so your clone's history has diverged and a plain pull will fight you — nothing you did wrong. Resync with: git fetch origin && git checkout main && git reset --hard origin/main. Your branch is preserved: I reconciled feat/53-local-AI onto current main as pr53-reconcile with your authorship intact. Happy to walk through any snags here. — Jesse (jesseray718)
_EOF_CMT_

if [[ "${CONFIRM:-0}" == "1" ]]; then
  git push origin pr53-reconcile
  gh issue comment 53 --body-file "$DATA/comment_v2_${STAMP}.md"
  echo "[banked] pushed pr53-reconcile + commented on issue #53"
  echo "[held] human gate remains: open PR from pr53-reconcile -> main, review, merge, close #53 citing it"
else
  echo "[held] CONFIRM=1 to: push pr53-reconcile + comment on issue #53 (review diff first: git log origin/main..pr53-reconcile)"
fi

sha256sum "$DATA/comment_v2_${STAMP}.md"
echo "[$CANARY] END $STAMP [exit=0]"
