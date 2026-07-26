#!/data/data/com.termux/files/usr/bin/bash
# Case Study Collective — dependency-free core
set -euo pipefail

SCRIPT_DIR="\( (cd " \)(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LEDGER="$ROOT/genesis/ledger.jsonl"
STATE="$ROOT/genesis/state.json"

mkdir -p "$ROOT/genesis"
export LEDGER STATE

init() {
  if [[ ! -f "$LEDGER" ]]; then
    echo '{"event":"genesis","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","note":"Case Study Collective — owned by no one, Agape source code"}' > "$LEDGER"
  fi
  if [[ ! -f "$STATE" ]]; then
    echo '{"contributions":0,"members":{},"last_updated":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$STATE"
  fi
  echo "Case Study Collective ready. Owned by no one."
}

status() {
  python3 -c '
import json, os
from pathlib import Path
s = json.loads(Path(os.environ["STATE"]).read_text())
print("=== Case Study Collective ===")
print(f"Recorded contributions : {s.get(\"contributions\", 0)}")
print(f"Active local members   : {len(s.get(\"members\", {}))}")
print(f"Last updated           : {s.get(\"last_updated\")}")
print("Agape source code active. No owners.")
'
}

contribute() {
  local note="${1:-unspecified contribution}"
  python3 - "$note" <<'PY'
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone
note = sys.argv[1]
ledger = Path(os.environ["LEDGER"])
state = Path(os.environ["STATE"])
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
event = {"event":"contribute","ts":ts,"note":note,"member":"local"}
with ledger.open("a") as f: f.write(json.dumps(event)+"\n")
s = json.loads(state.read_text())
s["contributions"] = s.get("contributions",0) + 1
s["members"]["local"] = s["members"].get("local", {"count":0})
s["members"]["local"]["count"] += 1
s["last_updated"] = ts
state.write_text(json.dumps(s, indent=2))
print(f"Contribution recorded: {note}")
PY
}

ledger() {
  echo "=== Transparent Ledger (last 40) ==="
  [[ -f "$LEDGER" ]] && tail -n 40 "$LEDGER" || echo "Empty"
}

handup() {
  echo "Hand-up ranking is determined by need + contribution + fidelity to lowest-node-first."
  echo "Full coefficient logic lives in the personal and business leveling pools."
  echo "This collective prioritizes the study and funding of decentralized solutions that reduce unnecessary suffering."
}

case "${1:-}" in
  init) init ;;
  status) status ;;
  contribute) contribute "${2:-unspecified}" ;;
  ledger) ledger ;;
  handup) handup ;;
  *)
    echo "Case Study Collective — owned by no one"
    echo "Usage: bash pool.sh {init|status|contribute|ledger|handup}"
    ;;
esac
