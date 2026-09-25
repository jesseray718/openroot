#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# pathway_closeout_v6.sh — blob-sha comparison for [PATHWAY] PRs → close if identical to main
# Canary: [PCV6] | Dry-run default. CONFIRM=1 executes closes+deletes.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
ROOT="/home/jesse/openroot"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/context_bridge/pathway_closeout_v6_${TS}.md"
CANARY="[PCV6]"
MODE="${CONFIRM:-0}"

mkdir -p "$ROOT/context_bridge"
echo "# Pathway Closeout v6 ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"

banner() { echo ""; echo "${CANARY} ==== $1"; }

banner "PRE-FLIGHT [gate]"
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }
REPOS="$(gh repo list "$OWNER" --limit 200 --json nameWithOwner,isFork,isArchived \
  --jq '.[] | select(.isArchived==false and .isFork==false) | .nameWithOwner')"
echo "[gate] gh auth OK"

banner "STAGE 1 — BLOB-SHA COMPARISON PER [PATHWAY] PR"
CLOSEABLE=0; HOLDPR=0
while read -r r; do
  PRS="$(gh pr list -R "$r" --state open --json number,title,headRefName,mergeStateStatus \
         --jq '.[] | [.number,.title,.headRefName,.mergeStateStatus] | @tsv' 2>/dev/null || true)"
  [ -z "$PRS" ] && continue
  while IFS=$'\t' read -r num title head mss; do
    case "$title" in "[PATHWAY]"*) ;; *) continue ;; esac
    FILES="$(gh pr view "$num" -R "$r" --json files --jq '.files[].path' 2>/dev/null || true)"
    IDENT=0; DIFF=0
    while read -r fp; do
      [ -z "$fp" ] && continue
      MS="$(gh api "repos/$r/contents/${fp}?ref=main" --jq '.sha' 2>/dev/null || echo "absent")"
      BS="$(gh api "repos/$r/contents/${fp}?ref=${head}" --jq '.sha' 2>/dev/null || echo "absent")"
      if [ "$MS" = "$BS" ]; then
        IDENT=$((IDENT+1))
      else
        DIFF=$((DIFF+1))
        BD="$(gh api "repos/$r/commits?sha=${head}&path=${fp}&per_page=1" --jq '.[0].commit.committer.date' 2>/dev/null || echo "?")"
        MD="$(gh api "repos/$r/commits?sha=main&path=${fp}&per_page=1" --jq '.[0].commit.committer.date' 2>/dev/null || echo "?")"
        echo "[held] DIFF $r:$fp branch@${BD} main@${MD}" | tee -a "$LOG"
      fi
    done <<< "$FILES"
    if [ "$DIFF" = "0" ]; then
      echo "[gate] $r #$num: all $IDENT files IDENTICAL to main — REDUNDANT, closeable" | tee -a "$LOG"
      if [ "$MODE" = "1" ]; then
        gh pr close "$num" -R "$r" --comment \
          "Closing: all content identical to main (blob-sha verified) — stale duplicate. [AI-assisted, human-gated]" \
          >> "$LOG" 2>&1
        gh api -X DELETE "repos/$r/git/refs/heads/${head}" >> "$LOG" 2>&1 || true
        echo "[banked] closed+deleted $r #$num '$head'"
      fi
      CLOSEABLE=$((CLOSEABLE+1))
    else
      echo "[held] $r #$num: $DIFF/$((IDENT+DIFF)) files differ — HUMAN ADJUDICATION" | tee -a "$LOG"
      HOLDPR=$((HOLDPR+1))
    fi
  done <<< "$PRS"
done <<< "$REPOS"
echo "[gate] redundant-closeable=$CLOSEABLE differ-held=$HOLDPR" | tee -a "$LOG"

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — review DIFF lines, then: CONFIRM=1 bash $0"
echo "${CANARY} [exit=0]"
exit 0
