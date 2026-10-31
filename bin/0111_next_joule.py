"""Next-joule score — picks the highest-η act."""

def score(delta_ju: float, delta_n: int, delta_g_last: float,
          delta_floor_min: float, synergy_mult: float,
          works_offline: bool, j_h: float, t: float,
          c_tax: float = 0.0, rework: float = 1.0) -> float:
    if j_h <= 0 or t <= 0:
        raise ValueError("J_h and t must be > 0")
    denom = j_h * t * (1 + c_tax) * rework
    if denom == 0:
        return 0.0
    return (delta_ju * delta_n * delta_g_last *
            delta_floor_min * synergy_mult *
            (1 if works_offline else 0.5)) / denom

def hard_reject(r: float, surplus_parked_high: bool,
                rederiving: bool, no_experiment: bool) -> str | None:
    if r < 1.0:
        return f"REJECT: R={r} < 1.0"
    if surplus_parked_high:
        return "REJECT: surplus parked in high node"
    if rederiving:
        return "REJECT: re-deriving closed postulate"
    if no_experiment:
        return "REJECT: theory without Experiment/Produce"
    return None
