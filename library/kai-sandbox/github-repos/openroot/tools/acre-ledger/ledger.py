#!/data/data/com.termux/files/usr/bin/env python
"""ACRE PoPW Ledger — minimal, immediately usable on Termux."""
import sqlite3, sys, argparse
from datetime import datetime
DB = "acre_ledger.db"

def init():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS work_logs (
        id INTEGER PRIMARY KEY, ts TEXT, work_type TEXT, description TEXT,
        units REAL, verified_by TEXT, verified INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS token_mints (
        id INTEGER PRIMARY KEY, work_id INTEGER, amount REAL, ts TEXT,
        FOREIGN KEY(work_id) REFERENCES work_logs(id))""")
    conn.commit(); conn.close()

def log_work(wtype, desc, units, verifier):
    init()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO work_logs (ts,work_type,description,units,verified_by) VALUES (?,?,?,?,?)",
              (datetime.utcnow().isoformat(), wtype, desc, units, verifier))
    conn.commit()
    wid = c.lastrowid
    conn.close()
    print(f"Logged work #{wid}: {wtype} — {units} units")

def verify(wid, verifier):
    init()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE work_logs SET verified=1, verified_by=? WHERE id=?", (verifier, wid))
    conn.commit(); conn.close()
    print(f"Work #{wid} verified by {verifier}")

def mint(wid, rate=10.0):
    init()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT verified FROM work_logs WHERE id=?", (wid,))
    row = c.fetchone()
    if not row or row[0] != 1:
        print("Work not verified — cannot mint"); return
    amount = rate
    c.execute("INSERT INTO token_mints (work_id,amount,ts) VALUES (?,?,?)",
              (wid, amount, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
    print(f"Minted {amount} ACRE for verified work #{wid}")

def balance():
    init()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM token_mints")
    total = c.fetchone()[0] or 0.0
    conn.close()
    print(f"Total ACRE minted: {total}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="ACRE PoPW Ledger")
    p.add_argument("cmd", choices=["log","verify","mint","balance"])
    p.add_argument("--wtype", default="NodeZero_cure")
    p.add_argument("--desc", default="")
    p.add_argument("--units", type=float, default=1.0)
    p.add_argument("--verifier", default="NodeZero")
    p.add_argument("--wid", type=int, default=0)
    args = p.parse_args()
    if args.cmd == "log":
        log_work(args.wtype, args.desc, args.units, args.verifier)
    elif args.cmd == "verify":
        verify(args.wid, args.verifier)
    elif args.cmd == "mint":
        mint(args.wid)
    elif args.cmd == "balance":
        balance()
