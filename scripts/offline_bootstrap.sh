#!/usr/bin/env bash
# scripts/offline_bootstrap.sh
# One-command local bootstrap for the OpenRoot offline toolkit.
# Works on Linux, macOS, and WSL/Windows-with-bash.
#
# Usage:
#   bash scripts/offline_bootstrap.sh
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"

echo "=== OpenRoot Offline Toolkit Bootstrap ==="
echo ""

# 1. Check Python 3.8+
python3 --version >/dev/null 2>&1 || { echo "ERROR: python3 not found. Install Python 3.8+ first."; exit 1; }
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python $PY_VER detected"

# 2. Create virtual environment if absent
if [ ! -d "$VENV_DIR" ]; then
  echo "  Creating virtual environment at .venv ..."
  python3 -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
echo "✓ Virtual environment active"

# 3. Install optional dependencies (non-fatal)
pip install --quiet --upgrade pip
pip install --quiet psutil python-dotenv 2>/dev/null || echo "  (optional packages unavailable – continuing without them)"
echo "✓ Dependencies installed"

# 4. Copy .env.example → .env if missing
if [ ! -f "${REPO_ROOT}/.env" ] && [ -f "${REPO_ROOT}/.env.example" ]; then
  cp "${REPO_ROOT}/.env.example" "${REPO_ROOT}/.env"
  echo "✓ Created .env from .env.example"
fi

# 5. Bootstrap the offline toolkit
python3 -m offline.cli init
echo ""
echo "=== Bootstrap complete! ==="
echo ""
echo "Quick-start commands:"
echo "  offline:status   →  python3 -m offline.cli status"
echo "  offline:work     →  python3 -m offline.cli work --type my_task --payload '{\"note\":\"hello\"}'"
echo "  offline:sync     →  python3 -m offline.cli sync"
echo "  offline:purge    →  python3 -m offline.cli purge [--confirm]"
echo "  offline:doctor   →  python3 -m offline.cli doctor"
echo ""
echo "See docs/offline-toolkit.md for architecture details."
