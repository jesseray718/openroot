#!/usr/bin/env python3
"""Thermodynamic ledger on SQLite — instrumented joules only."""
import sqlite3, sys, datetime, os

DB = "/data/data/com.termux/files/home/openroot/ledger/thermo.db"

def connect():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            type TEXT NOT NULL,          -- heat, cold, mech, elec, human, cpu
            joules REAL NOT NULL,
            kwh REAL NOT NULL,
            note TEXT
        )
    """)
    conn.commit()
    return conn

def record(work_type, joules, note=""):
    assert work_type in ("heat", "cold", "mech", "elec", "human", "cpu")
    kwh = joules / 3_600_000
    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    conn = connect()
    conn.execute(
        "INSERT INTO entries (ts, type, joules, kwh, note) VALUES (?, ?, ?, ?, ?)",
        (ts, work_type, float(joules), kwh, note)
    )
    conn.commit()
    conn.close()
    print(f"Recorded {joules:.1f} J ({kwh:.6f} kWh) [{work_type}] {note}")

def summary():
    conn = connect()
    rows = conn.execute(
        "SELECT type, SUM(joules), SUM(kwh) FROM entries GROUP BY type"
    ).fetchall()
    conn.close()
    print("\n=== LEDGER SUMMARY ===")
    total_useful = 0.0
    human = 0.0
    for typ, j, k in rows:
        print(f"{typ:8} {j:12.1f} J   {k:10.6f} kWh")
        if typ in ("mech", "elec"):
            total_useful += k
        elif typ in ("heat", "cold"):
            total_useful += 0.3 * k          # simple exergy weight
        elif typ == "human":
            human = k
    eta = total_useful / human if human > 0 else 0
    print(f"η (useful/human) ≈ {eta:.3f}")
    print("======================\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        summary()
        sys.exit(0)
    if sys.argv[1] == "summary":
        summary()
        sys.exit(0)
    if len(sys.argv) < 3:
        print("Usage:  thermo_ledger_sqlite.py <type> <joules> [note]")
        print("        thermo_ledger_sqlite.py summary")
        sys.exit(1)
    note = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
    record(sys.argv[1], float(sys.argv[2]), note)
