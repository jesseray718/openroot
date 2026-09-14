#!/bin/bash
set -euo pipefail
REPO="${1:-jesseray718/openroot}"
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"
python3 -m kernel.selftest || { echo "ABORT: selftest failed"; exit 1; }
git add .
git diff --cached --quiet || git commit -m "kernel: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin main
echo "Pushed to $REPO"
