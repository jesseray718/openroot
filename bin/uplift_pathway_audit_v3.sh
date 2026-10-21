#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# uplift_pathway_audit_v3.sh — audit PR-pathways-to-main for uplift debris branches
# Classes: MERGED (residue) | CLOSED-REJECTED (decision exists) | NO-PATHWAY (never adjudicated)
# CONFIRM=1: purges MERGED + CLOSED branches; opens PRs for NO-PATHWAY substantive ones.
# Canary: [UPAV3] | Dry-run by default
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="/home/jesse/openroot/context_bridge/pathway_audit_${TS}.md"
CANARY="[UPAV3]"
MODE="${CONFIRM:-0}"

mkdir -p /home/jesse/openroot/context_bridge
echo "# Pathway Audit v3 ${TS}" > "$LOG"
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
echo "[gate] gh auth OK"

banner "STAGE 1 — PATHWAY CLASSIFICATION"
SCANNED=0; MERGED=0; REJECTED=0; NOPATH_TRIV=0; NOPATH_SUB=0
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
    SCANNED=$((SCANNED+1))
    # ALL PRs ever, for this head branch
    PR_HISTORY="$(gh pr list -R "$r" --state all --json number,state,headRefName \
      --jq --arg h "$b" 'map(select(.headRefName == $h)) | sort_by(.number)' 2>/dev/null || echo "[]")"
    PR_COUNT="$(echo "$PR_HISTORY" | jq 'length')"
    HAS_MERGED="$(echo "$PR_HISTORY" | jq '[.[] | select(.state=="MERGED")] | length')"
    HAS_CLOSED="$(echo "$PR_HISTORY" | jq '[.[] | select(.state=="CLOSED")] | length')"

    if [ "$HAS_MERGED" -gt 0 ]; then
      echo "[banked] MERGED-RESIDUE $r '$b' (PR#$(echo "$PR_HISTORY" | jq -r '[.[]|select(.state=="MERGED")][0].number'))"
      echo "[banked] MERGED $r '$b'" >> "$LOG"; MERGED=$((MERGED+1))
    elif [ "$HAS_CLOSED" -gt 0 ]; then
      echo "[banked] CLOSED-REJECTED $r '$b' (PR#$(echo "$PR_HISTORY" | jq -r '[.[]|select(.state=="CLOSED")][0].number'))"
      echo "[banked] REJECTED $r '$b'" >> "$LOG"; REJECTED=$((REJECTED+1))
    else
      # No PR ever existed — classify payload
      FILES_JSON="$(gh api "repos/$r/compare/${DEFBR}...${b}" --jq '[.files[].filename]' 2>/dev/null || echo "ERR")"
      if [ "$FILES_JSON" = "ERR" ] || [ "$FILES_JSON" = "[]" ]; then
        echo "[held] $r '$b' — orphan/no-diff"; continue; fi
      TRIV=1
      while IFS= read -r f; do is_trivial_file "$f" || TRIV=0; done < <(echo "$FILES_JSON" | jq -r '.[]')
      if [ "$TRIV" = "1" ]; then
        echo "[held] NO-PATHWAY-TRIVIAL $r '$b' — bot droppings never offered; purge candidate"
        echo "[held] NOPATH-TRIV $r '$b'" >> "$LOG"; NOPATH_TRIV=$((NOPATH_TRIV+1))
      else
        echo "[gate] NO-PATHWAY-SUBSTANTIVE $r '$b' — $(echo "$FILES_JSON" | jq -r 'join(", ")')"
        echo "[gate] NOPATH-SUB $r '$b': $(echo "$FILES_JSON" | jq -r 'join(", ")')" >> "$LOG"
        NOPATH_SUB=$((NOPATH_SUB+1))
      fi
    fi
  done <<< "$BRANCHES"
done <<< "$REPOS"
echo "[gate] scanned=$SCANNED merged-residue=$MERGED rejected=$REJECTED nopath-trivial=$NOPATH_TRIV nopath-substantive=$NOPATH_SUB" | tee -a "$LOG"

if [ "$MODE" = "1" ]; then
  banner "STAGE 2 — EXECUTE"
  P=0
  # purge merged + rejected + no-pathway-trivial
  while read -r line; do
    r="$(cut -d' ' -f2 <<< "$line")"; b="$(cut -d' ' -f3 <<< "$line" | tr -d "'")"
    gh api -X DELETE "repos/${r}/git/refs/heads/${b}" >> "$LOG" 2>&1 && P=$((P+1)) || true
  done < <(grep -E '^\[(banked|held)\] (MERGED|REJECTED|NOPATH-TRIV) ' "$LOG")
  echo "[gate] purged $P branches (merged-residue + rejected + nopath-trivial)" | tee -a "$LOG"
  # open PRs for no-pathway substantive — content deserves adjudication
  O=0
  while read -r line; do
    r="$(cut -d' ' -f2 <<< "$line")"; b="$(cut -d' ' -f3 <<< "$line" | tr -d "'")"
    PR_URL="$(gh pr create -R "$r" --head "$b" --title "[PATHWAY] $b — uplift content, never adjudicated" \
      --body "Opening a pathway to main for uplift-era content that never received a PR. [AI-assisted, human-gated] Origin: pathway_audit_v3 $(date -Iseconds)." 2>&1 || true)"
    echo "[banked] PR-OPENED $r '$b' -> ${PR_URL}" | tee -a "$LOG"; O=$((O+1))
  done < <(grep '^\[gate\] NOPATH-SUB ' "$LOG")
  echo "[gate] opened $O PRs for substantive no-pathway content" | tee -a "$LOG"
fi

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — review classes, then CONFIRM=1"
echo "${CANARY} [exit=0]"
exit 0
