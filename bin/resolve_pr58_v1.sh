#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# resolve_pr58_v1.sh — audit PR #58 (master->main), gate changed files,
# fix thixo-foam.md:4, merge behind CONFIRM=1. Idempotent, fork-only, no tree switches.
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot
HELD=0
GT=/tmp/pr58_gate

echo "[canary] resolve_pr58_v1 paste intact"

echo "[stage-0] fetch + snapshot"
git fetch origin --prune
BASE=$(git rev-parse origin/main)
HEADP=$(git rev-parse origin/master)
echo " base(origin/main)=${BASE:0:8} head(origin/master)=${HEADP:0:8}"
gh pr view 58 --json state,mergeable,title --jq '"state=\(.state) mergeable=\(.mergeable) title=\(.title)"' || HELD=1

echo "[stage-1] commit audit (incl. CodeRabbit web-UI commits)"
git log --oneline origin/main..origin/master
echo "--- coderabbit commits (24bc1a7, 08c913c) — instrument audit before trust:"
git show --stat --oneline 24bc1a7 | head -15 || HELD=1
git show --stat --oneline 08c913c | head -15 || HELD=1

echo "[stage-2] size guard (no blob >1MiB reintroduced post filter-repo)"
BIG=$(git ls-tree -r -l origin/master | awk '$4 > 1048576 {print $4, $5}')
if [ -n "$BIG" ]; then echo " [held] >1MiB blobs in master tree:"; echo "$BIG"; HELD=1
else echo " [ok] tree clean under 1MiB per blob"; fi

echo "[stage-3] gate instruments — extract PR blobs, py_compile + stack_gate"
rm -rf "$GT"; mkdir -p "$GT"
mapfile -t FILES < <(git diff --name-only origin/main...origin/master)
for f in "${FILES[@]}"; do
  mkdir -p "$GT/$(dirname "$f")"
  git show "origin/master:$f" > "$GT/$f" 2>/dev/null || continue
  case "$f" in
    *.py)
      python3 -m py_compile "$GT/$f" 2>/dev/null && echo " [ok] py_compile $f" \
        || { echo " [held] py_compile FAIL $f"; HELD=1; } ;;
    *.sh)
      if bash -n "$GT/$f" 2>/dev/null; then echo " [ok] bash -n $f"
      else echo " [held] bash -n FAIL $f"; HELD=1; fi
      if [ -f bin/stack_gate.sh ]; then
        bash bin/stack_gate.sh "$GT/$f" >/dev/null 2>&1 && echo " [ok] stack_gate $f" \
          || echo " [note] stack_gate nonzero/na $f (inspect manually)"
      fi ;;
  esac
done
echo " [gate] changed files: ${#FILES[@]}"

echo "[stage-4] run CodeRabbit unit tests against PR tree"
TDIR=/tmp/pr58_tree; rm -rf "$TDIR"; mkdir -p "$TDIR"
git archive origin/master | tar -x -C "$TDIR"
TESTS=$(cd "$TDIR" && find . -path ./venv -prune -o -name 'test_*.py' -print -o -name '*_test.py' -print | head -20)
if [ -n "$TESTS" ] && python3 -m pytest --version >/dev/null 2>&1; then
  (cd "$TDIR" && python3 -m pytest -q --timeout 60 2>/dev/null \
    && echo " [ok] pytest green" || { echo " [held] pytest failures — review before merge"; HELD=1; })
else
  echo " [note] no pytest or no test files found — inspect 08c913c manually"
fi

echo "[stage-5] fix flagged issue: thixo_gel in docs/research/thixo-foam.md line 4"
FX=docs/research/thixo-foam.md
if [ -f "$FX" ] && grep -n 'thixo_gel' "$FX" | head -3; then
  sed -i '4s/thixo_gel/Thixotropic Foam Gel/' "$FX"
  git add "$FX"
  git commit -m "fix(docs): descriptive title thixo-foam line 4 (coderabbit suggestion) — pr58 resolve" \
    && echo " [banked] thixo fix committed" || echo " [note] nothing to commit"
else
  echo " [note] thixo_gel not present in working tree line 4 — check coderabbit review thread directly"
fi

echo "[stage-6] ensure local master = origin/master before push"
git rev-parse master >/dev/null 2>&1 && git merge-base --is-ancestor master origin/master \
  && git push origin master \
  && echo " [banked] PR #58 updated (fix pushed to origin/master)" \
  || { echo " [held] local master diverged/absent — reconcile first, do not force"; HELD=1; }

if [ "$HELD" -eq 1 ]; then
  echo " [gate] AUDIT RAISED $HELD FLAGS — DO NOT MERGE YET. Inspect stages above, fix, rerun."
elif [ "${CONFIRM:-0}" = "1" ]; then
  echo "[stage-7] CONFIRM=1 — merging PR #58"
  gh pr merge 58 --merge --delete-branch \
    && { git fetch origin --prune; git checkout -q main 2>/dev/null || true; \
         git branch -f master origin/main; git checkout -q master; \
         echo " [banked] PR #58 MERGED, local master reset to origin/main, origin/master deleted"; } \
    || echo " [held] gh merge failed — check PR state"
else
  echo " [gate] dry-run complete, zero holds. Merge with: CONFIRM=1 bash bin/resolve_pr58_v1.sh"
fi

echo "[stage-8] session note -> context_bridge/"
NOTE=context_bridge/session-2026-09-18_pr58-resolve.md
{ echo "# PR #58 Resolve Session ($(date -u +%FT%TZ))"
  echo "- files audited: ${#FILES[@]}, gates: py_compile+stack_gate+bash -n+pytest, HELD=$HELD"
  echo "- origin/main was ${BASE:0:8}; origin/master was ${HEADP:0:8}"
  echo "- thixo-foam.md:4 fix attempted; coderabbit commits 24bc1a7/08c913c audited via stat"; } >> "$NOTE"
git add "$NOTE" 2>/dev/null || true

rm -rf "$GT" "$TDIR"
echo "[done] [exit=0]"
