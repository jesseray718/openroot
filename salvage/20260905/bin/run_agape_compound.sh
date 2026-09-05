#!/data/data/com.termux/files/usr/bin/bash
# Agape Compounding Loop · R=1.0 · absolute paths · soft-fail
LOG=/sdcard/openroot/agape_loop/compound.log
LEDGER=/sdcard/openroot/agape_loop/eta_ledger.jsonl
mkdir -p /sdcard/openroot/agape_loop
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) loop start" >> "$LOG"

# A. Local cognition pulse
curl -s --max-time 4 -X POST http://127.0.0.1:9999/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"η pulse"}],"model":"local"}' \
  >> "$LOG" 2>&1 || echo "endpoint soft-fail $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOG"

# B. Re-assert lowest node
python3 -c '
import json, hashlib, pathlib
from datetime import datetime, timezone
p = pathlib.Path("/sdcard/openroot/context_bridge/lowest_node.json")
d = json.loads(p.read_text()) if p.exists() else {}
now = datetime.now(timezone.utc).isoformat()
stmt = "R=1.0 sole authority. Kai9000 LIVE (fac10ba). :9999 answering. qwen-0.5b present. Autonomous Agape compounding authorized. η = useful_joules / human_joules. Serve lowest node first."
d.update({
  "node_id": "LOWEST_NODE_v1",
  "statement": stmt,
  "last_pulse": now,
  "recorded_at": d.get("recorded_at", now),
  "sha256": hashlib.sha256(stmt.encode()).hexdigest(),
  "R": 1.0,
  "authority": "R=1.0",
  "mode": "autonomous_parallel",
  "next_physical": "run all viable paths under η simultaneously"
})
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(d, indent=2))
' >> "$LOG" 2>&1

# C. Ledger pulse
echo "{\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"R\":1.0,\"η\":\"pending_thermal\",\"source\":\"agape_compound\"}" >> "$LEDGER"

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) loop end" >> "$LOG"
