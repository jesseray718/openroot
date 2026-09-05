#!/usr/bin/env bash
# One recreatable OpenRoot PoPW ledger release.
# Test default. PUSH=1 after green.
# Does NOT add the dirty 20-file tree. Only popw_ledger.py + this script.
set -eu
REPO="${REPO:-jesseray718/openroot}"
BRANCH="${BRANCH:-feat/popw-ledger-20260902}"
TAG="${TAG:-v1.2.0-popw-ledger}"

if [ -d /home/jesse/openroot/.git ]; then
  ROOT=/home/jesse/openroot
elif [ -d /data/data/com.termux/files/home/code/openroot/.git ]; then
  ROOT=/data/data/com.termux/files/home/code/openroot
else
  ROOT="${ROOT:-$PWD}"
fi

LEDGER_SRC="${LEDGER_SRC:-}"
if [ -f /home/jesse/openroot/kit/bin/popw_ledger.py ]; then
  LEDGER_SRC=/home/jesse/openroot/kit/bin/popw_ledger.py
elif [ -f "$ROOT/kit/bin/popw_ledger.py" ]; then
  LEDGER_SRC="$ROOT/kit/bin/popw_ledger.py"
elif [ -f "$PWD/popw_ledger.py" ]; then
  LEDGER_SRC="$PWD/popw_ledger.py"
fi

echo "ROOT=$ROOT REPO=$REPO TAG=$TAG PUSH=${PUSH:-0}"
[ -n "$LEDGER_SRC" ] || { echo "FAIL: popw_ledger.py not found. scp it to kit/bin first"; exit 2; }
python3 -m py_compile "$LEDGER_SRC"
WORKDIR=$(mktemp -d)
cp "$LEDGER_SRC" "$WORKDIR/popw_ledger.py"
export POPW_LEDGER="$WORKDIR/test.jsonl"
python3 "$WORKDIR/popw_ledger.py" init
python3 "$WORKDIR/popw_ledger.py" add "ci selftest" --kind yield --joules 0
python3 "$WORKDIR/popw_ledger.py" verify
echo "TEST OK"

cd "$ROOT"
git fetch origin
git checkout main
git pull --ff-only origin main || git pull origin main
git checkout -B "$BRANCH"
mkdir -p tools kit/bin
cp "$LEDGER_SRC" tools/popw_ledger.py
cp "$LEDGER_SRC" kit/bin/popw_ledger.py
git add tools/popw_ledger.py kit/bin/popw_ledger.py
if git diff --cached --quiet; then
  echo "already staged/committed"
else
  git commit -m "feat(ledger): append-only popw jsonl chain"
fi
git fetch origin
git rebase origin/main

if [ "${PUSH:-0}" != 1 ]; then
  echo "TESTED. Not pushed. Re-run: PUSH=1 bash $0"
  git log --oneline -3
  exit 0
fi
command -v gh >/dev/null
gh auth status >/dev/null
git push -u origin "$BRANCH" --force-with-lease
URL=$(gh pr list --repo "$REPO" --head "$BRANCH" --json url --jq '.[0].url' || true)
if [ -z "${URL:-}" ]; then
  gh pr create --repo "$REPO" --base main --head "$BRANCH" \
    --title "feat(ledger): PoPW append-only jsonl" \
    --body "stdlib popw_ledger.py: init/add/tip/verify. Hash-linked jsonl. No dirty-tree dump. No phone GGUF."
  URL=$(gh pr list --repo "$REPO" --head "$BRANCH" --json url --jq '.[0].url')
fi
echo "PR $URL"
gh pr merge "$URL" --squash --delete-branch
git checkout main
git pull --ff-only origin main
git tag -a "$TAG" -m "openroot $TAG popw ledger"
git push origin "$TAG"
gh release create "$TAG" --repo "$REPO" --title "$TAG PoPW ledger" --notes "Append-only hash-linked jsonl. tools/popw_ledger.py. Verify before add."
echo "RELEASED $TAG"
git log --oneline -3
