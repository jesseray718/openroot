#!/usr/bin/env bash
# filter_pass2_safe_v1.sh — push locals, fresh mirror, CORRECT filter-repo, gated force-push
# CANARY:OPENROOT-FILTER-PASS2-SAFE-V1
# filter-repo uses --strip-blobs-bigger-than (generic, glob-free, same doctrine as pass 1)
set -eu
export GIT_PAGER=cat TERM=dumb
R=/home/jesse/openroot
cd "$R"

echo "[gate] stage 1 — untrack last monster (timeline.tsv, still in pending history)"
git rm --cached -q reports/gh-audit-20261008-194709/github_timeline.tsv 2>/dev/null || echo "[banked] already untracked"
git commit -q -m "hygiene v2b: untrack github_timeline.tsv (10MB, caught by numstat) [banked]" || echo "[banked] nothing to commit"
echo "[banked] HEAD: $(git rev-parse --short HEAD)"

echo "[gate] stage 2 — NORMAL push (no force) of local commits"
git push origin main
echo "[banked] pushed: $(git rev-parse --short HEAD) — today's work is safe on origin"

echo "[gate] stage 3 — discard stale mirror, re-clone post-push"
cd /home/jesse
rm -rf openroot-filter-temp   # STALE: predates today's commits — dead weight
git clone --mirror https://github.com/jesseray718/openroot.git openroot-filter-temp 2>&1 | tail -1
cd openroot-filter-temp
echo "[banked] mirror at: $(git rev-parse --short HEAD)"

echo "[gate] stage 4 — filter-repo (generic blob strip, mirrors pass-1 doctrine)"
git filter-repo --strip-blobs-bigger-than 10M --force
echo "[banked] filtered. sizes:"
du -sh /home/jesse/openroot-filter-temp
git rev-list --all --count
echo "   ^ commit count (changed hashes = rewrites happened)"

echo "[gate] stage 5 — verify mega-blobs are GONE from history"
BIG=$(git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $3 > 10000000 {print $4}' | head -5 || true)
if [ -n "$BIG" ]; then
  echo "[held] blobs >10MB STILL PRESENT — DO NOT PUSH:"
  echo "$BIG"
  exit 1
fi
echo "[banked] zero blobs >10MB in history — filter verified"

echo "[gate] stage 6 — force-push (BLAST RADIUS: rewrites origin history)"
if [ "${CONFIRM:-0}" = "1" ]; then
  git push --force origin
  echo "[banked] force-push complete"
  echo "[held] POST-PUSH MANDATORY: cd /home/jesse/openroot && git fetch origin && git reset --hard origin/main"
  echo "[held] and notify Reh1t (PR #53) — their clone just went stale AGAIN"
else
  echo "[held] dry-run only. Verified filter above; re-run with CONFIRM=1 to force-push"
fi
echo "[exit=0]"
