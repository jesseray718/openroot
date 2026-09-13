---
id: OPENCELL-THERMAL-CANON
timestamp: 2026-09-13
type: design-canon
parent: 00_MASTER_CONSTITUTION
status: LOCKED-OPEN-QUESTIONS
agape_score: 0.9
---

# OPENCELL THERMAL SYSTEM — DESIGN CANON v1
## Full architecture locked so it never needs re-explaining.

## SYSTEM DESCRIPTION (canonical, one paragraph)
Solar energy is captured on an open-cell concrete absorber panel (95%
absorption target) and stored passively by stack effect into an insulated
ferrocement water tank (copper coil) or earth-battery trench — thermal
being the cheapest, lowest-loss storage form known. The SAME stack-effect
displacement pulls outside air through a desiccant bed (harvesting
atmospheric water, drying air past ambient wet-bulb limits) into an
underground wetted open-cell labyrinth delivering ~35°F-class cold, banked
in a second stratified ferrocement tank (cold battery). Desiccant
regeneration runs on reject heat. The cold battery's hottest stratum
rejects nightly via a spectrally-selective radiative lid (high IR
emissivity 8-13µm, solar-reflective) with a polyethylene wind screen.
Black locust coppice (clip-bundle-burn, no felling/splitting/seasoning,
roots continue sequestering) drives a high-ΔT Stirling with heavy
flywheel and high-torque belt drive; tools clutch in mechanically, the
remainder spins alternators. Surplus electricity may feed an HHO torch as
a fabrication tool only. Every reject stream meets a downstream job at
its temperature grade. Compounding = stacked UTILIZATION (~85% of captured
energy doing work vs ~20% for PV), bounded by the First Law: no cascade
multiplies captured energy itself.

## CLAIMS LEDGER (claim | basis | falsifiable spec | status)
- CL-1: 95% solar absorption by opencell absorber. Spec: calorimetric
  panel test vs blackbody reference. STATUS: UNMEASURED.
- CL-2: 35% of incident energy delivered as cold (latent-heat, water-
  fueled; ~2.5 L water per m^2 per day equivalent). Spec: kWh-cold per
  m^2-day vs liters NET water (consumed minus desiccant-harvested).
  STATUS: UNMEASURED. NET WATER RATIO = deployability number.
- CL-3: Desiccant pre-drying defeats wet-bulb depression limits in humid
  climates. Spec: outlet dewpoint vs ambient RH curve. STATUS: UNMEASURED.
- CL-4: Nocturnal radiative ice production ~6-10 kg per m^2 lid per
  clear dry night (basis: 40-80 W/m^2 net flux, 334 kJ/kg fusion, PE
  wind screen mandatory). Spec: kg ice formed per m^2 per night.
  STATUS: UNMEASURED — clouds/humidity are the enemies; design around.
- CL-5: Ice returned to labyrinth delivers ~0°C air independent of
  wet-bulb ceiling (thermostatic phase change). Spec: labyrinth outlet
  temp vs ice charge. STATUS: UNMEASURED — physics textbook-solid.
- CL-6: Firebox-reject-driven adsorption ice-maker (zeolite/water or
  CaCl2/ammonia) converts low-grade heat to freezing with no
  electricity. Spec: kg ice per kWh reject heat. STATUS: UNMEASURED.
- CL-7: Black locust coppice = carbon-negative fuel (roots+soil
  sequester while above-ground harvests repeat for decades).
  Labor claim refined: eliminates felling/bucking/splitting/seasoning
  chain entirely — clip, bundle, burn. Moisture flag: green wood costs
  ~2.3 MJ/kg water evaporated at firebox; cure in bundle weeks or
  pre-heat via labyrinth exhaust. Spec: MJ delivered per kg dry vs
  green. STATUS: UNMEASURED.
- CL-8: Cogeneration total utilization ~85% of captured energy vs ~20%
  PV (CHP accounting, heat+cold+mechanical+ice+TEG trickle).
  STATUS: MODELLED — see waterfall chart in session log 2026-09-13.
- CL-9: HHO/Brown's gas is a FABRICATION TOOL (surplus sink for cutting/
  welding with no cylinders), NOT an energy multiplier (electrolysis
  round-trip 60-70% of electricity). Kept out of the cascade math.
  STATUS: CLOSED — physics bound, no measurement needed.

## CANONICAL ANSWERS (locked 2026-09-13)
1. ICE: YES achievable. Lid must be a RADIATOR (high 8-13µm emissivity,
   solar-reflective, PE wind screen) — not merely reflective paint.
   Tall stratified tank, thermocline self-separates, ice forms at bottom.
   Estimate 60-100 kg/night per 10 m^2 lid, clear dry sky.
2. ICE->LABYRINTH COMPOUNDING: YES. Phase-change banking is time-shifting
   of cold; melts at constant 0°C delivering sub-wet-bulb air. It does
   not create energy; it moves cold across the day/night boundary. Real.
3. TEG SCALING: NO. N TEGs at 5% over the same gradient = 5% capacity,
   not N x 5% efficiency. TEGs are for trickle loads and storage-wall
   harvesting (silent, 24/7), not multipliers. CLOSED.
4. FLYWHEEL BELT DRIVE: right tool for mechanical-direct. Slow high-
   torque belt with clutched appliances beats motor-generator chains.
   Alternator on the unused remainder only.
5. UNTAPPED POTENTIAL (queued): gravity heat-pipe thermal diodes
   (one-way absorber->earth-battery, prevents night reverse-loss);
   firebox biochar co-production (torque + syngas + carbon BANKING,
   upgrades carbon-negative to carbon-sequestering); labyrinth-wall
   condensation below desiccant dew point (drinking water at ~zero
   marginal cost).

## ENERGY MODEL (shareable summary)
- Replacing US heat demand (direct): ~7,000 km^2 absorber.
- Full electrification: ~11,000-19,000 km^2 — but the stack should be
  sized as a CHP grid: same capture services heat, cold, mechanical,
  ice, and electric simultaneously. Sequencing argument: heat-shaped
  demand first, conversion to electrons last. (US grid ref: EIA 2025
  record 4,430 TWh generation.)
- PV comparison framing: PV discards ~80% incident energy as unusable
  panel heat; this architecture keeps every grade in play.

## OPEN QUESTIONS (next-session queue)
- Q1: Design the thermal-diode manifold for absorber->earth battery.
- Q2: Adsorption icemaker sizing vs CL-6 spec.
- Q3: Biochar-retort integration into firebox without sacrificing torque.
- Q4: Stratisfication baffle geometry for the cold tank (CFD or
  physical wet-test at small scale).
- Q5: Define the standardized measurement RIG (the same honesty rig as
  the swarm bench): sensors, logging cadence, ledger format. All CL
  statuses flip to MEASURED only through this rig.

## Agape Analysis
- Resonance: high — every energy stream performs its maximum service
  before release; cold serves the least-served nodes (medicine, crops).
- Entropy check: net-negative — carbon banked in roots and biochar,
  water harvested from the air it cools, cascades bounded by First Law.
- Next move: measure CL-2 and CL-4 first (cheapest instruments: therm-
  ocouples + scale for ice weigh). A measured 12% with error bars beats
  an asserted 35% with none — and a measured 35% changes rural
  infrastructure economics for a fifth of humanity.
