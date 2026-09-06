# fractallattice

Six nanobots. Fractal depth. Small models, big structure.

```python
from fractallattice import Lattice
import asyncio

async def my_llm(prompt: str, system: str) -> str:
    # any local or remote model
    ...

lattice = Lattice(call_fn=my_llm, depth=2)
result = asyncio.run(lattice.run("Design a passive solar system"))
print(lattice.theoretical_nodes())   # 42 at depth 2
print(lattice.trace_hash())
```

Nanobots: translate → analyze → feedback → synthesize → validate → amplify.

License: GPL-3.0
