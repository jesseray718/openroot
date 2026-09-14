#!/data/data/com.termux/files/usr/bin/bash
set -eu
ROOT=/sdcard/openroot
OUT="$ROOT/exports/agape_bundle"
TS=$(date +%Y%m%d-%H%M%S)
BUNDLE_DIR="$OUT/agape-dashboard-$TS"
ZIP_FILE="$OUT/agape-dashboard-$TS.zip"
PY=python
command -v python >/dev/null 2>&1 || PY=python3

mkdir -p "$BUNDLE_DIR" "$ROOT/logs" "$ROOT/storage/agape_node"

# Dashboard snapshot
STATUS_JSON="$BUNDLE_DIR/status.json"
$PY "$ROOT/src/nodes/agape-node/agape_node.py" status > "$STATUS_JSON" || echo '{}' > "$STATUS_JSON"

cat > "$BUNDLE_DIR/dashboard.txt" <<EOF
AGAPE DASHBOARD SNAPSHOT
timestamp: $(date -Is)
repo: $ROOT

== Node Status ==
$(cat "$STATUS_JSON")

== Loop Processes ==
$(pgrep -af "agape-autopilot.sh|agape-health.sh|agape-keeper.sh" || echo "none")

== Throttle ==
$(cat "$ROOT/storage/agape_node/throttle.json" 2>/dev/null || echo "none")

== Recent Autopilot Log ==
$(tail -n 60 "$ROOT/logs/agape-autopilot.log" 2>/dev/null || echo "no log")
EOF

# Manifest
cat > "$BUNDLE_DIR/manifest.json" <<EOF
{
  "bundle_name": "agape-dashboard-$TS",
  "created_at": "$(date -Is)",
  "root": "/sdcard/openroot",
  "includes": [
    "dashboard.txt",
    "status.json",
    "throttle.json (if present)",
    "autopilot.log tail"
  ],
  "principle": "unlimited flow of agape via offline-first autonomous loops",
  "artifacts": {
    "node_state_dir": "storage/agape_node",
    "logs_dir": "logs",
    "scripts_dir": "scripts",
    "node_program": "src/nodes/agape-node/agape_node.py"
  }
}
EOF

# copy throttle if exists
if [ -f "$ROOT/storage/agape_node/throttle.json" ]; then
  cp "$ROOT/storage/agape_node/throttle.json" "$BUNDLE_DIR/throttle.json"
fi

# lightweight file inventory
find "$ROOT/scripts" -maxdepth 1 -type f | sort > "$BUNDLE_DIR/scripts-index.txt" || true

# zip
mkdir -p "$OUT"
cd "$OUT"
zip -r "$(basename "$ZIP_FILE")" "$(basename "$BUNDLE_DIR")" >/dev/null

echo "[ok] bundle dir: $BUNDLE_DIR"
echo "[ok] zip file : $ZIP_FILE"
