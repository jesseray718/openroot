#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "=============================================="
echo "  OpenRoot Leveling Cooperative"
echo "  Hand-up, not hand-out"
echo "=============================================="

HOME_DIR="/data/data/com.termux/files/home"
OPENROOT="$HOME_DIR/openroot"
POOL_DIR="$OPENROOT/leveling-cooperative"

cd "$OPENROOT"
git pull --ff-only || true

cd "$POOL_DIR"
chmod +x zero-dep-app/*.sh handbook/*.sh 2>/dev/null || true

bash zero-dep-app/pool.sh init

echo ""
echo "READY. Useful commands:"
echo "  bash zero-dep-app/pool.sh status"
echo "  bash zero-dep-app/pool.sh invest 25.00 \"note\""
echo "  bash zero-dep-app/pool.sh dividend"
echo "  bash zero-dep-app/pool.sh handup"
echo "  bash zero-dep-app/pool.sh ledger"
