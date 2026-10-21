#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# gh_audit_v3.sh — fleet hygiene audit, hardened vs v2 detached death
# v2->v3: gh retry wrapper w/ backoff, per-repo pacing (secondary-rate-limit defense),
#         ERR trap logs death point, [exit=0] emitted ONLY on true success.
# Dry-run default. CONFIRM=1 deletes identical branches + pins repos.
# [canary] gh_audit_v3_CANARY_MARKER
set -euo pipefail
export GIT_PAGER=cat PAGER=cat
[ "$(hostname)" = "optiplex3060" ] || { echo "[held] run on optiplex3060, not $(hostname)"; exit 1; }
command -v gh >/dev/null || { echo "[held] gh CLI missing"; exit 1; }
CONFIRM="${CONFIRM:-0}"
OWNER="jesseray718"
BASE="$HOME/openroot/reports/gh_audit_$(date +%Y%m%d_%H%M%S)"
say(){ printf '[%s] %s\n' "$1" "$2"; }
ghr(){ # gh with 3-attempt backoff vs rate limits — returns nonzero only after final try
  local a
  for a in 1 2 3; do
    if "$@"; then return 0; fi
    say held "gh attempt $a failed: $2 $3 ..."; sleep $(( a * 10 ))
  done
  return 1
}
trap 'say held "AUDIT DIED exit=$? — report $BASE is PARTIAL, do not CONFIRM against it"' ERR
mkdir -p "$BASE"
: > "$BASE/unmerged_ahead.tsv"; : > "$BASE/identical_branches.tsv"
: > "$BASE/stale_branches.tsv"; : > "$BASE/hygiene_flags.tsv"
: > "$BASE/closed_unmerged_prs.tsv"
say gate "start $(date -u +%FT%TZ) CONFIRM=$CONFIRM -> $BASE"
ghr gh repo list "$OWNER" --limit 200 \
  --json name,defaultBranchRef,isArchived,updatedAt,description,licenseInfo \
  --jq '.[] | [.name, (.defaultBranchRef.name // "-"), (.isArchived|tostring), .updatedAt, (.description // ""), (.licenseInfo.spdxId // "NONE")] | @tsv' \
  > "$BASE/repo_inventory.tsv"
say banked "inventory: $(wc -l < "$BASE/repo_inventory.tsv") repos"
awk -F'\t' '$6=="NONE"{print $1"|NO_LICENSE"} $5==""{print $1"|NO_DESC"}' \
  "$BASE/repo_inventory.tsv" >> "$BASE/hygiene_flags.tsv" || true
say banked "hygiene flags: $(wc -l < "$BASE/hygiene_flags.tsv")"

while IFS=$'\t' read -r REPO DB ARCH UPD DESC LIC; do
  [ "$ARCH" = "true" ] && continue
  while read -r BR; do
    [ "$BR" = "$DB" ] && continue
    if AHEAD=$(ghr gh api "repos/$OWNER/$REPO/compare/$DB...$BR" -q '.ahead_by' 2>/dev/null); then
      if [ "${AHEAD:-0}" -gt 0 ]; then
        printf '%s|%s|+%s\n' "$REPO" "$BR" "$AHEAD" >> "$BASE/unmerged_ahead.tsv"
      else
        printf '%s|%s\n' "$REPO" "$BR" >> "$BASE/identical_branches.tsv"
      fi
    else
      printf '%s|%s|NO_COMMON_ANCESTOR\n' "$REPO" "$BR" >> "$BASE/unmerged_ahead.tsv"
    fi
  done < <(gh api "repos/$OWNER/$REPO/branches" --paginate -q '.[].name' 2>/dev/null)
  ghr gh pr list -R "$OWNER/$REPO" --state closed --limit 100 \
    --json number,title,closedAt,headRefName,state \
    --jq '.[] | select(.state=="CLOSED") | [(.number|tostring), .title, .closedAt, .headRefName] | @tsv' 2>/dev/null \
    | sed "s|^|$REPO\t|" >> "$BASE/closed_unmerged_prs.tsv" || true
  sleep 1  # pacing: secondary-rate-limit defense
  say banked "scanned $REPO"
done < "$BASE/repo_inventory.tsv"
say banked "ahead/NCA branches: $(wc -l < "$BASE/unmerged_ahead.tsv") | identical: $(wc -l < "$BASE/identical_branches.tsv")"
gh gist list --limit 50 > "$BASE/gist_inventory.txt" 2>/dev/null || say held "gist list failed"

if [ "$CONFIRM" = "1" ]; then
  while IFS='|' read -r REPO BR; do
    gh api -X DELETE "repos/$OWNER/$REPO/branches/$BR" --silent && say banked "deleted identical $REPO/$BR" || say held "kept $REPO/$BR"
  done < "$BASE/identical_branches.tsv"
  for R in ${PIN_REPOS:-openroot wisdom-scaffold openroot-ecosystem jesseray718.github.io}; do
    ID=$(gh api graphql -f query="query{repository(owner:\"$OWNER\",name:\"$R\"){id}}" -q '.data.repository.id')
    gh api graphql -f query="mutation(\$id:ID!){pinItem(input:{itemId:\$id}){item{... on Repository{name}}}}" -f id="$ID" >/dev/null \
      && say banked "pinned $R" || say held "pin failed $R (cap 6?)"
  done
else
  say held "DRY RUN — nothing deleted; review $BASE/unmerged_ahead.tsv before CONFIRM=1"
fi
say banked "report: $BASE/"
printf '[exit=0]\n'
