#!/usr/bin/env python3
# OpenRoot - dome_sphere_vs_5_8 checker, 2026-09-04
# Builds geodesic sphere V=1..50 by graph construction (Class I alternate).
# Verifies E=30V^2 sphere identity, computes 5/8 dome strut count separately.
import json, math, os, csv

BASE = "/home/jesse"
OUT = BASE + "/openroot/outbox"
os.makedirs(OUT, exist_ok=True)

def dist(u, v):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(u, v)))

def norm(p):
    n = math.sqrt(sum(c * c for c in p))
    return tuple(c / n for c in p)

# --- base icosahedron ---
t = (1.0 + math.sqrt(5.0)) / 2.0
raw = []
for a in (-1.0, 1.0):
    for b in (-t, t):
        raw += [(0.0, a, b), (a, b, 0.0), (b, 0.0, a)]
verts = [norm(v) for v in raw]
n = len(verts)
ds = {(i, j): dist(verts[i], verts[j]) for i in range(n) for j in range(i + 1, n)}
m = min(ds.values())
adj = {i: set() for i in range(n)}
for (i, j), d in ds.items():
    if abs(d - m) < 1e-9:
        adj[i].add(j)
        adj[j].add(i)
faces = []
for i in range(n):
    for j in adj[i]:
        if j <= i:
            continue
        for k in adj[i] & adj[j]:
            if k > j:
                faces.append((i, j, k))
print("base icosahedron: verts=%d edges=30 faces=%d" % (n, len(faces)))

def geodesic(V):
    idx = {}
    def node(p):
        k = tuple(round(c, 6) for c in norm(p))
        idx.setdefault(k, k)
        return k
    E = set()
    for (ia, ib, ic) in faces:
        A, B, C = verts[ia], verts[ib], verts[ic]
        grid = {}
        for i in range(V + 1):
            for j in range(V + 1 - i):
                w = (V - i - j, i, j)
                p = (w[0] * A[0] + w[1] * B[0] + w[2] * C[0],
                     w[0] * A[1] + w[1] * B[1] + w[2] * C[1],
                     w[0] * A[2] + w[1] * B[1 - 1 + 1] + w[2] * C[2])
                p = (w[0] * A[0] + w[1] * B[0] + w[2] * C[0],
                     w[0] * A[1] + w[1] * B[1] + w[2] * C[1],
                     w[0] * A[2] + w[1] * B[2] + w[2] * C[2])
                grid[(i, j)] = node(tuple(c / V for c in p))
        for i in range(V + 1):
            for j in range(V + 1 - i):
                if (i, j + 1) in grid:
                    E.add(frozenset((grid[(i, j)], grid[(i, j + 1)])))
                if (i + 1, j) in grid:
                    E.add(frozenset((grid[(i, j)], grid[(i + 1, j)])))
                if j >= 1 and (i + 1, j - 1) in grid:
                    E.add(frozenset((grid[(i, j)], grid[(i + 1, j - 1)])))
    return list(idx.keys()), E

def dome_split(V):
    pts, E = geodesic(V)
    zs = sorted(set(round(p[2], 6) for p in pts))
    cut = min(zs, key=lambda h: abs(h - 0.25))  # 5/8 of diameter above bottom pole
    dome, ring, sliced = 0, 0, 0
    for e in E:
        u, v = tuple(e)
        zu, zv = u[2], v[2]
        if zu >= cut - 1e-9 and zv >= cut - 1e-9:
            dome += 1
            if abs(zu - cut) < 1e-6 and abs(zv - cut) < 1e-6:
                ring += 1
        elif (zu - cut) * (zv - cut) < -1e-15:
            sliced += 1
    lens = sorted({round(dist(u, v), 4) for e in dome for u, v in (tuple(e),)}, reverse=True)
    return len(pts), len(E), dome, ring, sliced, cut, lens

rows = []
bad = []
for V in range(1, 51):
    nv, ne, nd, ring, sliced, cut, lens = dome_split(V)
    ok = (ne == 30 * V * V) and (nv == 10 * V * V + 2)
    if not ok:
        bad.append((V, ne, nv))
    rows.append({
        "frequency": V,
        "sphere_edges": ne,
        "law_30V2": 30 * V * V,
        "sphere_verts": nv,
        "law_ok": ok,
        "dome_5_8_struts": nd,
        "base_ring_struts": ring,
        "sliced_edges_flag": sliced,
        "cut_height_R": cut,
        "dome_unique_chord_factors": len(lens),
        "overbuy_pct": round(100.0 * (ne - nd) / ne, 1)
    })

csv_path = OUT + "/dome_sphere_vs_5_8_V1_V50_20260904.csv"
with open(csv_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("")
print("== SPHERE LAW CHECK (30*V^2, closed mesh) ==")
print("violations:", bad if bad else "NONE - law holds V=1..50 (sphere only)")
print("")
print("== SPHERE vs 5/8 DOME STRUT COUNTS ==")
hdr = ("V", "sphere_E", "dome_5_8", "base_ring", "overbuy%", "chords")
print("%-4s %-9s %-9s %-10s %-9s %s" % hdr)
for r in rows[:12]:
    print("%-4d %-9d %-9d %-10d %-9.1f %d" % (
        r["frequency"], r["sphere_edges"], r["dome_5_8_struts"],
        r["base_ring_struts"], r["overbuy_pct"], r["dome_unique_chord_factors"]))
print("... full table in " + csv_path)
print("")
print("== V6 RECONCILIATION vs DB (7.21 / 7.11 / 7.02 in) ==")
v6 = [r for r in rows if r["frequency"] == 6][0]
_, _, _, _, _, _, lens6 = dome_split(6)
print("computed unique chord factors at 6V (unit sphere):", lens6)
db = [7.21, 7.11, 7.02]
print("DB length ratios (len/7.21): ", [round(x / db[0], 4) for x in db])
if len(lens6) > 3:
    span = round(max(lens6) / min(lens6), 4)
    print("WARNING: 6V sphere has %d distinct chord lengths (max/min=%.4f)." % (len(lens6), span))
    print("A 3-length table is NOT a universal 6V law - name radius, class, truncation, hub before cutting.")
print("")
print("saved:", csv_path)
