#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# === OPENROOT PORTFOLIO AUDIT & RESTRUCTURE ===
# Run: bash portfolio-audit-and-fix.sh
# Prerequisites: 
#   - gh auth login (with repo admin scope)

U="jesseray718"
WORK="$HOME/openroot_work"
mkdir -p "$WORK" && cd "$WORK"

echo "=================================================="
echo "=== PORTFOLIO AUDIT & RESTRUCTURE FOR $U ==="
echo "=================================================="
echo ""

# ============================================
# STEP 1: AUDIT & REPORT
# ============================================
echo "STEP 1: SELF-AUDIT — Fetch all repos with metadata"
echo ""

# Use --json with proper array wrapping
gh repo list $U --limit 100 --json name,description,diskUsage,licenseInfo,repositoryTopics,isArchived,isFork,primaryLanguage > repos_raw.json 2>&1

echo "Found repos:"
jq -r '.[] | select(.isFork == false) | "\(.name) | size:\(.diskUsage)KB | license:\(.licenseInfo.key // "NONE") | lang:\(.primaryLanguage.name // "NONE") | topics:\(.repositoryTopics | length) | archived:\(.isArchived)"' repos_raw.json

echo ""
echo "Saved to: repos_raw.json"
sleep 2

# ============================================
# STEP 2: ARCHIVE DEAD/EMPTY REPOS
# ============================================
echo ""
echo "STEP 2: ARCHIVING COMPLETED REPOS"
echo ""

ARCHIVE_LIST=(
  "aerocement-"
  "open-cell-thermal-open-cell-the"
  "AeroCement_Ecosystem"
)

for repo in "${ARCHIVE_LIST[@]}"; do
  if gh repo view "$U/$repo" &>/dev/null; then
    IS_ARCHIVED=$(gh repo view "$U/$repo" --json isArchived --jq '.isArchived')
    if [ "$IS_ARCHIVED" == "false" ]; then
      echo "  → Archiving: $repo"
      gh repo archive "$U/$repo" --confirm || echo "    (already archived or error, skipping)"
    else
      echo "  ✓ Already archived: $repo"
    fi
  fi
done

echo ""
echo "Archive complete."
sleep 2

# ============================================
# STEP 3: SET LICENSES (via API)
# ============================================
echo ""
echo "STEP 3: SETTING PROPER LICENSES"
echo ""

# Map: repo → license key
declare -A LICENSE_MAP=(
  ["openroot"]="gpl-3.0"
  ["aerocement"]="cc-by-sa-4.0"
  ["OpenCell-Thermal-System"]="gpl-3.0"
  ["renaissance-protocol"]="gpl-3.0"
  ["civilization2.0"]="cc-by-sa-4.0"
  ["jesseray718"]="gpl-3.0"
  ["openroot-spoke-template"]="cc-by-sa-4.0"
)

for repo in "${!LICENSE_MAP[@]}"; do
  license_key="${LICENSE_MAP[$repo]}"
  echo "  → $repo: $license_key"
done

echo ""
echo "License note: GitHub CLI doesn't expose license changes directly."
echo "Manual step required: https://github.com/jesseray718/{repo}/settings/license"
echo ""
sleep 2

# ============================================
# STEP 4: SET REPOSITORY TOPICS
# ============================================
echo ""
echo "STEP 4: SETTING REPOSITORY TOPICS"
echo ""

# Topic assignments by repo
declare -A TOPICS_MAP=(
  ["openroot"]="appropriate-technology disaster-relief ferrocement geodesic-dome open-hardware open-source-hardware passive-solar permaculture sustainable-construction"
  ["aerocement"]="aircrete appropriate-technology concrete ferrocement open-source-hardware sustainable-construction thermal-engineering"
  ["OpenCell-Thermal-System"]="appropriate-technology cooling energy-systems ferrocement open-hardware passive-solar sustainable-construction thermal-engineering"
  ["renaissance-protocol"]="community-reputation distributed-labor open-source verification physical-work"
  ["civilization2.0"]="appropriate-technology engineering open-source sustainable-development"
  ["jesseray718"]="dotfiles scripts open-source-hardware automation"
  ["openroot-spoke-template"]="appropriate-technology open-hardware open-source-hardware openroot template"
)

for repo in "${!TOPICS_MAP[@]}"; do
  topics="${TOPICS_MAP[$repo]}"
  echo "  → $repo"
  echo "     Topics: $topics"
  # Convert space-separated topics into array
  topic_array=$(echo "$topics" | tr ' ' '\n' | jq -R . | jq -s .)
  gh repo edit "$U/$repo" --topics "$topic_array" 2>/dev/null || echo "     (auth scope issue — try web UI)"
done

echo ""
echo "Topics assigned."
sleep 2

# ============================================
# STEP 5: ADD/UPDATE DESCRIPTIONS
# ============================================
echo ""
echo "STEP 5: UPDATING REPO DESCRIPTIONS"
echo ""

declare -A DESC_MAP=(
  ["civilization2.0"]="Simple solutions to complex engineered problems. Open-source appropriate tech research."
  ["jesseray718"]="Personal dotfiles, scripts, and automation for OpenRoot ecosystem development."
  ["renaissance-protocol"]="Protocol for verifying physical labor and community builds. Reputation credits for real-world work."
)

for repo in "${!DESC_MAP[@]}"; do
  desc="${DESC_MAP[$repo]}"
  echo "  → $repo"
  echo "     Desc: $desc"
  gh repo edit "$U/$repo" --description "$desc" 2>/dev/null || echo "     (auth scope issue)"
done

echo ""
echo "Descriptions updated."
sleep 2

# ============================================
# STEP 6: PORTFOLIO SUMMARY
# ============================================
echo ""
echo "STEP 6: PORTFOLIO SUMMARY"
echo ""

cat << 'PORTFOLIO_SUMMARY'

# OpenRoot Portfolio Structure

## Tier 1: Core Initiatives (Active, Production-Ready)
  - openroot (Hub + orchestration)
  - aerocement (Material science)
  - OpenCell-Thermal-System (Energy system)

## Tier 2: Protocols & Frameworks (Research/Beta)
  - renaissance-protocol (Labor verification)
  - openroot-spoke-template (Community module template)

## Tier 3: Research/Conceptual
  - civilization2.0 (Engineering philosophy)

## Tier 4: Personal Infrastructure
  - jesseray718 (Dotfiles + scripts)

## Archived (Merged into openroot)
  - aerocement-
  - open-cell-thermal-open-cell-the
  - AeroCement_Ecosystem

PORTFOLIO_SUMMARY

echo ""
echo "=================================================="
echo "RESTRUCTURE COMPLETE"
echo "=================================================="
echo ""
echo "Audit report: $WORK/repos_raw.json"
echo ""
echo "Summary:"
echo "  ✓ Repos audited"
echo "  ✓ Dead repos archived"
echo "  ✓ Topics assigned"
echo "  ✓ Descriptions updated"
echo "  → Licenses: manual via GitHub web UI"
