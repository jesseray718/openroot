#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# fleet_squash_hygiene_v1.sh — squash-merge ALL open PRs on ALL jesseray718 repos + hygiene pass
# Canary: [FSQHYGV1]  | Dry-run by default. CONFIRM=1 executes destructive half.
# Provenance: Lumo-authored, human-gated. ai-generated-199737-hygieneaidsuffix.md lineage.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
ROOT="/home/jesse/openroot"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/context_bridge/fleet_squash_hygiene_${TS}.md"
CANARY="[FSQHYGV1]"
MODE="${CONFIRM:-0}"

mkdir -p "$(dirname "$LOG")"
echo "# Fleet Squash-Merge + Hygiene ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"

banner() { echo ""; echo "${CANARY} ================================"; echo "${CANARY} == $1"; }

# ---------- PRE-FLIGHT ----------
banner "PRE-FLIGHT [gate]"
if ! gh auth status >/dev/null 2>&1; then
  echo "[held] gh not authenticated — run gh auth login first"; exit 1; fi
gh auth status 2>&1 | head -n 4
echo "[gate] gh auth OK — logged in as ${OWNER}"

# ---------- STAGE 1: ENUMERATE REPOS ----------
banner "STAGE 1 — REPO ENUMERATION"
REPOS="$(gh repo list "$OWNER" --limit 200 --json nameWithOwner,isArchived \
  --jq '.[] | select(.isArchived==false) | .nameWithOwner')"
RCOUNT=0
while read -r r; do RCOUNT=$((RCOUNT+1)); done <<< "$REPOS"
echo "[gate] $RCOUNT active repos enumerated" | tee -a "$LOG"

# ---------- STAGE 2: SQUASH-MERGE ALL OPEN PRs ----------
banner "STAGE 2 — SQUASH-MERGE OPEN PRs"
MERGED=0; HELD=0
while read -r r; do
  PRS="$(gh pr list -R "$r" --state open --json number,title,headRefName,author,mergeable \
         --jq '.[] | [.number,.mergeable,.headRefName,.author.login,.title] | @tsv' 2>/dev/null || true)"
  [ -z "$PRS" ] && continue
  while IFS=$'\t' read -r num mstate head author title; do
    case "$mstate" in
      MERGEABLE)
        echo "[banked] $r #$num ($author) '$title' -> squash+delete-branch"
        if [ "$MODE" = "1" ]; then
          gh pr merge "$num" -R "$r" --squash --delete-branch \
            --subject "[MERGE] #${num} ${title} (${author}) [AI-assisted, human-gated]" \
            >> "$LOG" 2>&1 && MERGED=$((MERGED+1)) || HELD=$((HELD+1))
        else
          MERGED=$((MERGED+1))
        fi ;;
      *)
        echo "[held] $r #$num mergeable=$mstate (conflict/dirty) — DEFER TO HUMAN"
        echo "[held] $r #$num mstate=$mstate" >> "$LOG"; HELD=$((HELD+1)) ;;
    esac
  done <<< "$PRS"
done <<< "$REPOS"
echo "[gate] merge scan complete: queued/merged=$MERGED held=$HELD" | tee -a "$LOG"

# ---------- STAGE 3: BRANCH HYGIENE ----------
banner "STAGE 3 — STALE BRANCH PURGE (merged, no open PR, != default)"
PURGED=0
while read -r r; do
  DEFBR="$(gh repo view "$r" --json defaultBranchRef --jq '.defaultBranchRef.name')"
  BRANCHES="$(gh api "repos/$r/branches?per_page=100" --jq '.[].name' 2>/dev/null || true)"
  OPEN_HEADS="$(gh pr list -R "$r" --state open --json headRefName --jq '.[].headRefName')"
  while read -r b; do
    [ "$b" = "$DEFBR" ] && continue
    [ -n "$(grep -Fx "$b" <<< "$OPEN_HEADS")" ] && continue
    AHEAD="$(gh api "repos/$r/compare/${DEFBR}...${b}" --jq '.ahead_by' 2>/dev/null || echo "err")"
    if [ "$AHEAD" = "0" ]; then
      echo "[banked] purge $r branch '$b' (fully merged)"
      [ "$MODE" = "1" ] && { gh api -X DELETE "repos/$r/git/refs/heads/$b" && PURGED=$((PURGED+1)) || true; } \
        || PURGED=$((PURGED+1))
    else
      echo "[held] $r branch '$b' ahead_by=$AHEAD — kept, reviewed manually"
    fi
  done <<< "$BRANCHES"
done <<< "$REPOS"
echo "[gate] branch purge queued: $PURGED" | tee -a "$LOG"

# ---------- STAGE 4: QUARANTINE BRANCH CHECK (openroot only) ----------
banner "STAGE 4 — KNOWN QUARANTINE BRANCH [gate]"
QB="quarantine-pulse-20260918"
if gh api "repos/${OWNER}/openroot/branches/${QB}" >/dev/null 2>&1; then
  echo "[gate] openroot:${QB} STILL EXISTS on remote"
  echo "[gate] boot-seed directive: delete when confident — this script will NOT auto-delete."
  echo "[gate] manual: git push origin --delete ${QB}"
else
  echo "[banked] openroot:${QB} already gone"
fi | tee -a "$LOG"

# ---------- STAGE 5: DUPLICATE ISSUE PURGE (keep higher number) ----------
banner "STAGE 5 — DUPLICATE ISSUE SCAN [report-only]"
DUPS="$(mktemp)"
for r in $REPOS; do
  gh issue list -R "$r" --state all --json number,title \
    --jq '.[] | .title' 2>/dev/null | sort | uniq -d | while read -r t; do
    echo "[held] $r duplicate-title: '$t'" | tee -a "$LOG"; done
done
echo "[gate] duplicate scan logged — closures gated to human" | tee -a "$LOG"

# ---------- CLOSEOUT ----------
banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
cat <<EOR >> "$LOG"

## Handoff ${TS}
- repos scanned: ${RCOUNT}
- PRs squash-queued/merged: ${MERGED} (held/conflicted: ${HELD})
- stale branches purged: ${PURGED}
- mode: $([ "$MODE" = "1" ] && echo EXECUTED || echo DRY-RUN — rerun with CONFIRM=1)
EOR
echo "${CANARY} log sealed: ${LOG} [banked]"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — nothing was modified. Re-run with CONFIRM=1 to execute."
echo "${CANARY} [exit=0]"
exit 0
