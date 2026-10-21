#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# master_finalize_v2.sh — supersedes v1: salvages BOTH master-unique test files, gates by
# RUNNING the tests (not py_compile), repoints master, purges bot branches, closes PR #59 (Path B),
# and banks the 13 untracked bin/ tools. DRY-RUN default, CONFIRM=1 executes.
# [canary] master_finalize_v2_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
WT=/tmp/wt-master-fin2
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }
say gate "master_finalize_v2 start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM"

git fetch origin --prune -q
say banked "dirty=$(git status --porcelain | wc -l) — preserved; work in $WT"

# [1] recompute master-unique paths AT RUNTIME (v1 hard-coded 1 file and was wrong — no hardcoded lists)
UNIQUE=$(git diff --name-status origin/main origin/master | awk '$1=="A"{print $2}')
say gate "master-unique files (runtime-computed):"; printf '%s\n' $UNIQUE | sed 's/^/    /'

if [ "$CONFIRM" != "1" ]; then
  say held "DRY-RUN — CONFIRM=1 will: salvage above into worktree, RUN tests as gate, push, repoint master, purge bot branches, close #59, bank untracked bin/"
  printf '[exit=0]\n'; exit 0
fi

# [2] PATH B: close stale-lineage PR #59 FIRST (stops bot pushing to its branch mid-flight)
if gh pr view 59 --json state --jq .state 2>/dev/null | grep -qx OPEN; then
  gh pr close 59 --comment "Closing stale-lineage PR: branch predates the filter-repo history rewrite (add/add conflicts across bin/). Please re-run your review against current main — fresh suggestions welcome." \
    && say banked "PR #59 closed"
fi

# [3] salvage ALL unique files in a worktree, gate by EXECUTING the tests
git worktree remove --force "$WT" 2>/dev/null || true
git worktree add --detach "$WT" origin/main
for F in $UNIQUE; do
  git -C "$WT" restore --source=origin/master -- "$F" && say banked "restored: $F"
done
git -C "$WT" add -A
git -C "$WT" diff --cached --quiet && { say banked "nothing to salvage"; exit 0; }

# REAL GATE: run the salvaged tests inside the worktree
cd "$WT"
if python3 -m unittest discover -s tests -p 'test_*.py' -v 2>&1 | tee /tmp/wt_test_out.txt; then
  say banked "unittest gate PASSED (all tests, not just salvaged ones)"
else
  RC=${PIPESTATUS[0]}
  say held "unittest FAILED (rc=$RC) — salvage aborted, NOTHING pushed. Inspect /tmp/wt_test_out.txt"
  cd "$REPO"; git worktree remove --force "$WT"; printf '[exit=0]\n'; exit 0
fi
cd "$REPO"

git -C "$WT" commit -m "salvage master-unique test suite (sqlite_params injection-binding + shell workflow tests) — unittest-executed gate passed in clean worktree; provenance: master_finalize_v2, human-gated" \
  && say banked "salvage commit $(git -C "$WT" rev-parse --short HEAD)"
git -C "$WT" push origin HEAD:main && say banked "salvage pushed to main"

# [4] bank the 13 untracked bin/ tools (same worktree, on top of fresh main)
git -C "$WT" pull --ff-only origin main -q 2>/dev/null || git -C "$WT" fetch origin main -q && git -C "$WT" reset --hard origin/main -q
for U in $(cd "$REPO" && git status --porcelain bin/ | awk '$1=="??"{print $2}' | grep -v '/$'); do
  cp "$REPO/$U" "$WT/$U" && git -C "$WT" add "$U" && say banked "banked untracked tool: $U"
done
if ! git -C "$WT" diff --cached --quiet; then
  PY_FAIL=0
  for F in $(git -C "$WT" diff --cached --name-only | grep '\.py$' || true); do
    python3 -m py_compile "$WT/$F" || { say held "py_compile FAIL: $F"; PY_FAIL=1; }
  done
  [ "$PY_FAIL" = "1" ] && { say held "bin/ banking aborted"; git worktree remove --force "$WT"; printf '[exit=0]\n'; exit 0; }
  grep -rl '^<<<<<<<\|^>>>>>>>' "$WT/bin" 2>/dev/null && { say held "conflict markers in bin/ — abort"; git worktree remove --force "$WT"; printf '[exit=0]\n'; exit 0; }
  git -C "$WT" commit -m "bank 13 untracked bin/ tools (incl. stack_gate.sh recovery) — py_compile + conflict-marker gates passed; provenance: master_finalize_v2" \
    && git -C "$WT" push origin HEAD:main && say banked "bin/ banked and pushed"
fi
git worktree remove --force "$WT"

# [5] master repoint + bot branch purge
git push origin origin/main:master --force && say banked "master REPOINTED to main"
for B in coderabbit/changes/eb9e4190 coderabbit/changes/3f27b749; do
  git ls-remote --heads origin "$B" | grep -q . && git push origin --delete "$B" && say banked "deleted $B"
done

say banked "final: main=$(git rev-parse --short origin/main) master=$(git rev-parse --short origin/master) — equal expected"
say banked "bin/: tracked=$(git ls-files bin/ | wc -l) (was 41, +13 expected)"
say banked "NEXT: README fill -> Reh1t #53 -> pin repos on profile"
printf '[exit=0]\n'
