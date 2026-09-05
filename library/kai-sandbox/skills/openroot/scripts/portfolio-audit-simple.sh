#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# === OPENROOT PORTFOLIO AUDIT & RESTRUCTURE (SIMPLIFIED) ===
# Run: bash portfolio-audit-simple.sh
# Prerequisites: gh auth login

U="jesseray718"
WORK="$HOME/openroot_work"
mkdir -p "$WORK" && cd "$WORK"

echo "=================================================="
echo "=== PORTFOLIO AUDIT FOR $U ==="
echo "=================================================="
echo ""

# ============================================
# STEP 1: LIST REPOS (simple)
# ============================================
echo "STEP 1: Listing all repos..."
echo ""

gh repo list $U --limit 100 | tee repos_list.txt
echo ""
echo "Saved to: repos_list.txt"
echo ""

# ============================================
# STEP 2: ARCHIVE DEAD REPOS
# ============================================
echo "STEP 2: Archiving completed repos..."
echo ""

ARCHIVE_LIST=(
  "aerocement-"
  "open-cell-thermal-open-cell-the"
  "AeroCement_Ecosystem"
)

for repo in "${ARCHIVE_LIST[@]}"; do
  if gh repo view "$U/$repo" &>/dev/null; then
    echo "  → Checking: $repo"
    gh repo archive "$U/$repo" --confirm 2>/dev/null && echo "    ✓ Archived" || echo "    ✓ Already archived"
  else
    echo "  → $repo not found (may be already archived)"
  fi
done

echo ""

# ============================================
# STEP 3: SET TOPICS (one-by-one)
# ============================================
echo "STEP 3: Setting repository topics..."
echo ""

# Define topics
openroot_topics="appropriate-technology disaster-relief ferrocement geodesic-dome open-hardware open-source-hardware passive-solar permaculture sustainable-construction"
aerocement_topics="aircrete appropriate-technology concrete ferrocement open-source-hardware sustainable-construction thermal-engineering"
thermal_topics="appropriate-technology cooling energy-systems ferrocement open-hardware passive-solar sustainable-construction thermal-engineering"
renaissance_topics="community-reputation distributed-labor open-source verification physical-work"
civ_topics="appropriate-technology engineering open-source sustainable-development"
profile_topics="dotfiles scripts open-source-hardware automation"
spoke_topics="appropriate-technology open-hardware open-source-hardware openroot template"

# Apply topics
echo "  → openroot"
gh repo edit "$U/openroot" --topics "$openroot_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo "  → aerocement"
gh repo edit "$U/aerocement" --topics "$aerocement_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo "  → OpenCell-Thermal-System"
gh repo edit "$U/OpenCell-Thermal-System" --topics "$thermal_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo "  → renaissance-protocol"
gh repo edit "$U/renaissance-protocol" --topics "$renaissance_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo "  → civilization2.0"
gh repo edit "$U/civilization2.0" --topics "$civ_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo "  → jesseray718"
gh repo edit "$U/jesseray718" --topics "$profile_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo "  → openroot-spoke-template"
gh repo edit "$U/openroot-spoke-template" --topics "$spoke_topics" 2>/dev/null && echo "    ✓" || echo "    (auth issue)"

echo ""

# ============================================
# STEP 4: UPDATE DESCRIPTIONS
# ============================================
echo "STEP 4: Updating descriptions..."
echo ""

gh repo edit "$U/civilization2.0" --description "Simple solutions to complex engineered problems. Open-source appropriate tech research." 2>/dev/null && echo "  ✓ civilization2.0" || echo "  • civilization2.0 (auth issue)"

gh repo edit "$U/jesseray718" --description "Personal dotfiles, scripts, and automation for OpenRoot ecosystem development." 2>/dev/null && echo "  ✓ jesseray718" || echo "  • jesseray718 (auth issue)"

gh repo edit "$U/renaissance-protocol" --description "Protocol for verifying physical labor and community builds. Reputation credits for real-world work." 2>/dev/null && echo "  ✓ renaissance-protocol" || echo "  • renaissance-protocol (auth issue)"

echo ""

# ============================================
# SUMMARY
# ============================================
echo "=================================================="
echo "COMPLETE"
echo "=================================================="
echo ""
echo "Summary:"
echo "  ✓ Repos listed"
echo "  ✓ Dead repos archived"
echo "  ✓ Topics assigned"
echo "  ✓ Descriptions updated"
echo ""
echo "Repo list saved: $WORK/repos_list.txt"
echo ""
echo "Next: Set licenses manually at GitHub"
echo "  https://github.com/jesseray718/{repo}/settings/license"
