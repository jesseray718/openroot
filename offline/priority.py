"""Quadratic-need prioritization engine.

Score formula:  score = (urgency ** 2) * impact * w_u * w_i

This emphasises urgent needs quadratically – small increases in urgency
produce large increases in score, ensuring the highest-need work rises
to the top of the queue.  Weights are configurable per deployment.
"""
import math
from typing import Any, Dict, Iterable, List


class PriorityScorer:
    """Scores and ranks work items by quadratic-urgency heuristic.

    Parameters
    ----------
    weight_urgency : float
        Multiplicative weight on the urgency dimension (default 1.0).
    weight_impact : float
        Multiplicative weight on the impact dimension (default 1.0).
    """

    def __init__(self, weight_urgency: float = 1.0, weight_impact: float = 1.0):
        self.weight_urgency = weight_urgency
        self.weight_impact = weight_impact

    def score(self, urgency: float, impact: float) -> float:
        """Return the priority score for a single item.

        Both ``urgency`` and ``impact`` should be positive real numbers.
        Negative values are clamped to 0 to prevent sign inversion.
        """
        u = max(0.0, urgency)
        i = max(0.0, impact)
        return (u ** 2) * i * self.weight_urgency * self.weight_impact

    def rank(self, items: Iterable[Dict]) -> List[Dict]:
        """Return items sorted by score (highest first).

        Each dict must contain ``urgency`` and ``impact`` keys.
        A ``_score`` key is added to each item in-place.
        """
        ranked = list(items)
        for item in ranked:
            item["_score"] = self.score(
                item.get("urgency", 1.0),
                item.get("impact", 1.0),
            )
        ranked.sort(key=lambda x: x["_score"], reverse=True)
        return ranked

    def explain(self, urgency: float, impact: float) -> Dict[str, Any]:
        """Return a human-readable breakdown of the score calculation."""
        u = max(0.0, urgency)
        i = max(0.0, impact)
        raw = (u ** 2) * i
        weighted = raw * self.weight_urgency * self.weight_impact
        return {
            "urgency": u,
            "impact": i,
            "urgency_squared": u ** 2,
            "raw_score": raw,
            "weight_urgency": self.weight_urgency,
            "weight_impact": self.weight_impact,
            "final_score": weighted,
            "formula": "urgency^2 * impact * w_u * w_i",
        }
