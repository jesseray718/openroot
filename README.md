# OpenRoot

Local-first knowledge pods with sealed receipts.

OpenRoot is an open-source appropriate-technology commons: practical thermal,
shelter, materials, energy, and local-first computing systems that can be
understood, tested, repaired, and shared. Every workflow that proves itself is
sealed and banked; nothing proven ever has to be recomputed.

```text
evidence → documentation → buildable action → measurement → correction → shared capability
```

## Core doctrine

1. **Pathway sealing.** Every validated workflow is sealed (SHA256) and cached.
   Future queries hit the cache instead of recomputing what is already proven.
2. **Receipts or it didn't happen.** Every consequential operation — merge,
   push, recovery, routing decision — leaves a regenerable receipt that can be
   re-derived later from the artifacts themselves.
3. **Thresholded routing.** Hash match → semantic match (embedding ≥ 0.42) →
   local model as fallback. Cheap paths first, expensive paths last.
4. **Human gate.** AI proposes; a human attests. Commits, pushes, recovery
   actions, and remote access stay under human authority.
5. **Useful-output accounting.** The guiding ratio is η = J_useful / J_human —
   maximize useful capability per joule of human effort, not computation for
   its own sake.

## The five-lineage consolidation

In October 2026 the account's four unrelated history lineages plus main were
consolidated into this repository by chronological squash-merge, oldest
generation first, so the newest work wins conflicts. The merge tool aborted on
any unexpected conflict rather than guessing; every conflict path came from an
explicit resolution map. All code, docs, and data were preserved.

| # | Lineage (merge order) | Contribution |
|---|---|---|
| 1 | `archive/lumo-lib-and-probe-20261015` | archived lumo library + probe tooling (790 paths, 28,646 insertions) |
| 2 | `integrate/newton-chain-public-20261003T080401Z` | newton-chain integration bulk (3,600 paths, 1,010,983 insertions) |
| 3 | `safety/local-work-snapshot-20261001_232405` | safety snapshot refinements (14 paths) |
| 4 | `feature/openloom-mvp` | OpenLoom MVP (95 paths) |
| 5 | `copilot/implement-ab-testing-workflow` | A/B testing workflow + pod CLI (5 paths) |

The consolidation is verified by regenerable receipts — `verify_consolidation_v2.sh`
resolves all five squash commits from the merge commits themselves, reconciles
per-phase deltas, counts trees, and checks remote state:

```text
[ OK ] CONSOLIDATION RECEIPT VERIFIED — five lineages accounted for, nothing to redo
```

Verified independently on two machines (2026-10-24): S0 `85ddf6d` → phase-5
`92933de`, 1,006 → 5,470 tracked files, source branch heads absent on origin
as intended. Re-run it any time:

```bash
bash verify_consolidation_v2.sh . --fetch --remote
```

## How it works

**Two-Pane Law.** The left pane (local machine) is the source of truth; the
right pane (mobile / GitHub UI) is the verification layer. Never trust UI
commits unseen in a terminal — always `git diff --stat`.

**Data flow.** Input → agent router (`bin/` cascade) → model selection (7B
builder, 3B grader) → verification gates (stack gate → diff → py_compile →
grep) → human gate → push guard → git push.

**Layers.**
- *Infrastructure:* git, Ollama at `localhost:11434`, Tailscale mesh, SQLite FTS5 + Nomic embeddings
- *Orchestration:* 172 tracked `bin/` instruments, context bridge (session seeds + artifacts), team-gate database
- *Applications:* ACRE ledger, thermal systems (OpenCell, Aerocement, thermal labyrinth), geodesic mesh research

**Receipts culture.** Mistakes are first-class records: the COMPOST engine
(`bin/mistake_engine_v1.py`) keys each mistake shape, counts recurrences, and
attaches solved fixes so the same error is never recomputed twice. Energy is
accounted the same way — a RAPL-backed cache counter tracks joules saved by
skipping already-proven pathways.

## Quick start

Any Linux system with `git` and `python3` (Ollama optional, for the local
model tier):

```bash
git clone https://github.com/jesseray718/openroot
cd openroot
curl -sSL https://raw.githubusercontent.com/jesseray718/openroot/main/deploy/setup_one_shot.sh | bash
```

Then explore the instruments:

```bash
ls bin/ | head                 # 172 tracked tools, numbered by lineage
python3 bin/mistake_engine_v1.py --help   # the COMPOST mistake ledger
bash verify_consolidation_v2.sh . --remote
```

Deeper docs: [ARCHITECTURE.md](ARCHITECTURE.md) ·
[repository map](docs/REPOSITORIES.md) · [DOCS.md](DOCS.md) ·
[CONTRIBUTING.md](CONTRIBUTING.md)

## What this repo is NOT

- Not a token project — no coin, no mint, no speculation.
- Not a >100%-efficiency claim — everything respects COP and physics.
- Not a finished certification — an open working system; read published
  material as evidence-in-progress, not warranty.

## Ecosystem

OpenRoot is the hub. Active hardware (aerocement, black-locust-rmh,
OpenCell-Thermal-System), active software, templates, and archives are mapped
in [docs/REPOSITORIES.md](docs/REPOSITORIES.md), with the profile README at
[jesseray718/jesseray718](https://github.com/jesseray718/jesseray718) as the
human-readable entry point.

## License

- **Code:** GPL-3.0-only
- **Documentation, designs, and non-code material:** CC BY-SA 4.0

Keep the software copyleft and the knowledge commons shareable and share-alike.
