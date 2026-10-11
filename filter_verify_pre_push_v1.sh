#!/usr/bin/env bash
# filter_verify_pre_push_v1.sh — inspect what survives, what's discarded, what's heavy
# CANARY:OPENROOT-FILTER-VERIFY-PRE-PUSH-V1
set -eu
export GIT_PAGER=cat TERM=dumb
cd /home/jesse/openroot

echo "[gate] stage 1 — the 25 surviving commits (is today's work all here?)"
git log --oneline HEAD | head -30

echo "[gate] stage 2 — what origin/main has that HEAD does not (discarded by force-push)"
echo "[banked] origin/main commits: $(git rev-list --count origin/main 2>/dev/null || echo 0)"
git log --oneline HEAD..origin/main 2>/dev/null | head -20
echo "   ^ if these are data-dump commits only, safe to discard; if ANY is code/docs, STOP"

echo "[gate] stage 3 — commit-tree content diff: what FILES exist on origin/main but not HEAD"
comm -13 \
  <(git ls-tree -r --name-only HEAD | sort) \
  <(git ls-tree -r --name-only origin/main | sort) \
  | grep -vE '\.(pyc|log|gz|bak|before)$|^\.next/' | head -20 || true
echo "   ^ non-junk files unique to origin/main (empty or ignorable = safe to overwrite)"

echo "[gate] stage 4 — dirty tree recheck (was 14 pre-filter)"
git status --porcelain | head -15
echo "[banked] dirty count: $(git status --porcelain | wc -l)"

echo "[gate] stage 5 — object census"
git count-objects -vH
echo "[banked] blobs 5-10MB (below strip bar): "
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3 > 5000000 && $3 <= 10000000 {print $3, $4}' | sort -rn | head -10 || true

echo "[gate] stage 6 — exact expected push"
echo "[banked] force-push command: git push --force origin main"
echo "[held] DECISION POINT: stages 2-3 output determines go/no-go"
echo "[exit=0]"
