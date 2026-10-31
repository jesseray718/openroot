#!/usr/bin/env bash
set -eu
cd /home/jesse/openroot
echo "[gate] Syncing state to GitHub..."
git add .
if ! git diff-index --quiet HEAD --; then
    git commit -m "chore: state sync - updated pods and reasoning logs"
    git push origin main
    echo "[banked] State synced."
else
    echo "[banked] No changes to sync."
fi
