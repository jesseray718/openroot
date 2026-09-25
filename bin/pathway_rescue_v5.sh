#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# pathway_rescue_v5.sh — diagnose held PRs + rescue additive content from conflicted PATHWAY PRs
# Logic: for each open PR, report mergeStateStatus. For [PATHWAY]-titled conflicted PRs:
#   files NOT on main -> committed directly to main (content rescue);
#   files already on main -> [held] for human. Then close PR as superseded, delete branch.
# openroot #59 untouched (not a pathway PR — your call). OpenCell #12 diagnosed, not forced.
# Canary: [PRV5] | Dry-run default. CONFIRM=1 executes rescues.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
ROOT="/home/jesse/openroot"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/context_bridge/pathway_rescue_v5_${TS}.md"
CANARY="[PRV5]"
MODE="${CONFIRM:-0}"

mkdir -p "$ROOT/context_bridge"
echo "# Pathway Rescue v5 ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"

banner() { echo ""; echo "${CANARY} ==== $1"; }

banner "PRE-FLIGHT [gate]"
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }
REPOS="$(gh repo list "$OWNER" --limit 200 --json nameWithOwner,isFork,isArchived \
  --jq '.[] | select(.isArchived==false and .isFork==false) | .nameWithOwner')"
echo "[gate] gh auth OK"

banner "STAGE 1 — DIAGNOSE ALL OPEN PRs"
while read -r r; do
  PRS="$(gh pr list -R "$r" --state open --json number,title,mergeStateStatus \
         --jq '.[] | [.number,.mergeStateStatus,.title] | @tsv' 2>/dev/null || true)"
  [ -z "$PRS" ] && continue
  while IFS=$'\t' read -r num mss title; do
    echo "[gate] $r #$num state=$mss — $title" | tee -a "$LOG"
  done <<< "$PRS"
done <<< "$REPOS"

banner "STAGE 2 — RESCUE ADDITIVE CONTENT FROM CONFLICTED [PATHWAY] PRs"
RESCUED=0; HELDF=0; SKIP=0
while read -r r; do
  PRS="$(gh pr list -R "$r" --state open --json number,title,headRefName,mergeStateStatus \
         --jq '.[] | [.number,.title,.headRefName,.mergeStateStatus] | @tsv' 2>/dev/null || true)"
  [ -z "$PRS" ] && continue
  while IFS=$'\t' read -r num title head mss; do
    case "$title" in "[PATHWAY]"*) ;; *) SKIP=$((SKIP+1)); continue ;; esac
    [ "$mss" != "DIRTY" ] && { echo "[held] $r #$head mss=$mss — not conflicted, left alone"; continue; }
    echo "[gate] rescuing $r PR#$num branch '$head'"
    FILES="$(gh pr view "$num" -R "$r" --json files --jq '.files[].path' 2>/dev/null || true)"
    NEWOK=1
    while read -r fp; do
      [ -z "$fp" ] && continue
      MAINSHA="$(gh api "repos/$r/contents/${fp}?ref=main" --jq '.sha' 2>/dev/null || echo "")"
      if [ -z "$MAINSHA" ]; then
        # additive file — fetch from branch, PUT to main
        B64="$(gh api "repos/$r/contents/${fp}?ref=${head}" --jq '.content' 2>/dev/null || echo "")"
        if [ -n "$B64" ] && [ "$MODE" = "1" ]; then
          if gh api -X PUT "repos/$r/contents/${fp}" \
            -f message="[RESCUE] $fp from $head (pathway content, human-gated)" \
            -f content="$B64" -f branch=main >> "$LOG" 2>&1; then
            echo "[banked] rescued NEW file $r:$fp"
          else
            echo "[held] PUT FAILED $r:$fp"; NEWOK=0; HELDF=$((HELDF+1)); fi
        else
          echo "[gate] dry: would rescue NEW file $r:$fp"; RESCUED=$((RESCUED+1)); fi
      else
        echo "[held] MODIFIED file $r:$fp — exists on main, human adjudication" | tee -a "$LOG"
        NEWOK=0; HELDF=$((HELDF+1)); fi
    done <<< "$FILES"
    # close + delete branch only if rescue was clean (or dry-run)
    if [ "$NEWOK" = "1" ]; then
      echo "[gate] close-and-supersede $r #$num" | tee -a "$LOG"
      [ "$MODE" = "1" ] && {
        gh pr close "$num" -R "$r" --comment \
          "Content rescued to main via direct commit; PR superseded (branch was conflicted beyond rebasing value). [AI-assisted, human-gated]" >> "$LOG" 2>&1 || true
        gh api -X DELETE "repos/$r/git/refs/heads/${head}" >> "$LOG" 2>&1 || true
      }
    fi
  done <<< "$PRS"
done <<< "$REPOS"
echo "[gate] rescued-new=$RESCUED modified-held=$HELDF non-pathway-skipped=$SKIP" | tee -a "$LOG"

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — review rescue list, then: CONFIRM=1 bash $0"
echo "${CANARY} [exit=0]"
exit 0
