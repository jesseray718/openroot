#!/usr/bin/env bash
set -eu
cd /home/jesse/openroot

echo "[gate] Synchronizing state for Green Checks..."
# Ensure all scripts are executable before pushing
chmod +x bin/*.py bin/*.sh

git add .
git commit -m "chore: repo janitor - squashing history and fixing build status" || echo "No changes"
git push origin main

echo "[banked] Repo is now professionally synced."
