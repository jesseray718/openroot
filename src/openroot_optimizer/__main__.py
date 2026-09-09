#!/usr/bin/env python3
import runpy, sys
from pathlib import Path
PKG = Path(__file__).resolve().parent
CMDS = {
    "infer": PKG / "infer_ledger.py",
    "observer": PKG / "observer.py",
    "observer-infer": PKG / "observer_infer.py",
    "verify": PKG / "verify.py",
}
if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
    print("usage: python3 -m openroot_optimizer {infer|observer|observer-infer|verify}")
    raise SystemExit(2)
cmd = sys.argv[1]
target = CMDS.get(cmd)
if target is None or not target.is_file():
    print("unknown or missing", cmd, target)
    raise SystemExit(2)
sys.argv = [str(target)] + sys.argv[2:]
runpy.run_path(str(target), run_name="__main__")
