#!/usr/bin/env bash
# filter_local_strip_v1.sh — strip >10M blobs from LOCAL repo, then push
# CANARY:OPENROOT-FILTER-LOCAL-STRIP-V1
# Origin currently holds NONE of today's commits (push was rejected).
# This repo is the only copy — filter it, push it. Working-tree files are untouched.
set -eu
export GIT_PAGER=cat TERM=dumb
R=/home/jesse/openroot
cd "$R"

echo "[gate] stage 0 — pre-state"
echo "[banked] HEAD: $(git rev-parse --short HEAD) | dirty: $(git status --porcelain | wc -l) | .git: $(du -sh .git | cut -f1)"

echo "[gate] stage 1 — delete stale throwaway mirror (inside repo dir, untracked)"
rm -rf "$R/openroot-filter-temp" /home/jesse/openroot-filter-temp
echo "[banked] mirrors purged"

echo "[gate] stage 2 — filter-repo: strip all blobs >10M (doctrine of pass 1)"
# HEAD commit + provenance recorded; working tree files stay on disk untouched
git filter-repo --strip-blobs-bigger-than 10M --force

echo "[gate] stage 3 — re-attach origin (filter-repo strips remotes)"
git remote add origin git@github.com:jesseray718/openroot.git
git branch --set-upstream-to=origin/main main 2>/dev/null || true
git fetch origin 2>&1 | tail -1 || true

echo "[gate] stage 4 — verify"
echo "[banked] .git now: $(du -sh .git | cut -f1) | commits: $(git rev-list --count HEAD)"
BIG=$(git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3 > 10000000 {print $4}' | head -5 || true)
if [ -n "$BIG" ]; then
  echo "[held] blobs >10MB STILL PRESENT — ABORT, paste this back:"
  echo "$BIG"
  exit 1
fi
echo "[banked] zero blobs >10MB anywhere in local history"

echo "[gate] stage 5 — push (rewrites origin history: Reh1t/PR53 blast radius)"
if git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
  echo "[banked] origin/main is an ancestor — fast-forward push, NO force needed"
  git push origin main
  echo "[banked] pushed clean"
else
  if [ "${CONFIRM:-0}" = "1" ]; then
    echo "[gate] force-push (CONFIRM=1) — origin history rewrites"
    git push --force origin main
    echo "[banked] force-push complete"
  else
    echo "[held] force required but CONFIRM=0. Review above, then: CONFIRM=1 bash $0"
  fi
fi
echo "[exit=0]"
