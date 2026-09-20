#!/usr/bin/env python3
"""CLI for Agape 3-symbol nomenclature + Godpan inference.

Examples (A15 / anywhere):
  python3 /abs/path/bin/nomen.py init
  python3 /abs/path/bin/nomen.py ingest "catch and store rain for the lowest node"
  python3 /abs/path/bin/nomen.py align "predatory extraction of labor from the poor"
  python3 /abs/path/bin/nomen.py search "agape resonance"
  python3 /abs/path/bin/nomen.py knn "serve the least among us"
  python3 /abs/path/bin/nomen.py cell AAA
  python3 /abs/path/bin/nomen.py chart A
  python3 /abs/path/bin/nomen.py stats
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "lib"))

from nomen_core import (  # noqa: E402
    AGAPE_ROOT_HASH,
    RESERVED,
    SPACE,
    USABLE,
    NomenDB,
    ascii_heat,
    decode_meaning,
    encode_triple,
    hash_address,
    svg_chart,
)

DB_PATH = os.environ.get(
    "AGAPE_NOMEN_DB",
    os.path.join(ROOT, "data", "nomen.sqlite"),
)
CHART_DIR = os.path.join(ROOT, "charts")


def db() -> NomenDB:
    return NomenDB(DB_PATH)


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, *rest = argv
    if cmd == "init":
        d = db()
        n = d.seed_defaults()
        print(json.dumps({"seeded": n, "stats": d.stats(), "root_hash": AGAPE_ROOT_HASH}, indent=2))
        return 0
    if cmd == "stats":
        print(json.dumps(db().stats(), indent=2))
        return 0
    if cmd == "cell" and rest:
        cell = rest[0].upper()
        d = db()
        m = d.ensure_cell(cell)
        print(json.dumps(m, indent=2))
        return 0
    if cmd == "addr" and rest:
        text = " ".join(rest)
        print(json.dumps({"text": text, "cell": hash_address(text), "meaning": decode_meaning(hash_address(text))}, indent=2))
        return 0
    if cmd == "ingest":
        text = " ".join(rest)
        print(json.dumps(db().ingest(text), indent=2, default=str))
        return 0
    if cmd == "align":
        text = " ".join(rest)
        print(json.dumps(db().align(text), indent=2, default=str))
        return 0
    if cmd == "search":
        print(json.dumps(db().search_fts(" ".join(rest)), indent=2))
        return 0
    if cmd == "knn":
        print(json.dumps(db().knn(" ".join(rest)), indent=2))
        return 0
    if cmd == "chart":
        letter = (rest[0] if rest else "A").upper()
        d = db()
        rows = d.chart_rows(letter)
        print(ascii_heat(rows, f"GODPAN CHART  domain={letter} polarity=A  space={SPACE} usable={USABLE}"))
        svg = svg_chart(rows, f"Godpan {letter}**A", os.path.join(CHART_DIR, f"godpan_{letter}.svg"))
        print(f"\nSVG {svg}")
        return 0
    if cmd == "encode" and rest:
        print(encode_triple(int(rest[0])))
        return 0
    print("unknown command. try help", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
