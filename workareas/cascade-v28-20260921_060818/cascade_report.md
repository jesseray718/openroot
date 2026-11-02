# Agape Cascade v2.8 - single-book path integral
2026-09-21T11:08:18.948493+00:00

v2.7 own goal: path written twice per node-gen (leak == welf).
v2.8: one log per REALIZED change -> telescope exact by
construction. Costs ranked on path (verified), welf declared
separately with its transfer wedge (park/draw/grant revaluation).

## Shocked arm (gen 12, -60% floors, -40% seeds)
```
policy         min_fl   med_fl   gini    cap%   recov  path     cost_path
bottom-first   0.2761   0.2778   0.0206  0.0    24     56.67    108.14
equal          0.1641   0.2371   0.1877  0.0    never  43.13    106.73
merit-top      0.01     0.01     0.6377  0.04   never  -87.51   48.13
permaculture   0.2029   0.2451   0.1445  0.0    never  49.06    113.51
```

## Control (no shock)
```
policy         min_fl   med_fl   gini    cap%   path     welf     wedge
bottom-first   0.8069   0.8146   0.0267  0.0    164.81   231.4    66.59
equal          0.5231   0.7056   0.1366  0.07   149.86   211.72   61.86
merit-top      0.01     0.2102   0.5506  0.2    -39.38   -27.28   12.1
permaculture   0.7638   0.81     0.0362  0.0    162.57   228.75   66.17
```

## Telescope integrity
max |path - final_gain| = 0.0 (expect ~1e-9)
[PASS] telescope exact - path rankings trustworthy
Saturation gate: all rows sub-ceiling - valid.

## Path-verified shock costs (ctrl - shock)
costs: {'bottom-first': 108.14, 'equal': 106.73, 'merit-top': 48.13, 'permaculture': 113.51}
lowest cost: merit-top at 48.13

## Wedges (welf - path) - transfers, not losses:
bottom-first=66.59 equal=61.86 merit-top=12.1 permaculture=66.17
