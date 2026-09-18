#!/usr/bin/env python3
# [canary] paste intact
# cosmo_rack.py — Tier-2 rack the 0D cosmology: retire misbadged theorems,
# append correctly-typed records, never edit in place (hash discipline).
# DEFAULT: dry-run. Execute with:  COSMO_CONFIRM=1 python3 cosmo_rack.py
import json, os, shutil, time

CONFIRM = os.environ.get("COSMO_CONFIRM") == "1"
STORE = "/home/jesse/src/openroot/axiom_engine/store"
ATTIC = os.path.join(STORE, "attic")

RETIRE_FROM_THEOREMS = {"TH-0D-LIGHT", "TH-GENESIS-BLOCK-0A", "TH-WORLDLINE-COLLAPSE"}
TIER2_TAG_AXIOMS = {"AX-0D-EXISTENCE","AX-0D-IDENTITY","AX-0D-CAUSALITY",
                    "AX-0D-CONSERVATION","AX-THEO-AGAPE-PRIMACY",
                    "AX-THEO-LOGOS-SPEECH","AX-STANDING_WAVE_REALITY"}

# What each retired theorem becomes: (file, kind, tier, note)
REBIRTH = {
  "TH-0D-LIGHT": ("postulates.jsonl","postulate",2,
      "Instantiation at the singularity emits light isotropically; "
      "space and time emerge from differentiation."),
  "TH-GENESIS-BLOCK-0A": ("axioms.jsonl","axiom",2,
      "A0 (Genesis Postulate): token 0A marks the void prior to "
      "instantiation; Agape as first principle. Numbered zero, "
      "preceding A1, matching the 37-char encoding's void-A."),
  "TH-WORLDLINE-COLLAPSE": ("postulates.jsonl","postulate",2,
      "Each observer's trajectory is a worldline; multiple observers "
      "generate branching timelines that interfere."),
}

def load(fn):
    return [json.loads(l) for l in open(os.path.join(STORE,fn)) if l.strip()]

def write(fn, recs):
    with open(os.path.join(STORE,fn),"w") as f:
        for r in recs: f.write(json.dumps(r,ensure_ascii=False)+"\n")

print("[canary] paste intact | mode:", "EXECUTE" if CONFIRM else "DRY-RUN")
thm = load("theorems.jsonl"); axi = load("axioms.jsonl")
retired = [r for r in thm if r.get("id") in RETIRE_FROM_THEOREMS]
print(f"[observe] theorems={len(thm)} matching_retire_set={len(retired)}")
for r in retired: print("  retire:", r["id"])

# Plan: retire from theorems; tag axioms tier2; append reborn records
new_thm = [r for r in thm if r.get("id") not in RETIRE_FROM_THEOREMS]
new_axi = []
for r in axi:
    if r.get("id") in TIER2_TAG_AXIOMS:
        r = dict(r); r["tier"]=2; r["status"]="SPECULATIVE"
    new_axi.append(r)

ts = int(time.time())
plan = []
for old in retired:
    fn, kind, tier, stmt = REBIRTH[old["id"]]
    rec = {"id": old["id"].replace("TH-","P-" ) if kind=="postulate" else "A0-GENESIS-BLOCK",
           "kind":kind,"tier":tier,"status":"SPECULATIVE","statement":stmt,
           "rebuilt_from":old["id"],"timestamp":ts,"prev":old.get("id")}
    plan.append((fn,rec))

print(f"[plan] retire {len(retired)} from theorems.jsonl -> attic/theorems.jsonl.{ts}.cosmo-retired")
for fn,rec in plan: print(f"[plan] append -> {fn}: {rec['id']} ({rec['kind']}, tier {rec['tier']})")
print(f"[plan] tier-tag {len(TIER2_TAG_AXIOMS)} axioms (SPECULATIVE)")

if not CONFIRM:
    print("[held] dry-run only. Re-run with COSMO_CONFIRM=1 to execute.")
    raise SystemExit(0)

os.makedirs(ATTIC, exist_ok=True)
shutil.copy(os.path.join(STORE,"theorems.jsonl"),
            os.path.join(ATTIC,f"theorems.jsonl.{ts}.cosmo-retired"))
write("theorems.jsonl", new_thm)
write("axioms.jsonl", new_axi)
for fn,rec in plan:
    with open(os.path.join(STORE,fn),"a") as f:
        f.write(json.dumps(rec,ensure_ascii=False)+"\n")
print(f"[banked] migration executed. attic backup: theorems.jsonl.{ts}.cosmo-retired")
print("[next] rebuild chain.jsonl, then: python3 /home/jesse/src/openroot/axiom_engine/chain_verify.py")
