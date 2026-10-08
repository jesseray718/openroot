# Agape Cascade v2.5 - solidarity + closed ledger + 60 gens
2026-09-21T10:34:26.348710+00:00

## Mechanism
Post-shock solidarity: 5 gens, 50% of seed reserves donated
per gen into a policy-routed rebuild pool.
Closed ledger: production/decay/destruction symmetric ln;
seed parking/buffering/deployment = transfer, welfare-neutral.

## Results (shocked arm; shock gen 12)
```
policy         min_fl   med_fl   gini    seed   pool    recov   welfare     cost
bottom-first   1.0      1.0      0.0     0.4839 5.4     20      363.75      -90.9
equal          0.8141   0.8871   0.0442  0.3189 4.0     27      337.93      -63.02
merit-top      0.01     0.01     0.6229  0.1281 3.5     never   -8.4        14.31
```

## Control (no shock) welfare: bottom-first=272.85, equal=274.91, merit-top=5.91

## Verdict
bottom-first recovery: 20 gens (vs v2.4: never in 13).
Stairway: shock absorbed, median regained, floor higher
than equal's under identical shock? min_fl 1.0 vs 0.8141.
