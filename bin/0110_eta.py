"""η — the only performance language."""

def eta(j_useful: float, j_human: float) -> float:
    if j_human <= 0:
        raise ValueError("J_human must be > 0")
    return j_useful / j_human

def eta_t(j_useful: float, n_reached: int, g_lasting: float,
          j_human: float, t: float) -> float:
    if j_human <= 0 or t <= 0:
        raise ValueError("J_human and t must be > 0")
    return (j_useful * n_reached * g_lasting) / (j_human * t)

def alpha_a(eta_t_prev: float, eta_t_next: float, dt: float) -> float:
    """dη_t/dt — how fast lasting-yield-per-human-joule is rising."""
    if dt <= 0:
        raise ValueError("dt must be > 0")
    return (eta_t_next - eta_t_prev) / dt
