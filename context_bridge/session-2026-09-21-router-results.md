# Router 5-Round Results — 2026-09-21
- COMPLETED (canary: multi-router-smoke-complete) in <30s wall — prior death-mark probe misjudged
  fast-completion as crash; verdict logic now canary-based (lesson bound)
- qwen3b_local 5/5 hops, 1664ms avg — 3B code/classify talent replicated under real routing load
- openrouter 0/10 hops — free lane produced zero successes; cause not yet isolated (next: capture
  its stderr per-hop; suspected unauth-list model resolution returned unusable model or silent None)
- lumo_manual 0/5 — paste-bridge lane waiting on human; FileNotFoundError on round005_t3 inbox file
  is the designed HOLD, not a crash (no traceback)
- OLD outbox crash class remains CLOSED under load (guard cf6c422a, this run is the proof)
## Provenance: lumo-assisted, human-gated
