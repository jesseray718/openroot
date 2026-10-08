# Agape Cascade v2.1 - desaturated (policies can differ)
2026-09-21T09:47:28.212506+00:00

## Why v2 printed identical rows (path-independence proof)
v2 supply saturated every node to CAP. Log utility telescopes:
cum_welfare = sum_i ln(CAP/f0_i) - independent of allocation.
258.39 was that constant. Fix: no saturation + additive decay.

## Regime
aggregate headroom: 73.5 | total supply: 37.5 (51% of headroom)
DECAY=0.010/gen | R_FRACTION=0.10 | GENS=25 | N=100

## Results (25 gens)
```
policy         min_fl   mean_fl  gini    cum_welfare gen_to_min_0.5  sat
bottom-first   0.3244   0.3896   0.1145  178.88      never           0
equal          0.145    0.3896   0.3154  204.78      never           0
merit-top      0.01     0.39     0.5616  232.76      never           0
```

## Verdict
Policies differentiated. Best cumulative welfare: merit-top.
