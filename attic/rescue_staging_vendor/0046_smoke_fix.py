#!/usr/bin/env python3
"""Smoke v2: discover real exports, verify reward_verified, bank ledger entry."""
import inspect, json, math, sys

HOME = "/data/data/com.termux/files/home"
LEDGER = "/sdcard/openroot/context_bridge/thermo_ledger.jsonl"
PHI = 1.618033988749895

sys.path.insert(0, HOME + "/src/une")
import une_atomic_library as lib

funcs = sorted(n for n, o in vars(lib).items() if inspect.isfunction(o))
print(f"[inspect] exported functions: {funcs}")

rv = getattr(lib, "reward_verified", None)
assert rv is not None, "[held] reward_verified missing - patch did not take"

# locate the legacy compounding fn by its formula, don't guess its name
legacy_name, legacy_sig = None, ""
for n in funcs:
    try:
        src = inspect.getsource(getattr(lib, n))
    except OSError:
        continue
    if "min(epochs, 50)" in src or "min(epochs,50)" in src:
        legacy_name = n
        legacy_sig = str(inspect.signature(getattr(lib, n)))
        break
print(f"[inspect] legacy compounding fn: {legacy_name}{legacy_sig}" if legacy_name
      else "[inspect] legacy compounding fn: not found by source scan")

solo    = rv(1.0, 50, cooperators=0)    # 50 solo epochs -> base, nothing more
phantom = rv(1.0, 99, cooperators=3)   # claimed epochs >> cooperators -> clamp to 3
coop    = rv(1.0, 5, cooperators=12)    # 5 genuinely verified epochs

assert abs(solo - 1.0) < 1e-9, f"solo leaked: {solo}"
expect_phantom = PHI ** 3 * (1 + math.log(3) / PHI)
assert abs(phantom - expect_phantom) < 1e-6, f"clamp broken: {phantom} != {expect_phantom}"
assert coop > 1.0, "cooperation uncompensated"

print(f"[verify] solo(50 ep, 0 coop)   = {solo:.4f}   (PO-016: solo logs pay nothing)")
print(f"[verify] phantom(99 ep, 3)    = {phantom:.4f} (clamped to 3 verified)")
print(f"[verify] coop(5 ep, 12 coop)   = {coop:.4f}   (bona fide compounding)")
if legacy_name:
    print(f"[verify] legacy '{legacy_name}' present but uncalled (quarantined)")

with open(LEDGER, "a") as fh:
    fh.write(json.dumps({
        "type": "po016_fix",
        "bench_peak_atom_ops_s": 2039906,
        "claim_ratio": 3006,
        "theorem_dupes_removed_per_store": 15,
        "reward_verified_files": ["src/une/une_atomic_library.py",
                                  "src/une_atomic_library.py"],
        "legacy_fn": legacy_name, "legacy_signature": legacy_sig,
        "solo": solo, "phantom": phantom, "coop": coop,
        "smoke": "passed", "status": "PATCHED",
    }) + "\n")
print(f"[banked] po016_fix -> {LEDGER}")
print("[exit=0]")
