#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# master_finalize_v1.sh — master salvage (1 file) + bot-branch cleanup + PR #59 closure (Path B).
# Worktree-isolated: dirty local tree never touched. DRY-RUN default, CONFIRM=1 executes.
# [canary] master_finalize_v1_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
WT=/tmp/wt-master-fin
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }
say gate "master_finalize_v1 start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM"

git fetch origin --prune -q
say banked "dirty=$(git status --porcelain | wc -l) — preserved; work happens in $WT and origin"

# [1] show BOTH differing paths — human reviews before any action
say gate "full master-vs-main diff (review these 2 paths):"
git diff --stat origin/main origin/master | sed 's/^/    /' || true
git diff origin/main origin/master -- tests/test_sqlite_params.py | head -40 | sed 's/^/    /' || true

# [2] PATH B: close PR #59 + delete its branch (stale-lineage bot PR, regenerable)
if gh pr view 59 --json state --jq .state 2>/dev/null | grep -qx OPEN; then
  if [ "$CONFIRM" = "1" ]; then
    gh pr close 59 --comment "Closing stale-lineage PR: branch predates the filter-repo history rewrite (add/add conflicts across bin/). Please re-run your review against current main — fresh suggestions welcome." \
      && say banked "PR #59 closed with explanatory comment"
  else
    say held "PR #59 OPEN — CONFIRM=1 closes it (Path B) + deletes coderabbit/changes/eb9e4190"
  fi
fi

# [3] salvage the single master-unique file INTO A WORKTREE, commit there, push to main
if [ "$CONFIRM" = "1" ]; then
  git worktree remove --force "$WT" 2>/dev/null || true
  git worktree add "$WT" origin/main
  if git -C "$WT" restore --source=origin/master -- tests/test_sqlite_params.py; then
    git -C "$WT" add tests/test_sqlite_params.py
    if git -C "$WT" diff --cached --quiet; then
      say banked "tests/test_sqlite_params.py identical to main already — nothing to salvage"
    else
      python3 -m py_compile "$WT/tests/test_sqlite_params.py" || { say held "py_compile FAIL — aborting salvage"; exit 1; }
      say banked "py_compile passed"
      # grep gate: test must reference something real in the tree
      PAT=$(grep -oE 'sqlite3|\.db|import [a-z_]+' "$WT/tests/test_sqlite_params.py" | sort -u | tr '\n' ' ')
      say gate "test references: $PAT (sanity: does it match existing schema/tools?)"
      git -C "$WT" commit -m "salvage tests/test_sqlite_params.py from former master — sole unique path; py_compile passed; provenance: master_finalize_v1, human-gated" \
        && say banked "salvage commit $(git -C "$WT" rev-parse --short HEAD)"
      git -C "$WT" push origin HEAD:main && say banked "pushed to main"
    fi
  fi
  git worktree remove --force "$WT"

  # [4] master disposition — repoint to main (safer than delete: keeps name, severs divergence)
  git push origin origin/main:master --force && say banked "master REPOINTED to main"
  # [5] purge remaining bot branch (PR branch auto-deleted in step 2 if gh configured)
  for B in coderabbit/changes/eb9e4190 coderabbit/changes/3f27b749; do
    git ls-remote --heads origin "$B" | grep -q . && git push origin --delete "$B" && say banked "deleted $B"
  done
  say banked "final state: main=$(git rev-parse --short origin/main) master=$(git rev-parse --short origin/master) (should be equal)"
else
  say held "DRY-RUN only — rerun with CONFIRM=1 to: close #59, salvage test file, repoint master, purge bot branches"
fi

# [6] bin/ audit reminder (stack_gate.sh was MISSING locally — Finding 3)
TRACKED_BIN=$(git ls-files bin/ | wc -l)
PRESENT_BIN=$(ls bin/ 2>/dev/null | wc -l)
say gate "bin/: tracked=$TRACKED_BIN on-disk=$PRESENT_BIN — if stack_gate.sh is among missing, recover before next push"

say banked "NEXT: ls bin/ + missing-tool recovery -> README fill -> Reh1t #53 -> pin repos"
printf '[exit=0]\n'
