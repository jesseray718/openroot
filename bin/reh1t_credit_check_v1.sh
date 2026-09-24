#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — verify PR #63 authorship landed in main, clean reconcile droppings, thank Reh1t
set -euo pipefail
export GIT_PAGER=cat
REPO=/home/jesse/openroot
STAMP=$(date +%Y%m%d_%H%M%S)
CANARY="REHCRED1"
LOG=/home/jesse/openroot/logs/reh1t_credit_${STAMP}.log
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
echo "[$CANARY] START $STAMP"
cd "$REPO"

# [status] how was #63 merged, by whom, which commit?
gh pr view 63 --json mergeCommit,mergedAt,mergedBy,author,mergeStateStatus \
  --jq '"author=" + .author.login + " | mergedBy=" + .mergedBy.login + " | mergedAt=" + .mergedAt + " | mergeCommit=" + .mergeCommit.oid'

# [gate] is Reh1t's name actually IN main history? (squash-merge can erase it)
MC=$(gh pr view 63 --json mergeCommit --jq '.mergeCommit.oid')
if git log --format='%H %an <%ae>' --all | grep -i "Reh1t" | head -5; then
  echo "[banked] Reh1t authorship present in history"
else
  echo "[gate] Reh1t name NOT in commit authors — checking co-author trailers on merge commit"
  git show -s --format='%an%n%b' "$MC" | head -10
fi
echo "[status] files #63 touched (proof the RAG work lives in main):"
git show --stat --oneline "$MC" | head -15

# [banked] delete dead branches — reconcile branch equals main, their branch already merged
git branch -D pr53-reconcile reh1t-53-local-AI 2>/dev/null || true
echo "[banked] dead local branches removed:"
git branch --list "pr53*" "reh1t*"

# [held] one genuine thank-you — CONFIRM=1 to post on the merged PR (better venue than the closed issue)
cat > /home/jesse/openroot/data/reh1t/thanks_${STAMP}.md <<_EOF_THX_
@Reh1t — merged and landed in main. Thank you for taking #53 end-to-end with a zero-dependency design, that restraint fits the project perfectly. Fair warning: main was force-pushed (filter-repo stripped large blobs), so your local clone may feel stale — git fetch origin && git reset --hard origin/main if so. Whenever you're ready for a next issue, ping me here or grab one from the board. — Jesse
_EOF_THX_

if [[ "${CONFIRM:-0}" == "1" ]]; then
  gh pr comment 63 --body-file /home/jesse/openroot/data/reh1t/thanks_${STAMP}.md
  echo "[banked] thank-you posted on PR #63"
else
  echo "[held] CONFIRM=1 to post thank-you on PR #63"
fi

sha256sum /home/jesse/openroot/data/reh1t/thanks_${STAMP}.md
echo "[$CANARY] END $STAMP [exit=0]"
