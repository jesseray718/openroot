# Agape Cascade v2.3 - seed reserves + floor ratchet + shock
2026-09-21T10:19:11.056484+00:00

## Mechanism (seed-as-buffer hysteresis)
income pays DECAY first; surplus fills seed reserve to 0.5,
remainder lifts floor. Floor falls only when seeds are exhausted.
Shock at gen 12: -60% floors, -40% seeds.
kappa=0.15 endogenous supply, BASE=1.5, DECAY=0.010.

## Results
```
policy         pre_min  post_min recov    fin_min  gini    seed   welfare
bottom-first   0.0236   0.01     never    0.0188   0.2642  0.1421 743.46
equal          0.02     0.01     never    0.01     0.4629  0.103  591.69
merit-top      0.01     0.01     1        0.01     0.5697  0.1577 271.36
```

## Verdict
Best cumulative welfare: bottom-first (743.46).
Bottom-first post-shock recovery: never gens.
Stairway confirmed iff bottom-first recovers (finite gens) AND
final_min >= pre-shock min (floor resumed at ratcheted level).
Seed stock column = resilience capital held by the network base.
