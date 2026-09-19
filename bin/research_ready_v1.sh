#!/usr/bin/env bash
set -eu
export GIT_PAGER=cat PAGER=cat
export OLLAMA_HOST=http://localhost:11434
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd) || exit 1
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && pwd) || exit 1
cd "$REPO_ROOT" || exit 1
echo "[canary-head] research_ready_v1 paste intact"

echo "[stage-1] research.db — claims ledger (assert nothing you have not measured)"
sqlite3 data/research.db <<'SQL'
CREATE TABLE IF NOT EXISTS claims (
  id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now')),
  subsystem TEXT, claim TEXT,
  status TEXT DEFAULT 'asserted',  -- asserted|measured|partially_measured|falsified
  measurement_protocol TEXT, instrument TEXT,
  uncertainty_pct REAL, target_metric TEXT,
  lit_anchor TEXT,                  -- nearest published result to compare against
  UNIQUE (subsystem, claim));
CREATE TABLE IF NOT EXISTS manuscripts (
  id INTEGER PRIMARY KEY, subsystem TEXT UNIQUE, path TEXT, stage TEXT DEFAULT 'skeleton');
CREATE TABLE IF NOT EXISTS experiments (
  id INTEGER PRIMARY KEY, ts TEXT DEFAULT (datetime('now')),
  subsystem TEXT, protocol TEXT, hypothesis TEXT,
  independent_vars TEXT, dependent_vars TEXT,
  instrument TEXT, calibration_std TEXT, notes TEXT, outcome TEXT DEFAULT 'planned');
SQL
for COLUMN_DEF in "instrument TEXT" "lit_anchor TEXT" "target_metric TEXT"; do
  COLUMN=${COLUMN_DEF%% *}
  if ! sqlite3 data/research.db "PRAGMA table_info(claims);" | cut -d'|' -f2 | grep -qxF "$COLUMN"; then
    sqlite3 data/research.db "ALTER TABLE claims ADD COLUMN $COLUMN_DEF;"
  fi
done
sqlite3 data/research.db <<'SQL'
DELETE FROM claims
WHERE id NOT IN (SELECT MIN(id) FROM claims GROUP BY subsystem, claim);
CREATE UNIQUE INDEX IF NOT EXISTS idx_claims_identity ON claims(subsystem, claim);
SQL
echo "   [banked] schema live"

echo "[stage-2] seed the claim register — honest status for every subsystem"
C=$(sqlite3 data/research.db 'SELECT COUNT(*) FROM claims;')
if [ "$C" -eq 0 ]; then
sqlite3 data/research.db <<'SQL'
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('opencell_mix','activated-carbon aerocement matrix absorbs >=95% of incident solar spectrum','asserted',
 'DIY integrating-sphere reflectance rig or spectrophotometer partner',
 'MWCNT/carbon solar absorbers report 98-99.9% (Vinetsky 2020, MDPI Coatings)','spectral absorbance 250-2500nm ±2%');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('cascade','thermal cascade delivers utilization ratio ~1.35 INCLUDING ambient heat transfer (COP-framing, never >solar)','asserted',
 'thermocouple grid + flow meter + pyranometer, 7-day continuous log',
 'solar-driven heat pump literature; COP framing standard','closed heat balance closes within 5%');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('thixo_gel','thixotropic surfactant-gel stator mixing produces bubble size distribution approaching monodisperse','asserted',
 'optical microscope + image analysis of cut sections (bubble diameter histogram)',
 'Weaire-Phelan / Kelvin foam packing literature','mean bubble dia 0.3-0.5mm, CV<20%');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('argf','alkali-resistant glass fiber reinforcement viable at >=20% ZrO2 for cement pH exposure','asserted',
 'accelerated aging: fiber tensile retention after 28d in 1N NaOH',
 'CemFil-ARG commercial fibers specify ~16-17% ZrO2','tensile strength retention >85% after alkaline soak');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('double_skin','double stress-skin ferrocement catenary shell carries gravity load in near-pure compression','asserted',
 'strain gauges on meridian ribs + load test to 1.5x design load',
 'funicular shell theory; Heyman stone shells','meridian bending moment <5% of axial thrust');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('cardboard_membrane','waterproofed cardboard membrane viable as sacrificial forming/weather skin >=2yr','asserted',
 'outdoor exposure coupon panels + water-head test',
 'bitumen/wax-treated paper packaging literature','zero moisture ingress at 100mm water head 24h');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('dish_mesh','wood-pallet parabolic with chicken-wire surface receives UHF signals effectively','asserted',
 'SNR comparison vs commercial dish at same frequency + sun-noise transit test',
 'mesh reflector rule: aperture < lambda/10','gain within 2dB of solid dish at <=600MHz');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('cloud9','buoyant tethered sphere at scale achieves favorable lift-to-surface-mass ratio (square-cube law)','asserted',
 'scaled 2m prototype: lift force vs envelope mass in sun-heated vs ambient condition',
 'Fuller Cloud Nine concept; Montgolfier solaire MIR flights','net positive lift per m2 envelope at deltaT>=15C');
INSERT INTO claims (subsystem,claim,status,instrument,lit_anchor,target_metric) VALUES
('labyrinth','buried wet-concrete labyrinth drops incoming air temp ~35F from 120F inlet','asserted',
 'inlet/outlet thermocouple pair + anemometer, whole-summer log',
 'earth-tube / PCM passive cooling literature','sustained deltaT >15F across hottest afternoon hours');
SQL
echo "   [banked] $(sqlite3 data/research.db 'SELECT COUNT(*) FROM claims;') claims registered — all honestly marked 'asserted'"
else
  echo "   [skip] claims already registered ($C)"
fi

echo "[stage-3] generate peer-review manuscript skeletons (IEEE/Elsevier structure)"
mkdir -p docs/research
gen_ms () {
  TITLE="$1"; SUB="$2"; SLUG="$3"; FILE="docs/research/${SLUG}.md"
  [ -f "$FILE" ] && { echo "   [skip] $FILE exists"; return; }
  cat > "$FILE" <<MS
# ${TITLE}: Measurement Protocol and Results

**Status:** manuscript skeleton — every claim herein awaits its experiment
**Claims register:** data/research.db, subsystem='${SUB}'

## Abstract (draft — must pass bin/hype_gate.sh before submission)
[Purpose in one sentence.] [Method in one sentence, naming instruments.] [Headline result with uncertainty, or 'measurements pending'.] [Implication for low-cost vernacular infrastructure in one sentence.]

## 1. Introduction
- Problem: X% of construction cost is [material/energy/formwork]; current solutions require [capital/skilled labor]
- Lineage: cite Fuller (Cloud Nine / synergetics), Heyman (shell theory), ARG fiber patent literature, carbon absorber spectroscopy
- Gap: no published closed-loop measurement of [specific thing] for [this material class]
- Contribution: falsifiable measurement protocol + dataset (sha256-published) for [subsystem]

## 2. Theory and Design Basis
- Governing equations (state them — e.g., E=30V^2 geodesic relation; funicular equilibrium; buoyancy F=rho_air*g*V*deltaT/T)
- Expected failure modes and the bounds within which this design remains physical
- Thermodynamic honesty clause: COP or utilization-ratio framing where applicable; NEVER implies >100% of incident energy

## 3. Materials and Methods
- Mix design (full recipe, water:cement, admixture dosages, temperature at pour)
- Instrument list with model numbers + calibration standard + calibration date
- Uncertainty budget table (instrument precision / repeatability / systematic — per term)
- Experimental matrix: independent vars, replicates, controls, sample sizes

## 4. Results
[Data tables + figures. Raw CSV under data/experiments/<slug>/, sha256 in appendix.]

## 5. Discussion
- Comparison to lit_anchor values from claims register
- Where results diverge from expectation and what that implies

## 6. Limitations and Falsification Conditions
- This work is falsified if: [explicit conditions]

## References
[Bibliography — Zotero/doikeys, GPL-3.0 code, CC-BY-SA-4.0 doc]
MS
  python3 bin/sqlite_params.py data/research.db \
    "INSERT OR REPLACE INTO manuscripts (subsystem,path,stage) VALUES (?, ?, 'skeleton')" \
    "$SUB" "$FILE"
  echo "   [banked] $FILE"
}
gen_ms "OpenCell Aerocement Solar Absorber" "opencell_mix" "opencell-absorber"
gen_ms "Thermal Cascade Heat Balance" "cascade" "cascade-heatbalance"
gen_ms "Thixotropic Gel Stator Foam Quality" "thixo_gel" "thixo-foam"
gen_ms "ARG Fiber Alkali Durability" "argf" "argf-durability"
gen_ms "Double Stress-Skin Catenary Ferrocement Shell" "double_skin" "double-skin-catenary"
gen_ms "Waterproofed Cardboard Membrane" "cardboard_membrane" "cardboard-membrane"
gen_ms "Pallet-Frame Mesh Reflector" "dish_mesh" "dish-mesh-reflector"
gen_ms "Tethered Buoyant Relay (Cloud Nine Scaled)" "cloud9" "cloud9-relay"
gen_ms "Thermal Labyrinth Passive Cooling" "labyrinth" "labyrinth-cooling"

echo "[stage-4] hype-detector gate — the phrases that get papers desk-rejected"
cat > bin/hype_gate.sh <<'HGATE'
#!/usr/bin/env bash
set -eu
FILE="${1:?usage: hype_gate.sh <manuscript.md>}"
CODE=0
while IFS= read -r LINE; do
  [ -z "$LINE" ] && continue
  MATCH=$(grep -inE "$LINE" "$FILE" || true)
  if [ -n "$MATCH" ]; then echo "   [FAIL] $LINE"; echo "$MATCH"; CODE=1; fi
done <<'BANNED'
free energy|over.?unity|perpetual
more than 100%|exceeds 100%|breakthrough|revolutionary
unprecedented|miracle|game.?changing.{0,20}efficien
magna.?flux|zero.?point
BANNED
if [ "$CODE" -eq 0 ]; then echo "[PASS] $FILE contains no desk-reject phrases"; else echo "[HELD] revise flagged lines in $FILE"; exit 1; fi
HGATE
chmod +x bin/hype_gate.sh
bash bin/hype_gate.sh docs/research/opencell-absorber.md && echo "   [ok] gate self-test passes on skeleton" || true

echo "[stage-5] 3B abstract rubric — grades any draft abstract in 30 seconds"
cat > bin/abstract_grade.sh <<'AGRADE'
#!/usr/bin/env bash
set -eu
export OLLAMA_HOST=http://localhost:11434
FILE="${1:?usage: abstract_grade.sh <manuscript.md>}"
ABSTRACT=$(sed -n '/^## Abstract/,/^## 1\./p' "$FILE" | tail -n +2 | head -20)
printf '%s\n' "$ABSTRACT" | timeout 90 ollama run qwen2.5:3b \
"Grade this research abstract against rubric. Output exactly 2 lines: 'VERDICT: PASS|FAIL' and 'FIRST_FIX: <one concrete improvement>'. Rubric: names a measurable quantity, names an instrument, states an uncertainty or says pending, avoids superlatives, is falsifiable." 2>/dev/null \
|| echo "VERDICT: UNAVAILABLE (3B offline)"
AGRADE
chmod +x bin/abstract_grade.sh
echo "   [banked] bin/hype_gate.sh + bin/abstract_grade.sh installed"

echo "[stage-6] stage for human commit"
git add data/research.db bin/research_ready_v1.sh bin/hype_gate.sh bin/abstract_grade.sh docs/research/ 2>/dev/null || true
git diff --cached --stat | tail -3
echo "   [gate] review then commit: git commit -m 'feat(research): claims register + manuscript skeletons + hype-gate (peer-review prep)'"

echo "[stage-7] seed"
SEED=context_bridge/session-$(date +%Y%m%d_%H%M%S)-research.md
{ echo "# session: research_ready_v1"
  echo "- claims registered: $(sqlite3 data/research.db 'SELECT COUNT(*) FROM claims;') (all honestly 'asserted')"
  echo "- manuscripts scaffolded: $(sqlite3 data/research.db 'SELECT COUNT(*) FROM manuscripts;')"
  echo "- gates installed: hype_gate.sh, abstract_grade.sh"
  echo "- HEAD: $(git rev-parse --short master)"; } > "$SEED"
sha256sum "$SEED" | tee -a seed_master.log
git add "$SEED"
echo "[done] [exit=0]"
