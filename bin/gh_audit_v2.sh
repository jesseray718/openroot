#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# gh_audit_v2.sh — fleet-wide hygiene audit + quick fixes (fixed jq var bug, per-repo default branch, real pin mutation)
# Dry-run default: reports only. CONFIRM=1 deletes identical-merged branches + pins repos.
# [canary] gh_audit_v2_CANARY_MARKER
set -euo pipefail
trap 'echo "[held] DIED at line $LINENO (exit $?)"' ERR
export GIT_PAGER=cat PAGER=cat

CONFIRM="${CONFIRM:-0}"
OWNER="jesseray718"
BASE="/home/jesse/openroot/reports/gh_audit_$(date +%Y%m%d_%H%M%S)"
PIN_REPOS="${PIN_REPOS:-openroot wisdom-scaffold openroot-ecosystem jesseray718.github.io}"
say(){ printf '[%s] %s\n' "$1" "$2"; }

mkdir -p "$BASE"
touch "$BASE/unmerged_ahead.tsv" "$BASE/identical_branches.tsv" "$BASE/stale_branches.tsv"
: > "$BASE/hygiene_flags.tsv"

say gate "start $(date -u +%Y-%m-%dT%H:%M:%SZ) CONFIRM=$CONFIRM -> $BASE"

# [1] repo inventory with REAL default branch (fix: never assume main)
gh repo list "$OWNER" --limit 100 --json name,defaultBranchRef,isArchived,updatedAt,description,licenseInfo \
  --jq '.[] | [.name, (.defaultBranchRef.name // "-"), (.isArchived|tostring), .updatedAt, (.description // ""), (.licenseInfo.spdxId // "NONE")] | @tsv' \
  > "$BASE/repo_inventory.tsv"
TOTAL=$(wc -l < "$BASE/repo_inventory.tsv")
say banked "inventory: $TOTAL repos (default branches resolved, not assumed)"

# [2] branch scan — shell holds branch name, jq only reads API JSON (fix: no $var in jq)
while IFS=$'\t' read -r REPO DB ARCH UPD DESC LIC; do
  say gate "scanning $REPO"
  [ "$ARCH" = "true" ] && continue
  gh api "repos/$OWNER/$REPO/branches" --paginate -q '.[].name' 2>/dev/null | while read -r BR; do
    [ "$BR" = "$DB" ] && continue
    CMP=$(gh api "repos/$OWNER/$REPO/compare/$DB...$BR" -q '{ahead: .ahead_by, behind: .behind_by, date: .merge_base_commit.committer.date}' 2>/dev/null) || continue
    AHEAD=$(echo "$CMP" | jq -r '.ahead'); BEHIND=$(echo "$CMP" | jq -r '.behind'); MDATE=$(echo "$CMP" | jq -r '.date')
    if [ "${AHEAD:-0}" -gt 0 ]; then
      printf '%s|%s|+%s\n' "$REPO" "$BR" "$AHEAD" >> "$BASE/unmerged_ahead.tsv"
    else
      printf '%s|%s\n' "$REPO" "$BR" >> "$BASE/identical_branches.tsv"
    fi
    [ "$MDATE" \< "$(date -u -d '90 days ago' +%Y-%m-%dT%H:%M:%SZ)" ] && printf '%s|%s|%s\n' "$REPO" "$BR" "$MDATE" >> "$BASE/stale_branches.tsv"
  done
done < "$BASE/repo_inventory.tsv"
say banked "branches: $(wc -l < "$BASE/unmerged_ahead.tsv") ahead-of-default (review), $(wc -l < "$BASE/identical_branches.tsv") identical (delete-bait)"

# [3] closed-unmerged PRs fleet-wide (resurrection candidates incl. lost work)
: > "$BASE/closed_unmerged_prs.tsv"
while IFS=$'\t' read -r REPO _ _ _ _ _; do
  gh pr list -R "$OWNER/$REPO" --state closed --limit 100 --json number,title,closedAt,headRefName,state \
    --jq '.[] | select(.state == "CLOSED") | [$__arg_repo, (.number|tostring), .title, .closedAt, .headRefName] | @tsv' \
    --arg __arg_repo "$REPO" 2>/dev/null >> "$BASE/closed_unmerged_prs.tsv" || true
done < "$BASE/repo_inventory.tsv"
say banked "closed-unmerged PRs: $(wc -l < "$BASE/closed_unmerged_prs.tsv") candidates"

# [4] gists + hygiene flags
gh gist list --limit 50 > "$BASE/gist_inventory.txt" 2>/dev/null || say held "gist list failed (auth?)"
awk -F'\t' '$6=="NONE" {print $1 "|NO_LICENSE"} $5=="" {print $1"|NO_DESC"}' "$BASE/repo_inventory.tsv" >> "$BASE/hygiene_flags.tsv" || true
say banked "hygiene flags: $(wc -l < "$BASE/hygiene_flags.tsv") (missing license/description); gists: $(wc -l < "$BASE/gist_inventory.txt")"

# [5] CONFIRM actions
if [ "$CONFIRM" = "1" ]; then
  while IFS='|' read -r REPO BR; do
    gh api -X DELETE "repos/$OWNER/$REPO/branches/$BR" --silent && say banked "deleted identical branch $REPO/$BR" || say held "keep $REPO/$BR"
  done < "$BASE/identical_branches.tsv"
  for R in $PIN_REPOS; do
    ID=$(gh api graphql -f query="query{repository(owner:\"$OWNER\",name:\"$R\"){id}}" -q '.data.repository.id')
    gh api graphql -f query="mutation(\$id:ID!){pinItem(input:{itemId:\$id}){item{... on Repository{name}}}}" -f id="$ID" >/dev/null \
      && say banked "pinned $R" || say held "pin failed $R (cap 6? already pinned?)"
  done
  gh api graphql -f query='{viewer{pinnedItems(first:6){nodes{... on Repository{name}}}}}' -q '.data.viewer.pinnedItems.nodes[].name' | while read -r n; do say gate "pinned: $n"; done
else
  say held "DRY RUN — identical-branch deletes and pinning listed but not executed"
  say held "review $BASE/unmerged_ahead.tsv (your eyes-only rule: NO auto-delete of ahead branches) then CONFIRM=1"
fi

say banked "full report: $BASE/"
printf '[exit=0]\n'
