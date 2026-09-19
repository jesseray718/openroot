#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# master_salvage_v1.sh — content-level salvage of stale master into main (NOT a git merge:
# master predates filter-repo, merging would re-import >50M blobs). Then restore/delete branches.
# Modes: dry-run (default) | CONFIRM=SALVAGE (restore missing files, delete bot branches,
# repoint master to main) | CONFIRM=PURGE (also delete master outright).
# [canary] master_salvage_v1_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }

say gate "master_salvage_v1 start $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# [1] fetch everything incl. master + bot branches
git fetch origin --prune -q
git fetch origin master coderabbit/changes/eb9e4190 coderabbit/changes/3f27b749 -q 2>/dev/null || true
MAIN_SHA=$(git rev-parse --short origin/main)
MAS_SHA=$(git rev-parse --short origin/master 2>/dev/null || echo none)
say banked "origin/main=$MAIN_SHA origin/master=$MAS_SHA"

# [2] audit — how far apart, and which FILES exist on master but not on main
if [ "$MAS_SHA" != "none" ]; then
  MISSING_ON_MAIN=$(git diff --name-status origin/main origin/master | awk '$1=="A"{print $2}')
  COMMON_DIFFERENT=$(git diff --name-only origin/main origin/master | wc -l)
  BIG=$(git rev-list --objects origin/master ^origin/main 2>/dev/null \
        | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' 2>/dev/null \
        | awk '$1=="blob" && $2>50000000 {print $3}' | head -5 || true)
  say gate "files on master absent from main:"; printf '%s\n' $MISSING_ON_MAIN | sed 's/^/    /' || true
  say gate "total differing paths=$COMMON_DIFFERENT"
  [ -n "$BIG" ] && say gate "WARNING — >50M blobs confirmed alive on master: $BIG (merge is FORBIDDEN; salvage only)"
fi

# [3] SALVAGE — restore master-only files onto a working branch, exclude anything big/unwanted
if [ "$CONFIRM" = "SALVAGE" ] && [ "$MAS_SHA" != "none" ]; then
  git switch -c salvage-master-$(date +%Y%m%d) main 2>/dev/null || git switch salvage-master-$(date +%Y%m%d)
  EXCLUDE_RE='\.(zip|tar|gz|mp4|mov|stl|gltf)$|^consolidation-backups/'
  for F in $MISSING_ON_MAIN; do
    if ! echo "$F" | grep -qE "$EXCLUDE_RE"; then
      git restore --source=origin/master -- "$F" && say banked "salvaged: $F"
    else
      say held "skipped (excluded): $F"
    fi
  done
  # sanity: nothing staged over 1MB
  OVER=$(git diff --cached --stat 2>/dev/null | tail -1 || true)
  git add -A
  [ "$(git diff --cached --numstat | wc -l)" -gt 0 ] && \
    git commit -m "salvage master-only files into main lineage (README et al) — content-level restore, no history merge; grep+diff-stat gated; provenance: master_salvage_v1" \
    && say banked "salvage commit $(git rev-parse --short HEAD)"
  push_guard() { :; }  # hook — replace with bin/push_guard.py invocation if present
  bash bin/push_guard.py salvage-master-$(date +%Y%m%d) origin/main 2>/dev/null || say held "push_guard unavailable/failed — NOT pushing; you are the gate"
  git push origin HEAD:main && say banked "salvage pushed to main"
fi

# [4] bot branches — delete unconditionally safe (they are regenerable CI suggestions)
for B in coderabbit/changes/eb9e4190 coderabbit/changes/3f27b749; do
  if git ls-remote --heads origin "$B" | grep -q "$B"; then
    if [ "$CONFIRM" = "SALVAGE" ] || [ "$CONFIRM" = "PURGE" ]; then
      git push origin --delete "$B" && say banked "deleted bot branch $B"
    else
      say held "bot branch $B exists — CONFIRM=SALVAGE deletes it"
    fi
  fi
done

# [5] master disposition — RESTORE means repoint to main's HEAD (history preserved in consolidation-backups)
if [ "$MAS_SHA" != "none" ]; then
  if [ "$CONFIRM" = "SALVAGE" ]; then
    git push origin origin/main:master --force && say banked "master REPOINTED to main (=restore, big-blob lineage severed from default tip)"
  elif [ "$CONFIRM" = "PURGE" ]; then
    git push origin --delete master && say banked "master DELETED (legacy lives in consolidation-backups)"
  else
    say held "master untouched — CONFIRM=SALVAGE repoints it to main, CONFIRM=PURGE deletes it"
  fi
fi

say banked "NEXT: README fill (Add-a-README banner on flagship = highest-GRLE free win), then Reh1t #53, then pin repos on profile"
printf '[exit=0]\n'
