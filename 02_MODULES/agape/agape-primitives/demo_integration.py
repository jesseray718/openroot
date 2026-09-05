#!/usr/bin/env python3
"""
demo_integration.py — Shows all three primitives working together.
etaledger + fractallattice + agaperesonance
Local path injection so it works on Termux without broken editable installs.
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root / "etaledger"))
sys.path.insert(0, str(_root / "fractallattice"))
sys.path.insert(0, str(_root / "agaperesonance"))

import asyncio
import time
from etaledger import measure, landauer_cost, BottleneckTracker, capture, merkle_root
from fractallattice import Lattice
from agaperesonance import ResonanceFilter

# ─── Mock LLM (replace with real local model call) ───────────────────────────
async def mock_llm(prompt: str, system: str) -> str:
    """Replace this with your actual LLM call (llama.cpp, Ollama, etc.)"""
    await asyncio.sleep(0.01)
    return f"[{system[:30]}...] Analyzing: {prompt[:100]}..."


async def main():
    print("=" * 60)
    print("AGAPE PRIMITIVES — INTEGRATION DEMO")
    print("etaledger + fractallattice + agaperesonance")
    print("=" * 60)

    tracker = BottleneckTracker()
    start_time = time.time()

    print("\n[1] Launching fractal lattice (depth=2)...")
    lattice = Lattice(call_fn=mock_llm, depth=2)
    query = "What is the most efficient way to cool a building in a hot climate?"
    result = await lattice.run(query)

    elapsed = time.time() - start_time
    print(f"    Theoretical nodes: {lattice.theoretical_nodes()}")
    print(f"    Elapsed: {elapsed:.2f}s")
    print(f"    Trace hash: {lattice.trace_hash()[:32]}...")

    print("\n[2] Running resonance filtering...")
    filt = ResonanceFilter(agape_coefficient=0.9)
    for bot_name in ["translate", "analyze", "feedback", "synthesize", "validate", "amplify"]:
        if bot_name in result:
            filt.add_prediction(
                content=result[bot_name],
                confidence=0.6,
                source=bot_name,
                tags=[bot_name],
            )

    wave = filt.standing_wave()
    if wave:
        print(f"    Standing wave confidence: {wave.confidence:.2%}")
        print(f"    Coherence: {wave.coherence_score:.2%}")
        print(f"    Synergy: {wave.synergy:.2f}x")
        print(f"    Coordination cost: {filt.coordination_cost():.4f}")

    print("\n[3] Measuring thermodynamic efficiency...")
    useful_j = len(str(result))
    human_j = elapsed
    η = measure(useful_j=float(useful_j), human_j=human_j)
    landauer = landauer_cost(useful_j * 8)
    provenance_hash, capture_j = capture(str(result).encode())
    merkle = merkle_root([lattice.trace_hash(), provenance_hash])
    tracker.record("lattice_run", η)

    print(f"    η (efficiency): {η:.1f}")
    print(f"    Landauer cost: {landauer:.6f} (scaled J)")
    print(f"    System bottleneck: {tracker.worst()}")
    print(f"    Provenance Merkle root: {merkle[:32]}...")
    print(f"    capture() returned: {provenance_hash[:16]}...  {capture_j}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
