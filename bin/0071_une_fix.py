#!/usr/bin/env python3
"""OpenRoot one-shot: bank bench, dedupe theorems, PO-016 reward_verified. Idempotent."""
import gc, hashlib, json, math, os, py_compile, shutil, time

HOME  = "/data/data/com.termux/files/home"
STORE = os.path.join(HOME, "src/openroot/axiom_engine/store")
SDST  = "/sdcard/openroot/axiom_engine/store"
ATTIC = os.path.join(STORE, "attic")
CTX   = "/sdcard/openroot/context_bridge"
AUDIT = os.path.join(CTX, "swarm_bench_audit.jsonl")
LEDGER= os.path.join(CTX, "thermo_ledger.jsonl")
for d in (ATTIC, CTX):
    os.makedirs(d, exist_ok=True)

# ---------- STAGE 1: honest bench, trimmed so it completes ----------
print("[capture] stage 1: bench (trimmed)", flush=True)
gc.disable()
def f1(p): p["t"]=time.time(); return p
def f2(p): p["h"]=hashlib.sha256(str(p["t"]).encode()).hexdigest()[:8]; return p
def f3(p): return p
def f4(p): return p
def f5(p): p["c"]=p["h"]; return p
def f6(p): p["v"]=(p["c"]==p["h"]); return p
def f7(p): p["E"]=2.87e-21; return p
def f8(p): return p
def f9(p): return p
def f10(p): p["y"]=p["v"]; return p
def f11(p): return p
def f12(p): return p
ATOMS=[f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12]
def leaf():
    p={}
    for f in ATOMS: p=f(p)
    return p
def build(n,d):
    fn=leaf
    for _ in range(d):
        ch=[fn]*n
        def runner(ch=ch):
            r=None
            for c in ch: r=c()
            return r
        fn=runner
    return fn
rows=[]
for n,d in [(3,4),(3,5),(3,7),(12,4)]:
    fn=build(n,d)
    assert fn().get("v") is True, "[held] verify failed"
    opc=len(ATOMS)*(n**d); cyc=0
    t0=time.perf_counter()
    while time.perf_counter()-t0<1.5:
        for _ in range(8): fn()
        cyc+=8
    dt=time.perf_counter()-t0
    rate=opc*cyc/dt
    rows.append({"n":n,"l":d,"atom_ops_per_cycle":opc,"cycles_per_s":round(cyc/dt,2),"measured_atom_ops_s":round(rate,1)})
    print(f"  N={n} L={d}: {rate:,.0f} atom-ops/s", flush=True)
peak=max(r["measured_atom_ops_s"] for r in rows)
claim=6_131_462_173.0
entry={"id":"swarm_bench_"+hashlib.sha256(str(rows).encode()).hexdigest()[:12],
 "timestamp":time.strftime("%Y-%m-%dT%H:%M:%S%z"),"type":"fractal_swarm_benchmark",
 "method":"trimmed wall-clock, gc off, verify-gated","peak_measured_atom_ops_s":peak,
 "claim_6.13B_ratio":round(claim/peak),"refuted":claim/peak>2.0,"rows":rows,
 "hash":hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:16],"status":"MEASURED"}
with open(AUDIT,"a") as fh: fh.write(json.dumps(entry)+"\n")
print(f"[banked] bench audit -> {AUDIT}  (claim/refuted ratio {claim/peak:,.0f}x)", flush=True)

# ---------- STAGE 2: dedupe theorems.jsonl (earliest ts wins) ----------
print("[capture] stage 2: theorems dedupe", flush=True)
def dedupe(path):
    if not os.path.exists(path): print(f"  [inspect] missing: {path}"); return
    best={}
    for line in open(path,encoding="utf-8"):
        line=line.strip()
        if not line: continue
        try: rec=json.loads(line)
        except json.JSONDecodeError: continue
        rid=rec.get("id"); ts=rec.get("ts",0)
        if rid not in best or ts<best[rid].get("ts",0): best[rid]=rec
    dup=sum(1 for l in open(path,encoding="utf-8") if l.strip())-len(best)
    if dup==0: print(f"  [guard] clean already: {path}"); return
    bak=os.path.join(ATTIC,os.path.basename(path)+"."+str(int(time.time()))+".retired")
    shutil.copy2(path,bak)
    with open(path,"w",encoding="utf-8") as fh:
        for rid in best: fh.write(json.dumps(best[rid])+"\n")
    print(f"  [banked] {path}: removed {dup} dupes ({len(best)} kept), backup {bak}", flush=True)
dedupe(os.path.join(STORE,"theorems.jsonl"))
dedupe(os.path.join(SDST,"theorems.jsonl"))

# ---------- STAGE 3: PO-016 reward_verified in une_atomic_library.py ----------
print("[capture] stage 3: PO-016 reward_verified patch", flush=True)
FN = '''

def reward_verified(base, verified_epochs, cooperators=0, phi=1.618033988749895):
    """PO-016 compliant reward. verified_epochs = epochs confirmed by >=2 distinct
    validator nodes. Solo/entry-count epochs compound to NOTHING (phi^0 = 1).
    Guard: verified epochs cannot exceed cooperators (no phantom verification)."""
    ve = max(0, min(int(verified_epochs), int(cooperators)))
    coop_mult = 1 + math.log(max(int(cooperators), 1)) / phi
    return base * (phi ** ve) * coop_mult
'''
for path in [os.path.join(HOME,"src/une/une_atomic_library.py"),
             os.path.join(HOME,"src/une_atomic_library.py"),
             "/sdcard/openroot/une_atomic_library.py"]:
    if not os.path.exists(path): print(f"  [inspect] missing: {path}"); continue
    src=open(path,encoding="utf-8").read()
    if "def reward_verified" in src:
        print(f"  [guard] already patched: {path}"); continue
    with open(path,"a",encoding="utf-8") as fh: fh.write(FN)
    py_compile.compile(path, doraise=True)
    ok="def reward_verified" in open(path,encoding="utf-8").read()
    print(f"  [{'banked' if ok else 'FAIL'}] patched + py_compile + grep: {path}", flush=True)

# ---------- smoke test ----------
sys_spec = ("import sys; sys.path.insert(0,'%s/src/une'); "
 "from une_atomic_library import reward_verified; "
 "solo=reward_verified(1.0, 50, cooperators=0); "
 "coop=reward_verified(1.0, 5, cooperators=12); "
 "assert abs(solo-1.0)<1e-9, 'solo leaked'; "
 "assert coop>1.0 and coop<(phi_val:=1.618033988749895)**5*1.65, 'unbounded'; "
 "print('SMOKE-OK solo=%.4f coop=%.4f'%(solo,coop))") % HOME
if os.system("python3 -c \"%s\"" % sys_spec.replace('"','\\"'))!=0:
    print("[held] smoke failed — inspect manually", flush=True)
else:
    with open(LEDGER,"a") as fh:
        fh.write(json.dumps({"type":"po016_fix","bench_peak_atom_ops_s":peak,
                             "theorem_dupes_removed":True,"reward_verified_added":True,
                             "hash":entry["hash"],"status":"PATCHED"})+"\n")
    print(f"[banked] po016_fix -> {LEDGER}", flush=True)
print("[exit=0]", flush=True)
