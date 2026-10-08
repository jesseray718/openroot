# Agape Cascade v2.4 - repaired instruments
2026-09-21T10:27:46.249119+00:00

## Repairs
- welfare debits destruction at shock (net-zero rubble accounting)
- recovery vs pre-shock MEDIAN (min-baseline vacuity eliminated)
- SEED_TAX=0.30 proportional skim replaces seed-first starvation
- control arm isolates resilience cost

## Results (SHOCKED arm: gen 12, -60% floors, -40% seeds)
```
policy         min_fl   med_fl   gini    seed   recov   welfare     cost_vs_ctrl
bottom-first   0.1758   0.1804   0.0669  0.0492 never   191.65      104.27
equal          0.0886   0.1616   0.2637  0.0413 never   223.62      81.02
merit-top      0.01     0.0484   0.6253  0.0536 never   125.65      125.39
```

## Control (no shock) min floors: bottom-first=0.7454, equal=0.4433, merit-top=0.01

## Verdict: stairway NOT confirmed under repaired metrics
bottom-first recov=never, final min floor=0.1758.
Honest negative - instruments now trustworthy; the
dynamics (SEED_TAX, DECAY, kappa) are the tuning knobs.
