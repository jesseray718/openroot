#!/usr/bin/env python3
"""
real_llm_runner.py — Agape Primitives + real (or mock) LLM.
Tries Ollama first. Falls back to a deterministic mock so the pipeline never dies.
"""
import sys
import asyncio
import time
import json
from pathlib import Path

_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root / "etaledger"))
sys.path.insert(0, str(_root / "fractallattice"))
sys.path.insert(0, str(_root / "agaperesonance"))

from etaledger import measure, landauer_cost, capture, merkle_root, BottleneckTracker
from fractallattice import Lattice
from agaperesonance import ResonanceFilter

# ── LLM backend ─────────────────────────────────────────────────────────────
async def ollama_call(prompt: str, system: str, model: str = "llama3.2:1b") -> str:
    """Minimal Ollama HTTP call. No extra deps."""
    import urllib.request
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"num_predict": 256, "temperature": 0.3},
    }).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode())
            return data.get("response", "").strip() or "[empty]"
    except Exception as e:
        return f"[ollama error: {type(e).__name__}]"

async def mock_call(prompt: str, system: str) -> str:
    await asyncio.sleep(0.005)
    return f"[{system[:40]}] → {prompt[:120]}..."

async def get_call_fn():
    """Return the best available call_fn and a label."""
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2)
        print("  backend: Ollama (local)")
        return ollama_call, "ollama"
    except Exception:
        print("  backend: mock (start Ollama for real inference)")
        return mock_call, "mock"

# ── main ────────────────────────────────────────────────────────────────────
async def main():
    print("=" * 64)
    print("AGAPE PRIMITIVES — REAL LLM RUNNER")
    print("=" * 64)

    call_fn, backend = await get_call_fn()
    tracker = BottleneckTracker()
    t0 = time.time()

    print("\n[1] fractal lattice (depth=2) ...")
    lattice = Lattice(call_fn=call_fn, depth=2)
    query = "What is the most joule-efficient way to cool a small building in a hot, humid climate using only passive and low-tech methods?"
    result = await lattice.run(query)
    elapsed = time.time() - t0

    print(f"    theoretical nodes : {lattice.theoretical_nodes()}")
    print(f"    wall time         : {elapsed:.3f}s")
    print(f"    trace hash        : {lattice.trace_hash()[:32]}...")

    print("\n[2] resonance filter ...")
    filt = ResonanceFilter(agape_coefficient=0.9)
    for name in ["translate", "analyze", "feedback", "synthesize", "validate", "amplify"]:
        if name in result:
            filt.add_prediction(content=str(result[name])[:800], confidence=0.65, source=name, tags=[name])

    wave = filt.standing_wave()
    if wave:
        print(f"    standing wave     : {wave.content[:120]}...")
        print(f"    confidence        : {wave.confidence:.1%}")
        print(f"    coherence         : {wave.coherence_score:.1%}")
        print(f"    synergy           : {wave.synergy:.2f}x")
        print(f"    coordination cost : {filt.coordination_cost():.4f}")

    print("\n[3] thermodynamic ledger ...")
    useful = float(len(str(result)))
    η = measure(useful_j=useful, human_j=max(elapsed, 1e-6))
    landauer = landauer_cost(int(useful * 8))
    prov_hash, _ = capture(str(result).encode())
    root = merkle_root([lattice.trace_hash(), prov_hash])
    tracker.record("lattice_run", η)

    print(f"    η                 : {η:.1f}")
    print(f"    Landauer (scaled) : {landauer:.6f}")
    print(f"    bottleneck        : {tracker.worst()}")
    print(f"    merkle root       : {root[:32]}...")
    print(f"    backend used      : {backend}")

    print("\n" + "=" * 64)
    print("COMPLETE — provenance live, standing wave recorded")
    print("=" * 64)

if __name__ == "__main__":
    asyncio.run(main())
