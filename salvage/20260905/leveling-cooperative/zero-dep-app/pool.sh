#!/data/data/com.termux/files/usr/bin/bash
# OpenRoot Leveling Cooperative — zero dependency core
set -euo pipefail

SCRIPT_DIR="\( (cd " \)(dirname "${BASH_SOURCE[0]}")" && pwd)"
POOL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LEDGER_DIR="$POOL_ROOT/genesis"
LEDGER_FILE="$LEDGER_DIR/ledger.jsonl"
STATE_FILE="$LEDGER_DIR/state.json"

mkdir -p "$LEDGER_DIR"
export LEDGER_FILE STATE_FILE

init() {
  if [[ ! -f "$LEDGER_FILE" ]]; then
    echo '{"event":"genesis","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","note":"Leveling Cooperative genesis — no owners"}' > "$LEDGER_FILE"
  fi
  if [[ ! -f "$STATE_FILE" ]]; then
    cat > "$STATE_FILE" <<EOF2
{
  "total_invested": 0.0,
  "total_dividends_paid": 0.0,
  "total_handup_paid": 0.0,
  "members": {},
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF2
  fi
  echo "Ready."
}

status() {
  python3 -c '
import json, os
from pathlib import Path
s = json.loads(Path(os.environ["STATE_FILE"]).read_text())
print("=== Leveling Cooperative Status ===")
print(f"Total invested     : {s.get(\"total_invested\", 0):.2f}")
print(f"Dividends paid     : {s.get(\"total_dividends_paid\", 0):.2f}")
print(f"Hand-up paid       : {s.get(\"total_handup_paid\", 0):.2f}")
print(f"Members            : {len(s.get(\"members\", {}))}")
print(f"Last updated       : {s.get(\"last_updated\")}")
print("No owners. Fixed hand-up. Fully local.")
'
}

invest() {
  local amount="${1:-}"
  local note="${2:-manual investment}"
  [[ -z "$amount" ]] && { echo "Usage: bash pool.sh invest <amount> [note]"; exit 1; }
  python3 - "$amount" "$note" <<'PY'
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone
amount = float(sys.argv[1]); note = sys.argv[2]
ledger = Path(os.environ["LEDGER_FILE"]); state = Path(os.environ["STATE_FILE"])
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
event = {"event":"invest","ts":ts,"amount":amount,"note":note,"member":"local"}
with ledger.open("a") as f: f.write(json.dumps(event)+"\n")
s = json.loads(state.read_text())
s["total_invested"] = round(s.get("total_invested",0)+amount,2)
s["last_updated"] = ts
m = s["members"].setdefault("local",{"invested":0.0,"need_score":0.5,"joined":ts})
m["invested"] = round(m.get("invested",0)+amount,2)
state.write_text(json.dumps(s,indent=2))
print(f"Invested {amount:.2f}. New total: {s['total_invested']:.2f}")
PY
}

ledger() {
  echo "=== Transparent Ledger (last 30) ==="
  [[ -f "$LEDGER_FILE" ]] && tail -n 30 "$LEDGER_FILE" || echo "No ledger yet."
}

dividend() {
  python3 -c '
import json, os
from pathlib import Path
from datetime import datetime, timezone
state = Path(os.environ["STATE_FILE"]); ledger = Path(os.environ["LEDGER_FILE"])
s = json.loads(state.read_text())
total = s.get("total_invested",0.0)
if total <= 0: print("No capital yet."); raise SystemExit
rate=0.015; gross=round(total*rate,2); handup=round(gross*0.15,2); to_members=round(gross-handup,2)
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
event={"event":"dividend_cycle","ts":ts,"gross":gross,"to_members":to_members,"handup":handup}
with ledger.open("a") as f: f.write(json.dumps(event)+"\n")
s["total_dividends_paid"]=round(s.get("total_dividends_paid",0)+to_members,2)
s["total_handup_paid"]=round(s.get("total_handup_paid",0)+handup,2)
s["last_updated"]=ts
state.write_text(json.dumps(s,indent=2))
print(f"Dividend cycle: gross={gross:.2f}  members={to_members:.2f}  hand-up={handup:.2f}")
'
}

handup() {
  python3 -c '
import json, os, math
from pathlib import Path
s = json.loads(Path(os.environ["STATE_FILE"]).read_text())
members = s.get("members",{})
if not members: print("No members."); raise SystemExit
def coeff(m):
    need=float(m.get("need_score",0.5)); inv=float(m.get("invested",0))
    return (need*0.45) + (math.log1p(inv)/10*0.35) + 0.20
ranked = sorted(members.items(), key=lambda x: coeff(x[1]), reverse=True)
print("=== Hand-up Ranking ===")
for name,m in ranked:
    print(f"  {name:12} need={m.get(\"need_score\",0):.2f} invested={m.get(\"invested\",0):.2f} coeff={coeff(m):.4f}")
print("Highest coefficient gets priority hand-up.")
'
}

case "${1:-}" in
  init) init ;;
  status) status ;;
  invest) invest "\( {2:-}" " \){3:-manual}" ;;
  ledger) ledger ;;
  dividend) dividend ;;
  handup) handup ;;
  *)
    echo "Usage: bash pool.sh {init|status|invest|ledger|dividend|handup}"
    echo "No owners. Fixed hand-up. Fully local."
    ;;
esac
