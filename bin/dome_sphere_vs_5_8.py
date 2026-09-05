#!/usr/bin/env python3
"""OpenRoot — sphere vs 5/8 dome strut law, 2026-09-04.

Builds the Class-I alternate geodesic sphere V=1..50 by actual graph
construction (icosahedron -> subdivide -> project -> dedupe), so the dome
count is COMPUTED, not asserted. Two separate columns so the 30V^2 law
can never be misread as a shopping list again.
"""
import csv, math, os

BASE = "/home/jesse"
OUT = BASE + "/openroot/outbox"
os.makedirs(OUT, exist_ok=True)

def dist(u, v):
    return sum((a - b) ** 2 for a, b in zip(u, v)) ** 0.5

def norm(p):
    n = sum(c * c for c in p) ** 0.5
    return (v / n for v in p)  # placeholder, replaced below
