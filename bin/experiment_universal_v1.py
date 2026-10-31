# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""CANARY:OPENROOT-UNIVERSAL-EXPERIMENT-V1 — Experiments 1-3 on the exp clone."""
import sqlite3, time
DB = "/home/jesse/pods/exp_universal_20261016T090321Z/pod.db"
db = sqlite3.connect(DB, timeout=30); db.execute("PRAGMA busy_timeout=30000")
print("="*60); print("EXP 1: DOSSIER QUALITY AUDIT"); print("="*60)
QUESTIONS = [
    "How does the Merkle ledger verify lattice integrity?",
    "What is the energy accounting doctrine for RAPL joules?",
    "How do aerocement panels achieve structural strength?",
    "What permaculture principles guide the workflow loops?",
    "How does the push_guard prevent unverified pushes?",
    "What is the agape cascade simulation's known flaw?",
    "How does the heartbeat engine route directives?",
    "What was the loss from the git history rewrite?",
    "How is the Newton Chain structured into axioms?",
    "What cooling performance does the thermal labyrinth show?",
]
def dossier_for(word, limit=12):
    parts = []
    for r in db.execute("SELECT snippet(chunks_fts,0,'[',']','…',12) "
                        "FROM chunks_fts WHERE chunks_fts MATCH ? LIMIT ?", (word, limit)):
        parts.append(r[0])
    return "\n".join(parts)
STOP = {"how","does","the","what","is","are","do","and","to","of","for","in","on","a","it","its","was","show"}
audit_path = "/home/jesse/pods/exp_universal_20261016T090321Z/dossier_audit.md"
with open(audit_path, "w") as f:
    for q in QUESTIONS:
        words = [w.strip("?.,'\"").lower() for w in q.split()]
        kws = [w for w in words if w not in STOP and len(w) > 2][:4]
        f.write(f"## {q}\nkeywords: {kws}\n\n")
        for w in kws:
            f.write(f"### {w}\n{dossier_for(w)[:900]}\n\n")
print(f"[banked] audit written: {audit_path}")
print("="*60); print("EXP 2: CACHE BENCHMARK"); print("="*60)
KW = ["merkle","ledger","agape","aerocement","stirling","permaculture","rapl","joules",
      "lattice","cascade","newton","axiom","push","guard","tunnel","thermo","seed","dossier"]
db.execute("CREATE TABLE IF NOT EXISTS dossiers(word TEXT PRIMARY KEY, dossier TEXT, built_utc TEXT)")
results = []
for w in KW:
    t0 = time.perf_counter()
    d = dossier_for(w)[:6000]
    db.execute("INSERT OR REPLACE INTO dossiers VALUES (?,?,?)", (w, d,
               time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())))
    db.commit()
    build = (time.perf_counter()-t0)*1000
    t0 = time.perf_counter()
    db.execute("SELECT dossier FROM dossiers WHERE word=?", (w,)).fetchone()
    cached = (time.perf_counter()-t0)*1000
    results.append((w, build, cached))
avg_b = sum(r[1] for r in results)/len(results); avg_c = sum(r[2] for r in results)/len(results)
for w,b,c in results: print(f"  {w:<13} build {b:7.1f} ms  cached {c:6.2f} ms")
print(f"  AVG: build {avg_b:.1f} ms | cached {avg_c:.2f} ms | speedup {avg_b/max(avg_c,0.001):.0f}x")
print("="*60); print("EXP 3: FTS STRESS"); print("="*60)
for label,q in [('common: data','data'),('common: openroot','openroot'),
                ('phrase','"merkle root"'),('near','agape NEAR/5 cascade'),
                ('prefix','aero*'),('chars','rapl+joules')]:
    try:
        t0=time.perf_counter()
        n=db.execute("SELECT COUNT(*) FROM chunks_fts WHERE chunks_fts MATCH ?",(q,)).fetchone()[0]
        print(f"  {label:<20} {n:>7} hits  {(time.perf_counter()-t0)*1000:7.1f} ms")
    except Exception as e:
        print(f"  {label:<20} ERROR: {e!r}")
print("[banked] exp 1-3 complete [exit=0]")
