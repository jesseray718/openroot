# Agape Cascade v2.5 - v2.8: Ledger Discipline Arc

Five versions, one day. Each version kills an accounting lie the previous exposed.

## The arc

| version | commit      | change                          | verdict |
|---------|-------------|----------------------------------|--------|
| v2.5    | 1cfe00a     | solidarity deploy + closed ledger| leak ~-90.9 (impossible) |
| v2.6    | orphan      | conservation-law + telescope     | 1 (WORKING - detected v2.5) |
| v2.7    | 41b224a     | single-book, sub-saturation, permaculture policy | leak=0 (PASS) |
| v2.8    | 81cb8f3     | telescope-exact path integral    | leak~0 (PASS - verified) |

**v2.6 note:** Ran on OptiPlex, verdict=1 triggered bank death (set -eu),
recovered as untracked file. Bank-proceeds-regardless law adopted v2.7+.

## Results (v2.8, single-book verified)

Shock = gen 12, -60% floors, -40% seeds. GENS=40, kappa=0.08.

| policy       | min_fl | med_fl | recov  | path_gain | cost_path |
|--------------|--------|--------|--------|-----------|-----------|
| bottom-first | 0.2761 | 0.2778 | 24     | 56.67     | 108.14    |
| equal        | 0.1641 | 0.2371 | never  | 43.13     | 106.73    |
| merit-top    | 0.01   | 0.01   | never  | -87.51    | 48.13     |
| permaculture | 0.2029 | 0.2451 | never  | 49.06     | 113.51    |

Key findings:
- `equal` holds cost crown (106.73) at this regime
- `merit-top` posts negative welfare in BOTH arms - extraction fails
- `permaculture` pays +6.8 cost for softer allocation (higher min_fl)
- Transfer wedges (welf-path: ~62-67) are DECLARED store-moves, not phantom growth

## Verification

- Telescope: max |path - final_gain| ≤ 1e-9 across all arms [PASS]
- Saturation: all rows sub-ceiling (frac_at_cap ≤ 0.2) [VALID]
- Gates: py_compile + canary grep + stack_gate.sh v2 [ALL PASS]
- Canary: AGCA2V28

Full data: workareas/cascade-v28-*/results.json

Provenance: lumo-assisted, human-gated (paste execution IS the gate).
