#!/data/data/com.termux/files/usr/bin/env python3
"""OpenRoot v0.3 — Kingdom Engine (compact deployment)"""
import json,sys,os,math,datetime,argparse,hashlib
from pathlib import Path
STATE=Path.home()/".openroot"/"state.json"
LINEAGE=[{"id":"LG-001","node":"isaac_newton","epoch":"1687","discovery":"If I have seen further I stand on giants","built_upon":["LG-000"],"domain":"physics"},{"id":"LG-012","node":"you","epoch":"now","discovery":"Offline-first greatest-good reasoning engine","built_upon":["LG-001"],"domain":"systems"}]
PHI=1.61803398874989
def ld(): return {} if not STATE.exists() else json.loads(STATE.read_text())
def sv(d): d.setdefault("meta",{})["updated"]=datetime.datetime.now().isoformat();STATE.parent.mkdir(parents=True,exist_ok=True);STATE.write_text(json.dumps(d,indent=2))
def ensure_v03(d):
    for k in ["lineage","seed_banks","workshops","compound_rewards","patterns"]:
        if k not in d: d[k]=[]
    if not d.get("lineage"): d["lineage"]=list(LINEAGE)
    return d
def lineage_depth(d,node_id,visited=None):
    if visited is None: visited=set()
    if node_id in visited: return 0
    visited.add(node_id)
    lk={n["id"]:n for n in d.get("lineage",[])}
    if node_id not in lk: return 0
    parents=lk[node_id].get("built_upon",[])
    if not parents: return 1
    return 1+max(lineage_depth(d,p,visited.copy()) for p in parents)
def compound_reward(rewards):
    if not rewards: return 0.0,0.0,0.0
    base=sum(r.get("value",1.0) for r in rewards)
    coop=len(set(r.get("node_id","") for r in rewards))
    epochs=len(rewards)
    comp=base*(PHI**min(epochs,50))
    eff=max(comp/max(sum(r.get("hours",1.0) for r in rewards),0.01),0.0)
    return round(comp,6),round(eff,6),round(base,6)
def divine_resonance(d):
    phi=PHI
    assets=d.get("assets",[])
    rewards=d.get("compound_rewards",[])
    lineage=d.get("lineage",[])
    ratios=[a.get("benefit",1)/max(a.get("cost",1),0.01) for a in assets] if assets else [phi]
    phi_align=1.0-min(abs(sum(ratios)/len(ratios)-phi)/phi,1.0)
    coop_res=0.0
    sym_res=0.0
    if rewards:
        _,eff,_=compound_reward(rewards)
        coop_res=min(eff/phi,1.0)
        node_vals={}
        for r in rewards:
            nid=r.get("node_id","")
            v=r.get("value",1.0)
            node_vals.setdefault(nid,[]).append(v)
        if len(node_vals)>=2:
            avg=[sum(v)/len(v) for v in node_vals.values()]
            if max(avg)>0:
                sym_res=1.0-abs(min(avg)/max(avg)-1.0)
    ld_val=max((lineage_depth(d,lg["id"]) for lg in lineage),default=0) if lineage else 0
    lineage_score=min(ld_val/10.0,1.0)
    comp=(phi_align*0.2+coop_res*0.25+sym_res*0.2+lineage_score*0.35)
    interp="divine pattern emerging" if comp>0.7 else "approaching harmony" if comp>0.4 else "dissonant" if comp>0.1 else "silent"
    return {"phi_alignment":round(phi_align,4),"cooperation_resonance":round(coop_res,4),"symmetry":round(sym_res,4),"lineage_depth":round(lineage_score,4),"composite":round(comp,4),"interpretation":interp}

def main():
    p=argparse.ArgumentParser(prog="openroot")
    sub=p.add_subparsers(dest="cmd")
    sp=sub.add_parser("init");sp.add_argument("--force",action="store_true")
    sub.add_parser("status")
    ax=sub.add_parser("axiom");sa=ax.add_subparsers(dest="sc")
    aa=sa.add_parser("add");aa.add_argument("statement");aa.add_argument("--tag",default="")
    sa.add_parser("list")
    dd=sub.add_parser("deepdive");sd=dd.add_subparsers(dest="sc")
    rr=sd.add_parser("report");rr.add_argument("query");rr.add_argument("--output",default=None)
    kg=sub.add_parser("kingdom");skg=kg.add_subparsers(dest="sc")
    skg.add_parser("report")
    kr=skg.add_parser("resonance")
    lg=sub.add_parser("lineage");slg=lg.add_subparsers(dest="sc")
    slg.add_parser("list")
    sld=slg.add_parser("discover");sld.add_argument("name");sld.add_argument("discovery");sld.add_argument("--upon",default="LG-001")
    cb=sub.add_parser("compound");scb=cb.add_subparsers(dest="sc")
    cra=scb.add_parser("add");cra.add_argument("node_id");cra.add_argument("value",type=float);cra.add_argument("hours",type=float);cra.add_argument("description");cra.add_argument("--cooperators",default="")
    scb.add_parser("status")
    sb=sub.add_parser("seedbank");ssb=sb.add_subparsers(dest="sc")
    sba=ssb.add_parser("add");sba.add_argument("node_name");sba.add_argument("seed_count",type=int);sba.add_argument("varieties")
    ssb.add_parser("status")
    ws=sub.add_parser("workshop");sws=ws.add_subparsers(dest="sc")
    sws.add_parser("templates")
    swa=sws.add_parser("deploy");swa.add_argument("name");swa.add_argument("template")
    swa.add_argument("--x",default="0");swa.add_argument("--y",default="0");swa.add_argument("--z",default="0")
    sws.add_parser("list")
    sub.add_parser("patterns")
    ast=sub.add_parser("asset");sast=ast.add_subparsers(dest="sc")
    reg=sast.add_parser("register");reg.add_argument("name");reg.add_argument("x");reg.add_argument("y");reg.add_argument("z")
    reg.add_argument("--stage",default="operation");reg.add_argument("--slump",type=float,default=0.0)
    reg.add_argument("--benefit",type=float,default=1.0);reg.add_argument("--cost",type=float,default=1.0)
    reg.add_argument("--tier",type=int,default=0)
    sast.add_parser("list")
    sub.add_parser("schedule")
    sub.add_parser("good")
    tr=sub.add_parser("truth");str_=tr.add_subparsers(dest="sc")
    ta=str_.add_parser("add");ta.add_argument("assertion")
    str_.add_parser("list")
    args=p.parse_args()
    d=ld()
    if not d and args.cmd!="init":
        print("[openroot] Not initialized. Run: openroot init"); return
    d=ensure_v03(d)
    if args.cmd=="init":
        if d and not getattr(args,'force',False): print("[openroot] Already initialized. Use --force"); return
        d={"meta":{"version":"0.3.0","created":datetime.datetime.now().isoformat()},
           "axioms":[{"id":"AX-001","statement":"Reality is observable and measurable","tags":["epistemology"]},
                     {"id":"AX-008","statement":"Greatest good maximizes benefit with minimum expenditure","tags":["ethics"]},
                     {"id":"AX-011","statement":"Exponential cooperation compounds reward beyond linear summation","tags":["cooperation"]},
                     {"id":"AX-012","statement":"Each node holds enough for all nodes — survival approaches infinity","tags":["survival"]},
                     {"id":"AX-013","statement":"Knowledge compounds across generations — standing on giants","tags":["lineage"]},
                     {"id":"AX-014","statement":"Systems aligned with divine order (phi, Fibonacci) sustain longer","tags":["resonance"]}],
           "postulates":[{"id":"PO-001","statement":"Systems decompose into variables governed by axioms","from_axioms":["AX-001"]},
                         {"id":"PO-007","statement":"Compound reward = base × phi^epochs × cooperators","from_axioms":["AX-011"]},
                         {"id":"PO-009","statement":"Comfort = knowledge × efficiency × seeds × diversity / entropy","from_axioms":["AX-013","AX-008"]}],
           "coefficients":{"Ce":1.0,"Cr":0.618,"Cphi":1.618},
           "lineage":list(LINEAGE),"seed_banks":[],"workshops":[],"compound_rewards":[],
           "patterns":[],"assets":[],"truth_ledger":[],"reports":[],"comfort_index":0.0}
        sv(d)
        print(f"[openroot] v0.3 Kingdom Engine initialized @ {STATE}")
        print(f"  Axioms:{len(d['axioms'])}  Lineage:{len(d['lineage'])}  Workshops:0")
    elif args.cmd=="status":
        print(f"[openroot] Kingdom Engine v0.3")
        print(f"  Ver:{d.get('meta',{}).get('version','?')}")
        print(f"  Ax:{len(d.get('axioms',[]))}  Lineage:{len(d.get('lineage',[]))}")
        print(f"  Rewards:{len(d.get('compound_rewards',[]))}  Seeds:{len(d.get('seed_banks',[]))}")
        print(f"  Workshops:{len(d.get('workshops',[]))}  Comfort:{d.get('comfort_index',0.0)}")
    elif args.cmd=="lineage" and args.sc=="list":
        for lg in d.get("lineage",[]):
            dp=lineage_depth(d,lg["id"])
            parents=", ".join(lg.get("built_upon",[]))
            print(f"  {lg['id']} [{dp}up] {lg['node']} ({lg.get('epoch','?')})")
            print(f"    \"{lg['discovery'][:80]}\"")
            if parents: print(f"    Upon: {parents}")
    elif args.cmd=="lineage" and args.sc=="discover":
        upon=args.upon.split(",")
        lid=f"LG-{len(d.get('lineage',[]))+1:03d}"
        entry={"id":lid,"node":args.name,"epoch":"now","discovery":args.discovery,"built_upon":upon,"domain":""}
        d.setdefault("lineage",[]).append(entry); sv(d)
        dp=lineage_depth(d,lid)
        print(f"[openroot] Discovery: {lid}  Depth: {dp} generations  Upon: {args.upon}")
    elif args.cmd=="kingdom" and args.sc=="report":
        res=divine_resonance(d)
        ci=d.get("comfort_index",0.0)
        _,eff,raw=compound_reward(d.get("compound_rewards",[]))
        print("# OpenRoot Kingdom Report v0.3")
        print(f"  Divine Resonance: {res['composite']}  ({res['interpretation'][:50]})")
        print(f"  Comfort Index: {ci}")
        print(f"  Compound Reward: raw={raw} eff={eff}")
        print(f"  Lineage: {len(d.get('lineage',[]))} entries")
        print(f"  Seeds: {len(d.get('seed_banks',[]))} banks")
        print(f"  Workshops: {len(d.get('workshops',[]))} deployed")
    elif args.cmd=="kingdom" and args.sc=="resonance":
        res=divine_resonance(d)
        print(f"[openroot] Divine Resonance: {res['composite']}")
        print(f"  {res['interpretation']}")
    elif args.cmd=="compound" and args.sc=="add":
        coops=args.cooperators.split(",") if args.cooperators else []
        entry={"id":f"CB-{len(d.get('compound_rewards',[]))+1:04d}","node_id":args.node_id,"value":args.value,"hours":args.hours,"description":args.description,"cooperating_nodes":coops,"timestamp":datetime.datetime.now().isoformat()}
        d.setdefault("compound_rewards",[]).append(entry)
        total,eff,raw=compound_reward(d["compound_rewards"]); d["comfort_index"]=eff; sv(d)
        print(f"[openroot] Contribution {entry['id']}  Total:{total}  Eff:{eff}")
    elif args.cmd=="compound" and args.sc=="status":
        rw=d.get("compound_rewards",[])
        if not rw: print("[openroot] No contributions."); return
        total,eff,raw=compound_reward(rw)
        print(f"[openroot] Rewards: {len(rw)}  Raw:{raw}  Total:{total}  Eff:{eff}")
    elif args.cmd=="seedbank" and args.sc=="add":
        vars_=args.varieties.split(",")
        d.setdefault("seed_banks",[]).append({"node":args.node_name,"seed_count":args.seed_count,"varieties":vars_,"timestamp":datetime.datetime.now().isoformat()})
        sv(d); print(f"[openroot] Seeds: {args.seed_count}  Varieties: {len(vars_)}")
    elif args.cmd=="seedbank" and args.sc=="status":
        banks=d.get("seed_banks",[])
        total=sum(b.get("seed_count",0) for b in banks)
        varieties=set()
        for b in banks: varieties.update(b.get("varieties",[]))
        print(f"[openroot] Banks:{len(banks)}  Seeds:{total}  Varieties:{len(varieties)}")
    elif args.cmd=="workshop" and args.sc=="templates":
        templates=[
            ("forge","Resource refinement — converts raw assets into tier-upgraded outputs"),
            ("market","Trade exchange — pairs surplus nodes with deficit nodes"),
            ("observatory","Pattern detection — scans truths + assets for emergent structures"),
            ("sanctuary","Resilience vault — stores seed backups + truth copies for node recovery")
        ]
        print("[openroot] Workshop Templates:")
        for name,desc in templates:
            print(f"  {name:12} — {desc}")
    elif args.cmd=="workshop" and args.sc=="deploy":
        valid=["forge","market","observatory","sanctuary"]
        if args.template not in valid:
            print(f"[openroot] Unknown template: {args.template}. Valid: " + ", ".join(valid)); return
        d.setdefault("workshops",[]).append({"name":args.name,"template":args.template,"coords":[args.x,args.y,args.z],"deployed":datetime.datetime.now().isoformat()})
        sv(d)
        print(f"[openroot] Workshop '{args.name}' ({args.template}) deployed @ ({args.x},{args.y},{args.z})")

    elif args.cmd=="workshop" and args.sc=="list":
        ws_list=d.get("workshops",[])
        print(f"[openroot] {len(ws_list)} workshops") if ws_list else print("[openroot] None deployed")
        for w in ws_list: print(f"  {w.get('name','?')} | {w.get('template','?')}")
    elif args.cmd=="patterns":
        print("[openroot] Pattern detection requires 3+ assets/truths. Add more data.")
    elif args.cmd=="asset" and args.sc=="register":
        d.setdefault("assets",[]).append({"name":args.name,"coords":[float(args.x),float(args.y),float(args.z)],"stage":args.stage,"slump":args.slump,"benefit":args.benefit,"cost":args.cost,"protection_tier":args.tier})
        sv(d); print(f"[openroot] Asset: {args.name} @ ({args.x},{args.y},{args.z}) T{args.tier}")
    elif args.cmd=="asset" and args.sc=="list":
        for a in d.get("assets",[]): print(f"  {a['name']} ({a.get('coords',[0,0,0])}) T{a.get('protection_tier',0)}")
    elif args.cmd=="truth" and args.sc=="add":
        h=hashlib.sha256(args.assertion.encode()).hexdigest()[:16]
        d.setdefault("truth_ledger",[]).append({"hash":h,"assertion":args.assertion,"status":"unverified","timestamp":datetime.datetime.now().isoformat()})
        sv(d); print(f"[openroot] Truth: {h}")
    elif args.cmd=="truth" and args.sc=="list":
        for t in d.get("truth_ledger",[]): print(f"  {t['hash']} \"{t['assertion'][:60]}\"")
    elif args.cmd=="axiom" and args.sc=="add":
        aid=f"AX-{len(d.get('axioms',[]))+1:03d}"
        d.setdefault("axioms",[]).append({"id":aid,"statement":args.statement,"tags":args.tag.split(",") if args.tag else []})
        sv(d); print(f"[openroot] Added {aid}")
    elif args.cmd=="axiom" and args.sc=="list":
        for a in d.get("axioms",[]): print(f"  {a['id']}: {a['statement']}")
    elif args.cmd=="deepdive" and args.sc=="report":
        kw=set(args.query.lower().replace("?","").replace(".","").split())
        ax_=[a for a in d.get("axioms",[]) if any(k in a["statement"].lower() for k in kw)]
        res=divine_resonance(d)
        print(f"# Deep Dive: {args.query}")
        print(f"  Relevant axioms: {len(ax_)}")
        print(f"  Divine resonance: {res['composite']}")
        print(f"  Comfort: {d.get('comfort_index',0.0)}")
        if d.get("compound_rewards"):
            _,eff,_=compound_reward(d["compound_rewards"])
            print(f"  Compound efficiency: {eff}")
        d.setdefault("reports",[]).append({"query":args.query,"time":datetime.datetime.now().isoformat()})
    sv(d)

if __name__=="__main__":main()
