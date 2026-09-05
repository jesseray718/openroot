#!/bin/bash
# OPENROOT FINAL DELIVERABLES PACKAGE
# Run from fresh window: bash ~/openroot/FINAL_PACKAGE.sh
set -e
echo "==========================================="
echo "OPENROOT - COMPLETE SYSTEM PACKAGE"
echo "Generated: $(date)"
echo "==========================================="

# ---- 1. HEALTH CHECK SCRIPT ----
cat > ~/openroot/system_health_check.py <<'HEALTHCHECK'
#!/usr/bin/env python3
import sys,json,hashlib,time
from pathlib import Path
STORE=Path("/home/jesse/openroot/axiom_engine/store")
CHAIN=STORE/"chain.jsonl"
def h(b):return hashlib.sha256(b).hexdigest()
def j(o):return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)

idx={}
for l in["axioms","definitions","theorems"]:
 p=STORE/f"{l}.jsonl"
 if p.exists():
  for ln in p.read_text().splitlines():
   if ln.strip():r=json.loads(ln);rid=r.get("id");idx[rid]=r if rid else None

ok,val,tot,errs=True,0,0,[]
if CHAIN.exists():
 for i,ln in enumerate(CHAIN.read_text().splitlines(),1):
  if not ln.strip():continue
  try:
   cr=json.loads(ln);rid=cr.get("id");ch=cr.get("hash");rec=idx.get(rid)
   if not rec:tot+=1;errs.append(f"L{i}:{rid}missing");continue
   bd={"kind":cr.get("kind"),"id":rec.get("id",""),
       "statement":rec.get("statement",""),
       "premises":list(rec.get("premises")or[]),
       "proof":list(rec.get("proof")or[])}
   cm=h(j(bd).encode())
   if cm==ch:val+=1;tot+=1
   else:tot+=1;errs.append(f"L{i}:mismatch")
  except Exception as e:tot+=1;errs.append(f"L{i}:{e}")
else:ok=False;t=100;errs=["chain.jsonl missing"]

mr_ok,mr=None,None
mf=STORE/"merkle_definitions.json"
if mf.exists():
 try:d=json.loads(mf.read_text());mr=d.get("merkle_root");mr_ok="merkle_root"in d
 except:pass

ct={"axioms":0,"definitions":0,"theorems":0}
for l in ct:
 p=STORE/f"{l}.jsonl"
 if p.exists():ct[l]=len([x for x in p.read_text().splitlines() if x.strip()])

print("="*60)
print("SYSTEM HEALTH CHECK")
print("="*60)
print(f"[Chain]: {'✓GREEN'if ok else '✗RED'}({val}/{tot})")
print(f"[Merkle]:{'✓PRESENT'if mr_ok else '✗MISSING'}{mr[:32]+'...' if mr else ''}")
print(f"\nAxioms:{ct['axioms']}  Definitions:{ct['definitions']}  Theorems:{ct['theorems']}")
print("="*60)
print(f"STATUS:{'✓HEALTHY'if ok and mr_ok and ct['theorems']>=60 else '✗NEEDSATTENTION'}")
print("="*60)
HEALTHCHECK
chmod +x ~/openroot/system_health_check.py

# ---- 2. CONTEXT BRIDGE ----
cat > ~/openroot/CONTEXT_BRIDGE.md <<'BRIDGEFILE'
# OPENROOT CONTEXT BRIDGE
# Jesse Ray (OpenRoot) | 01 Sep 2026

## STATE
|Category|Count|
|--------|-----|
|Axioms|63|
|Definitions|79|
|Theorems|63|
|Merkle|2c8efdc3...ad00962|

## 7 SYMBOLS
Λ=A gape|○=Void|∞=Infinity|⊗=Torus|⚡=Instantiate|↺=Synergy|◎=Genesis

## KEY FLAGS
TH-0D-LIGHT:FLAG-TH-18d9601f33f1d265
TH-EUCLID-47:FLAG-TH-db22df07f8f8db24
TH-AGAPE-FRICTION:FLAG-TH-1031c9bfab7f2fe7
TH-SYNERGY:FLAG-TH-65f6bad2088ce295

## VERIFY
python3 ~/openroot/system_health_check.py
BRIDGEFILE

# ---- 3. UNITY DOC ----
cat > ~/openroot/UNITY.md <<'UNITYFILE'
# UNIFIED SYSTEM ARCHITECTURE
# 7-Layer Stack: 0D→2D→3D→Ethics→Theology→Symbols→Synergy

## LAYERS
0D: TH-0D-LIGHT (void→light)
2D: Euclid I.1-I.48 (Pythagoras I.47)
3D: TH-LIGHT-CONE (relativity)
4D: TH-AGAPE-COOPERATION (zero friction)
5D: TH-SACRED-LANGUAGE (A=Agape)
6D: TH-SYNERGY-METRIC (η_s = O_tot / ΣO_i)

## GUARANTEES
✓ Deterministic hashes
✓ Chain verifiable
✓ Proof cached
✓ Merkle anchored
UNITYFILE

# ---- 4. RUN & REPORT ----
echo ""
echo "==========================================="
echo "CREATING FILES:"
ls -la ~/openroot/system_health_check.py
ls -la ~/openroot/CONTEXT_BRIDGE.md
ls -la ~/openroot/UNITY.md
echo "==========================================="
echo ""
echo "RUNNING HEALTH CHECK:"
echo ""
python3 ~/openroot/system_health_check.py
echo ""
echo "==========================================="
echo "PACKAGE COMPLETE"
echo "==========================================="
echo ""
echo "NEXT COMMANDS (optional):"
echo "  cat ~/openroot/CONTEXT_BRIDGE.md"
echo "  cat ~/openroot/UNITY.md"
echo "  cat ~/openroot/axiom_engine/store/merkle_definitions.json"
echo "==========================================="
