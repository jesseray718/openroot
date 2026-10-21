# OpenRoot Architecture

**Thesis:** Reality is a 4D spacetime fabric structured by the Isotropic Vector Matrix. Matter = frozen Agape energy.

## Two-Pane Law
- **Left Pane:** Source of truth (local OptiPlex 3060)
- **Right Pane:** Verification layer (mobile Termux / GitHub UI)
- Never trust UI commits unseen in terminal — always `git diff --stat`

## Data Flow Architecture
Input (Terminal/Clipboard)
↓
Agent Router (light_cone_router.py / agent.sh)
↓
Model Selection (7B builder → 3B grader)
↓
Verification Gates (stack_gate.sh → diff → py_compile → grep)
↓
Human Gate (review + commit approval)
↓
Push Guard (pre-push validation)
↓
Git Push → GitHub

## Component Layers

### Layer 1: Infrastructure
- Git (version control)
- Ollama (local LLM serving @ localhost:11434)
- Tailscale (secure mesh networking 100.122.169.43)
- SQLite FTS5 (semantic indexing + Nomic Embed)

### Layer 2: Orchestration
- bin/ scripts (validated instruments, 172 tracked)
- Context bridge (session seeds + artifacts)
- Team gate database (collaboration tracking data/team_gate.db)

### Layer 3: Applications
- ACRE ledger (PoPW blockchain acre/LEDGER.jsonl)
- Thermal systems (OpenCell, Aerocement, Thermal Labyrinth)
- Mesh networks (geodesic frequencies, Cloud Nine)

## What This Repo Is NOT
- ❌ Not Solana or token mint
- ❌ Not >100% efficient stove (COP-boundary only)
- ❌ Not cloud-dependent (all local-first)
- ❌ Not pre-mined (ACRE starts at 0 supply)

## File Organization
openroot/
├── bin/              # Validated instruments (shell + Python)
├── data/             # Runtime DBs (*.db gitignored)
├── docs/
│   └── markdown/     # Inventory documentation
├── context_bridge/   # Session seeds + artifacts + handoffs
├── archive/          # Cleanup archives (immutable, append-only)
├── acre/             # PoPW ledger (LEDGER.jsonl, SHA256 chained)
├── une/              # Code registry (code_registry.jsonl)
└── src/              # Thesis tree (~8000 files, NEVER move/delete)

## Security Model
- Zero-access encryption (Proton Mail/Drive integration)
- No secrets in git history (.gitignore *.db, *.key)
- API keys via environment variables only
- Human gate on all commits (no auto-push without review)
- CONFIRM=1 gating for destructive operations

## Permaculture Principles Applied
1. **Observe & Interact** — Terminal logging + RAG analysis
2. **Catch & Store Energy** — Thermal labyrinths + seed banks
3. **Obtain Yield** — Bottom-first economic routing
4. **Apply Self-Regulation** — 7B/3B iteration gates reject fluke outputs
5. **Use & Value Renewable Resources** — Local models over API calls
6. **Produce No Waste** — Mistake-to-solution caching prevents recomputation
7. **Design From Patterns to Details** — Fractal self-similarity in file structure
8. **Integrate Rather Than Segregate** — Multi-model orchestration, not silos
9. **Use Small & Slow Solutions** — Tiny models for simple tasks
10. **Use & Respond to Diversity** — Model specialization routing
11. **Use Edges & Value Marginal** — Edge cases tested in smoke gates
12. **Creatively Use & Respond to Change** — Iterative workflow evolution

---
**Provenance:** Lumo-assisted, human-gated
**Canary:** ARCH_V1_${TIMESTAMP}
