#!/bin/bash
# publish.sh — Create the three standalone repos on GitHub and push.
#
# Requires: gh CLI authenticated, git installed.
# Run from the agape_primitives/ directory.

set -e

PACKAGES=("etaledger" "fractallattice" "agaperesonance")

echo "═══════════════════════════════════════════════════════"
echo "  AGAPE PRIMITIVES — Publishing to GitHub"
echo "  github.com/jesseray718/"
echo "═══════════════════════════════════════════════════════"

for pkg in "${PACKAGES[@]}"; do
    echo ""
    echo "── ${pkg} ──────────────────────────────────────"
    cd "${pkg}"

    # Init git
    git init
    git add .
    git commit -m "Initial release: ${pkg} v0.1.0 — extracted from OpenRoot/UNE

Universal Computational Primitive.
Part of the Agape Primitives collection.
License: GPL-3.0. No patents. Ever.

Author: Jesse Ray (OpenRoot)"

    # Create GitHub repo (private initially, flip to public when ready)
    gh repo create "jesseray718/${pkg}" --public --source=. --push \
        --description "$(head -2 README.md | tail -1)"

    # Tag the release
    git tag v0.1.0
    git push origin v0.1.0

    echo "  ✓ Published: https://github.com/jesseray718/${pkg}"

    cd ..
done

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  ALL PACKAGES PUBLISHED"
echo ""
echo "  To make pip-installable:"
echo "    pip install twine"
echo "    for pkg in etaledger fractallattice agaperesonance; do"
echo "      cd \$pkg && python setup.py sdist bdist_wheel"
echo "      twine upload dist/*"
echo "      cd .."
echo "    done"
echo ""
echo "  Or publish to GitHub Packages / TestPyPI first."
echo "═══════════════════════════════════════════════════════"
