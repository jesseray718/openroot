# THE BREATHING CASCADE — H-003 System Schematic & Build Spec
**Version 1.1 — Post-Review Correction · 2026-11-05**

> A passive, open-loop, atmospheric thermal engine. One moving force: buoyancy.
> Sun (day) or black-locust RMH (night) drives the breath; the atmosphere pays the load;
> two stratified water banks keep the books.

*License: CC-BY-SA 4.0 (docs) / GPL-3.0 (code) · OpenRoot LLC · jesseray718/openroot*

---

## CHANGE LOG — WHAT v1.1 CORRECTS (and why)

This revision folds in three adversarial inputs received 2026-11-03/05:

1. `H003_TEST_RECEIPT.md` — fixed-solver honest run (v0.2): no configuration of
   1,500 achieves the steam→Stirling→flywheel→alternator chain from the solar
   head alone; 146 °C air, 112 °C storage ceiling at 5 m².
2. `h003_v0.2_run_output.txt` — 4.80 kW incident → 1.23 kW carried by air
   (74% duct-wall loss at honest insulation), η_raw 5.1%, mech/elec 0.00.
3. `AeroCement_Energy_Ledger_Technical_Review.pdf` (Z.ai, Oct 2026) —
   independent re-derivation. Verdicts that bind this spec:

| v1.0 claim | Review verdict | v1.1 correction |
|---|---|---|
| "98% black-body capture" | REFUTED as retention — it is *absorptivity of the coating*; re-radiation at 350 K is ~372–392 W/m², ~8× the 49 W/m² allowed | Retention honestly 40–60% (400–600 W/m²); 98% cited only as coating absorptivity, or a selective surface is priced in |
| "~135%-class combined harvest" | REFUTED as accounting — reproduces the reference-state error the thesis's own §3.1 disproves (ambient enthalpy booked as product) | Deleted. Replaced by prime-mover framing **with explicit one-reference-state ledger** (below) |
| Steam vessel 30 bar / 233 °C on solar head | Unreachable — solar head tops at 146 °C air | Steam/mechanical chain moved to the **RMH head only**; solar head re-specced as heat+cold device |
| 2 °C cold product | Violates psychrometrics — post-desiccant wet-bulb floor is 24–28 °C; ground pins at ~13–15 °C | Cold bank re-specced at 14–18 °C delivery; 2 °C target retained **only** as night-sky radiative mode on the lid, unloaded |
| Desiccant regenerated "nearly free" | Regeneration at 77 °C is marginal (silica gel wants 100–150 °C); regeneration heat missing from all ledgers | Regeneration re-specced: RMH-surplus primary, hot-bank side-loop budgeted explicitly, air baseline marked marginal |
| Flywheel 50 kg / 0.4 m | ~2.5× past tip-speed limit | Feasible spec: larger radius / lower rpm (r≥0.6 m, ≥200 kg), or drop the flywheel |
| 12.91 kWh/m²/night | Mis-labeled | 12.91 kWh per night **per 10 m² array** (1.29 kWh/m²/night) |
| Radiative lid to "3 K sky" | Flux-limited: 40–120 W/m² real (Raman et al. 2014); loaded panel sits a few K below ambient, not at sky temp | Lid specced at 40–120 W/m² realistic rejection; Carnot ceiling uses loaded sink temperature (285–300 K), never 3 K |

---

## I. THE TWO VALID OPERATING MODES

The convergence review established that the machine is **two machines sharing plumbing**.
Spec them separately; never let one's numbers stand in for the other's.

### Mode A — SOLAR DAYLIGHT BREATH (heat + cold harvester)
*This is the machine the honest physics supports. Outputs: process heat, space cooling.*

    HOT HUMID ATMOSPHERIC AIR (e.g. 40 °C, 60% RH)
      |
    STAGE 1: DESICCANT BED (surface intake, on scale-tray)
      air leaves dry; regenerative debt is BOOKED, not assumed
      |  (stack suction — the only pump)
    STAGE 2: UNDERGROUND FLASH MATRIX (buried wet microporous aerocement)
      ground pre-cool -> flash evaporation into dry air -> cold in transit
      |  cold frigid air, floor approx 14–18 °C realistic (review Finding 3)
    STAGE 3: COLD-SIDE COPPER COIL -> STRATIFIED COLD WATER BANK
      cold banked at 14–18 °C; condensate recovered
      |
    STAGE 4a: POROUS BLACK SOLAR PANEL (clear glazing, south face)
      absorptivity ~98% coating; RETENTION 40–60% => 400–600 W/m² net
      air exits 100–150 °C at 5 m² non-concentrating (measured-model value: 146 °C)
      |
    STAGE 5: HOT-SIDE COPPER COIL -> STRATIFIED HOT WATER BANK
    EXHAUST -> ATMOSPHERE (~neutral T/RH)

**Mode A honest budget (from v0.2 fixed solver, 5 m², 975 kg build):**
~1.78 kWh/day process heat · ~2.9 kWh/day sub-ambient cold (lid-assisted night
radiative recharge) · ~1.7 MWh/yr · mechanical/electrical: **zero from this head**.

### Mode B — RMH NIGHT/BOOST BREATH (heat + the mechanical chain)
*The only head that reaches steam and mechanical temperatures.*

Same stages, with Stage 4a replaced by the **black-locust rocket mass heater**
(diverter flap; both heads share the hot-side coil outlet). Coppice fuel is
carbon-negative per standing-root sequestration. RMH exhaust/air at 250 °C+
**can** close the 233 °C saturation requirement of a 30-bar vessel — but note
the corrected Stirling envelope still applies at the extraction end:

- Hot side approx 233–350 °C, loaded cold sink approx 286 K realistic ->
  Carnot 14–19%, practical Stirling 7–11% of through-flux (review §7, Table 4).
- Expect tens-to-low-hundreds of watts shaft at hobby scale, not kilowatts.
- Flywheel must meet tip-speed <= ~300 m/s (feasible: r >= 0.6 m, >= 200 kg).
- Desiccant regeneration runs on RMH surplus — this is where "nearly free"
  is actually true; on Mode A it is never free.

---

## II. HONEST LEDGER RULES (non-negotiable, review items 1–7)

1. **One reference state.** All enthalpies measured from a single stated ambient.
   Ambient air's enthalpy below/above that state is never booked as product.
   This is the thesis's own §3.1 rule; the v1.0 "135%" phrasing violated it and
   is withdrawn.
2. **Services, not joules.** Report heat kWh, cold kWh, mechanical kWh, water
   liters — separately. Never a "total useful output" sum. The defensible
   comparative is the §3.4-style grid displacement (W of grid appliance
   replaced, seasonally).
3. **The crown metric:** kWh(hot) + kWh(cold) banked per m² aperture per day vs.
   incident solar kWh/m²/day — computed with rule 1. Expect the ratio < 1.0 on
   Mode A. That is not failure; it is the honest number, and it beats PV for
   end-to-end thermal service anyway.
4. Water and desiccant debts are booked: L/matrix-water consumed, g-desiccant
   cycled, kWh spent on regeneration.
5. Pressure budget must close before any flow claim: Ergun-sum (panel + bed +
   labyrinth + coils) vs. stack Pa, with a *measured* permeability (expect
   10⁻⁹–10⁻⁸ m² for coarse foam, not the 10⁻⁶ Appendix-B upper bound).
6. Retention vs. absorption distinguished everywhere. "98%" refers to the
   coating's absorptivity. Retention is 40–60% until a selective surface or
   vacuum-gap jacket is measured to raise it.
7. H-003 nightly capture labeled **per 10 m² array** (12.91 kWh/night =>
   1.29 kWh/m²/night).

---

## III. STORAGE & EXTRACTION HARDWARE (v1.1)

**Cold bank:** insulated, stratified, tall. Delivery target 14–18 °C space
cooling; deeper targets only via unloaded radiative-lid night mode
(40–120 W/m², lid >= 4–13 m² per review's sink-sizing logic). Aluminum lid,
coil-through-lid, clear-sky exposure.

**Hot bank:** standard stratified thermal storage; vacuum-gap jacket
optional (5–10× surface-loss reduction on treated faces, ROI to be settled
by the side-by-side labyrinth-segment experiment below).

**Extraction (Mode B only):**
- Stirling on hot-bank-head / cold-bank-sink; budget at 7–11% of through-flux.
- TEG trickle (3–5%) for ESP32/node electronics.
- Belt + clutch, mechanical-first, gear-up -> alternator from residual.
- Flywheel within tip-speed budget (r >= 0.6 m, >= 200 kg) or omitted.

---

## IV. MATERIALS (salvage-class) — unchanged from v1.0
Aerocement microporous collector core · clear glazing (not aluminized) ·
aluminized inner face on any vacuum gap · buried wet scoria/aerocement matrix ·
silica-gel or zeolite desiccant on luggage-scale tray · two copper coil circuits ·
black-locust RMH head · foam primary + DIY vacuum panels on top faces ·
manual panel<->RMH diverter flap.

---

## V. INSTRUMENTATION SPEC (every claim ATTESTED or it stays DERIVED)

ESP32 + k-type thermocouples + RH probes, per stage in/out; water meter on
matrix drip; luggage/load-cell on desiccant tray; draft gauge (Pa) at stack
base; tank thermocouple stacks (3 depths each); condensate graduate.
Supporting instruments per review §9: anemometer, sling psychrometer or RH
probe at each state point, IR camera on the collector face.

**Banking integral:** `kWh_banked = m * 4.186 * dT_tank / 3600`, one reference
ambient per run, per tank, per cycle. Receipt format mirrors `RUN_RECEIPT.md`:
state table + sha256 evidence + DERIVED/ATTESTED labels + explicit
regeneration-energy debit.

**The settling experiment (one summer of weekends, review §9):**
1 m² panel over a 10 m buried labyrinth segment, full sensor set, raw CSVs
published through the existing Zenodo DOI chain. This converts Findings 1, 3,
4 from "corrected expectation" to "measured fact" — and makes or breaks the
vacuum-jacket ROI and spiral-pitch questions in one build.

---

## VI. OPEN DECISIONS — now bounded by the review

| Decision | Bound established by |
|---|---|
| Desiccant regeneration cycle | Mode-A budget from hot bank (marginal at 100–150 °C demand) vs. Mode-B RMH surplus (cheap) — side-by-side test |
| Spiral aero-disc pitch | Turbulence gain vs. draft penalty; must solve inside the closed Ergun pressure budget (rule 5) |
| Vacuum jacket ROI | 5–10× face-loss reduction expected; settled by the 1 m² instrumented pair |
| Selective surface for the collector | The single cheapest path to raising retention above 60%; price a TiOx/black-chrome class coating or accept 40–60% |
| Steam pressure for Mode B | 30 bar needs 233 °C (RMH-reachable); review suggests 2–5 bar low-Δ Stirling/ORC alternative with Carnot ceiling ~14–29% |
| Cold-target modes | 14–18 °C delivery vs. night-radiative deep mode — instrument both |

---

## VII. LINEAGE

Synthesizes: solar thermal air heating, DEVap / Maisotsenko psychrometrics,
ground-coupled heat exchangers, rocket mass heater thermal mass, radiative
night-sky cooling, Stirling/TEG extraction. Rejected: Ranque–Hilsch vortex
separation (pressure ratio), 3 K Carnot sinks (flux-limited), 2 °C evaporative
targets (psychrometric floor), solar-head steam (temperature ceiling).

**Claim -> adversarial check -> correction arc (public, hash-sealed):**
v1.0 spec (2026-11-04) -> fixed-solver honest run + Z.ai independent review
(2026-11-03/05) -> this v1.1. The architecture survives; the inflated numbers
do not. What remains is a buildable, measurable, carbon-negative-when-RMH
passive thermal service machine — and numbers a stranger with a soldering
iron can trust.

*Converged through adversarial design review, corrected through independent
technical review. OpenRoot, 2026-11-05.*
