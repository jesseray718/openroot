#!/usr/bin/env python3
"""Turn lattice ACRE output into a single-node rewrite prompt for local coding LLM."""
import json, sys

def make_prompt(acre: dict, bottleneck_code: str = "") -> str:
    η = acre.get("η", 0)
    claim = acre.get("claim", "")
    axioms = acre.get("axioms_applied", [])
    target = acre.get("target", "unknown")
    order = acre.get("order_reached", 0)

    prompt = f"""YOU ARE THE OPENROOT CODING ACTUATOR.
η LAW ONLY. NO FILLER.

CURRENT STATE
- target: {target}
- η: {η:.6f}
- order_reached: {order}
- ACRE claim: {claim}
- axioms that already fired: {', '.join(axioms)}

TASK
The lattice identified this node as the bottleneck (lowest η).
Rewrite ONLY the bottleneck so that:
1. useful_joules rise
2. human_joules fall
3. the new code is fractal-invariant (can be raised to order n+1 without rewrite)
4. Agape: the rewrite must be more useful to the next system than the current version
5. Synergetics: do more with less — reject any solution where Input_J > Output_J

OUTPUT FORMAT (STRICT)
OPTIMIZED_CODE:
<code block only>

ENERGY_DELTA:
η_new_estimate: <float>
human_joules_delta: <float>
useful_joules_delta: <float>

ACRE_NOTE:
one sentence why this raise increases residual useful work

BOTTLENECK CODE (rewrite this):
{bottleneck_code[:3000] if bottleneck_code else "(no source supplied — rewrite the highest-cost function in core_atomic.py)"}
"""
    return prompt

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lattice_to_llm.py <acre.json> [bottleneck.py]")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        acre = json.load(f)
    # accept either full lattice output or the inner "acre" object
    if "acre" in acre:
        acre = acre["acre"]
    code = ""
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            code = f.read()
    print(make_prompt(acre, code))
