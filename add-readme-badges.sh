#!/usr/bin/env bash
set -euo pipefail

# Run from repo root (openroot/)
if [[ ! -d .git ]]; then
  echo "❌ Not in a git repository. cd into openroot first."
  exit 1
fi

if [[ ! -f README.md ]]; then
  echo "❌ README.md not found in current directory."
  exit 1
fi

echo "==> Backing up README.md -> README.md.bak.$(date +%Y%m%d-%H%M%S)"
cp README.md "README.md.bak.$(date +%Y%m%d-%H%M%S)"

python3 - <<'PY'
from pathlib import Path

readme = Path("README.md")
text = readme.read_text(encoding="utf-8")

badge_block = """[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20549528.svg)](https://doi.org/10.5281/zenodo.20549528)
[![PoPW ledger](https://img.shields.io/badge/PoPW-v1.2.1-blue)](https://github.com/jesseray718/openroot/releases/tag/v1.2.1-popw-ledger)
[![thermo](https://img.shields.io/badge/thermo-v1.1.0-blue)](https://github.com/jesseray718/openroot/releases/tag/v1.1.0-native-thermo)
[![CI](https://github.com/jesseray718/openroot/actions/workflows/tests.yml/badge.svg)](https://github.com/jesseray718/openroot/actions/workflows/tests.yml)
[![License: GPL v3](https://img.shields.io/badge/code-GPL--3.0-blue.svg)](LICENSE)
[![License: CC BY-SA 4.0](https://img.shields.io/badge/docs-CC--BY--SA--4.0-lightgrey.svg)](LICENSE-docs.md)
"""

# Idempotency check (avoid duplicate insertion)
if "[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20549528.svg)]" in text:
    print("✅ Badge block already present in README.md; no changes made.")
    raise SystemExit(0)

lines = text.splitlines()

# Try to place badges right after the first H1 line "# OpenRoot"
inserted = False
for i, line in enumerate(lines):
    if line.strip() == "# OpenRoot":
        # Insert with a blank line before and after for readability
        lines = lines[:i+1] + ["", badge_block.rstrip(), ""] + lines[i+1:]
        inserted = True
        break

if not inserted:
    # Fallback: prepend at top
    new_text = badge_block + "\n" + text
else:
    new_text = "\n".join(lines) + ("\n" if not text.endswith("\n") else "")

readme.write_text(new_text, encoding="utf-8")
print("✅ Inserted badge block into README.md")
PY

echo "==> Showing diff"
git --no-pager diff -- README.md || true

echo "==> Staging + commit"
git add README.md
git commit -m "docs(readme): add badges to root README"

echo "✅ Done. Next: git push"
echo "   Run: git push"
