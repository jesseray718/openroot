#!/bin/bash
#
# OpenRoot Dependency Validation Script
# Checks that the project follows the defined build order from SYSTEM-MAP.md
#

set -e

echo "🔍 OpenRoot Dependency Validation"
echo "=================================="
echo

ERRORS=0

# Define the dependency chain (must be built in this order)
declare -a LAYERS=(
    "construction/SIKESTON-NODE-ZERO-IMPLEMENTATION.md"     # Layer 1: Mesh
    "technical/SMART-CONTRACT-IMPLEMENTATION-DETAILS.md"    # Layer 2: Contribution Ledger
    "construction/GEODESIC-DOME-AE-GFRC-HOUSING-SYSTEM.md"  # Layer 4: Shelter (Thermal is lighter)
    "governance/CONTRIBUTOR-TRANSITION-AND-501C3-PREPAREDNESS-FRAMEWORK.md"
    "core/OPENROOT-SYSTEM-LEVEL-RISK-ASSESSMENT.md"
    "core/KEY-CONVERSATION-BRIEF.md"
    "SYSTEM-MAP.md"
    "README.md"
)

echo "Checking core documents in dependency order..."
echo

for doc in "${LAYERS[@]}"; do
    if [ -f "docs/$doc" ]; then
        echo "✅  $doc"
    else
        echo "❌  MISSING: $doc"
        ERRORS=$((ERRORS + 1))
    fi
done

echo
echo "Checking for critical cross-references..."

# Check that SYSTEM-MAP is referenced in key docs
if grep -q "SYSTEM-MAP.md" docs/core/KEY-CONVERSATION-BRIEF.md 2>/dev/null; then
    echo "✅  KEY-CONVERSATION-BRIEF.md references SYSTEM-MAP.md"
else
    echo "⚠️   KEY-CONVERSATION-BRIEF.md should reference SYSTEM-MAP.md"
fi

if grep -q "SYSTEM-MAP.md" docs/README.md 2>/dev/null; then
    echo "✅  README.md references SYSTEM-MAP.md"
else
    echo "⚠️   README.md should prominently reference SYSTEM-MAP.md"
fi

echo
if [ $ERRORS -eq 0 ]; then
    echo "✅ All critical dependencies satisfied."
    exit 0
else
    echo "❌ $ERRORS critical document(s) missing."
    echo "Please create the missing files before proceeding with deeper layers."
    exit 1
fi
