# SARE Grant Framing — OpenRoot Passive Thermal Cascade
Status: DRAFT v0.1 (staged, unverified, human-gated) | License: CC-BY-SA-4.0

## Applicant identity
OpenRoot LLC — open-source appropriate-technology commons.
Lead: Jesse McMillen Ray (github.com/jesseray718). All claims below trace to
public, version-controlled evidence (PoPW: proof of physical work).

## The problem (farmer-facing, not technology-facing)
Small farms pay twice for thermal energy: once for propane/electric heating
and once for refrigerated-cold losses. Rural energy costs compress farm
margins hardest — the energy floor IS the economic floor for smallholders.

## The proposed system (honest boundary)
A passive, glazed aerocement solar absorber array with underground thermal
labyrinth storage, sized by audited simulation (thermal_balance v6.3):
- Selective-surface emission eps=0.10, single-glazing transmission tau=0.88
- Thermosiphon airflow, stack-driven, no pumps
- Temperature grade: see Frontier Scan (pending bank) — the system does NOT
  claim process steam; delivered heat is bounded by verified simulation.
- 5 equivalent sun-hours/day capacity basis (CF ~0.21), never 12h peak-only.

## What SARE funds that we cannot
- Materials + instrumentation for ONE replicated pilot build on a host farm
- Independent measurement: inlet/outlet temps, mass-flow, seasonal CF
- Third-party verification of the COP-boundary absorbance claims (95%+
  framed as collector-absorptance within a control-volume, never >100%)

## Deliverables (all public, GPL/CC)
1. BOM at three cost tiers (scrap / retail / new-materials)
2. Construction drawings + aerocement mix specification
3. Instrumented performance dataset (raw CSVs in-repo, sha-chained)
4. Replication guide written for builders with no engineering background

## Why us (evidence-first)
- Full computation pipeline is open, audited, and reproducible:
  v6.3 sweep REFUSED to claim unphysical performance (0 configs meet
  264C) — our negative results are published, which is the proof the
  positive results are trustworthy.
- Prior verified engineering: thermal labyrinth 35F drop from 120F inlet;
  geodesic dome BOM (E=30*V^2); black-locust RMH carbon-negative framing.

## Outreach plan (mandatory SARE element)
Field-day demonstration at host farm; open build weekends; collaboration
with [extension office TBD]; all documentation in plain language with
video stepthroughs.

## Budget sketch (placeholder for gate discussion)
- Aerocement materials, glazing, selective coating: $X
- Instrumentation (thermocouple arrays, flow meters, datalogger): $Y
- Stipend for measurement season: $Z
- Total request target: under $15k (SARE Farmer/Rancher tier)

## Risks stated plainly
- Absorber durability of AR-GFRC under freeze-thaw cycles (test plan TBD)
- CF varies by region; replication in 3 climates before broad claims
- Pressure systems EXCLUDED by design (no steam loop, no vessel)

## Open questions for the human gate
1. Which SARE program: Farmer/Rancher ($15k) vs Partnership ($50k+ with university)?
2. Host farm identified? Extension partner contact?
3. Pilot climate zone — drives the CF honesty envelope.
