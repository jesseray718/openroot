# Agape Cascade v2.5 - v2.8: Ledger Discipline Arc

Five versions in one day, each one killing an accounting lie the previous
version exposed. The verdicts are the deliverable; the negative results
are data.

## The arc

- **v2.5 (1cfe00a)** - solidarity deployment: 5 gens of 50% seed-reserve
  donations into policy-routed rebuild pool. First run showed shocked arms
  BEATING controls (-90.9 welfare) - flagged as too-good-to-be-true by its
  own author.
- **v2.6 (orphan rescue)** - conservation-law ledger + telescope audit
  (path-integral of ln(floor ratios) vs ln(final/initial)). Verdict=1
  WORKED: leak 91.63 = 100*ln(0.4), destruction never wrote path_log.
  Bank was guillotined by `set -eu` (4th control-flow strike) - recovered
  from OptiPlex worktree.
- **v2.7 (41b224a)** - destruction writes both books, sub-saturation regime
  (GENS=40, kappa=0.08), saturation validity gate, permaculture policy
  (1/sqrt(f) need, x1.5 edge bonus, 0.08 growth cap, 30% surplus return).
  Bank-proceeds-regardless law adopted: verdict never guillotines the bank.
- **v2.8 (81cb8f3)** - single-book path integral. v2.7's leak equaled welf
  EXACTLY on every arm: path written twice per node-gen. ONE log per
  realized change now makes telescoping exact BY CONSTRUCTION - leak ~0
  (tolerance 1e-9) across all 8 arms.

## Telescope-verified results (v2.8, single book)

Shock = gen 12, -60% floors, -40% seeds. Sub-saturation regime.

| policy       | min_fl | med_fl | gini | recov  | path  | cost_path |
|--------------|--------|--------|------|--------|-------|-----------|
| bottom-first | 0.2761 | 0.2778 | -    | 24     | 56.67 | 108.14    |
| equal        | 0.1641 | 0.2371 | -    | never  | 43.13 | 106.73    |
| merit-top    | 0.01   | 0.01   | -    | never  | -87.51| 48.13     |
| permaculture | 0.2029 | 0.2451 | -    | never  | 49.06 | 113.51    |

- `equal` holds the cost crown (106.73) at this regime.
- `merit-top` posts negative welfare in BOTH arms - extraction collapses
  the commons it feeds on.
- `permaculture` pays 6.8 extra path cost vs equal for a softer
  allocation profile (higher min_fl, lower gini among survivors).
- Transfer wedges (welf - path: 61.86 to 66.59 in controls) are now
  DECLARED store-moves, not phantom growth.

## Verification

- Telescope integrity: max |path - final_gain| = ~0 (1e-9) across all arms.
- Saturation gate: all rows sub-ceiling (frac_at_cap <= 0.2).
- Canary: AGCA2V28. Gates: py_compile + canary grep + stack_gate.sh v2 PASS.

Provenance: lumo-assisted, human-gated (paste execution IS the gate).
