#!/usr/bin/env bash
set -Eeuo pipefail

BASE="${HOME}/openroot"
cd "$BASE"

echo "======================================================================"
echo "OPENROOT VERIFICATION"
echo "Timestamp: $(date --iso-8601=seconds)"
echo "Canary: VERIFY_OPENROOT_V2"
echo "======================================================================"

echo
echo "=== Required Files ==="
required=(
  "bin/shared_context_store.py"
  "bin/superlinear_setup.py"
  "context_bridge/memory_enable_guide.md"
)

for path in "${required[@]}"; do
  if [[ -f "$path" ]]; then
    printf '✓ %s\n' "$path"
  else
    printf '✗ MISSING: %s\n' "$path"
    exit 1
  fi
done

echo
echo "=== Python Syntax ==="
python3 -m py_compile \
  bin/shared_context_store.py \
  bin/superlinear_setup.py
echo "✓ Python syntax valid"

echo
echo "=== Context Database ==="
if [[ -f data/shared_context.db ]]; then
  ls -lh data/shared_context.db
  echo "✓ Shared context database present"
else
  echo "✗ Missing data/shared_context.db"
  exit 1
fi

echo
echo "=== Context Store Read Test ==="
if output="$(python3 bin/shared_context_store.py get test_workflow 2>&1)"; then
  printf '%s\n' "$output"
  echo "✓ Context-store read completed"
else
  printf '%s\n' "$output"
  echo "✗ Context-store command failed"
  exit 1
fi

echo
echo "=== Git Working Tree ==="
git status --short

echo
echo "=== Staged Changes ==="
git diff --cached --name-status

echo
echo "=== Whitespace Check ==="
git diff --check
git diff --cached --check
echo "✓ No whitespace errors in tracked or staged diffs"

echo
echo "=== Git Identity ==="
git branch --show-current
git log -1 --oneline

echo
echo "✓ VERIFY_OPENROOT_V2 complete"
