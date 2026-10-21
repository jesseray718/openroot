#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — reconcile Reh1t PR #53 onto post-filter-repo main
# eta = useful_joules / human_joules
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="REH53V1"
LOG=/home/jesse/openroot/logs/reh1t_pr53_${STAMP}.log
DATA=/home/jesse/openroot/data/reh1t
mkdir -p "$(dirname "$LOG")" "$DATA"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"

cd /home/jesse/openroot

# [gate] clean tree required
if ! git diff-index --quiet HEAD --; then
  echo "[gate] DIRTY TREE — commit or stash first, then rerun"
  exit 1
fi

git fetch origin --prune
git checkout main
git pull --ff-only

# [status] PR truth from GitHub
STATE=$(gh pr view 53 --json state,mergeable --jq '"state=" + .state + " mergeable=" + (.mergeable|tostring)')
echo "[status] PR53 $STATE"

# [banked] fetch their branch + authoritative patch
git fetch origin pull/53/head:pr53-reh1t-head
ANAME=$(git log -1 --format='%an' pr53-reh1t-head)
AEMAIL=$(git log -1 --format='%ae' pr53-reh1t-head)
NCOMMITS=$(git rev-list --count origin/main..pr53-reh1t-head)
echo "[status] head author: $ANAME <$AEMAIL>, commits-not-in-main: $NCOMMITS"
PATCH="$DATA/pr53_${STAMP}.patch"
gh pr diff 53 > "$PATCH"
echo "[banked] patch: $PATCH ($(wc -l < "$PATCH") lines)"

# [gate] reconcile onto current main (filter-repo rewrote history, direct merge lies)
git checkout -B pr53-reconcile origin/main
if git apply --3way "$PATCH"; then
  git add -A
  PYFAIL=0
  for f in $(git diff --cached --name-only | grep '\.py$' || true); do
    python3 -m py_compile "$f" || PYFAIL=1
  done
  if [[ "$PYFAIL" == "1" ]]; then
    echo "[gate] PY_COMPILE FAIL — reconcile branch left for human inspection, not committed"
    exit 1
  fi
  git commit -m "[MERGE] Reh1t #53 RAG ingestion — reconciled onto post-filter-repo main" \
    -m "Original author: ${ANAME}; source: PR #53; patch: pr53_${STAMP}.patch" \
    -m "Co-authored-by: ${ANAME} <${AEMAIL}>"
  echo "[banked] reconciled commit:"
  git show --stat HEAD | head -20
else
  echo "[gate] PATCH CONFLICT — 3way failed. Manual review needed on pr53-reconcile"
  exit 1
fi

# [held] gentle comment for Rehan — post only with CONFIRM=1
cat > "$DATA/comment_${STAMP}.md" <<_EOF_CMT_
Hey @Reh1t — thanks for taking #53. Heads-up: main was force-pushed recently (git filter-repo stripped >50 MB blobs; repo is now ~15 MiB), so your clone's history has diverged from main and a plain pull will fight you. Nothing you did wrong. To resync:

    git fetch origin
    git checkout main
    git reset --hard origin/main

Your work is preserved: I reconciled the PR diff onto current main as branch pr53-reconcile, with your authorship intact (Co-authored-by trailer). Happy to walk through any rebase snags here. — Jesse (jesseray718)
_EOF_CMT_

if [[ "${CONFIRM:-0}" == "1" ]]; then
  git push origin pr53-reconcile
  gh pr comment 53 --body-file "$DATA/comment_${STAMP}.md"
  if gh pr view 53 --json mergeable --jq '.mergeable' | grep -q MERGEABLE; then
    echo "[held] PR53 is directly mergeable — recommend: gh pr merge 53 --merge (human decides, keeps your commit graph)"
  else
    echo "[status] PR conflicts with rewritten main — merge pr53-reconcile instead, then close #53 citing it"
  fi
else
  echo "[held] CONFIRM=1 to: push pr53-reconcile + post comment on #53"
fi

sha256sum "$PATCH" "$DATA/comment_${STAMP}.md"
echo "[$CANARY] END $STAMP [exit=0]"
