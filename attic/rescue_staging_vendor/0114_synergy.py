"""S — synergy multiplier."""
import math

def synergy(n: int, r: float, b: int = 6) -> float:
    if n < 1:
        raise ValueError("N must be >= 1")
    return 1 + r * 0.5 * math.log(n, b)
