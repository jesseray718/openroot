#!/usr/bin/env python3
import os
from pathlib import Path
root = Path(os.environ.get("OPENROOT_ROOT", "/home/jesse/openroot"))
paths = [
    root / "closed-loop" / "ledger" / "eta-ledger.jsonl",
    root / "ledger" / "joule_ledger.jsonl",
    root / "seed-core" / "ledger" / "eta_ledger.jsonl",
]
ok = False
for p in paths:
    n = 0
    if p.is_file():
        n = sum(1 for line in p.open(encoding="utf-8", errors="replace") if line.strip())
        ok = True
    print(("FOUND" if p.is_file() else "MISS"), n, str(p))
print("PASS" if ok else "WARN no ledger yet")
