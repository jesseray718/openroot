#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="/data/data/com.termux/files/home/openroot"
QUERY="${*:-}"
STAMP=$(date -u +%Y%m%d_%H%M%S)
OUTDIR="$ROOT/context_bridge/hive_runs"
mkdir -p "$OUTDIR"
OUTFILE="\( OUTDIR/hive_ \){STAMP}.txt"

if [ -z "$QUERY" ]; then
  echo "Usage: bash bin/hive.sh \"your question\""
  exit 1
fi

echo "Running offline fractal nanobot lattice..."
cd "$ROOT"
python3 nanobot_lattice.py "$QUERY" | tee "$OUTFILE"

echo ""
echo "Result saved to: $OUTFILE"
