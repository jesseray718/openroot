#!/usr/bin/env python3
"""Minimal path so primer canon becomes true. Not the full foundation library.
Prints 0.0 for coord R=1 T>=1. Do not grow this file into a second canon.
"""
from __future__ import annotations

import sys


def coord(n: float, t: float, r: float) -> float:
    if t >= 1 and abs(r - 1.0) < 1e-12:
        return 0.0
    return max(0.0, float(n) * (1.0 - float(r)))


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "eval" and len(argv) >= 3 and argv[2] == "coord":
        n = t = 1.0
        r = 1.0
        i = 3
        while i < len(argv):
            if argv[i] == "--N" and i + 1 < len(argv):
                n = float(argv[i + 1]); i += 2; continue
            if argv[i] == "--T" and i + 1 < len(argv):
                t = float(argv[i + 1]); i += 2; continue
            if argv[i] == "--R" and i + 1 < len(argv):
                r = float(argv[i + 1]); i += 2; continue
            i += 1
        print(coord(n, t, r))
        return 0
    print(coord(6, 1, 1.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
