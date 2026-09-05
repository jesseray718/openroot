#!/usr/bin/env python3
"""
NANOBOT LATTICE — joule-native recursive composition engine
order 0 atoms → triad → sparse n^n up to symbolic order 12
η = useful_joules / human_joules
Every evaluation path produces a merkle root + ACRE claim.
"""

import json
import hashlib
import time
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

LANDAUER = 2.85e-21
BASE_HUMAN_J_PER_LINE = 0.0008
AGAPE_DOWNSTREAM = 0.15

@dataclass
class Node:
    id: str
    jps: float = 0.0
    human_j: float = 0.0
    useful_j: float = 0.0
    children: List[str] = None
    axiom_hits: List[str] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.axiom_hits is None:
            self.axiom_hits = []

    @property
    def η(self) -> float:
        return self.useful_j / self.human_j if self.human_j > 0 else 0.0

@dataclass
class Trace:
    order: int
    path: List[str]
    Δη: float
    axiom_id: str
    ts: float

class NanobotLattice:
    def __init__(self, axiom_path: str):
        with open(axiom_path) as f:
            self.axioms = json.load(f)
        self.layer0 = {a["id"]: a for a in self.axioms["layer_0_axioms"]}
        self.traces: List[Trace] = []
        self.nodes: Dict[str, Node] = {}
        self.merkle_leaves: List[str] = []

    def f1_measure_jps(self, node: Node, metrics: Dict) -> Node:
        lines = metrics.get("lines", 1)
        complexity = metrics.get("complexity_score", lines)
        bits = metrics.get("chars", lines * 40) * 8
        node.human_j = (lines * BASE_HUMAN_J_PER_LINE) + (bits * LANDAUER * 1e12)
        node.useful_j = metrics.get("useful_estimate", complexity * 0.0003)
        node.jps = node.human_j / max(metrics.get("time_budget", 1.0), 0.001)
        self._commit(f"f1:{node.id}:{node.jps:.6f}")
        return node

    def f2_score_axiom(self, node: Node, axiom_id: str, context: Dict = None) -> float:
        ax = self.layer0.get(axiom_id)
        if not ax:
            return 0.0
        Δη = 0.0
        if axiom_id == "PHYS_01":
            if node.useful_j > node.human_j * 10:
                Δη = -999.0
        elif axiom_id == "PERMA_03":
            red = context.get("redundant_ratio", 0.0) if context else 0.0
            Δη -= red * 0.5
        elif axiom_id == "AGAPE_01":
            consumers = context.get("downstream", 1) if context else 1
            node.useful_j *= (1.0 + consumers * AGAPE_DOWNSTREAM)
            Δη += consumers * 0.12
        elif axiom_id == "SYNER_01":
            if node.human_j > node.useful_j:
                Δη = -0.8
        elif axiom_id == "GEO_01":
            if context and context.get("fractal_invariant"):
                Δη += 0.25
        elif axiom_id == "PERMA_01":
            if not context or not context.get("measured"):
                Δη -= 0.4
        node.axiom_hits.append(axiom_id)
        self.traces.append(Trace(order=0, path=[node.id], Δη=Δη, axiom_id=axiom_id, ts=time.time()))
        self._commit(f"f2:{axiom_id}:{Δη:.4f}")
        return Δη

    def f3_merkle_commit(self, data: str) -> str:
        h = hashlib.sha256(data.encode()).hexdigest()
        self.merkle_leaves.append(h)
        return h

    def _commit(self, leaf: str):
        self.f3_merkle_commit(leaf)

    def triad(self, node: Node, metrics: Dict, axioms_to_apply: List[str]) -> Tuple[Node, float]:
        node = self.f1_measure_jps(node, metrics)
        total_Δη = 0.0
        for ax_id in axioms_to_apply:
            total_Δη += self.f2_score_axiom(node, ax_id, {"measured": True, "downstream": 3})
        root = self.f3_merkle_commit(json.dumps({"id": node.id, "η": node.η, "Δη": total_Δη}))
        return node, total_Δη

    def raise_order(self, bottleneck_id: str, current_order: int) -> str:
        new_id = f"{bottleneck_id}_o{current_order+1}"
        self.nodes[new_id] = Node(id=new_id)
        self._commit(f"raise:{bottleneck_id}->{new_id}")
        return new_id

    def find_bottleneck(self) -> Optional[str]:
        if not self.nodes:
            return None
        return min(self.nodes.values(), key=lambda n: n.η).id

    def merkle_root(self) -> str:
        if not self.merkle_leaves:
            return hashlib.sha256(b"empty").hexdigest()
        layer = self.merkle_leaves[:]
        while len(layer) > 1:
            next_layer = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i+1] if i+1 < len(layer) else left
                next_layer.append(hashlib.sha256((left + right).encode()).hexdigest())
            layer = next_layer
        return layer[0]

    def mint_acre(self, target_file: str, final_η: float, order_reached: int) -> Dict:
        root = self.merkle_root()
        claim = {
            "type": "ACRE",
            "version": "1",
            "target": target_file,
            "η": round(final_η, 6),
            "order_reached": order_reached,
            "merkle_root": root,
            "useful_joules": sum(n.useful_j for n in self.nodes.values()),
            "human_joules": sum(n.human_j for n in self.nodes.values()),
            "traces": len(self.traces),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "axioms_applied": list({t.axiom_id for t in self.traces}),
            "claim": f"PoCW:{root[:16]}"
        }
        return claim

    def process(self, target_json: Dict, max_order: int = 4) -> Dict:
        metrics = target_json if "lines" in target_json else target_json.get("metrics", {"lines": 42, "complexity_score": 30, "chars": 1200})
        root_id = target_json.get("id", "root")
        self.nodes[root_id] = Node(id=root_id)
        axioms = list(self.layer0.keys())
        node, Δη = self.triad(self.nodes[root_id], metrics, axioms)
        current_η = node.η + Δη
        order = 1
        while order < max_order:
            bott = self.find_bottleneck()
            if not bott or self.nodes[bott].η > 0.85:
                break
            new_id = self.raise_order(bott, order)
            sparse_ax = ["SYNER_01", "SYNER_02", "GEO_01", "AGAPE_01", "PERMA_03"]
            n2, d2 = self.triad(self.nodes[new_id], metrics, sparse_ax)
            current_η = n2.η
            order += 1
        claim = self.mint_acre(target_json.get("source", "unknown"), current_η, order)
        return {
            "final_η": current_η,
            "order_reached": order,
            "bottleneck": self.find_bottleneck(),
            "merkle_root": claim["merkle_root"],
            "acre": claim,
            "node_count": len(self.nodes),
            "trace_count": len(self.traces)
        }

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 nanobot_lattice.py <axiom_lattice.json> <target.json> [max_order]")
        sys.exit(1)
    axiom_path = sys.argv[1]
    target_path = sys.argv[2]
    max_order = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    with open(target_path) as f:
        target = json.load(f)
    lattice = NanobotLattice(axiom_path)
    result = lattice.process(target, max_order=max_order)
    out = {
        "η": result["final_η"],
        "order": result["order_reached"],
        "merkle": result["merkle_root"],
        "acre_claim": result["acre"]["claim"],
        "acre": result["acre"]
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
