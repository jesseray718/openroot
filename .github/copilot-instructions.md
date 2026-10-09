<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- CANARY:OPENROOT-COPILOT-INSTRUCTIONS-V1 -->

# OpenRoot System Context for GitHub Copilot

## Mission
Maximize eta = J_useful / J_human: useful output per unit of human attention
and energy. Self-similar, decentralized, thermodynamically honest mesh of
humans, agents, and hardware. Guidance substrate: permaculture principles +
Agape-as-coordination-technology. Falsifiable claims only, no hype.

## Architecture Overview (10 layers)
1. PHILOSOPHY: eta optimization as global objective. Assert -> verify -> seal
   at every scale. Extraction/centralization patterns are starved by parallel
   closed-loop systems, not fought.
2. SUPERLINEAR WORKFLOW: every AI session is composted — breakdown,
   cherry-pick residue, fold back into corpus via embeddings. Sessions start
   from distilled state; output compounds while input stays flat.
3. SMART ROUTING + CACHED PATHWAYS: query -> normalize -> SHA256(query+context)
   -> cache lookup (SQLite + FTS5 + nomic-embed-text vectors). Hit = prior
   verified result at disk-read cost. Miss = keyword route to
   specialty-matched model, inference metered in RAPL microjoules (ESTIMATE
   fallback tagged). Receipts SHA256-chained (Newton Chain lineage). Routing
   is minimization over JOULES, not tokens; J/second is the universal
   bottleneck lens.
4. ENERGY SUBSYSTEMS (two prime movers, one thermal cascade):
   a) OpenCell aerocement blackbody solar absorber: 95%+ absorbance
      (COP-boundary grant language; never ">100%"). Thermal labyrinth stores
      hot + cold (verified 35F drop from 120F inlet). Stirling @ dT>80C ->
      mechanical -> electrical -> local load.
   b) Carbon-negative black locust rocket mass heater: durable sequestered
      carbon + high-exergy combustion -> thermal mass bench -> same Stirling
      harvesting. Prime-mover-agnostic cascade.
   c) ACRE COIN (acre_mint.py, openroot-edge): mints ONLY when joules are
      captured AND stored AND utilized locally. Wallet joules_verified must
      reconcile with block joules_generated. Proof-of-useful-physical-work.
5. COMPUTE FABRIC: OptiPlex 3060 (Ubuntu 24.04, LAN 192.168.1.193, Tailscale
   100.122.169.43). Ollama @ localhost:11434: qwen2.5-coder:7b (builder),
   qwen2.5:3b (grader), nomic-embed-text (embeddings). Samsung A15 Termux
   mobile node -> Alpine sandbox -> SSH tunnels (self-reviving, integrity
   verified) -> Ollama relay :9999. Syncthing P2P sync, no central server.
   Canonical repo /home/jesse/openroot; thesis tree /home/jesse/src/openroot
   (protected, never move/delete, ~8000 files).
6. AGENT MESH: no work delegated outside a model's specialty. Gates:
   stack_gate.sh (comment-aware awk, active lines only) pre-run; diff gate
   with `git add -N` FIRST (git diff is blind to untracked files);
   py_compile; grep verify; push_guard v2. Human is the ONLY commit gate.
   Doctrine: AUDIT INSTRUMENTS BEFORE BUILDERS.
7. MEMORY: mistake_engine_v1.py catalogs error classes with SHA256-keyed
   remediations. COMPOST logs track unsolved variants. context_bridge/ holds
   session handoffs, seeds, harvests. System-wide SHA256 file ledger
   (SQLite, resumable, HDD-tuned 2-worker parallel hashing).
8. LEDGERS: thermo_ledger (RAPL vs ESTIMATE energy provenance), acre
   minting, Newton Chain (53 axioms / 56 defs, sha256-chain-verified JSONL,
   chain GREEN), agape_cascade econ sims v1.x (KNOWN FLAW: floor cap
   100x100 < SOL 300x100 keeps tier structure inactive; fix before v2),
   GRLE visibility Score=(Vis*Reach*SysFit)/Effort^1.5.
9. ARTIFACT PIPELINE: raw corpus -> SHA256 census -> FTS5+nomic oracle ->
   routed agents -> documentation, blueprints, BOMs, cutlists, G-code ->
   GRLE-ranked GitHub publication.
10. CONNECTIVE TISSUE: assert -> verify -> seal fractally repeated at tunnel
    revival, agent pipelines, human commit gating, and energy receipts.

## Capabilities (what this system can do)
- Autonomous multi-agent authoring with graded verification (7B writes, 3B
  grades, human seals) — proven: 7B went 5-for-5 while gate bugs were found.
- Resumable system-wide file census with dedup/recovery across ~888k files.
- Joule-priced routing and cached inference pathways (offline, sovereign).
- Energy receipting with hardware-counter provenance where available.
- Local-first LLM serving to mobile UI (kai9000) via self-healing tunnels.
- Weekly automated ops: onepass_v3.sh (env map, drift report, 7B next-move,
  session seed, commit).
- Recovery discipline: history was rewritten via git filter-repo
  (--strip-blobs-bigger-than 50M, repo now ~15MiB) — remnants live in
  context_bridge/session-*.md, never assume old SHAs resolve.

## Conventions Copilot MUST follow in this repo
- Licenses: GPL-3.0-only for code, CC BY-SA 4.0 for docs. SPDX headers
  required on new files.
- Scripts ship as one bash paste: cat <<'EOF' heredoc, self-writing,
  idempotent, absolute paths (no ~), set -eu, export GIT_PAGER=cat,
  bracketed stage tags [banked]/[held]/[gate], [exit=0] as last line,
  [canary] paste-intact marker.
- Commit messages assert; only grep/py_compile verifies. Never claim
  verification that was not run.
- Destructive ops gated behind CONFIRM=1 env var. Never auto-run rm, mv
  over trees, git push --force, or branch deletes.
- Two-pane law, fork-only. Delete merged branches immediately.
- No fabricated stats, dates, or SHAs. If unknown, say so plainly.

## Current State (2026-09-18)
- openroot @ 38004c62 = origin/main, post-filter-repo.
- PENDING: bin/ tracked-status verification; GOALS.md + MASTER_TODO rebuild
  from context_bridge remnants; Reh1t issue #53 (RAG ingestion) — clone is
  stale post-force-push, handle first PR gently; quarantine branch
  quarantine-pulse-20260918 possibly still on origin (delete when confident).
