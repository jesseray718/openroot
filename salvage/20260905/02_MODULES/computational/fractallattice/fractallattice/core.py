"""
fractallattice.core — Six-nanobot recursive processing lattice.
"""
import asyncio
import json
import hashlib
from typing import Callable, Dict, List, Optional, Any

NANOBOT_PROMPTS = {
    "translate": {
        "task": "Decompose the following into its fundamental components. Break it down into parts, inputs, outputs, and dependencies.",
        "role": "You are a decomposition engine. Return structured components only.",
    },
    "analyze": {
        "task": "Analyze the structure and key relationships in the following. Identify patterns, tensions, and leverage points.",
        "role": "You are an analyst. Identify patterns, relationships, and structural insights.",
    },
    "feedback": {
        "task": "Evaluate the following for completeness and coherence. Flag gaps, redundancies, and circular logic.",
        "role": "You are a feedback loop monitor. Detect gaps, redundancies, and circular reasoning.",
    },
    "synthesize": {
        "task": "Synthesize the following perspectives into one unified, coherent whole. Resolve contradictions through integration.",
        "role": "You are a synthesizer. Merge multiple perspectives into one coherent whole.",
    },
    "validate": {
        "task": "Validate that the following synthesis faithfully represents the original source. Flag any distortions or losses.",
        "role": "You are a validator. Check fidelity between source and output. Flag distortions honestly.",
    },
    "amplify": {
        "task": "Amplify the following insight. Sharpen it, deepen it, make it actionable. Do not add information — reveal what is implicit.",
        "role": "You are an amplifier. Enhance clarity, depth, and impact without distortion.",
    },
}
NANOBOT_NAMES = list(NANOBOT_PROMPTS.keys())

async def default_merge(results: List[Dict]) -> Dict:
    merged = {}
    for r in results:
        for k, v in r.items():
            if k in merged:
                if isinstance(merged[k], str) and isinstance(v, str):
                    merged[k] = merged[k] + "\n---\n" + v
                else:
                    merged[k] = str(merged[k]) + "\n---\n" + str(v)
            else:
                merged[k] = v
    return merged

async def _call_nanobot(name: str, context: Dict, call_fn: Callable, extra_system: str = "") -> Dict:
    if name not in NANOBOT_PROMPTS:
        return {name: f"[unknown nanobot: {name}]"}
    config = NANOBOT_PROMPTS[name]
    system = config["role"]
    if extra_system:
        system = system + "\n" + extra_system
    context_str = json.dumps({k: v for k, v in context.items()}, default=str, indent=2)
    prompt = config["task"] + "\n\n" + context_str
    result = await call_fn(prompt=prompt, system=system)
    return {name: result}

async def _fractal_level(
    context: Dict, level: int, max_depth: int, call_fn: Callable, merge_fn: Callable,
    extra_system: str = "", active_only: bool = True, bottleneck: Optional[str] = None,
) -> Dict:
    if level >= max_depth:
        return context

    # Guard: only treat bottleneck as a nanobot if it is one of the six
    if active_only and bottleneck and bottleneck in NANOBOT_NAMES:
        bots_to_run = [bottleneck] + [n for n in NANOBOT_NAMES if n != bottleneck][:2]
    else:
        bots_to_run = NANOBOT_NAMES

    results = await asyncio.gather(*[
        _call_nanobot(name, context.copy(), call_fn, extra_system) for name in bots_to_run
    ])
    merged = await merge_fn(results)
    merged["_level"] = level
    merged["_bots_run"] = bots_to_run
    return await _fractal_level(
        merged, level + 1, max_depth, call_fn, merge_fn, extra_system, active_only, bottleneck,
    )

class Lattice:
    def __init__(
        self, call_fn: Callable, depth: int = 3, merge_fn: Callable = default_merge,
        extra_system: str = "", sparse: bool = False,
    ):
        self.call_fn = call_fn
        self.depth = depth
        self.merge_fn = merge_fn
        self.extra_system = extra_system
        self.sparse = sparse
        self._trace: List[Dict] = []

    async def run(self, query: str, bottleneck: Optional[str] = None) -> Dict:
        initial_context = {"input": query}
        result = await _fractal_level(
            context=initial_context, level=0, max_depth=self.depth,
            call_fn=self.call_fn, merge_fn=self.merge_fn, extra_system=self.extra_system,
            active_only=self.sparse, bottleneck=bottleneck,
        )
        self._trace.append(result)
        return result

    def theoretical_nodes(self) -> int:
        return sum(6 ** (i + 1) for i in range(self.depth))

    def trace_hash(self) -> str:
        blob = json.dumps(self._trace, default=str, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()

    @property
    def trace(self) -> List[Dict]:
        return self._trace
