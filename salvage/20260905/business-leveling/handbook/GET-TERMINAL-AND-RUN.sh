#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
echo "=== OpenRoot Business Leveling Cooperative ==="
cd $HOME/openroot/business-leveling
chmod +x zero-dep-app/*.sh handbook/*.sh 2>/dev/null || true
bash zero-dep-app/pool.sh init
echo ""
echo "Ready. Commands:"
echo "  bash zero-dep-app/pool.sh status"
echo "  bash zero-dep-app/pool.sh invest 100 \"LLC seed\""
echo "  bash zero-dep-app/pool.sh dividend"
echo "  bash zero-dep-app/pool.sh handup"
echo "Anti-capture rules active (whale cap + diminishing influence)."
