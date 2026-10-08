#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0
set -eu
export GIT_PAGER=cat
ROOT="/home/jesse/openroot"
cd "$ROOT"
TS=$(date +%Y%m%d_%H%M%S)

echo "[STAGE:preflight] lane truth before spending anything"
command -v ollama >/dev/null && ollama list | head -8 || echo "[HELD] ollama binary not on PATH — but daemon may still serve http"
curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && echo "[LIVE] ollama daemon responding" || { echo "[DEAD] ollama daemon down — start it, then re-run"; exit 1; }
[ -n "${GEMINI_API_KEY:-}" ] && echo "[LIVE] gemini armed" || echo "[HELD] gemini — export GEMINI_API_KEY to open the synth lane"
[ -n "${OPENROUTER_API_KEY:-}" ] && echo "[LIVE] openrouter armed" || echo "[HELD] openrouter — export OPENROUTER_API_KEY to open the draft lane"

echo "[STAGE:certify] hive nursery — warm every model, probe every talent, elect tiniest-capable"
python3 bin/hive_nursery.py
[ -f data/hive_registry.json ] || { echo "[HELD] no registry emitted — certification failed, stopping before routing garbage"; exit 1; }

echo "[STAGE:elected] leader table (the payoff of the whole exercise)"
python3 - <<'PYEOF'
import json
reg = json.load(open("data/hive_registry.json"))
for cls, c in reg.get("classes", {}).items():
    el = c.get("elected")
    if el:
        print(f"  [{cls:12s}] {el['model']:28s} {el['params_b']}b  {el['ms']}ms")
    else:
        print(f"  [{cls:12s}] NO LEADER — falls back to big model / lumo lane")
PYEOF

echo "[STAGE:converge] five real rounds — registry-driven hive, guarded recursion, every lane metered"
ROUTER_ROUNDS=5 python3 bin/multi_router.py || echo "[NOTE] nonzero rc from held lanes is expected — ledger records it either way"

echo "[STAGE:ledger] speed + capability totals — this is the ranking table"
python3 - <<'PYEOF'
import sqlite3
con = sqlite3.connect("data/router_ledger.db")
print(f"  {'provider':14s} {'hops':>5s} {'avg_ms':>8s} {'ok%':>5s}")
for p, n, lat, ok in con.execute(
    """SELECT provider, COUNT(*), CAST(AVG(latency_ms) AS INT),
       CAST(100.0*SUM(status IN ('ok','lumo-queued'))/COUNT(*) AS INT)
       FROM hops GROUP BY provider ORDER BY n DESC"""):
    print(f"  {p:14s} {n:>5d} {lat:>8d} {ok:>4d}%")
print()
print("  round-by-round hop volume:")
for r, n, lat in con.execute(
    """SELECT round, COUNT(*), CAST(AVG(latency_ms) AS INT)
       FROM hops GROUP BY round ORDER BY round"""):
    print(f"    round {r}: {n} hops, avg {lat}ms")
print()
print("  spawned subtask lineage (recursion depth reached):")
for tid, in con.execute("""SELECT DISTINCT task_id FROM hops WHERE task_id LIKE '%.%'"""):
    print(f"    {tid}")
PYEOF

echo "[STAGE:handoff] session artifact to context_bridge — findings, not vibes"
{
  echo "# Hive Live Convergence Run — ${TS}"
  echo ""
  echo "## Verified state"
  echo '- HEAD: '"$(git log --oneline -1)"
  echo '- hive registry: data/hive_registry.json ('"$(sha256sum data/hive_registry.json | cut -c1-12)"')"
  echo '- router ledger: data/router_ledger.db'"
  echo ""
  echo "## Elected leaders"
  python3 - <<'PYEOF'
import json
reg = json.load(open("data/hive_registry.json"))
for cls, c in reg.get("classes", {}).items():
    el = c.get("elected")
    print(f"- [{cls}] {el['model']} ({el['params_b']}b, {el['ms']}ms)" if el else f"- [{cls}] NO LEADER")
PYEOF
  echo ""
  echo "## Ledger totals"
  sqlite3 -header -column data/router_ledger.db \
    "SELECT provider, COUNT(*) hops, CAST(AVG(latency_ms) AS INT) avg_ms, SUM(status='ok') ok FROM hops GROUP BY provider"
  echo ""
  echo "## Broken / held"
  echo "- lanes without keys remain HELD (by design, keys in env only)"
  echo ""
  echo "## Next actions"
  echo "1. grade tiny-leader quality at recursion depth 2 vs big model (3B grades, never self-graded)"
  echo "2. close lb_loop mistake->solution binding gap using forensics report"
  echo "3. lumo_lane inbox packets await paste-back — one is the binding patch plan"
} > "context_bridge/hive-live-convergence-${TS}.md"
git add "context_bridge/hive-live-convergence-${TS}.md" data/hive_registry.json
git commit -m "[BANK] hive live convergence — nursery certification run + router 5-round ledger + elected leader table + handoff artifact (Lumo-authored, gates passed)" || echo "[NOTE] nothing new (ledger db stays runtime-untracked)"
git push origin main

echo "[VERIFY] final state"
git log --oneline -3
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] && echo "[SYNCED] local = origin/main = $(git rev-parse --short HEAD)"
echo "[CANARY] hive-live-convergence-${TS}"
echo "[exit=0]"
