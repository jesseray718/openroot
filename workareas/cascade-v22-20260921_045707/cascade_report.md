# Agape Cascade v2.2 - synergetic compounding (endogenous supply)
2026-09-21T09:57:07.546709+00:00

## Mechanism
supply_g = BASE + kappa * (sum_sqrt(f) - sum_sqrt(f_init))
Concave production: flattened floor distributions yield more total
output. Sustained routing is an investment in the supply curve.

## Sweep (GENS=25, DECAY=0.010, BASE=1.5)
```
kappa  policy         min_fl   gini    sat    welfare     tot_supply
0.0    bottom-first   0.3244   0.1145  0      178.88      37.5
0.0    equal          0.145    0.3154  0      204.78      37.5
0.0    merit-top      0.01     0.5616  0      232.76      37.5
0.05   bottom-first   0.5085   0.0613  0      204.09      54.3
0.05   equal          0.2773   0.2352  0      223.21      50.7
0.05   merit-top      0.01     0.5531  0      250.37      40.0
0.1    bottom-first   0.85     0.0249  0      239.37      86.8
0.1    equal          0.5339   0.1309  0      252.49      76.4
0.1    merit-top      0.01     0.5421  0      274.2       43.4
0.15   bottom-first   0.99     0.0     0      280.34      136.7
0.15   equal          0.9479   0.0057  0      287.68      117.8
0.15   merit-top      0.01     0.5273  0      302.93      48.0
0.2    bottom-first   0.99     0.0     0      325.88      190.6
0.2    equal          0.99     0.0     0      327.41      168.4
0.2    merit-top      0.01     0.5085  0      339.39      54.1
0.3    bottom-first   0.99     0.0     0      421.57      302.6
0.3    equal          0.99     0.0     0      415.01      275.3
0.3    merit-top      0.0186   0.4532  0      426.25      72.1
```

## No flip within sweep (honest negative)
Bottom-first did NOT overtake merit-top at any tested kappa.
Either coupling weaker than 0.30 in reality, or production is
more linear than sqrt - regime needs rethink, not faith.
