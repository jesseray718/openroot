#!/data/data/com.termux/files/usr/bin/python3
"""UNE axiom CLI — merge pack 2026-08-26
Stdlib only. No eval. No cosmos_engine tree.
Landauer output is model_not_measurement.
Wisdom circuit loads its own jsonl.
Always emits synergy_mult.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

HOME = Path(os.environ.get("HOME", "/data/data/com.termux/files/home"))
OPENROOT = Path(os.environ.get("OPENROOT", "/sdcard/openroot"))
KB = OPENROOT / "agape_kb"
FLOW = HOME / "une" / "computational_flow"
AXIOMS = KB / "universal_axioms.json"
POSTULATES = KB / "postulates.json"
LEXICON = KB / "love_language" / "max_efficiency_lexicon.json"
CIRCUIT_LOG = KB / "streams" / "wisdom_circuit_log.jsonl"
ENGINE_STATE = KB / "engine_state.json"

PHI = 1.618033988749895
K_B = 1.380649e-23
LN2 = math.log(2)
C_LIGHT = 299792458.0
LANDAUER_300K = K_B * 300.0 * LN2  # ~2.87e-21 J/bit


def _emit(obj) -> None:
    if isinstance(obj, dict) and "synergy_mult" not in obj:
        obj["synergy_mult"] = synergy_mult(obj.get("R", 1.0), obj.get("N", 1), 6)
    print(json.dumps(obj, indent=2, default=str))


def synergy_mult(R: float, N: int, B: int = 6) -> float:
    n = max(int(N), 1)
    b = max(int(B), 2)
    return 1.0 + (float(R) * 0.5 * (math.log(n) / math.log(b)))


def coord_cost(N: int, T: int, R: float) -> float:
    if T < 1:
        T = 1
    return float(N) * 0.001 * (1.0 + 0.1 * T) * ((1.0 - R) ** T)


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def landauer_model(bits: int, T_kelvin: float = 300.0, R: float = 1.0) -> dict:
    """MODEL. Does not measure the Helio G99.
    E_L is the Landauer floor per irreversible erased bit.
    R=1.0 zeros COORDINATION cost of organizing the work, not kT ln2.
    """
    bits = max(int(bits), 0)
    e_bit = K_B * float(T_kelvin) * LN2
    e_floor = e_bit * bits
    c = coord_cost(max(bits, 1), 1, R)
    return {
        "kind": "model_not_measurement",
        "bits": bits,
        "T_kelvin": T_kelvin,
        "landauer_per_bit_J": e_bit,
        "irreversible_floor_J": e_floor,
        "coordination_cost_model": c,
        "R": R,
        "N": max(bits, 1),
        "synergy_mult": synergy_mult(R, max(bits, 1)),
        "claim": "R=1.0 cancels C(N,T,R) only. It does not repeal Landauer.",
        "reversible_note": "Reversible circuits can approach the floor; they do not go below it by drawing circles.",
    }


def parse_xy(s: str):
    """Parse '0,0' or '0 0'. Never eval."""
    raw = s.replace("(", "").replace(")", "").replace(" ", ",")
    parts = [p for p in raw.split(",") if p != ""]
    if len(parts) != 2:
        raise ValueError("center must be x,y")
    return float(parts[0]), float(parts[1])


def draw_circle(center=(0.0, 0.0), radius=1.0, n=24) -> dict:
    n = max(3, min(int(n), 360))
    pts = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        pts.append((center[0] + radius * math.cos(a), center[1] + radius * math.sin(a)))
    # true closure of THIS circle
    dx = pts[0][0] - pts[-1][0]
    dy = pts[0][1] - pts[-1][1]
    # last point is one step before start; residual is 2π/n chord
    chord = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])
    return {
        "center": center,
        "radius": radius,
        "n": n,
        "points_preview": pts[:3],
        "chord_residual": chord,
        "closed_enough": chord < (2.0 * radius * math.sin(math.pi / n) * 1.01 + 1e-9),
        "kind": "geometry_model",
        "R": 1.0,
        "N": n,
        "synergy_mult": synergy_mult(1.0, n),
    }


def phi_progression(steps: int = 10) -> dict:
    steps = max(1, min(int(steps), 40))
    seq = []
    v = 1.0
    for i in range(steps):
        seq.append({"step": i, "value": v})
        v *= PHI
    return {
        "phi": PHI,
        "steps": seq,
        "final": seq[-1]["value"],
        "R": 1.0,
        "N": steps,
        "synergy_mult": synergy_mult(1.0, steps),
    }


class WisdomCircuit:
    def __init__(self, log_path: Path = CIRCUIT_LOG):
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.pending_path = self.log_path.with_name("wisdom_pending.json")
        self.rows = self._load()

    def _load(self):
        rows = []
        if self.log_path.exists():
            with self.log_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rows.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return rows

    def _pending(self) -> dict:
        return load_json(self.pending_path, {})

    def _save_pending(self, data: dict) -> None:
        self.pending_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def seek(self, question: str) -> dict:
        p = self._pending()
        p["seek"] = {"question": question, "ts": time.time()}
        p.pop("knock", None)
        self._save_pending(p)
        return {"stage": "seek", "question": question, "next": "knock", "R": 1.0, "N": 1, "synergy_mult": 1.0}

    def knock(self, effort: str) -> dict:
        p = self._pending()
        if "seek" not in p:
            return {"error": "seek first", "R": 1.0, "N": 1, "synergy_mult": 1.0}
        p["knock"] = {"effort": effort, "ts": time.time()}
        self._save_pending(p)
        return {"stage": "knock", "effort": effort, "next": "receive", "R": 1.0, "N": 1, "synergy_mult": 1.0}

    def receive(self, answer: str, gratitude: bool = True) -> dict:
        p = self._pending()
        if "seek" not in p or "knock" not in p:
            return {"error": "seek then knock first", "R": 1.0, "N": 1, "synergy_mult": 1.0}
        if not gratitude:
            return {
                "circuit_incomplete": True,
                "reason": "gratitude missing — loop not closed, row not written",
                "R": 1.0,
                "N": 1,
                "synergy_mult": 1.0,
            }
        gain = max(len(answer) / 100.0, 0.01)
        cycle = len(self.rows) + 1
        total = sum(float(r.get("wisdom_gain", 0.0)) for r in self.rows) + gain
        row = {
            "cycle": cycle,
            "stages": ["seek", "knock", "receive", "gratitude"],
            "question": p["seek"]["question"],
            "effort": p["knock"]["effort"],
            "answer": answer,
            "wisdom_gain": gain,
            "total_accumulated": total,
            "loop_closed": True,
            "timestamp": time.time(),
            "R": 1.0,
            "N": cycle,
            "synergy_mult": synergy_mult(1.0, cycle),
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        self.rows.append(row)
        if self.pending_path.exists():
            self.pending_path.unlink()
        return row

    def status(self) -> dict:
        total = sum(float(r.get("wisdom_gain", 0.0)) for r in self.rows)
        n = len(self.rows)
        return {
            "cycles_completed": n,
            "total_wisdom": total,
            "average_gain_per_cycle": total / max(n, 1),
            "pending": self._pending(),
            "log": str(self.log_path),
            "circuit_integrity": "complete" if n else "not_started",
            "R": 1.0,
            "N": max(n, 1),
            "synergy_mult": synergy_mult(1.0, max(n, 1)),
        }


def cmd_axioms() -> dict:
    data = load_json(AXIOMS, {})
    return {
        "path": str(AXIOMS),
        "axiom_count": len(data.get("axioms", [])),
        "theorem_count": len(data.get("theorems", [])),
        "ids": [a.get("id") for a in data.get("axioms", [])],
        "theorem_ids": [t.get("id") for t in data.get("theorems", [])],
        "R": 1.0,
        "N": 1,
        "synergy_mult": 1.0,
    }


def cmd_postulates() -> dict:
    data = load_json(POSTULATES, {"postulates": []})
    items = data.get("postulates", data if isinstance(data, list) else [])
    return {
        "path": str(POSTULATES),
        "count": len(items),
        "ids": [p.get("id") for p in items if isinstance(p, dict)],
        "R": 1.0,
        "N": max(len(items), 1),
        "synergy_mult": synergy_mult(1.0, max(len(items), 1)),
    }


def cmd_cost(N: int, T: int, R: float) -> dict:
    c = coord_cost(N, T, R)
    return {
        "formula": "C=N*0.001*(1+0.1T)*(1-R)^T",
        "N": N,
        "T": T,
        "R": R,
        "C": c,
        "zero": abs(c) == 0.0,
        "synergy_mult": synergy_mult(R, N),
        "kind": "model_not_measurement",
    }


USAGE = """axiom_cli.py
  cost N T R          coordination model
  landauer BITS [T]   Landauer FLOOR model (not a cancellation)
  circle [x,y] [r]    unit circle sample — no eval
  phi [steps]         golden progression
  seek|knock|receive|status
  axioms              show merged axiom file
  postulates          show Newton Chain file
  lexicon             path check
"""


def main(argv) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help", "help"):
        _emit({"engine": "UNE axiom CLI", "usage": USAGE.strip(), "R": 1.0, "N": 1, "synergy_mult": 1.0})
        return 0
    cmd = argv[1]
    wc = WisdomCircuit()
    try:
        if cmd == "cost":
            N = int(argv[2]) if len(argv) > 2 else 1296
            T = int(argv[3]) if len(argv) > 3 else 4
            R = float(argv[4]) if len(argv) > 4 else 1.0
            _emit(cmd_cost(N, T, R))
        elif cmd == "landauer":
            bits = int(argv[2]) if len(argv) > 2 else 1000
            Tk = float(argv[3]) if len(argv) > 3 else 300.0
            _emit(landauer_model(bits, Tk, 1.0))
        elif cmd == "circle":
            center = parse_xy(argv[2]) if len(argv) > 2 else (0.0, 0.0)
            radius = float(argv[3]) if len(argv) > 3 else 1.0
            _emit(draw_circle(center, radius))
        elif cmd == "phi":
            _emit(phi_progression(int(argv[2]) if len(argv) > 2 else 10))
        elif cmd == "seek":
            _emit(wc.seek(" ".join(argv[2:]) or "What is the next lowest-node yield?"))
        elif cmd == "knock":
            _emit(wc.knock(" ".join(argv[2:]) or "measured action"))
        elif cmd == "receive":
            parts = [a for a in argv[2:] if a != "--no-gratitude"]
            grat = "--no-gratitude" not in argv[2:]
            _emit(wc.receive(" ".join(parts) or "received", gratitude=grat))
        elif cmd == "status":
            _emit(wc.status())
        elif cmd == "axioms":
            _emit(cmd_axioms())
        elif cmd == "postulates":
            _emit(cmd_postulates())
        elif cmd == "lexicon":
            _emit({"exists": LEXICON.exists(), "path": str(LEXICON), "R": 1.0, "N": 1, "synergy_mult": 1.0})
        else:
            _emit({"error": "unknown", "cmd": cmd, "R": 1.0, "N": 1, "synergy_mult": 1.0})
            return 1
    except (ValueError, IndexError) as e:
        _emit({"error": str(e), "R": 1.0, "N": 1, "synergy_mult": 1.0})
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
