# Agape Cascade v2.6 - conservation-law ledger
2026-09-21T10:47:56.812732+00:00

## Ledger law
LOGGED: production, decay, destruction. NEUTRAL: park/draw/grant.
Telelescope check: path-integral must equal ln(final/initial).

## Results (SHOCKED arm)
```
policy         min_fl   med_fl   gini    seed   idle    recov  welfare     cost
bottom-first   1.0      1.0      0.0     0.3447 0       19     255.54      -0.51
equal          0.8601   0.9331   0.0323  0.3239 0       26     247.49      9.18
merit-top      0.01     0.01     0.6212  0.0846 0       never  -111.15     106.34
```

## Control (no shock)
```
policy         min_fl   med_fl   gini    seed   idle   welfare    
bottom-first   1.0      1.0      0.0     0.3193 23     255.03     
equal          1.0      1.0      0.0     0.3152 16     256.67     
merit-top      0.01     0.3486   0.4908  0.109  0      -4.81      
```

## Telescope integrity
max |path_log - final_gain| across runs: 91.629073
[LEAK] implementation bug - results INVALID
