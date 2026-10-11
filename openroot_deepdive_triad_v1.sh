#!/usr/bin/env bash
# openroot_deepdive_triad_v1.sh — combined deep dive + monetization triad
# CANARY:OPENROOT-DEEPDIVE-TRIAD-V1
# Host-gated: run on OptiPlex only (canonical git repo lives there).
# Idempotent, read-only except reports/docs dirs. NO git commits — human gate.
set -eu
export GIT_PAGER=cat TERM=dumb
R=/home/jesse/openroot
OUT="$R/docs/monetization"
DD_DIR="$R/reports/deepdive"
TS=$(date -u +%Y%m%dT%H%M%SZ)
HOST=$(hostname)

echo "[gate] stage 0 — host check"
case "$HOST" in
  optiplex*) echo "[banked] host=$HOST canonical repo" ;;
  *) echo "[held] host=$HOST is not optiplex3060 — this script reads the canonical git repo."; exit 1 ;;
esac
cd "$R"
mkdir -p "$OUT" "$DD_DIR"
REPORT="$DD_DIR/deepdive-$TS.md"

echo "[gate] stage 1 — repo fingerprint"
{
echo "# openroot deep dive — $TS"
echo
echo "## 1. Fingerprint"
echo '- HEAD: ' $(git rev-parse HEAD)
echo '- dirty entries: ' $(git status --porcelain | wc -l)
echo '- tracked files: ' $(git ls-files | wc -l)
echo '- bin/ tracked: ' $(git ls-files bin/ | wc -l)
echo '- repo size (.git): ' "$(du -sh "$R/.git" | cut -f1)"
} > "$REPORT"

echo "[gate] stage 2 — language census"
{
echo
echo "## 2. Extension census"
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
} >> "$REPORT"

echo "[gate] stage 3 — churn hotspots"
{
echo
echo "## 3. Churn hotspots (top 20)"
git log --pretty=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -20
} >> "$REPORT"

echo "[gate] stage 4 — monotonicity checks"
{
echo
echo "## 4. Duct checks"
echo '- tracked files > 5MiB: ' $(git ls-files -z | xargs -0 du -b 2>/dev/null | awk '$1>5000000' | wc -l)
echo '- orphaned ~/deepdive_latest.md exists: ' $(test -f /home/jesse/deepdive_latest.md && echo YES-integrate || echo no)
echo '- quarantine branch on origin: ' $(git ls-remote --heads origin 2>/dev/null | grep -c quarantine || true)
} >> "$REPORT"

echo "[gate] stage 5 — commit cadence (90d)"
{
echo
echo "## 5. Cadence"
echo '- commits last 90d: ' $(git log --since="90 days ago" --oneline | wc -l)
} >> "$REPORT"

echo "[gate] stage 6 — monetizable asset census"
{
echo
echo "## 8. Sellable asset candidates"
echo '### Design packets / BOMs / specs'
git ls-files | grep -Ei '(bom|spec|packet|design|thermal)' | head -40 || true
echo
echo '### Evidence (receipts, benchmarks, verification)'
git ls-files | grep -Ei '(receipt|benchmark|evidence|verify|popw)' | head -40 || true
echo
echo '### Tutorial-grade docs'
git ls-files | grep -Ei '(wiki|guide|tutorial|README)' | head -40 || true
} >> "$REPORT"

echo "[gate] stage 7 — skill inventory"
{
echo
echo "## 9. Skill inventory"
echo '- local-LLM/agent scripts: ' $(git ls-files | grep -cEi '(ollama|agent|llm|embed|relay)' || true)
echo '- ledger/chain/popw: ' $(git ls-files | grep -cEi '(ledger|sha|mint|chain|popw|prove)' || true)
echo '- thermal/energy: ' $(git ls-files | grep -cEi '(thermal|stirling|solar|carnot|aero|cement)' || true)
echo '- orchestration/gates: ' $(git ls-files | grep -cEi '(gate|engine|heartbeat|swarm|onepass|daemon)' || true)
} >> "$REPORT"

echo "[gate] stage 8 — TRIAD DRAFTS (standalone, no prior-report dependency)"
cat > "$OUT/gumroad_listing_draft-$TS.md" <<'INNER_EOF_G'
# Gumroad Listing Draft — OpenCell Thermal Design Packet (v1)
## Title
OpenCell Aerocement + Passive Solar Thermal Design Packet — Buildable Plans with Evidence Chain
## Price
$24 launch ($15 early-bird first 20), raise to $29 after 50 sales.
## Pitch
Drill-and-bucket opencell concrete wall system + passive solar thermal cascade, with
BOMs, tolerances, verification checklist, and SHA-256 evidence receipts.
## Contents
- OpenCell AR-GFRC wall system: mix ratios, ~0.3mm bubble targets, formwork, load notes
- Blackbody solar absorber: coating spec, mounting, absorbance measured as fraction only
- Thermal labyrinth: inlet/outlet sizing, documented 35F drop from 120F inlet
- Stirling integration: dT > 80C threshold, coupling diagrams
- BOM priced retail (US) per subsystem + verification checklist + evidence appendix
## License honesty
Base docs stay CC-BY-SA-4.0 free online; buyers pay for curation, assembly, print
formatting, and the evidence appendix. State plainly — trust signal, not weakness.
Future packets: author CC BY-NC 4.0 for resale protection.
## Needed from Jesse
[ ] absorber build photo [ ] pour photo [ ] labyrinth temp plot [ ] cover render
[ ] BOM priced [ ] receipts resolve to repo hashes [ ] PDF review [ ] Gumroad account
INNER_EOF_G

cat > "$OUT/sare_grant_framing-$TS.md" <<'INNER_EOF_S'
# SARE Grant Framing — OpenRoot Passive Thermal Systems (v1)
## Target
SARE Farmer/Rancher (~$15k cap) or Research & Education (~$30k+). Screen also:
REAP, NCAT/ATTRA, state on-farm energy programs.
## Core paragraph
Small farms face simultaneous heating, cooling, and energy-cost pressure with no
on-site engineering support. OpenRoot develops open-source appropriate technology —
blackbody solar absorber, opencell aerocement construction, thermal-labyrinth passive
cooling — documented with verifiable build evidence and published under open licenses.
We propose deploying and instrumenting these on a working farm boundary, publishing
measured performance, and producing farmer-buildable design packets with BOMs.
## Hard constraints
- NEVER >100% thermo language; COP-boundary / Carnot framing only
- Every claim falsifiable, tied to a planned measurement
- Budget: instrumentation, replication materials, farmer stipend — not overhead
- Open licensing framed as maximizing public return on federal funds
## Measurement plan (budget hooks)
1. Absorber: irradiance vs fluid heat out (joules), >= 4 seasons
2. Panels: compressive sampling (3rd-party lab if affordable), R-value/thermal mass
3. Labyrinth: inlet/outlet/humidity/flow; reproduce 35F drop across deployments
4. Stirling: output vs dT curve, validate dT > 80C threshold
5. PoPW ledger: SHA-256 chained sensor streams (one sentence, do not oversell)
## TODOs
[ ] confirm 2026-2027 regional SARE cycle deadline [ ] partner farm letter
[ ] lab quote [ ] budget map [ ] reuse black-locust-carbon-negative-energy-v1.md
INNER_EOF_S

cat > "$OUT/hn_post_draft-$TS.md" <<'INNER_EOF_H'
# Hacker News Post Draft — PoPW Thermo-Ledger (Show HN)
## Title options
A) Show HN: I run my build logs on a proof-of-physical-work ledger — joules in, SHA-256 out
B) I measure every watt-hour of my homebrew compute workflow and put it on a hash chain
## Body (~300 words, restrained first-person)
I maintain a small off-grid appropriate-tech lab, and I kept hitting the same trust
problem: open hardware projects publish claims, but the evidence behind them is
unverifiable — a temperature chart with no chain of custody.
So I started logging every physically measured quantity through a proof-of-physical-work
layer: sensor readings and energy measurements (RAPL microjoule counters on compute,
thermal instrumentation on hardware) hashed with SHA-256, chained, timestamped into
SQLite. Reproducibility failures show up as broken hashes, not vibes.
Deployments: blackbody solar absorber runs (joules captured, never >100% of input),
thermal labyrinth passive cooling (35F drop from 120F inlet), local-LLM compute metered
in energy not tokens. Everything GPL/CC open.
Design tension: evidence chains add friction; I automated the ingestion/grading so the
integrity overhead stays near zero, with human sign-off on commits.
Happy to go deep on: chaining scheme, joule-vs-token accounting, failure modes when
counters lie (RAPL estimates vs measurements).
## Pre-submit requirements
- Needs permalinked PoPW explainer page FIRST (blog post or README section)
- DO NOT submit pointing at bare repo root
- Tue-Thu morning ET; submitter first comment expands chaining schema in one code block
- HN will stress-test claims — hash chain demos ARE the asymmetry
INNER_EOF_H

echo "[gate] stage 9 — seal"
SHA=$(sha256sum "$REPORT" | awk '{print $1}')
{
echo "---"
echo "Generated: $TS | Host: $HOST | Canopy report: $REPORT"
echo "Deep dive sha256: $SHA"
echo "Drafts:"
for f in "$OUT"/*-$TS.md; do echo "  $(basename "$f")  sha256=$(sha256sum "$f" | awk '{print $1}')"; done
echo "CANARY:OPENROOT-DEEPDIVE-TRIAD-V1 COMPLETE — NO COMMITS MADE"
} | tee "$OUT/TRIAD_RECEIPT-$TS.txt"
echo "[held] review, then human-gated: git add reports/deepdive docs/monetization && git commit"
echo "[exit=0]"
