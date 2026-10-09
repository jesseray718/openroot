#!/usr/bin/env bash
# ledger rebuild — regenerate files.sha256 from tracked files
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
git ls-files | grep -v '^ledger/files.sha256$' | while read -r f; do
  [ -f "$f" ] && printf '%s  %s\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$f"
done > ledger/files.sha256
echo "ledger rebuilt: $(wc -l < ledger/files.sha256) files"
