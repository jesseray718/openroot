#!/usr/bin/env bash
set -euo pipefail

# agape-ipfs installer — for public users
# Usage: ./install.sh

SCRIPT_DIR="\( (cd " \)(dirname "$0")" && pwd)"
BIN_DIR="${1:-$HOME/.local/bin}"
DEST="$BIN_DIR/agape-ipfs"

mkdir -p "$BIN_DIR"
cp "$SCRIPT_DIR/bin/agape-ipfs" "$DEST"
chmod +x "$DEST"

PROFILE="$HOME/.bashrc"
if ! grep -q "$BIN_DIR" "$PROFILE" 2>/dev/null; then
  echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$PROFILE"
  echo "Added $BIN_DIR to PATH in \~/.bashrc"
  echo "Run: source \~/.bashrc"
fi

mkdir -p "$HOME/openroot/agape_net/ledger" "$HOME/openroot/agape_net/ipfs"

echo ""
echo "agape-ipfs v1.0.0 installed to: $DEST"
echo "Ledger: $HOME/openroot/agape_net/ledger/pins.jsonl"
echo ""
echo "Quick start:"
echo "  agape-ipfs pin ./some-file"
echo "  agape-ipfs status"
echo "  agape-ipfs proof <cid>"
echo ""
echo "Optional: Set PINATA_JWT for cloud fallback pinning."
echo "Optional: Set GITHUB_TOKEN for gist proofs."
