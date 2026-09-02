#!/usr/bin/env bash
set -euo pipefail
BIN=./bin/agape-ipfs
PASS=0; FAIL=0
ok()  { echo "  ✓ $1"; PASS=$((PASS+1)); }
nok() { echo "  ✗ $1"; FAIL=$((FAIL+1)); }
echo "Running agape-ipfs tests..."
$BIN version | grep -q "1.0.0" && ok "version" || nok "version"
$BIN help | grep -q "Usage" && ok "help" || nok "help"
TMPF=$(mktemp); echo "agape test" > "$TMPF"
HASH=$($BIN hash "$TMPF"); [ -n "$HASH" ] && ok "hash file" || nok "hash file"
rm -f "$TMPF"
TMPD=$(mktemp -d); echo a > "$TMPD/file1.txt"; echo b > "$TMPD/file2.txt"
DIRHASH=$($BIN hash "$TMPD"); [ -n "$DIRHASH" ] && ok "hash dir" || nok "hash dir"
rm -rf "$TMPD"
bash -n "$BIN" && ok "syntax" || nok "syntax"
$BIN bogus 2>/dev/null && nok "should reject" || ok "rejects unknown"
echo "Results: $PASS passed, $FAIL failed"
exit $FAIL
