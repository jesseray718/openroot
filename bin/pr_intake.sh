#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# pr_intake.sh — standardized external-PR intake for OpenRoot.
# Proven on PR #63 (Reh1t). Pipeline: fetch->isolate->conflict check->
# py_compile+SPDX audit->diff review->human CONFIRM->squash merge->
# contributor README credit->optional thanks comment.
# USAGE: bin/pr_intake.sh <PR_NUMBER> <CONTRIBUTOR_HANDLE> <SHORT_DESCRIPTION> [--thanks "message"]
# DRY-RUN by default; CONFIRM=1 executes merge. Human is the only commit gate.
set -eu
export GIT_PAGER=cat
cd /home/jesse/openroot

PR="${1:?usage: pr_intake.sh <PR#> <handle> <desc> [--thanks msg]}"
HANDLE="${2:?need contributor handle}"
DESC="${3:?need short description}"
THANKS="${5:-}"
BRANCH="pr-${PR}-audit"

echo "[stage 1] fetch + isolate PR ref"
git fetch origin "pull/${PR}/head:${BRANCH}"
echo "[banked] origin/main=$(git rev-parse --short origin/main)  pr_head=$(git rev-parse --short "$BRANCH")"

echo "[stage 2] merge-safety"
MERGE_BASE=$(git merge-base origin/main "$BRANCH" 2>/dev/null || echo "")
if [ -z "$MERGE_BASE" ]; then
  echo "[held] NO COMMON ANCESTOR (stale clone / pre-rewrite base)."
  echo "  Comment on PR asking contributor: git fetch origin && git rebase origin/main"
  exit 1
fi
if git merge-tree "$MERGE_BASE" "$BRANCH" origin/main 2>/dev/null | grep -qE "CONFLICT|changed in both"; then
  echo "[held] CONFLICTS — request rebase from $HANDLE. NO MERGE."
  exit 1
fi
echo "[banked] merge clean"

echo "[stage 3] changed-file inventory + audit — AUDIT BEFORE BUILDERS"
TMPD=$(mktemp -d /tmp/pr_intake.XXXXXX)
git diff --name-status origin/main..."$BRANCH" | tee "$TMPD/files.txt"
FAILS=0
while IFS=$'\t' read -r STATUS FPATH; do
  case "$FPATH" in
    *.py)
      git show "$BRANCH:$FPATH" > "$TMPD/audit.py"
      if python3 -m py_compile "$TMPD/audit.py" 2>"$TMPD/err"; then
        echo "  [banked] py_compile OK: $FPATH"
      else
        echo "  [held] py_compile FAIL: $FPATH — $(tail -1 "$TMPD/err")"; FAILS=$((FAILS+1))
      fi
      if head -5 "$TMPD/audit.py" | grep -q "SPDX-License-Identifier"; then
        echo "  [banked] SPDX: $FPATH"
      else
        echo "  [warn] no SPDX header: $FPATH"
      fi ;;
    *.db)
      echo "  [note] binary $FPATH committed — verify intentional" ;;
  esac
done < "$TMPD/files.txt"
rm -rf "$TMPD"
if [ "$FAILS" -gt 0 ]; then echo "[held] $FAILS gate failures. NO MERGE."; exit 1; fi
echo "[banked] gates green"

echo "[stage 4] diff summary — REVIEW BEFORE CONFIRMING"
git diff --stat origin/main..."$BRANCH"

if [ "${CONFIRM:-0}" = "1" ]; then
  echo "[stage 5] execute"
  [ -n "$THANKS" ] && gh pr comment "$PR" --body "$THANKS"
  gh pr merge "$PR" --squash --delete-branch
  git branch -D "$BRANCH" 2>/dev/null || true
  git pull --ff-only origin main
  echo "[stage 6] wire contributor credit into README"
  bash bin/readme_contributors.sh "$HANDLE" "$DESC"
  git add README.md
  git diff --cached --quiet || { git commit -m "docs(readme): credit $HANDLE ($DESC, PR #$PR)"; git push origin main; }
  echo "[banked] PR #$PR merged, $HANDLE credited in README"
else
  echo "[stage 5] DRY-RUN — rerun with CONFIRM=1 to merge+credit:"
  echo "  CONFIRM=1 bin/pr_intake.sh $PR '$HANDLE' '$DESC' [--thanks 'msg']"
fi
echo "[exit=0]"
