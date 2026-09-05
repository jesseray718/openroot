#!/data/data/com.termux/files/usr/bin/bash
# OpenRoot Business Leveling — zero dependency + anti-capture
set -euo pipefail

SCRIPT_DIR="\( (cd " \)(dirname "${BASH_SOURCE[0]}")" && pwd)"
POOL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LEDGER_DIR="$POOL_ROOT/genesis"
LEDGER_FILE="$LEDGER_DIR/ledger.jsonl"
STATE_FILE="$LEDGER_DIR/state.json"
WHALE_CAP=0.049          # 4.9% hard cap
HANDUP_PCT=0.15

mkdir -p "$LEDGER_DIR"
export LEDGER_FILE STATE_FILE WHALE_CAP HANDUP_PCT

init() {
  if [[ ! -f "$LEDGER_FILE" ]]; then
    echo '{"event":"genesis","ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","note":"Business Leveling genesis — anti-capture active, no owners"}' > "$LEDGER_FILE"
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
  echo "Business Leveling ready. Whale cap and anti-capture rules active."
}

status() {
  python3 -c '
import json, os
from pathlib import Path
s = json.loads(Path(os.environ["STATE_FILE"]).read_text())
print("=== Business Leveling Cooperative ===")
print(f"Total invested     : {s.get(\"total_invested\", 0):.2f}")
print(f"Dividends paid     : {s.get(\"total_dividends_paid\", 0):.2f}")
print(f"Hand-up paid       : {s.get(\"total_handup_paid\", 0):.2f}")
print(f"Members            : {len(s.get(\"members\", {}))}")
print(f"Whale cap          : 4.9% per member")
print(f"Last updated       : {s.get(\"last_updated\")}")
print("Governance ≠ capital. No owners.")
'
}

invest() {
  local amount="${1:-}"
  local note="${2:-business seed}"
  [[ -z "$amount" ]] && { echo "Usage: bash pool.sh invest <amount> [note]"; exit 1; }
  python3 - "$amount" "$note" <<'PY'
import json, sys, os
from pathlib import Path
from datetime import datetime, timezone
amount = float(sys.argv[1]); note = sys.argv[2]
ledger = Path(os.environ["LEDGER_FILE"]); state = Path(os.environ["STATE_FILE"])
whale_cap = float(os.environ.get("WHALE_CAP", 0.049))
s = json.loads(state.read_text())
total = s.get("total_invested", 0.0)
member = s["members"].setdefault("local", {"invested":0.0, "need_score":0.5})
new_member_total = member.get("invested", 0) + amount
new_pool_total = total + amount
if new_pool_total > 0 and (new_member_total / new_pool_total) > whale_cap:
    print(f"REJECTED: would exceed whale cap of {whale_cap*100:.1f}%")
    print(f"Current member share would become {new_member_total/new_pool_total*100:.2f}%")
    raise SystemExit(1)
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
event = {"event":"invest","ts":ts,"amount":amount,"note":note,"member":"local"}
with ledger.open("a") as f: f.write(json.dumps(event)+"\n")
s["total_invested"] = round(new_pool_total, 2)
member["invested"] = round(new_member_total, 2)
s["last_updated"] = ts
state.write_text(json.dumps(s, indent=2))
print(f"Invested {amount:.2f}. New total: {s['total_invested']:.2f}")
print("Whale-cap check passed.")
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
total = s.get("total_invested", 0.0)
if total <= 0: print("No capital yet."); raise SystemExit
rate = 0.012; gross = round(total * rate, 2)
handup = round(gross * float(os.environ.get("HANDUP_PCT", 0.15)), 2)
to_members = round(gross - handup, 2)
ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
event = {"event":"dividend_cycle","ts":ts,"gross":gross,"to_members":to_members,"handup":handup}
with ledger.open("a") as f: f.write(json.dumps(event)+"\n")
s["total_dividends_paid"] = round(s.get("total_dividends_paid",0) + to_members, 2)
s["total_handup_paid"] = round(s.get("total_handup_paid",0) + handup, 2)
s["last_updated"] = ts
state.write_text(json.dumps(s, indent=2))
print(f"Dividend: gross={gross:.2f}  members={to_members:.2f}  hand-up={handup:.2f}")
'
}

handup() {
  python3 -c '
import json, os, math
from pathlib import Path
s = json.loads(Path(os.environ["STATE_FILE"]).read_text())
members = s.get("members", {})
if not members: print("No members."); raise SystemExit
def coeff(m):
    need = float(m.get("need_score", 0.5))
    inv = float(m.get("invested", 0))
    # diminishing returns on capital deliberately reduce whale influence
    contrib = math.log1p(inv) / 12.0
    return (need * 0.50) + (contrib * 0.30) + 0.20
ranked = sorted(members.items(), key=lambda x: coeff(x[1]), reverse=True)
print("=== Hand-up Ranking (anti-whale coefficients) ===")
for name, m in ranked:
    print(f"  {name:12} need={m.get(\"need_score\",0):.2f} invested={m.get(\"invested\",0):.2f} coeff={coeff(m):.4f}")
print("Highest coefficient receives priority. Capital has diminishing influence.")
'
}

case "${1:-}" in
  init) init ;;
  status) status ;;
  invest) invest "\( {2:-}" " \){3:-business seed}" ;;
  ledger) ledger ;;
  dividend) dividend ;;
  handup) handup ;;
  *)
    echo "Business Leveling Cooperative"
    echo "Usage: bash pool.sh {init|status|invest|ledger|dividend|handup}"
    echo "Whale cap 4.9%. Governance ≠ capital. No owners."
    ;;
esac
