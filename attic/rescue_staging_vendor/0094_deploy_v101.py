#!/usr/bin/env python3
"""OpenRoot Kernel v1.0.1 — Executable Computation + CI + Profile + une."""
import os, sys, subprocess, pathlib, shutil

HOME = pathlib.Path(os.environ.get('HOME', '/tmp'))
SRC = HOME / 'src'
KDIR = SRC / 'openroot-kernel'

FILES = {
'kernel/eta.py': '''"""η — the only performance language."""

def eta(j_useful: float, j_human: float) -> float:
    if j_human <= 0:
        raise ValueError("J_human must be > 0")
    return j_useful / j_human

def eta_t(j_useful: float, n_reached: int, g_lasting: float,
          j_human: float, t: float) -> float:
    if j_human <= 0 or t <= 0:
        raise ValueError("J_human and t must be > 0")
    return (j_useful * n_reached * g_lasting) / (j_human * t)

def alpha_a(eta_t_prev: float, eta_t_next: float, dt: float) -> float:
    """dη_t/dt — how fast lasting-yield-per-human-joule is rising."""
    if dt <= 0:
        raise ValueError("dt must be > 0")
    return (eta_t_next - eta_t_prev) / dt
''',

'kernel/coordination.py': '''"""C(N,T,R) — coordination cost. R=1.0 ⇒ C=0."""

def coord_cost(n: int, t: int, r: float) -> float:
    if r < 0.0 or r > 1.0:
        raise ValueError(f"R must be in [0,1], got {r}")
    return n * 0.001 * (1 + 0.1 * t) * ((1 - r) ** t)

def resonance_holds(c: float, threshold: float = 1e-6) -> bool:
    return c < threshold
''',

'kernel/synergy.py': '''"""S — synergy multiplier."""
import math

def synergy(n: int, r: float, b: int = 6) -> float:
    if n < 1:
        raise ValueError("N must be >= 1")
    return 1 + r * 0.5 * math.log(n, b)
''',

'kernel/next_joule.py': '''"""Next-joule score — picks the highest-η act."""

def score(delta_ju: float, delta_n: int, delta_g_last: float,
          delta_floor_min: float, synergy_mult: float,
          works_offline: bool, j_h: float, t: float,
          c_tax: float = 0.0, rework: float = 1.0) -> float:
    if j_h <= 0 or t <= 0:
        raise ValueError("J_h and t must be > 0")
    denom = j_h * t * (1 + c_tax) * rework
    if denom == 0:
        return 0.0
    return (delta_ju * delta_n * delta_g_last *
            delta_floor_min * synergy_mult *
            (1 if works_offline else 0.5)) / denom

def hard_reject(r: float, surplus_parked_high: bool,
                rederiving: bool, no_experiment: bool) -> str | None:
    if r < 1.0:
        return f"REJECT: R={r} < 1.0"
    if surplus_parked_high:
        return "REJECT: surplus parked in high node"
    if rederiving:
        return "REJECT: re-deriving closed postulate"
    if no_experiment:
        return "REJECT: theory without Experiment/Produce"
    return None
''',

'kernel/postulates.py': '''"""Newton Chain — verified relations become postulates."""

POSTULATES: dict[str, dict] = {
    "p001_c_zero": {
        "id": "P001",
        "statement": "At R=1.0, C=0 for all N, T>=1",
        "verified": True,
        "falsifier": "Measure C > 0 at R=1.0",
    },
    "p002_synergy": {
        "id": "P002",
        "statement": "S = 1 + R*0.5*log_B(N), base-6 depth-4 N=1296 gives S=3.0",
        "verified": True,
        "falsifier": "Compute S != 3.0 at N=1296, R=1.0, B=6",
    },
    "p003_eta_bound": {
        "id": "P003",
        "statement": "H is an alias of eta. Do not compute them separately.",
        "verified": True,
        "falsifier": "Code path computes H independently of eta",
    },
}

def lookup(key: str) -> dict | None:
    return POSTULATES.get(key)

def all_postulates() -> list[dict]:
    return list(POSTULATES.values())

def count() -> int:
    return len(POSTULATES)
''',

'kernel/__init__.py': '''from .eta import eta, eta_t, alpha_a
from .coordination import coord_cost, resonance_holds
from .synergy import synergy
from .next_joule import score, hard_reject
from .postulates import lookup, all_postulates, count

__all__ = [
    "eta", "eta_t", "alpha_a",
    "coord_cost", "resonance_holds",
    "synergy",
    "score", "hard_reject",
    "lookup", "all_postulates", "count",
]
''',

'kernel/selftest.py': '''#!/usr/bin/env python3
"""OpenRoot Kernel Self-Test v1.0.1 — all modules."""
import math, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import kernel
from kernel.eta import eta, eta_t, alpha_a
from kernel.coordination import coord_cost, resonance_holds
from kernel.synergy import synergy
from kernel.next_joule import score, hard_reject
from kernel.postulates import POSTULATES, count
import pathlib

def test_eta():
    assert eta(1000, 100) == 10.0
    assert eta_t(1000, 1296, 1.0, 100, 1.0) == 12960.0
    assert abs(alpha_a(10.0, 20.0, 1.0) - 10.0) < 1e-9
    print(f"OK  eta, eta_t, alpha_a")

def test_coord():
    c = coord_cost(1296, 1, 1.0)
    assert c == 0.0, f"C={c}"
    assert resonance_holds(c)
    c2 = coord_cost(1296, 1, 0.9)
    assert c2 > 0
    assert not resonance_holds(c2, threshold=1.0)
    print(f"OK  C=0 at R=1.0, C={c2:.4f} at R=0.9")

def test_synergy():
    s = synergy(1296, 1.0, 6)
    assert abs(s - 3.0) < 0.01, f"S={s}"
    print(f"OK  synergy_mult={s:.1f}")

def test_next_joule():
    sc = score(100, 10, 2.0, 1.0, 3.0, True, 10, 1.0)
    assert sc > 0
    rej = hard_reject(0.9, False, False, False)
    assert rej is not None and "REJECT" in rej
    ok = hard_reject(1.0, False, False, False)
    assert ok is None
    print(f"OK  score={sc:.1f}, reject logic")

def test_postulates():
    n = count()
    assert n >= 3
    p = POSTULATES["p001_c_zero"]
    assert p["verified"]
    print(f"OK  {n} postulates in Newton Chain")

def main():
    print("=== OpenRoot Kernel v1.0.1 Self-Test ===")
    test_eta()
    test_coord()
    test_synergy()
    test_next_joule()
    test_postulates()
    print("=== kernel.selftest OK ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
''',

'.github/workflows/selftest.yml': '''name: selftest
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python3 -m kernel.selftest
''',

'scripts/push_with_gh.sh': '''#!/bin/bash
set -euo pipefail
REPO="${1:-jesseray718/openroot}"
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR"
python3 -m kernel.selftest || { echo "ABORT: selftest failed"; exit 1; }
git add .
git diff --cached --quiet || git commit -m "kernel: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git push origin main
echo "Pushed to $REPO"
''',
}

def write():
    for rel, content in FILES.items():
        p = KDIR / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content.strip() + "\n")
        if rel.endswith('.sh'):
            p.chmod(0o755)
    print(f"  wrote {len(FILES)} files")

def git(*args):
    subprocess.run(["git"] + list(args), cwd=KDIR, check=True,
                   capture_output=True, text=True)

def cmd(*args, cwd=None):
    subprocess.run(list(args), cwd=cwd, check=True)

def main():
    print("OpenRoot Kernel v1.0.1 — executable computation layer")
    print("-" * 50)

    # 1. Write modules
    write()

    # 2. Selftest
    r = subprocess.run(["python3", "-m", "kernel.selftest"],
                       cwd=KDIR, capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(1)

    # 3. Commit + push openroot
    git("add", ".")
    git("commit", "-m", "kernel v1.0.1: eta, coord, synergy, next_joule, postulates, CI")
    git("push", "origin", "main")
    print("  pushed openroot")

    # 4. Profile fix
    prof = SRC / "jesseray718"
    if prof.exists():
        (prof / "README.md").write_text((KDIR / "PROFILE_README.md").read_text())
        subprocess.run(["git", "add", "."], cwd=prof, check=True)
        subprocess.run(["git", "diff", "--cached", "--quiet"],
                       cwd=prof, capture_output=True, check=False)
        r2 = subprocess.run(["git", "diff", "--cached", "--quiet"],
                           cwd=prof, capture_output=True, check=False)
        if r2.returncode != 0:
            subprocess.run(["git", "commit", "-m", "profile README"],
                           cwd=prof, check=True)
            subprocess.run(["git", "push"], cwd=prof, check=True)
            print("  pushed profile")
        else:
            print("  profile already current")

    # 5. une install
    une = SRC / "une"
    if une.exists() and (une / ".git").exists():
        for item in (KDIR).iterdir():
            dst = une / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)
        subprocess.run(["git", "add", "."], cwd=une, check=True)
        r3 = subprocess.run(["git", "diff", "--cached", "--quiet"],
                            cwd=une, capture_output=True, check=False)
        if r3.returncode != 0:
            subprocess.run(["git", "commit", "-m", "kernel v1.0.1 installed"],
                           cwd=une, check=True)
            subprocess.run(["git", "push"], cwd=une, check=True)
            print("  pushed une")
        else:
            print("  une already current")
    else:
        print("  une not cloned — skip (run: gh repo clone jesseray718/une ~/src/une)")

    print("-" * 50)
    print("DONE. Copilot imports kernel.eta, kernel.coordination,")
    print("kernel.synergy, kernel.next_joule, kernel.postulates.")
    print("CI runs selftest on every push. No drift.")

if __name__ == "__main__":
    main()
