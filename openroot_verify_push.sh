#!/usr/bin/env bash
set -Eeuo pipefail

REPO_DIR="${HOME}/openroot"
cd "$REPO_DIR"

REMOTE_URL="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$REMOTE_URL" ]]; then
    echo "FATAL: no origin remote configured."
    exit 1
fi

echo "Remote origin: $REMOTE_URL"
echo "Local branch:  $(git rev-parse --abbrev-ref HEAD)"
echo "Local HEAD:    $(git rev-parse HEAD)"

echo "[1/3] Verifying remote access..."
if ! git ls-remote --exit-code origin HEAD >/dev/null 2>&1; then
    echo "STATUS: REMOTE_UNREACHABLE_OR_MISSING"
    echo "Do not claim synchronization."
    exit 2
fi

echo "[2/3] Fetching remote main..."
if ! git fetch origin main --quiet; then
    echo "STATUS: FETCH_FAILED"
    exit 3
fi

LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse origin/main 2>/dev/null || true)"

if [[ -z "$REMOTE_SHA" ]]; then
    echo "STATUS: REMOTE_MAIN_MISSING"
    exit 4
fi

echo "Remote main SHA: $REMOTE_SHA"

if [[ "$LOCAL_SHA" == "$REMOTE_SHA" ]]; then
    echo "STATUS: LOCAL_MAIN_MATCHES_VERIFIED_REMOTE_MAIN"
else
    echo "STATUS: LOCAL_AND_REMOTE_DIFFER"
    git log --oneline --left-right --cherry-pick \
        "$REMOTE_SHA...$LOCAL_SHA" | head -n 20
fi

echo "[3/3] Comparing local and remote tags..."
COMM -3 \
    <(git tag -l | sort) \
    <(git ls-remote --tags origin 2>/dev/null |
      awk -F'/' '{print $NF}' | sed 's/\^{}//' | sort -u) |
    sed 's/^\t/REMOTE_ONLY: /; s/^\([^\t]\)/LOCAL_ONLY: \1/' |
    head -n 30
