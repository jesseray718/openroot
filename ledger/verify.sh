#!/usr/bin/env bash
# ledger verify — recorded vs actual sha256
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; LEDGER="$ROOT/ledger/files.sha256"; fail=0
while read -r hash path; do
  [ -z "$hash" ] && continue; case "$hash" in \#*) continue;; esac
  actual="$(sha256sum "$ROOT/$path" 2>/dev/null | cut -d' ' -f1 || true)"
  [ "$actual" != "$hash" ] && { echo "MISMATCH $path"; fail=1; }
done < "$LEDGER"
[ "$fail" -eq 0 ] && echo "ledger OK" || { echo "ledger FAILED"; exit 1; }
