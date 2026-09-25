#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
# Permaculture Orchestrator v3 — compact, short-line, paste-safe
set -euo pipefail
export GIT_PAGER=cat
cd /home/jesse/openroot

CANARY="[PERMA-V3]"
DB="data/log_feed.db"
DEBATE="data/debate_ledger.jsonl"
LEDGER="data/cost_ledger.jsonl"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT="context_bridge/permaculture-${STAMP}.md"
mkdir -p logs context_bridge data

echo "$CANARY boot — 12 principles, one chain"

int() {
  local v
  read -r v _ <<< "${1:-0}"
  [[ "$v" =~ ^[0-9]+$ ]] && echo "$v" || echo 0
}

sqlc() { sqlite3 "$DB" "$1" 2>/dev/null || echo 0; }

log() { printf '%s|%s|%s\n' "$STAMP" "$1" "$2" >> "$LEDGER"; }

TAGS="$(curl -s --max-time 5 http://localhost:11434/api/tags \
  || echo '{"models":[]}')"
MSTATS="$(python3 -c '
import json,sys
try:
  ms=[m.get("name","").lower() for m in json.loads(sys.argv[1]).get("models",[])]
except Exception:
  ms=[]
print(len(ms),sum("3b" in m for m in ms),sum("7b" in m for m in ms))
' "$TAGS")"
read -r MT M3B M7B <<< "$MSTATS"
MT=$(int "$MT"); M3B=$(int "$M3B"); M7B=$(int "$M7B")

# P1 Observe and Interact
MEM=$(free -m | awk 'NR==2{printf "%.1f",$3/$2*100}')
DISK=$(df --output=pcent . | tail -1 | tr -dc '0-9')
LOAD=$(cut -d' ' -f1 /proc/loadavg)
if pgrep -x ollama >/dev/null; then SV=up; else SV=down; fi
log P1 "mem_pct=$MEM disk_pct=$DISK load=$LOAD ollama=$SV"
echo "[P1] mem=${MEM}% disk=${DISK}% load=$LOAD ollama=$SV"

# P2 Catch and Store Energy
FTS=$(sqlc "SELECT COUNT(*) FROM fts_evidence;")
log P2 "warm_models=$MT fts_excerpts=$FTS"
echo "[P2] $MT models warm, $FTS FTS5 excerpts"

# P3 Obtain a Yield
PN=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE dispatch_status='pending';")
GR=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE dispatch_status='graded';")
PA=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE verdict='pass';")
HO=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE verdict='hold';")
FA=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE verdict='fail';")
log P3 "pending=$PN graded=$GR pass=$PA hold=$HO fail=$FA"
echo "[P3] pending=$PN graded=$GR pass=$PA hold=$HO fail=$FA"

# P4 Apply Self-Regulation
EP=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE COALESCE(CAST(errs AS INTEGER),0)>0;")
log P4 "errs_blocked=$EP"
echo "[P4] $EP files behind errs>0 gate"

# P5 Use Renewable Resources
DL=0
if [ -f "$DEBATE" ]; then DL=$(wc -l < "$DEBATE"); fi
log P5 "local_models=$MT debate_entries=$DL"
echo "[P5] $MT local models, $DL debate entries"

# P6 Produce No Waste
TT=$(sqlc "SELECT COUNT(*) FROM log_feed;")
DP=$(sqlc "SELECT COUNT(*) FROM (SELECT sha256 FROM log_feed GROUP BY sha256 HAVING COUNT(*)>1);")
log P6 "dupes=$DP total=$TT graded=$GR"
echo "[P6] dupes=$DP total=$TT"

# P7 Design from Patterns
SH=$(sqlite3 "$DB" ".schema log_feed" 2>/dev/null | sha256sum | cut -c1-12)
[ -n "$SH" ] || SH=none
CP=$(git log --oneline -5 | grep -c '\[' || true)
log P7 "schema=$SH patterned_commits=$(int "$CP")"
echo "[P7] schema=$SH patterned=$(int "$CP")"

# P8 Integrate Rather Than Segregate
JN=$(sqlc "SELECT COUNT(*) FROM fts_evidence f JOIN log_feed l ON f.sha256=l.sha256;")
log P8 "fts=$FTS log_feed=$TT joined=$JN"
echo "[P8] $FTS fts rows, $JN joined"

# P9 Small and Slow Solutions
MOT=$((MT - M3B - M7B))
log P9 "tiny_3b=$M3B small_7b=$M7B other=$MOT"
echo "[P9] 3b=$M3B 7b=$M7B other=$MOT"

# P10 Use and Value Diversity
VS=$(sqlc "SELECT COUNT(DISTINCT verdict) FROM log_feed WHERE verdict IS NOT NULL AND verdict!='';")
SC=$(find bin -maxdepth 1 -type f \( -name '*.sh' -o -name '*.py' \) | wc -l)
log P10 "models=$MT verdict_types=$VS scripts=$SC"
echo "[P10] $MT models, $VS verdict types, $SC scripts"

# P11 Edges and Value the Marginal
HQ=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE verdict='hold';")
BW=$(sqlc "SELECT COUNT(*) FROM log_feed WHERE COALESCE(warns,0)>0 AND COALESCE(CAST(errs AS INTEGER),0)=0;")
QD=$(find . -maxdepth 1 -type d -name 'quarantine*' | wc -l)
log P11 "holds=$HQ borderline=$BW quarantine_dirs=$QD"
echo "[P11] holds=$HQ borderline=$BW quarantine=$QD"

# P12 Creatively Respond to Change
CU=$(git rev-parse --short HEAD 2>/dev/null || echo unknown)
RB=$(git tag 2>/dev/null | wc -l)
log P12 "head=$CU rollback_tags=$RB"
echo "[P12] head=$CU rollback_tags=$RB"

{
  echo "# Permaculture Orchestrator v3 — $STAMP"
  echo ""
  echo "- key=value ledger: $LEDGER (1 line per principle per run)"
  echo "- single shared Ollama fetch; all numerics sanitized"
  echo ""
  grep "^$STAMP" "$LEDGER" || true
} > "$REPORT"

echo "$CANARY 12 stages complete"
sha256sum "$REPORT" | awk '{print "["$2"] "$1}'
echo "$CANARY [banked] staged: $REPORT — review, then commit yourself"
echo "$CANARY [exit=0]"
