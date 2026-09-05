#!/data/data/com.termux/files/usr/bin/bash
set -eu

ROOT=/sdcard/openroot
TS=$(date +%Y%m%d-%H%M%S)
REL_ROOT="$ROOT/exports/agape_release"
PKG_DIR="$REL_ROOT/agape-release-$TS"
ZIP_FILE="$REL_ROOT/agape-release-$TS.zip"
PY=python
command -v python >/dev/null 2>&1 || PY=python3

mkdir -p "$PKG_DIR" "$REL_ROOT" "$ROOT/logs" "$ROOT/storage/agape_node" "$ROOT/backups/agape_node"

echo "[1/7] capture live status"
$PY "$ROOT/src/nodes/agape-node/agape_node.py" status > "$PKG_DIR/status.json" || echo '{}' > "$PKG_DIR/status.json"

echo "[2/7] include throttle + logs tail"
cp "$ROOT/storage/agape_node/throttle.json" "$PKG_DIR/throttle.json" 2>/dev/null || true
tail -n 200 "$ROOT/logs/agape-autopilot.log" > "$PKG_DIR/autopilot.log.tail.txt" 2>/dev/null || true
tail -n 120 "$ROOT/logs/health.out" > "$PKG_DIR/health.out.tail.txt" 2>/dev/null || true
tail -n 120 "$ROOT/logs/keeper.out" > "$PKG_DIR/keeper.out.tail.txt" 2>/dev/null || true

echo "[3/7] generate backup snapshot"
if [ -x "$ROOT/scripts/agape-backup.sh" ]; then
  bash "$ROOT/scripts/agape-backup.sh"
fi
LATEST_BACKUP=$(ls -1t "$ROOT"/backups/agape_node/agape-node-*.tgz 2>/dev/null | head -n1 || true)
if [ -n "${LATEST_BACKUP:-}" ]; then
  cp "$LATEST_BACKUP" "$PKG_DIR/"
fi

echo "[4/7] include docs and registry"
cp "$ROOT/docs/offline-toolkit.md" "$PKG_DIR/" 2>/dev/null || true
cp "$ROOT/registry/contribution-backlog.md" "$PKG_DIR/" 2>/dev/null || true
cp "$ROOT/README_CONTRIBUTION_HUB.md" "$PKG_DIR/" 2>/dev/null || true
cp "$ROOT/CONTRIBUTION_HUB_POLICY.md" "$PKG_DIR/" 2>/dev/null || true

echo "[5/7] include scripts + node source indexes"
mkdir -p "$PKG_DIR/index"
find "$ROOT/scripts" -maxdepth 1 -type f | sort > "$PKG_DIR/index/scripts-index.txt" || true
find "$ROOT/src/nodes/agape-node" -maxdepth 2 -type f | sort > "$PKG_DIR/index/agape-node-index.txt" || true

echo "[6/7] write manifest + dashboard"
cat > "$PKG_DIR/manifest.json" <<EOF
{
  "release_name": "agape-release-$TS",
  "created_at": "$(date -Is)",
  "root": "/sdcard/openroot",
  "mode": "offline-first autonomous node",
  "principle": "unlimited flow of agape through resilient, compounding loops",
  "includes": [
    "status.json",
    "throttle.json (if present)",
    "autopilot/health/keeper log tails",
    "latest agape_node backup archive",
    "offline-toolkit.md",
    "contribution-backlog.md",
    "contribution policy docs",
    "scripts and node indexes"
  ],
  "ops": {
    "start": "nohup bash scripts/agape-health.sh & nohup bash scripts/agape-keeper.sh & nohup bash scripts/agape-autopilot.sh &",
    "status": "python src/nodes/agape-node/agape_node.py status",
    "stop": "pkill -f agape-autopilot.sh; pkill -f agape-health.sh; pkill -f agape-keeper.sh"
  }
}
EOF

cat > "$PKG_DIR/dashboard.txt" <<EOF
AGAPE RELEASE DASHBOARD
timestamp: $(date -Is)

== STATUS ==
$(cat "$PKG_DIR/status.json")

== PROCESSES ==
$(pgrep -af "agape-autopilot.sh|agape-health.sh|agape-keeper.sh" || echo "none")

== THROTTLE ==
$(cat "$PKG_DIR/throttle.json" 2>/dev/null || echo "none")

== QUEUE FILE ==
$(ls -lah "$ROOT/storage/agape_node/queue.jsonl" 2>/dev/null || echo "no queue file")
EOF

echo "[7/7] zip package"
cd "$REL_ROOT"
zip -r "$(basename "$ZIP_FILE")" "$(basename "$PKG_DIR")" >/dev/null

echo
echo "[ok] release folder: $PKG_DIR"
echo "[ok] release zip   : $ZIP_FILE"
