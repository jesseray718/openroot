# The Superlinear Workflow: Sub-Second Local AI on a $200 Tower
Status: DRAFT v0.1 (staged, human-gated) | License: CC-BY-SA-4.0
Evidence: github.com/jesseray718/openroot (every claim git-verifiable)

## The problem
Agent pipelines recompute. Every new chat window, every fresh session,
re-solves yesterday's problems. The result is linear progress at
superlinear cost — attention burned re-deriving what the system already
knew. This is a caching failure dressed up as a workflow.

## The thesis (three load-bearing claims)
1. THE GAP IS THE THROTTLE: computing capacity concentrated at the top
   saturates; the same compute routed to the floor compounds. Routing
   is therefore an engineering decision, not charity.
2. MARGINAL UTILITY IS THE ROUTER: priority weight w = 1/(f+eps).
   Attention flows to the highest marginal value, always.
3. FLOW-THROUGH, NOT HOARD: verified output compounds when it passes
   through; it rots when it accumulates.

## The triad (why sessions stop starting from zero)
- CACHE: SQLite, problem-sha -> solution-sha. A mistake class that has
  been solved once is never re-computed. Measured result: 48x speedup
  on embedding retrieval (embed_cache.py, sha-keyed vector cache).
- CHAIN: sha-linked, append-only lesson ledger with staging gates.
  Every lesson passes deterministic checks, then a human gate, then
  graduates. Verification is what makes cached answers appreciate.
- ROUTER: FTS5-first dispatch. If the corpus answers it, the answer
  returns in milliseconds — no model call at all. Only genuine misses
  escalate to a 7B builder, whose draft faces a grader model from a
  DIFFERENT model family (cross-family grading closes the shared-blind-
  spot hole that let same-lineage graders pass hallucinations).

## The measured result
- Exact-hit retrieval: sub-second (SQLite FTS5, no inference)
- Embedded retrieval: 48x faster than baseline after cache
- Model calls reserved for novel work only — the tier system
- Negative results are published: our simulation suite refuses
  unphysical claims (0-configs-found is a shipped feature, see
  thermal_balance v6.3), which is why the positive claims hold

## The stack (all local, all sovereign)
One repurposed OptiPlex 3060. Ollama serving tuned Modelfile builders
(7B-class) and graders (3B-class). nomic-embed-text for vectors.
SQLite everywhere — no server, no cloud dependency, no API bill.
Termux on a $130 Android phone as a satellite node over Tailscale SSH.
Total infrastructure cost: the electricity.

## The discipline that makes it work
1. Atomic specs: one bounded task per model call, never open-ended asks
2. Grade gates before any output is trusted; cross-family graders
3. CONFIRM=1 human graduation: no artifact enters the cache or the
   repository without a human gate. The human is the only commit gate.
4. Provenance in every commit message: who drafted, what verified
5. Audit instruments before builders — a file that survived tests is
   not a product

## Try it
The loop, the cache, the router, and the staging gates are all in
github.com/jesseray718/openroot (GPL-3.0 / CC-BY-SA-4.0).
Read SUPERLINEAR.md in the repo root for the one-prompt bootstrap.

## Why this matters beyond AI
The same triad (cache verified work, chain it so it appreciates, route
attention by marginal value) governs the thermal cascade farm in our
SARE proposal: energy captured, stored, and routed bottom-first.
Computation is just the fastest place to prove the doctrine.
