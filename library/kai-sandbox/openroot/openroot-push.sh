#!/bin/bash
set -e

echo "🌱 OpenRoot → GitHub Setup & Push"
echo "=================================="
echo ""

if [ ! -f "README.md" ]; then
    echo "❌ README.md not found. Are you in the openroot directory?"
    exit 1
fi

echo "✅ Found README.md. Proceeding..."
echo ""

echo "📋 Creating license files..."

cat > LICENSE-HARDWARE.md << 'EOF'
# Creative Commons Attribution-ShareAlike 4.0 International

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/4.0/

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material for any purpose, even commercially

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made
- ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original
EOF

cat > LICENSE-SOFTWARE.md << 'EOF'
# GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
EOF

echo "✅ License files created"
echo ""

echo "🚫 Creating .gitignore..."

cat > .gitignore << 'EOF'
.DS_Store
Thumbs.db
*.swp
node_modules/
__pycache__/
.vscode/
.idea/
.env
*.pyc
EOF

echo "✅ .gitignore created"
echo ""

if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repo initialized"
fi

echo ""

if ! grep -q "## License" README.md; then
    echo "📝 Adding license section to README.md..."
    cat >> README.md << 'EOF'

---

## License

- **Hardware:** CC-BY-SA-4.0 — See [`LICENSE-HARDWARE.md`](LICENSE-HARDWARE.md)
- **Software:** GPL-3.0 — See [`LICENSE-SOFTWARE.md`](LICENSE-SOFTWARE.md)

**No patents. Ever.**
EOF
fi

echo ""
echo "📦 Staging files..."
git add .
git status

echo ""
read -p "Ready to commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Initial commit: OpenRoot foundation designs and token mechanics"
    echo "✅ Committed"
else
    echo "⏭️  Skipped"
    exit 0
fi

echo ""
echo "🔗 Setting up GitHub remote..."

git branch -M main
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/jesseray718/openroot.git"

echo "✅ Remote set to: https://github.com/jesseray718/openroot.git"
echo ""

echo "🚀 Pushing to GitHub..."
echo "(Enter your GitHub username and personal access token)"
echo ""

git push -u origin main

echo ""
echo "✅ Done! Repo is at https://github.com/jesseray718/openroot"
echo "Go to Settings and set it to Public"
