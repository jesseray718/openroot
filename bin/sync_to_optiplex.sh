#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
# Sync local Termux openroot node with OptiPlex 3060 & force GitHub Push

TARGET_IP="100.122.169.43"
TARGET_USER="jesse"
REMOTE_PATH="~/openroot"

echo "[1/4] Syncing local Termux repository to OptiPlex 3060..."
rsync -avz -e ssh --exclude='.git/' /data/data/com.termux/files/home/openroot/ ${TARGET_USER}@${TARGET_IP}:${REMOTE_PATH}/

echo "[2/4] Executing Master Deploy & Git Remote Link on OptiPlex..."
ssh ${TARGET_USER}@${TARGET_IP} << 'REMOTECMD'
cd ~/openroot

# Run local deploy engine on OptiPlex
python3 bin/openroot_master_deploy.py

# Check if git remote origin exists; if missing, construct from gh CLI
if ! git remote | grep -q "origin"; then
    echo "[!] Setting git remote origin via gh CLI..."
    REPO_NAME=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
    if [ -n "$REPO_NAME" ]; then
        git remote add origin "https://github.com/${REPO_NAME}.git"
        echo "[+] Added remote origin: https://github.com/${REPO_NAME}.git"
    else
        echo "[!] Remote identification failed. Ensure gh auth status is active on OptiPlex."
    fi
fi

# Stage, commit, and push to remote repository
git add .
git commit -m "feat(optiplex): automated node sync, wiki generate, and remote push" || true
git push -u origin $(git branch --show-current) || git push origin main || git push origin master
REMOTECMD

echo "[3/4] Pulling updated Git state back to Termux..."
REMOTE_ORIGIN=$(ssh ${TARGET_USER}@${TARGET_IP} "cd ~/openroot && git remote get-url origin 2>/dev/null")
if [ -n "$REMOTE_ORIGIN" ]; then
    git remote rm origin 2>/dev/null || true
    git remote add origin "$REMOTE_ORIGIN"
    git fetch origin
    git branch --set-upstream-to=origin/main main 2>/dev/null || true
    echo "[+] Termux local remote synced to: $REMOTE_ORIGIN"
fi

echo "[4/4] Sync Complete."
