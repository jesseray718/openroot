# Minimal CrewAI-style example using the fractal lattice roles
# (drop into any local CrewAI project that already talks to Ollama)
from fractallattice import Lattice
import asyncio

async def run_lattice_crew(query: str):
    async def call(prompt, system):
        # replace with your existing Ollama / LLM call
        return f"[{system[:30]}] {prompt[:80]}"
    lattice = Lattice(call_fn=call, depth=2)
    return await lattice.run(query)

if __name__ == "__main__":
    print(asyncio.run(run_lattice_crew("Your multi-step local task here")))
