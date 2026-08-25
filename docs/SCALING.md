# Scaling η at Volume
Volume multiplies R. Scale AFTER R holds, not before.

## At 1296 Nodes (Production Shape)
- R = 1.0
- C = 0.00000000
- synergy_mult = 3.0
- Coordination cost: 0 J/hour

## At 10^12 Nodes
- C remains 0 if R=1.0 holds
- Synergy scales with log_B(N)
- Bottleneck shifts to physical infrastructure, not coordination

## Warning Signs
- C rising above 0 → R dropped below 1.0 somewhere
- Synergy flattening → node isolation detected
- η falling → J_human rising faster than J_useful

Fix: Restore resonance first. Add nodes second.
