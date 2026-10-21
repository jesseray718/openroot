#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# fleet_squash_hygiene_v2.sh — squash-merge all PRs + fork-aware branch purge + dup-issue triage
# Canary: [FSQHYGV2] | Dry-run by default. CONFIRM=1 executes.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
ROOT="/home/jesse/openroot"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/context_bridge/fleet_squash_hygiene_v2_${TS}.md"
CANARY="[FSQHYGV2]"
MODE="${CONFIRM:-0}"

mkdir -p "$ROOT/context_bridge" "$ROOT/bin"
echo "# Fleet Hygiene v2 ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"

banner() { echo ""; echo "${CANARY} ================================"; echo "${CANARY} == $1"; }

banner "PRE-FLIGHT [gate]"
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }
echo "[gate] gh auth OK as ${OWNER}"

REPOS="$(gh repo list "$OWNER" --limit 200 --json nameWithOwner,isArchived \
  --jq '.[] | select(.isArchived==false) | .nameWithOwner')"
R_COUNT=0
while read -r r; do R_COUNT=$((R_COUNT+1)); done <<< "$REPOS"
echo "[gate] $R_COUNT repos enumerated" | tee -a "$LOG"

banner "STAGE 1 — SQUASH-MERGE OPEN PRs"
MERGED=0; HELD=0
while read -r r; do
  PRS="$(gh pr list -R "$r" --state open --json number,title,headRefName,author,mergeable \
         --jq '.[] | [.number,.mergeable,.headRefName,.author.login,.title] | @tsv' 2>/dev/null || true)"
  [ -z "$PRS" ] && continue
  while IFS=$'\t' read -r num mstate head author title; do
    if [ "$mstate" = "MERGEABLE" ]; then
      echo "[banked] $r #$num ($author) -> squash+delete-branch"
      if [ "$MODE" = "1" ]; then
        gh pr merge "$num" -R "$r" --squash --delete-branch \
          --subject "[MERGE] #${num} ${title} (${author}) [AI-assisted, human-gated]" \
          >> "$LOG" 2>&1 && MERGED=$((MERGED+1)) || HELD=$((HELD+1))
      else MERGED=$((MERGED+1)); fi
    else
      echo "[held] $r #$num mergeable=$mstate — DEFER TO HUMAN"; HELD=$((HELD+1)); fi
  done <<< "$PRS"
done <<< "$REPOS"
echo "[gate] merged=$MERGED held=$HELD" | tee -a "$LOG"

banner "STAGE 2 — BRANCH PURGE (forks EXEMPT)"
PURGED=0; FORKS=0
while read -r r; do
  ISFORK="$(gh repo view "$r" --json isFork --jq '.isFork' 2>/dev/null || echo "false")"
  if [ "$ISFORK" = "true" ]; then
    echo "[held] $r is a FORK — branches exempt"; FORKS=$((FORKS+1)); continue; fi
  DEFBR="$(gh repo view "$r" --json defaultBranchRef --jq '.defaultBranchRef.name')"
  BRANCHES="$(gh api "repos/$r/branches?per_page=100" --jq '.[].name' 2>/dev/null || true)"
  OPEN_HEADS="$(gh pr list -R "$r" --state open --json headRefName --jq '.[].headRefName')"
  while read -r b; do
    [ "$b" = "$DEFBR" ] && continue
    [ -n "$(grep -Fx "$b" <<< "$OPEN_HEADS" 2>/dev/null)" ] && continue
    AHEAD="$(gh api "repos/$r/compare/${DEFBR}...${b}" --jq '.ahead_by' 2>/dev/null || echo "err")"
    if [ "$AHEAD" = "0" ]; then
      echo "[banked] purge $r '$b'"
      if [ "$MODE" = "1" ]; then
        gh api -X DELETE "repos/$r/git/refs/heads/$b" >> "$LOG" 2>&1 || true
      fi
      PURGED=$((PURGED+1))
    else
      echo "[held] $r '$b' ahead=$AHEAD — HUMAN REVIEW"
    fi
  done <<< "$BRANCHES"
done <<< "$REPOS"
echo "[gate] purged=$PURGED fork-exempt=$FORKS" | tee -a "$LOG"

banner "STAGE 3 — DUPLICATE ISSUES (keep-higher/close-lower)"
CLOSED=0
while read -r r; do
  DUP_TITLES="$(gh issue list -R "$r" --state open --json number,title \
    --jq 'group_by(.title) | map(select(length > 1)) | .[].title' 2>/dev/null || true)"
  [ -z "$DUP_TITLES" ] && continue
  while read -r t; do
    [ -z "$t" ] && continue
    NUMS="$(gh issue list -R "$r" --state open --json number,title \
      --jq --arg t "$t" 'map(select(.title == $t)) | sort_by(.number) | .[].number')"
    LOWER="$(head -n 1 <<< "$NUMS")"
    KEEP="$(tail -n 1 <<< "$NUMS")"
    [ "$LOWER" = "$KEEP" ] && continue
    echo "[gate] $r '$t': close #${LOWER}, keep #${KEEP}"
    if [ "$MODE" = "1" ]; then
      gh issue close "$LOWER" -R "$r" \
        --comment "Closed as duplicate of #${KEEP} (keep-higher-number convention). [AI-assisted, human-gated]" \
        >> "$LOG" 2>&1 || true
      CLOSED=$((CLOSED+1))
    else CLOSED=$((CLOSED+1)); fi
  done <<< "$DUP_TITLES"
done <<< "$REPOS"
echo "[gate] dups closed: $CLOSED" | tee -a "$LOG"

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
cat <<EOR >> "$LOG"

## Handoff v2 ${TS}
- repos: ${R_COUNT} | forks-exempt: ${FORKS}
- PRs: merged=${MERGED} held=${HELD}
- branches purged: ${PURGED}
- dups closed: ${CLOSED}
- mode: $([ "$MODE" = "1" ] && echo EXECUTED || echo DRY-RUN)
EOR
echo "${CANARY} log sealed: ${LOG} [banked]"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — run: CONFIRM=1 bash /home/jesse/openroot/bin/fleet_squash_hygiene_v2.sh"
echo "${CANARY} [exit=0]"
exit 0
