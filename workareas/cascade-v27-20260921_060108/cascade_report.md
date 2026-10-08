# Agape Cascade v2.7 - telescope fix + permaculture policy
2026-09-21T11:01:08.742721+00:00

Regime: GENS=40 kappa=0.08 (sub-saturation attempt),
validity gate: frac_at_cap per row (saturated rows VOID).

## Shocked arm (gen 12, -60% floors, -40% seeds)
```
policy         min_fl   med_fl   gini    cap%   seed    recov  welfare     cost
bottom-first   0.2761   0.2778   0.0206  0.0    0.0491  24     83.94       147.46
equal          0.1641   0.2371   0.1877  0.0    0.043   never  65.55       146.17
merit-top      0.01     0.01     0.6377  0.04   0.0642  never  -88.37      61.09
permaculture   0.2029   0.2451   0.1445  0.0    0.0455  never  74.54       154.21
```

## Control (no shock)
```
policy         min_fl   med_fl   gini    cap%   seed   welfare    
bottom-first   0.8069   0.8146   0.0267  0.0    0.2517 231.4      
equal          0.5231   0.7056   0.1366  0.07   0.2051 211.72     
merit-top      0.01     0.2102   0.5506  0.2    0.0753 -27.28     
permaculture   0.7638   0.81     0.0362  0.0    0.2398 228.75     
```

## Telescope integrity
max |path - final| = 231.397144
[LEAK] implementation bug - flag for audit


Saturation gate: all rows sub-ceiling - valid.

## Costs (ctrl - shock): {'bottom-first': 147.46, 'equal': 146.17, 'merit-top': 61.09, 'permaculture': 154.21}
Permaculture policy: 1/sqrt(f) need, x1.5 edge bonus,
0.08 growth cap with spill, 30% hi->lo surplus return.
Compare vs equal (v2.4/2.5 equal-cost winner).
