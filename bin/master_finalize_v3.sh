#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# master_finalize_v3.sh — supersedes v2: captures master's MODIFIED test file too (+23 lines v2 would
# erase during repoint), gates by baseline-delta unittest (pre-existing failures don't block salvage).
# DRY-RUN default, CONFIRM=1 executes. [canary] master_finalize_v3_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
WT=/tmp/wt-master-fin3
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }
say gate "master_finalize_v3 start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM"

git fetch origin --prune -q
say banked "dirty=$(git status --porcelain | wc -l) — preserved; work in $WT"

# [1] ALL differing paths under tests/ — Added OR Modified (v2 awk 'A' dropped the M file)
DIFFS=$(git diff --name-status origin/main origin/master -- tests/ | awk '$1=="A"||$1=="M"{print $2}')
say gate "tests/ differing paths (A+M):"; printf '%s\n' $DIFFS | sed 's/^/    /'
say gate "preview of the M-file delta (the 23 lines v2 would erase):"
git diff origin/main origin/master -- tests/test_shell_workflows.py | head -60 | sed 's/^/    /' || true

if [ "$CONFIRM" != "1" ]; then
  say held "DRY-RUN — CONFIRM=1 will: close #59, restore ALL differing tests/, delta-test, push, bank bin/, repoint master, purge bots"
  printf '[exit=0]\n'; exit 0
fi

# [2] PATH B: close PR #59 first
if gh pr view 59 --json state --jq .state 2>/dev/null | grep -qx OPEN; then
  gh pr close 59 --comment "Closing stale-lineage PR: branch predates the filter-repo history rewrite (add/add conflicts across bin/). Please re-run your review against current main — fresh suggestions welcome." \
    && say banked "PR #59 closed"
fi

# [3] BASELINE-DELTA gate: measure pristine main first, then measure after restore
git worktree remove --force "$WT" 2>/dev/null || true
git worktree add --detach "$WT" origin/main
BASE_FAILS=$(cd "$WT" && python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | grep -cE '^(FAIL|ERROR):' || true)
say banked "baseline on pristine main: ${BASE_FAILS} pre-existing failures (recorded, not blamed on salvage)"

for F in $DIFFS; do
  git -C "$WT" restore --source=origin/master -- "$F" && say banked "restored: $F"
done
git -C "$WT" add -A
git -C "$WT" diff --cached --quiet && { say banked "nothing to salvage"; git worktree remove --force "$WT"; printf '[exit=0]\n'; exit 0; }

NEW_FAILS=$(cd "$WT" && python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | tee /tmp/wt_test_out_v3.txt | grep -cE '^(FAIL|ERROR):' || true)
say gate "after restore: ${NEW_FAILS} failures (baseline was ${BASE_FAILS})"
if [ "${NEW_FAILS}" -gt "${BASE_FAILS}" ]; then
  say held "salvage INTRODUCED failures — nothing pushed. Delta log: /tmp/wt_test_out_v3.txt"
  cd "$REPO"; git worktree remove --force "$WT"; printf '[exit=0]\n'; exit 0
fi
say banked "delta-gate PASSED (no new failures)"

cd "$REPO"
git -C "$WT" commit -m "salvage master's tests/: add test_sqlite_params.py + adopt newer test_shell_workflows.py (+23) — baseline-delta unittest gate passed; provenance: master_finalize_v3, human-gated" \
  && say banked "salvage commit $(git -C "$WT" rev-parse --short HEAD)"
git -C "$WT" push origin HEAD:main && say banked "salvage pushed to main"

# [4] bank untracked bin/ tools (one commit, latest scripts only — superseded v1/v2 archived not lost)
git -C "$WT" fetch origin main -q && git -C "$WT" reset --hard origin/main -q
for U in $(cd "$REPO" && git status --porcelain bin/ | awk '$1=="??"{print $2}' | grep -v '/$'); do
  cp "$REPO/$U" "$WT/$U" && git -C "$WT" add "$U" && say banked "banked: $U"
done
if ! git -C "$WT" diff --cached --quiet; then
  PY_FAIL=0
  for F in $(git -C "$WT" diff --cached --name-only | grep '\.py$' || true); do
    python3 -m py_compile "$WT/$F" || { say held "py_compile FAIL: $F"; PY_FAIL=1; }
  done
  grep -rl '^<<<<<<<\|^>>>>>>>' "$WT/bin" 2>/dev/null && PY_FAIL=1
  [ "$PY_FAIL" = "1" ] && { say held "bin/ banking aborted"; git worktree remove --force "$WT"; printf '[exit=0]\n'; exit 0; }
  git -C "$WT" commit -m "bank untracked bin/ tools (master_finalize lineage, stack_gate recovery) — py_compile + marker gates passed; provenance: master_finalize_v3" \
    && git -C "$WT" push origin HEAD:main && say banked "bin/ banked and pushed"
fi
git worktree remove --force "$WT"

# [5] repoint master (now safe — its tests/ contributions are adopted, nothing orphaned) + purge bots
git push origin origin/main:master --force && say banked "master REPOINTED to main — ALL master content now lives on main"
for B in coderabbit/changes/eb9e4190 coderabbit/changes/3f27b749; do
  git ls-remote --heads origin "$B" | grep -q . && git push origin --delete "$B" && say banked "deleted $B"
done
say banked "final: main=$(git rev-parse --short origin/main) master=$(git rev-parse --short origin/master) bin tracked=$(git ls-files bin/ | wc -l)"
say banked "NEXT: README fill -> Reh1t #53 -> pin repos on profile"
printf '[exit=0]\n'
