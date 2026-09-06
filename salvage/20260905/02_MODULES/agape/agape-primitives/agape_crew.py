#!/usr/bin/env python3
"""
agape_crew.py — CrewAI-style hierarchical orchestration using only Agape Primitives.
Zero new dependencies. Runs on A15/Termux.
"""
import sys
import asyncio
import time
import json
from pathlib import Path
from typing import Callable, Optional

_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root / "etaledger"))
sys.path.insert(0, str(_root / "fractallattice"))
sys.path.insert(0, str(_root / "agaperesonance"))

from etaledger import measure, landauer_cost, capture, merkle_root, BottleneckTracker
from fractallattice import Lattice, NANOBOT_NAMES
from agaperesonance import ResonanceFilter

async def ollama_call(prompt: str, system: str, model: str = "llama3.2:1b") -> str:
    import urllib.request
    body = json.dumps({
        "model": model, "prompt": prompt, "system": system,
        "stream": False, "options": {"num_predict": 192, "temperature": 0.25},
    }).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate", data=body,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
            return (data.get("response") or "").strip() or "[empty]"
    except Exception as e:
        return f"[ollama unavailable: {type(e).__name__}]"

async def mock_call(prompt: str, system: str) -> str:
    await asyncio.sleep(0.008)
    return f"[{system[:36]}] → {prompt[:110]}..."

async def resolve_call_fn():
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=1.5)
        return ollama_call, "ollama"
    except Exception:
        return mock_call, "mock"

class AgapeCrew:
    def __init__(self, call_fn: Callable, depth: int = 2, agape_r: float = 0.9):
        self.call_fn = call_fn
        self.depth = depth
        self.agape_r = agape_r
        self.tracker = BottleneckTracker()
        self.lattice = Lattice(call_fn=call_fn, depth=depth, sparse=True)
        self.last_result = None
        self.last_wave = None
        self.last_η = 0.0
        self.last_merkle = ""

    async def kickoff(self, query: str) -> dict:
        t0 = time.time()

        print("  [manager] first pass — discovering structure ...")
        result = await self.lattice.run(query)          # full set, no bottleneck
        elapsed1 = time.time() - t0

        useful = float(len(str(result)))
        η1 = measure(useful_j=useful, human_j=max(elapsed1, 1e-6))
        self.tracker.record("first_pass", η1)

        # Pick a real nanobot to deepen (simple heuristic: longest output = most work)
        candidates = {k: len(str(v)) for k, v in result.items() if k in NANOBOT_NAMES}
        if candidates:
            bottleneck = max(candidates, key=candidates.get)
        else:
            bottleneck = None
        print(f"  [manager] chosen nanobot to deepen → {bottleneck}")

        print(f"  [manager] sparse deepen on {bottleneck} ...")
        t1 = time.time()
        result2 = await self.lattice.run(query, bottleneck=bottleneck)
        elapsed2 = time.time() - t1

        print("  [manager] resonance filter (standing wave) ...")
        filt = ResonanceFilter(agape_coefficient=self.agape_r)
        for name, content in result2.items():
            if name.startswith("_") or name not in NANOBOT_NAMES:
                continue
            filt.add_prediction(
                content=str(content)[:900], confidence=0.62,
                source=name, tags=[name],
            )

        wave = filt.standing_wave()
        total_elapsed = time.time() - t0
        useful_final = float(len(str(wave.content)) if wave else len(str(result2)))
        η = measure(useful_j=useful_final, human_j=max(total_elapsed, 1e-6))
        self.tracker.record("crew_kickoff", η)

        prov_hash, _ = capture(str(result2).encode())
        merkle = merkle_root([self.lattice.trace_hash(), prov_hash])

        self.last_result = result2
        self.last_wave = wave
        self.last_η = η
        self.last_merkle = merkle

        return {
            "standing_wave": wave.content if wave else None,
            "confidence": wave.confidence if wave else 0.0,
            "coherence": wave.coherence_score if wave else 0.0,
            "synergy": wave.synergy if wave else 1.0,
            "η": η,
            "bottleneck": bottleneck,
            "theoretical_nodes": self.lattice.theoretical_nodes(),
            "elapsed": total_elapsed,
            "merkle": merkle,
            "trace_hash": self.lattice.trace_hash(),
            "coordination_cost": filt.coordination_cost(),
        }

async def main():
    print("=" * 66)
    print("AGAPE CREW — hierarchical multi-agent (CrewAI mapping, zero deps)")
    print("=" * 66)

    call_fn, backend = await resolve_call_fn()
    print(f"  backend: {backend}")

    crew = AgapeCrew(call_fn=call_fn, depth=2, agape_r=0.9)

    query = (
        "Design the most joule-efficient passive cooling + thermal-mass system "
        "for a small geodesic structure in a hot humid climate (Missouri summer). "
        "Prioritize open-cell aerocement, night-sky radiation, and zero external power. "
        "Return concrete, buildable steps and expected η gains."
    )

    print("\n[kickoff] query loaded")
    out = await crew.kickoff(query)

    print("\n" + "-" * 66)
    print("STANDING WAVE (manager consensus)")
    print("-" * 66)
    if out["standing_wave"]:
        print(out["standing_wave"][:700])
        if len(out["standing_wave"]) > 700:
            print("... [truncated]")
    else:
        print("(no standing wave)")

    print("\n" + "-" * 66)
    print("THERMODYNAMIC + PROVENANCE LEDGER")
    print("-" * 66)
    print(f"  η (efficiency)       : {out['η']:.1f}")
    print(f"  bottleneck           : {out['bottleneck']}")
    print(f"  theoretical nodes    : {out['theoretical_nodes']}")
    print(f"  wall time            : {out['elapsed']:.3f}s")
    print(f"  confidence           : {out['confidence']:.1%}")
    print(f"  coherence            : {out['coherence']:.1%}")
    print(f"  synergy              : {out['synergy']:.2f}x")
    print(f"  coordination cost    : {out['coordination_cost']:.4f}")
    print(f"  merkle root          : {out['merkle'][:40]}...")
    print(f"  lattice trace        : {out['trace_hash'][:40]}...")
    print(f"  backend              : {backend}")

    print("\n" + "=" * 66)
    print("CREW COMPLETE — structure held, joules accounted, standing wave recorded")
    print("=" * 66)

if __name__ == "__main__":
    asyncio.run(main())
