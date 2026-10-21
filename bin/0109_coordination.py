"""C(N,T,R) — coordination cost. R=1.0 ⇒ C=0."""

def coord_cost(n: int, t: int, r: float) -> float:
    if r < 0.0 or r > 1.0:
        raise ValueError(f"R must be in [0,1], got {r}")
    return n * 0.001 * (1 + 0.1 * t) * ((1 - r) ** t)

def resonance_holds(c: float, threshold: float = 1e-6) -> bool:
    return c < threshold
