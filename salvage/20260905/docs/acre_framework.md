# ACRE: Energy-Tokenized Computation

Hash-chained ledger. Real CPU joules measured and tokenized at 1000 J = 1 ACRE. Bitcoin OpenTimestamps anchors.

**Pipeline:**
AI inference → CPU frequency × cores × time → joules → Landauer floor comparison → ACRE mint → Merkle root → OTS stamp → previous-hash chain.

**Commands (existing):**
./bin/aider-lite --write --commit --ots --mint "prompt" file
./bin/thermo-audit acre/LEDGER.jsonl   # or equivalent audit path
python3 bin/reversible_sim.py <bits> <joules>
./bin/acre-dashboard

**Current measured gap:** \~10¹⁷× above Landauer floor. Theoretical reversible recovery approaches 100 %.

**Next:** ARM vs x86 cross-architecture, only measured joules enter the ledger, lattice-mediated mint.
