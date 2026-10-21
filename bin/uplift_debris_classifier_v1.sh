#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# uplift_debris_classifier_v1.sh — classify Aug-2026 chore/uplift-* debris branches by diff content
# Canary: [UDCV1] | Trivial = only .github/, *.md, LICENSE, config files. CONFIRM=1 purges trivial-only.
set -euo pipefail
export GIT_PAGER=cat
export TZ=UTC

OWNER="jesseray718"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="/home/jesse/openroot/context_bridge/uplift_debris_${TS}.md"
CANARY="[UDCV1]"
MODE="${CONFIRM:-0}"

mkdir -p /home/jesse/openroot/context_bridge
echo "# Uplift Debris Classification ${TS}" > "$LOG"
echo "mode: $([ "$MODE" = "1" ] && echo EXECUTE || echo DRY-RUN)" >> "$LOG"

banner() { echo ""; echo "${CANARY} ==== $1"; }

is_trivial_file() {
  case "$1" in
    .github/*|*.md|LICENSE|*.gitignore|CODEOWNERS|.editorconfig|\
    pyproject.toml|ruff.toml|.flake8|setup.cfg|requirements*.txt|\
    .pre-commit-config.yaml|Makefile|.gitmodules|dependabot.yml) return 0 ;;
    *) return 1 ;;
  esac
}

banner "PRE-FLIGHT [gate]"
gh auth status >/dev/null 2>&1 || { echo "[held] gh not authed"; exit 1; }
echo "[gate] gh auth OK"

REPOS="$(gh repo list "$OWNER" --limit 200 --json nameWithOwner,isFork,isArchived \
  --jq '.[] | select(.isArchived==false and .isFork==false) | .nameWithOwner')"

banner "STAGE 1 — SCAN FOR UPLIFT DEBRIS"
SCANNED=0; TRIVIAL=0; SUBSTANTIVE=0; ORPHAN=0
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
    FILES_JSON="$(gh api "repos/$r/compare/${DEFBR}...${b}" --jq '[.files[].filename]' 2>/dev/null || echo "ERR")"
    if [ "$FILES_JSON" = "ERR" ] || [ "$FILES_JSON" = "[]" ]; then
      echo "[held] $r '$b' — orphan/no-diff — EXEMPT"; ORPHAN=$((ORPHAN+1)); continue
    fi
    TRIV=1
    while IFS= read -r f; do
      is_trivial_file "$f" || TRIV=0
    done < <(echo "$FILES_JSON" | jq -r '.[]')
    if [ "$TRIV" = "1" ]; then
      echo "[banked] TRIVIAL  $r '$b' — $(echo "$FILES_JSON" | jq -r 'join(", ")')"
      echo "[banked] TRIVIAL $r '$b': $(echo "$FILES_JSON" | jq -r 'join(", ")')" >> "$LOG"
      TRIVIAL=$((TRIVIAL+1))
    else
      echo "[held] SUBSTAN   $r '$b' — $(echo "$FILES_JSON" | jq -r 'join(", ")')"
      echo "[held] SUBSTANTIVE $r '$b': $(echo "$FILES_JSON" | jq -r 'join(", ")')" >> "$LOG"
      SUBSTANTIVE=$((SUBSTANTIVE+1))
    fi
  done <<< "$BRANCHES"
done <<< "$REPOS"
echo "[gate] scanned=$SCANNED trivial=$TRIVIAL substantive=$SUBSTANTIVE orphan=$ORPHAN" | tee -a "$LOG"

if [ "$MODE" = "1" ] && [ "$TRIVIAL" -gt 0 ]; then
  banner "STAGE 2 — PURGE TRIVIAL DEBRIS (CONFIRMED)"
  P=0
  while read -r line; do
    r="$(cut -d' ' -f2 <<< "$line")"; b="$(cut -d' ' -f3 <<< "$line" | tr -d "'")"
    [ -z "$r" ] || [ -z "$b" ] && continue
    gh api -X DELETE "repos/${r}/git/refs/heads/${b}" >> "$LOG" 2>&1 && P=$((P+1)) || true
  done < <(grep '^\[banked\] TRIVIAL ' "$LOG")
  echo "[gate] deleted $P trivial branches" | tee -a "$LOG"
fi

banner "SUMMARY"
sha256sum "$LOG" | tee -a "$LOG"
[ "$MODE" = "1" ] || echo "${CANARY} [DRY-RUN] — review TRIVIAL vs SUBSTAN lines, then CONFIRM=1"
echo "${CANARY} [exit=0]"
exit 0
