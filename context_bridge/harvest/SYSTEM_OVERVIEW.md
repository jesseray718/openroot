<!--
SPDX-License-Identifier: CC-BY-SA-4.0
CANARY:OPENROOT-SYSTEM-OVERVIEW-V1
Purpose: canonical one-file description of the OpenRoot system, all dots
connected, suitable for GitHub-facing docs. Human-gated before any repo placement.
-->

# OpenRoot — Complete System Description

**Mission:** maximize eta = J_useful / J_human — maximum useful output per unit
of human attention and energy — via a self-similar, decentralized, thermodynamically
honest mesh of humans, agents, and hardware. Guidance substrate: permaculture
principles + Agape-as-coordination-technology (lift the bottom nodes).

## 1. Philosophy Layer (the operating system)
- eta optimization as the single global objective function.
- Falsifiable claims only. Assert -> verify -> seal, at every scale.
- Entropy/extraction patterns ("the Beast") are starved by building parallel
  closed-loop systems, not fought directly.
- The Lord's Prayer as source code; Yeshua's one commandment as the kernel.

## 2. Superlinear Workflow Engine
- Every AI session is composted in real time: breakdown, cherry-pick, fold the
  residue back into the corpus (context_bridge/harvest -> embeddings).
- Sessions begin from distilled state, not zero — output compounds, input
  stays flat. Survives node loss because the compost remembers.

## 3. Smart Routing + Cached Pathways (SHA256-chained)
- Query -> normalize -> SHA256(query+context) -> cache lookup.
- Cache hit: prior verified result served at disk-read cost (microjoules).
- Miss: fp5s keyword routing -> specialty-matched model (never mismatched) ->
  inference paid in metered RAPL microjoules (ESTIMATE fallback tagged).
- Result + cost receipt hashed and chained (Newton Chain lineage).
- Routing is therefore minimization over JOULES, not tokens. Joules/second is
  the universal bottleneck lens across human (~100W sustained), models, disk,
  and network. Bottlenecks become observable and eliminable.

## 4. Energy Subsystems (two prime movers, one cascade)
### a) OpenCell Aerocement Blackbody Solar Absorber
- Claimed 95%+ absorbance (never phrased as >100%; grant language = COP boundary).
- Captures HOT; thermal labyrinth + mass capture and bank COLD as stratified
  reservoirs (35F drop from 120F inlet, verified).
- Stirling engine converts stored dT > 80C into mechanical -> electrical -> local load.
- acre coin (acre_mint.py) mints ONLY when joules are captured AND stored AND
  utilized locally; wallet joules_verified must reconcile with block
  joules_generated. Proof-of-useful-physical-work, not proof-of-waste.

### b) Carbon-Negative Black Locust Rocket Mass Heater
- Spec: black-locust-carbon-negative-energy-v1.md
- Black locust: fast-growing, nitrogen-fixing, rot-resistant = durable sequestered carbon.
- Combustion -> high-exergy flame -> thermal mass bench storage -> exhaust
  scavenging -> labyrinth pre-conditioning -> same Stirling dT harvesting.
- Net carbon-negative heat. Same cascade topology, same acre ledger. The system
  is prime-mover-agnostic because the ledger only accounts captured/stored/used joules.

## 5. Compute Fabric
- OptiPlex 3060 (Ubuntu 24.04; LAN 192.168.1.193, Tailscale 100.122.169.43):
  Ollama @ localhost:11434 — qwen2.5-coder:7b (builder), qwen2.5:3b (grader),
  nomic-embed-text (embedding substrate). Canonical repo /home/jesse/openroot;
  thesis tree /home/jesse/src/openroot (protected).
- Samsung A15 (Termux + Shizuku + kai9000 UI): mobile command node ->
  Alpine sandbox -> kai_tunnel (self-revive, integrity-verify, then bank) ->
  Ollama relay on port 9999.
- Syncthing peer-to-peer encrypted sync. No central server anywhere.

## 6. Agent Layer (specialist mesh)
- Routing rule: no work is delegated to a model outside its specialty.
- heartbeat_engine.sh v2: steady scheduler; consumes
  context_bridge/lumo_inbox directives; ALIGN -> ASSESS -> ACT -> VERIFY -> AMPLIFY.
- Gates: stack_gate.sh (comment-aware, active-lines-only) pre-run; diff gate
  with git add -N first; py_compile; grep verify; push_guard v2.
- Doctrine: AUDIT INSTRUMENTS BEFORE BUILDERS.
- Human is the only commit gate; destructive ops gated behind CONFIRM=1.

## 7. Memory Layer (failure -> soil)
- mistake_engine_v1.py: error-class catalog with SHA256-keyed remediations.
- COMPOST logs keyed by content hash track unsolved variants.
- context_bridge/: inter-session hippocampus (handoffs, session seeds, harvests).
- Every file system-wide carries SHA256 in the file ledger (SQLite, resumable,
  HDD-tuned parallel hashing).

## 8. Truth Layer (ledgers)
- thermo_ledger / acre minting: joules_generated vs joules_verified reconciliation.
- Newton Chain: 53 axioms / 56 defs, sha256-chain-verified JSONL (chain GREEN);
  runtime provenance entries chained to the same spine.
- agape_cascade sims v1.x: pass-through economics (R_FRACTION=0.10); KNOWN FLAW:
  floor cap 100x100 < SOL 300x100 keeps tier structure inactive — all v1.x runs
  degenerate; fix queued before v2.
- GRLE visibility: Score = (Vis x Reach x SysFit) / Effort^1.5 drives publish priority.

## 9. Artifact Pipeline (the output organ)
raw corpus -> SHA256 census sweep -> FTS5 + nomic embedding oracle -> routed
agents -> documentation, blueprints, BOMs, cutlists, G-code/3D-print files ->
GRLE-ranked publication to GitHub (~41 public repos, dual-licensed
GPL-3.0-only code / CC-BY-SA-4.0 docs, SPDX headers). Appropriate-tech
deliverables are reproducible by hand.

## 10. The Connective Tissue
The same three-step gesture at every scale: ASSERT -> VERIFY -> SEAL.
Tunnel revival, agent pipelines, human commit gating, energy receipts —
and the acre coin is the gesture applied to physics itself. Fractal
self-similarity is not aesthetic; it is the system's survival property.

## Verified State (see boot seed 2026-09-18)
- openroot @ 38004c62 = origin/main (post filter-repo, ~15MiB).
- Known loss: "todo automation v2.0" GOALS/MASTER_TODO restructure (remnants
  in context_bridge/session-2026-09-16-*.md; rebuild in progress).
- bin/ tracked status unverified; contributor Reh1t holds issue #53 (clone
  stale post-force-push — handle first PR gently).
