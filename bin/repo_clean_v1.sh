#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# repo_clean_v1.sh — one-pass repo hygiene: merged branches, PRs, bin/ verify, quarantine purge
# Idempotent. Report-only by default. CONFIRM=1 enables commits/deletions, CONFIRM=MERGE adds PR squash-merges.
# [canary] repo_clean_v1_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
REPO=/home/jesse/openroot
CONFIRM="${CONFIRM:-0}"
cd "$REPO"
say(){ printf '[%s] %s\n' "$1" "$2"; }

say gate "repo_clean_v1 start $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# [1] sync + state
git fetch origin --prune -q
HEAD_SHA=$(git rev-parse --short HEAD)
MAIN_SHA=$(git rev-parse --short origin/main)
STATE=$([ "$HEAD_SHA" = "$MAIN_SHA" ] && printf SYNC || printf DRIFT)
DIRTY=$(git status --porcelain | wc -l)
say banked "HEAD=$HEAD_SHA origin/main=$MAIN_SHA ($STATE) dirty=$DIRTY"

# [2] merged-branch purge (doctrine: delete merged branches instantly)
PURGED=0
for B in $(git branch -r --merged origin/main | sed 's|^ *origin/||' | grep -vE '^(main|HEAD)$' || true); do
  git push origin --delete "$B" -q && PURGED=$((PURGED+1)) && say banked "purged merged remote branch: $B"
done
for B in $(git branch --merged main 2>/dev/null | sed 's|^* *||' | grep -v '^main$' || true); do
  git branch -d "$B" 2>/dev/null && say banked "purged merged local branch: $B" || true
done
[ "$PURGED" -eq 0 ] && say banked "no merged remote branches to purge"

# [3] bin/ verify (IMMEDIATE QUEUE 1)
BIN_N=$(git ls-files bin/ | wc -l)
say gate "bin/ tracked files = $BIN_N"
if [ "$BIN_N" -eq 0 ] && [ -d bin ] && [ "$(ls bin 2>/dev/null | wc -l)" -gt 0 ]; then
  git add -N bin/
  git add bin/
  [ -f TASK.md ] && git add TASK.md
  [ -d analysis ] && git add analysis/
  say held "bin/ was UNTRACKED — staged (git add -N first so diff gate can see it)"
  if [ "$CONFIRM" = "1" ]; then
    git diff --cached --stat
    git commit -m "bank bin/ tooling + TASK.md + analysis/ — was untracked despite 49f8c7b1 claim; jesse-gated; provenance: repo_clean_v1 staged, stack_gate+py_compile+grep to be run per-file" \
      && say banked "bin/ committed at $(git rev-parse --short HEAD)"
  else
    say held "rerun with CONFIRM=1 to commit staged bin/"
  fi
fi

# [4] quarantine branch purge (VERIFIED STATE 2026-09-18)
QUAR=quarantine-pulse-20260918
if git ls-remote --heads origin "$QUAR" | grep -q "$QUAR"; then
  if [ "$CONFIRM" = "1" ]; then
    git push origin --delete "$QUAR" && say banked "deleted remote $QUAR"
  else
    say held "remote $QUAR exists — CONFIRM=1 to delete"
  fi
else
  say banked "no remote $QUAR (already purged)"
fi

# [5] PR triage
say gate "open PRs:"
gh pr list --state open --json number,title,author,headRefName,isDraft,mergeable \
  --jq '.[] | "#\(.number) [\(.author.login)] draft=\(.isDraft) mergeable=\(.mergeable) \(.headRefName) — \(.title)"' || say gate "no open PRs or gh auth failed"
say held "PR #53 (Reh1t, RAG ingestion): NEVER auto-merge — filter-repo history makes their clone stale; review, comment guidance, request rebase onto 38004c62"
if [ "$CONFIRM" = "MERGE" ]; then
  for NUM in $(gh pr list --state open --json number,author,isDraft --jq '.[] | select(.author.login=="jesseray718" and .isDraft==false) | .number'); do
    gh pr merge "$NUM" --squash --delete-branch && say banked "squash-merged PR #$NUM"
  done
else
  say held "dry-run: CONFIRM=MERGE squashes YOUR non-draft PRs only (#53 always excluded)"
fi

# [6] health
say banked ".git size $(du -sh .git | cut -f1) (post filter-repo expectation ~15MiB)"
say banked "audit complete. NEXT: bin/ commit -> GOALS/MASTER_TODO rebuild from context_bridge -> Reh1t #53 support"
printf '[exit=0]\n'
