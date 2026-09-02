#!/data/data/com.termux/files/usr/bin/env python3
"""OpenRoot Business v0.4 — Expense & Hardware Asset Tracker"""
import json,sys,os,datetime,argparse
from pathlib import Path

STATE=Path.home()/".openroot"/"state.json"

def ld():
    if not STATE.exists(): return {}
    return json.loads(STATE.read_text())

def sv(d):
    d.setdefault("meta",{})["updated"]=datetime.datetime.now().isoformat()
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(d,indent=2))

def ensure_biz(d):
    for k in ["expenses","hardware_assets"]:
        if k not in d: d[k]=[]
    return d

def add_expense(desc,amount,category):
    d=ensure_biz(ld())
    eid=f"EX-{len(d['expenses'])+1:03d}"
    d["expenses"].append({"id":eid,"desc":desc,"amount":float(amount),"category":category,"ts":datetime.datetime.now().isoformat()})
    sv(d)
    print(f"Logged {eid}: ${amount:.2f} — {desc} [{category}]")

def add_hw(hwid,status,desc,note,cost):
    d=ensure_biz(ld())
    existing={h["id"] for h in d["hardware_assets"]}
    if hwid in existing:
        for h in d["hardware_assets"]:
            if h["id"]==hwid:
                h["status"]=status;h["desc"]=desc;h["note"]=note;h["cost"]=float(cost)
                print(f"Updated {hwid}: {status} — {desc} (${cost:.2f})")
                break
    else:
        d["hardware_assets"].append({"id":hwid,"status":status,"desc":desc,"note":note,"cost":float(cost),"ts":datetime.datetime.now().isoformat()})
        print(f"Added {hwid}: {status} — {desc} (${cost:.2f})")
    sv(d)

def biz_report():
    d=ensure_biz(ld())
    exp=d.get("expenses",[])
    hw=d.get("hardware_assets",[])
    total_exp=sum(e["amount"] for e in exp)
    total_hw=sum(h["cost"] for h in hw)
    by_cat={}
    for e in exp:
        by_cat.setdefault(e["category"],0)
        by_cat[e["category"]]+=e["amount"]
    hw_status={}
    for h in hw:
        hw_status.setdefault(h["status"],0)
        hw_status[h["status"]]+=1
    print("="*50)
    print("  OPENROOT BUSINESS REPORT")
    print("="*50)
    print(f"\n  Expenses: {len(exp)} entries | Total: ${total_exp:.2f}")
    if by_cat:
        print("  By Category:")
        for cat,val in sorted(by_cat.items()):
            print(f"    {cat}: ${val:.2f}")
    print(f"\n  Hardware Assets: {len(hw)} items | Total: ${total_hw:.2f}")
    if hw_status:
        print("  By Status:")
        for st,cnt in sorted(hw_status.items()):
            print(f"    {st}: {cnt}")
    print(f"\n  Grand Total: ${total_exp+total_hw:.2f}")
    print("\n"+"="*50)

def main():
    p=argparse.ArgumentParser(prog="or-biz")
    sub=p.add_subparsers(dest="cmd")
    e=sub.add_parser("expense");e.add_argument("desc");e.add_argument("amount",type=float);e.add_argument("category")
    h=sub.add_parser("hardware");h.add_argument("id");h.add_argument("status");h.add_argument("desc");h.add_argument("note");h.add_argument("cost",type=float)
    sub.add_parser("report")
    a=p.parse_args()
    if a.cmd=="expense": add_expense(a.desc,a.amount,a.category)
    elif a.cmd=="hardware": add_hw(a.id,a.status,a.desc,a.note,a.cost)
    elif a.cmd=="report": biz_report()
    else: p.print_help()

if __name__=="__main__":
    main()
