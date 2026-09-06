"""
agaperesonance.core — Predictive resonance filtering.
"""
import hashlib, math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

PHI = (1 + math.sqrt(5)) / 2

@dataclass
class Prediction:
    content: str
    confidence: float = 0.5
    source: str = "unknown"
    tags: List[str] = field(default_factory=list)
    def hash(self):
        blob = f"{self.content}:{self.source}".encode()
        return hashlib.sha256(blob).hexdigest()[:16]

def _text_similarity(a, b):
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

def _tag_similarity(a, b):
    if not a or not b:
        return 0.0
    return len(set(a) & set(b)) / len(set(a) | set(b))

@dataclass
class ResonanceResult:
    content: str
    confidence: float
    coherence_score: float
    agape_coefficient: float
    synergy: float
    survivor_count: int
    total_predictions: int
    hash: str

class ResonanceFilter:
    def __init__(self, agape_coefficient=0.8, similarity_threshold=0.3, min_confidence=0.1):
        self.R = max(0.01, min(1.0, agape_coefficient))
        self.sim_threshold = similarity_threshold
        self.min_confidence = min_confidence
        self._predictions: List[Prediction] = []

    def add_prediction(self, content, confidence=0.5, source="unknown", tags=None):
        self._predictions.append(Prediction(
            content=content, confidence=max(0.0, min(1.0, confidence)),
            source=source, tags=tags or [],
        ))

    def add_predictions(self, predictions):
        for p in predictions:
            self.add_prediction(**p)

    def _reinforce(self):
        results = []
        for i, pred in enumerate(self._predictions):
            if pred.confidence < self.min_confidence:
                continue
            cooperators = 0
            boost = 0.0
            for j, other in enumerate(self._predictions):
                if i == j:
                    continue
                sim = max(_text_similarity(pred.content, other.content),
                          _tag_similarity(pred.tags, other.tags) * 0.7)
                if sim >= self.sim_threshold:
                    cooperators += 1
                    boost += other.confidence * sim * self.R
            reinforced = min(1.0, pred.confidence + boost * (1.0 - pred.confidence))
            synergy = 1.0 + math.log(max(cooperators, 1)) / (PHI * self.R)
            results.append((
                pred,
                min(1.0, reinforced * (1.0 + math.log(max(cooperators, 1)) / (PHI * self.R) - 1.0)),
                cooperators,
            ))
        return results

    def filter(self, top_n=1):
        reinforced = self._reinforce()
        if not reinforced:
            return []
        reinforced.sort(key=lambda x: x[1], reverse=True)
        results = []
        for pred, conf, coop in reinforced[:top_n]:
            total = len(self._predictions)
            synergy = 1.0 + math.log(max(coop, 1)) / (PHI * self.R)
            results.append(ResonanceResult(
                content=pred.content, confidence=conf,
                coherence_score=coop / max(total - 1, 1),
                agape_coefficient=self.R, synergy=synergy,
                survivor_count=coop, total_predictions=total, hash=pred.hash(),
            ))
        return results

    def standing_wave(self):
        results = self.filter(top_n=1)
        return results[0] if results else None

    def hedged_array(self):
        return self.filter(top_n=len(self._predictions))

    def coordination_cost(self):
        return 1.0 / self.R - 1.0

    def clear(self):
        self._predictions = []
