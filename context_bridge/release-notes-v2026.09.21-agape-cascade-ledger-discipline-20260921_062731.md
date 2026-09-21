# Agape Cascade v2.5 - v2.8: Ledger Discipline Arc

Five versions, one day. Each version kills an accounting lie the previous exposed.

## The arc

- **v2.5 (1cfe00a)** - solidarity deploy + closed ledger. Shocked arms beat
  controls (-90.9 welf) - flagged as impossible by its own author.
- **v2.6 (orphan rescue)** - conservation-law telescope. Verdict=1 WORKING:
  leak 91.63 = 100*ln(0.4), destruction never wrote path_log. Bank was
  guillotined by set -eu (4th control-flow strike); recovered from worktree.
- **v2.7 (41b224a)** - both books written, sub-saturation regime
  (GENS=40, kappa=0.08), saturation gate, permaculture policy. Leaked
  exactly == welf (double-count) - caught by its own telescope.
- **v2.8 (81cb8f3)** - single-book path integral: ONE log per realized
  change. Telescope exact BY CONSTRUCTION, leak ~1e-9 across all 8 arms.

## Results (v2.8, telescope-verified)

Shock = gen 12, -60% floors, -40% seeds. GENS=40, kappa=0.08.

| policy       | min_fl | med_fl | recov  | path_gain | cost_path |
|--------------|--------|--------|--------|-----------|-----------|
| bottom-first | 0.2761 | 0.2778 | 24     | 56.67     | 108.14    |
| equal        | 0.1641 | 0.2371 | never  | 43.13     | 106.73    |
| merit-top    | 0.01   | 0.01   | never  | -87.51    | 48.13     |
| permaculture | 0.2029 | 0.2451 | never  | 49.06     | 113.51    |

- `equal` holds the cost crown (106.73) at this regime.
- `merit-top` negative welfare in BOTH arms - extraction collapses the commons.
- `permaculture` pays +6.8 path cost for softer allocation (higher min_fl).
- Transfer wedges (welf-path: ~62-67 controls) DECLARED store-moves, not phantom growth.

## Verification

- Telescope: max |path - final_gain| ~ 1e-9, all arms [PASS]
- Saturation: all rows sub-ceiling (frac_at_cap <= 0.2) [VALID]
- Gates: py_compile + canary + stack_gate.sh v2 [PASS]. Canary: AGCA2V28.
- Full data: workareas/cascade-v28-*/results.json

Provenance: lumo-assisted, human-gated (paste execution IS the gate).
