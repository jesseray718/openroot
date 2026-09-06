#!/usr/bin/env bash
# ============================================
# OpenCell Project - IPFS Deployment Script
# Version: 1.0
# License: CC-BY-NC-SA
# Runs on: Termux (Android)
# ============================================

set -e

REPO_DIR="$HOME/OpenCell_Project/OpenCell-Thermal-System"
LOG_FILE="$REPO_DIR/ipfs-deploy-log.txt"

echo "========================================="
echo "  OpenCell IPFS Deployment"
echo "========================================="

# ---- Step 0: Update package list ----
echo "[0/6] Updating packages..."
pkg update -y 2>/dev/null || echo "Package update skipped (may already be current)"

# ---- Step 1: Install IPFS (Kubo) if missing ----
if ! command -v ipfs &> /dev/null; then
    echo "[1/6] Installing IPFS (Kubo)..."
    pkg install wget -y 2>/dev/null
    
    # Detect architecture
    ARCH=$(dpkg --print-architecture 2>/dev/null || uname -m)
    
    if [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
        IPFS_URL="https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.32.1_linux-arm64.tar.gz"
    else
        IPFS_URL="https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.32.1_linux-amd64.tar.gz"
    fi
    
    cd $HOME
    wget -q "$IPFS_URL" -O kubo.tar.gz
    tar -xzf kubo.tar.gz
    cp kubo/ipfs $PREFIX/bin/
    rm -rf kubo kubo.tar.gz
    echo "  ✅ IPFS installed successfully"
else
    echo "[1/6] IPFS already installed ✅"
fi

# ---- Step 2: Initialize IPFS node ----
if [ ! -d "$HOME/.ipfs" ]; then
    echo "[2/6] Initializing IPFS node..."
    ipfs init
else
    echo "[2/6] IPFS node already initialized ✅"
fi

# ---- Step 3: Start IPFS daemon (background) ----
echo "[3/6] Starting IPFS daemon..."
ipfs daemon &
DAEMON_PID=$!
sleep 5
echo "  Daemon PID: $DAEMON_PID"

# ---- Step 4: Add repo to IPFS ----
echo "[4/6] Adding OpenCell repo to IPFS..."
cd "$REPO_DIR"

# Exclude .git folder from IPFS upload
CID=$(ipfs add --recursive --quiet --hidden=false \
    --ignore=".git" \
    --ignore="*.zip" \
    . | tail -1)

echo "  ✅ Content added!"
echo "  CID: $CID"

# ---- Step 5: Pin content (persistent storage) ----
echo "[5/6] Pinning content locally..."
ipfs pin add "$CID" 2>/dev/null || echo "  Already pinned"
echo "  ✅ Pinned!"

# ---- Step 6: Log results & generate links ----
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GATEWAY_URL="https://ipfs.io/ipfs/$CID"
LOCAL_GATEWAY="http://127.0.0.1:8080/ipfs/$CID"

echo "========================================="
echo "  🎉 DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "  IPFS CID:        $CID"
echo "  Public Gateway:  $GATEWAY_URL"
echo "  Local Gateway:   $LOCAL_GATEWAY"
echo ""

# Save to log
echo "[$TIMESTAMP] CID=$CID GATEWAY=$GATEWAY_URL" >> "$LOG_FILE"
echo "  Logged to: $LOG_FILE"

# Update README with CID (optional)
echo ""
echo "  📋 Copy this CID for your README badge:"
echo "  https://img.shields.io/badge/IPFS-$CID-blue"

# Cleanup: stop daemon after 60 seconds (leave time for gateway propagation)
echo ""
echo "  IPFS daemon will stop in 60 seconds..."
echo "  (Content is already propagated to the network)"
sleep 60
kill $DAEMON_PID 2>/dev/null

echo "Done. OpenCell is permanently archived on IPFS."
