# Handoff 20260927_232932 — Vision: repo family + raw-material-to-OSHW pipeline

## DECISION MADE
first_release acknowledged via Option A: panel repo accepted as v0-shipped.
Purpose confirmed by operator: the ladder exists so ideas can become things
strangers can pick up and build. Release and presentation are the goal.

## REPO FAMILY PLANNED (standalone open-source hardware repos, all yet to be built)
1. aerocement (OVERHAUL of existing aerocement-calc repo): the different mixes —
   OpenCell, thixotropic, stator-mixer process, closest-packing-of-spheres model,
   alkali-resistant glass fiber reinforcement — hypotheses stated with evidence levels.
2. AeroDisk / Blackbody Thermal Solar Absorber — standalone OSHW repo.
3. Black Locust Coppicing Rocket Mass Heater — standalone repo BUT ALSO fuses with
   thermal cascade (its most powerful heating source organ). Bridge artifact required.
4. (More to be enumerated by operator later.)

## RAW-MATERIAL-TO-OSHW PIPELINE (the gap being closed)
Goal: a system that scans and observes all owned files across A15 + OptiPlex,
knows the required format for a successful open-source hardware page, and
transforms/indexes existing material toward that format — staging, not just filing.

## DEDUP DOCTRINE (decided this session)
- Tier 1: every file, cheap fingerprint (size + first-4KB hash + mtime).
- Tier 2: full SHA-256 only on tier-1 candidates. Stored forever (non-recompute).
- Short labels OK: first 8-12 hex of stored sha256 as working ID.
- Random short symbols are content-blind — forbidden as dedup keys.
- Downstream systems (oracle/router/FTS5) feed on deduplicated stream as fuel.

## LEGACY CONCEPTS CONFIRMED AS CURRENT ARCHITECTURE
seeds/chunks = turing_tidbits sha256 splitting. absorbers = compost + knowledge_intake.
oracles = A1 router + FTS5 + local models. context bridges = handoffs. Already
built and verified — need naming and further wiring, not invention.

## LONG ARC (operator's words, preserve)
Knowledge as sha256-hashed immutable chained ideas for the betterment of mankind —
a Library of Alexandria 2.0: all available knowledge, compiled into the maximally
efficient and absorbable form, available to everyone, uncensorable. Ideas hashed and
fused into a chain of knowledge. Newton: standing on shoulders of giants — the
platform lets everyone stand there. Resource flows lift the bottom floor.

## VERIFIED STATE AT THIS HANDOFF
main = origin/main = 2265c4aa, release v0.3.1 published, aerocement-panel-v0 public,
ladder 7-8 of 8 (see this session acknowledge output), RAPL sampler metering.

## NEXT SESSION PRIORITIES
1. Verify acknowledge output (first_release verified, open_invitation unlocked).
2. Repo family: start with aerocement overhaul (existing repo to transform).
3. Pipeline v1: tier-1/tier-2 dedup sweep across A15 + OptiPlex → fuel stream.
4. open_invitation rung 8 content when ready.
