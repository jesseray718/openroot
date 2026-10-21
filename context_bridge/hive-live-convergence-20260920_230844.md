# Hive Live Convergence Run - 20260920_230844

## Verified state
- HEAD: 44346bf3 [FIX] hive_nursery v1.1 - election stage list-vs-dict TypeError; wrap probe rows in dict carrying elected leader (Lumo-authored, py_compile+grep passed)
- hive registry: data/hive_registry.json (09b965ab15e4)
- router ledger: data/router_ledger.db

## Elected leaders
- [classify] qwen2.5:3b (3.0b, 29125.2ms)
- [code-edit] qwen2.5:3b (3.0b, 756.5ms)
- [draft] qwen2.5:3b (3.0b, 1282.1ms)
- [outline] qwen2.5:3b (3.0b, 1249.3ms)
- [scope-reject] qwen2.5:3b (3.0b, 1183.9ms)
- [embed] nomic-embed-text:latest (0.1b, 5512.8ms)

## Ledger totals
```
  provider        hops   avg_ms   ok%

  round-by-round hop volume:

  spawned subtask lineage (recursion depth reached):
```

## Broken / held
- lanes without keys remain HELD (by design, keys in env only)

## Next actions
1. grade tiny-leader quality at recursion depth 2 vs big model (3B grades, never self-graded)
2. close lb_loop mistake-to-solution binding gap using forensics report
3. lumo_lane inbox packets await paste-back - one is the binding patch plan
