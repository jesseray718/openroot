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
