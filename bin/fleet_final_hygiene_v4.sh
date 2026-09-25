#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# fleet_final_hygiene_v4.sh — purge uplift debris + open pathways + squash-merge ALL open PRs
# v4 delta: kills log-reparse (root cause of v3 no-op); TSV-driven execution; final
#   fleet-wide squash-merge of every mergeable open PR. CONFLICTING PRs held for human.
# Canary: [FH4V4] | Dry-run by default. CONFIRM=1 executes.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
ROOT="/home/jesse/openroot"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$ROOT/context_bridge/fleet_final_hygiene_v4_${TS}.md"
TSV="$(mktemp /tmp/fleet_v4_${TS}_XXXXXX.tsv)"
CANARY="[FH4V4]"
MODE="${CONFIRM:-0}"

mkdir -p "$ROOT/context_bridge"
echo "# Fleet Final Hygiene v4 ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"

banner() { echo ""; echo "${CANARY} ==== $1"; }

is_trivial_file() {
  case "$1" in
    .github/*|*.md|LICENSE|*.gitignore|CODEOWNERS|.editorconfig|\
    pyproject.toml|ruff.toml|.flake8|setup.cfg|requirements*.txt|\
    .pre-commit-config.yaml|Makefile|.gitmodules|dependabot.yml|\
    .openrabbit.json|.openrabbit.yml|openrabbit.json|openrabbit.yml) return 0 ;;
    *) return 1 ;;
  esac
}

banner "PRE-FLIGHT [gate]"
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }
REPOS="$(gh repo list "$OWNER" --limit 200 --json nameWithOwner,isFork,isArchived \
  --jq '.[] | select(.isArchived==false and .isFork==false) | .nameWithOwner')"
echo "[gate] gh auth OK as ${OWNER}"

# ---------- STAGE 1: CLASSIFY uplift branches -> TSV (repo TAB branch TAB action) ----------
banner "STAGE 1 — CLASSIFY"
SCAN=0
while read -r r; do
  DEFBR="$(gh repo view "$r" --json defaultBranchRef --jq '.defaultBranchRef.name')"
  BRANCHES="$(gh api "repos/$r/branches?per_page=100" --jq '.[].name' 2>/dev/null || true)"
  OPEN_HEADS="$(gh pr list -R "$r" --state open --json headRefName --jq '.[].headRefName')"
  while read -r b; do
    case "$b" in
      chore/uplift-*|chore/foundation-uplift-*|chore/knowledge-unify-*) ;;
      *) continue ;;
    esac
    [ -n "$(grep -Fx "$b" <<< "$OPEN_HEADS" 2>/dev/null)" ] && continue
    SCAN=$((SCAN+1))
    FILES_JSON="$(gh api "repos/$r/compare/${DEFBR}...${b}" --jq '[.files[].filename]' 2>/dev/null || echo "ERR")"
    if [ "$FILES_JSON" = "ERR" ] || [ "$FILES_JSON" = "[]" ]; then continue; fi
    TRIV=1
    while IFS= read -r f; do is_trivial_file "$f" || TRIV=0; done < <(echo "$FILES_JSON" | jq -r '.[]')
    if [ "$TRIV" = "1" ]; then
      printf '%s\t%s\tPURGE\n' "$r" "$b" >> "$TSV"
      echo "[banked] PURGE  $r '$b'"
    else
      printf '%s\t%s\tPR\n' "$r" "$b" >> "$TSV"
      echo "[gate] PR-OPEN $r '$b' — $(echo "$FILES_JSON" | jq -r 'join(", ")')"
    fi
  done <<< "$BRANCHES"
done <<< "$REPOS"
P_CNT=$(grep -c $'\tPURGE$' "$TSV" || true); P_CNT=${P_CNT:-0}
R_CNT=$(grep -c $'\tPR$' "$TSV" || true); R_CNT=${R_CNT:-0}
echo "[gate] classified: purge=$P_CNT pr-open=$R_CNT (scan=$SCAN)" | tee -a "$LOG"
echo "--- TSV head ---"; head -n 5 "$TSV"

# ---------- STAGE 2: EXECUTE classification actions ----------
if [ "$MODE" = "1" ]; then
  banner "STAGE 2 — EXECUTE"
  DEL=0; OPENED=0
  while IFS=$'\t' read -r r b act; do
    [ -z "$r" ] && continue
    case "$act" in
      PURGE)
        if gh api -X DELETE "repos/${r}/git/refs/heads/${b}" >> "$LOG" 2>&1; then
          DEL=$((DEL+1)); echo "[banked] deleted $r '$b'"
        else
          echo "[held] delete FAILED $r '$b'" | tee -a "$LOG"
        fi ;;
      PR)
        if URL="$(gh pr create -R "$r" --head "$b" \
          --title "[PATHWAY] $b — uplift content, never adjudicated" \
          --body "Pathway to main for uplift-era content that never received a PR. [AI-assisted, human-gated] Source: fleet_final_hygiene_v4 ${TS}")"; then
          OPENED=$((OPENED+1)); echo "[banked] PR opened $r '$b' -> $URL" | tee -a "$LOG"
        else
          echo "[held] PR create FAILED $r '$b' — check output above" | tee -a "$LOG"
        fi ;;
    esac
  done < "$TSV"
  echo "[gate] deleted=$DEL prs-opened=$OPENED" | tee -a "$LOG"
else
  banner "STAGE 2 — SKIPPED (dry-run)"
fi

# ---------- STAGE 3: SQUASH-MERGE ALL OPEN PRs FLEET-WIDE ----------
banner "STAGE 3 — SQUASH-MERGE ALL OPEN PRs"
TM=0; TH=0
while read -r r; do
  PRS="$(gh pr list -R "$r" --state open --json number,title,mergeable,author \
         --jq '.[] | [.number,.mergeable,.author.login,.title] | @tsv' 2>/dev/null || true)"
  [ -z "$PRS" ] && continue
  while IFS=$'\t' read -r num mst author title; do
    if [ "$mst" = "MERGEABLE" ]; then
      echo "[banked] merge $r #$num ($author) '$title'"
      if [ "$MODE" = "1" ]; then
        gh pr merge "$num" -R "$r" --squash --delete-branch \
          --subject "[MERGE] #${num} ${title} (${author}) [AI-assisted, human-gated]" \
          >> "$LOG" 2>&1 && TM=$((TM+1)) || TH=$((TH+1))
      else TM=$((TM+1)); fi
    else
      echo "[held] $r #$num mergeable=$mst '$title' — HUMAN GATE"; TH=$((TH+1)); fi
  done <<< "$PRS"
done <<< "$REPOS"
echo "[gate] squash-merged=$TM held=$TH" | tee -a "$LOG"

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
rm -f "$TSV"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — review, then: CONFIRM=1 bash /home/jesse/openroot/bin/fleet_final_hygiene_v4.sh"
echo "${CANARY} [exit=0]"
exit 0
