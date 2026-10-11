#!/usr/bin/env python3
"""Edge lengths for platonic / 1V icosa statues. Radius is circumscribed mm."""
from __future__ import annotations
import json
import math
import sys

PHI = (1 + math.sqrt(5)) / 2


def ico_verts(r: float):
    u = r / math.sqrt(1 + PHI * PHI)
    v = PHI * u
    return [
        (0, u, v), (0, u, -v), (0, -u, v), (0, -u, -v),
        (u, v, 0), (u, -v, 0), (-u, v, 0), (-u, -v, 0),
        (v, 0, u), (v, 0, -u), (-v, 0, u), (-v, 0, -u),
    ]


def dist(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def unique_edges(r: float):
    v = ico_verts(r)
    lengths = []
    for i, a in enumerate(v):
        for b in v[i + 1 :]:
            d = dist(a, b)
            if d < r * 1.3:  # icosa edges only, drop long diameters
                lengths.append(d)
    lengths.sort()
    # cluster
    classes = []
    for L in lengths:
        if not classes or abs(L - classes[-1][0]) > 0.01 * r:
            classes.append([L, 1])
        else:
            classes[-1][1] += 1
            classes[-1][0] = (classes[-1][0] * (classes[-1][1] - 1) + L) / classes[-1][1]
    return classes


def tetra_edge(r: float) -> float:
    # vertices (1,1,1)... normalized then scaled
    return r * (2 * math.sqrt(6) / 3)


def main():
    r = float(sys.argv[1]) if len(sys.argv) > 1 else 200.0
    out = {
        "radius_mm": r,
        "tetrahedron_edge_mm": round(tetra_edge(r), 2),
        "icosahedron_1V_edge_classes_mm": [
            {"edge_mm": round(L, 2), "count": n} for L, n in unique_edges(r)
        ],
        "triangle_height_1V_mm": None,
        "mold_note": "cut one melamine cavity per edge class. 1V icosa has one class.",
    }
    if out["icosahedron_1V_edge_classes_mm"]:
        e = out["icosahedron_1V_edge_classes_mm"][0]["edge_mm"]
        out["triangle_height_1V_mm"] = round(e * math.sqrt(3) / 2, 2)
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
