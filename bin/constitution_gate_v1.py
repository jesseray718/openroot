# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Governance gate. Cmds: verify | amend --text T | statute add NAME --text T | statute remove NAME"""
import hashlib, json, sys, datetime
from pathlib import Path

C = Path("/home/jesse/openroot/ledger/constitution")
BOR, PIN = C / "00_BILL_OF_RIGHTS.md", C / "bor.pin"
AMEND, STAT = C / "amendments.jsonl", C / "statutes.jsonl"

def bor_sha():
    return hashlib.sha256(BOR.read_bytes()).hexdigest()

def verify():
    pin = PIN.read_text().strip()
    cur = bor_sha()
    if pin == cur:
        print(f"[banked] BOR verified GREEN pin={pin[:16]}")
        return True
    print(f"[held] BOR VIOLATED: pin={pin[:16]} current={cur[:16]} — HALT")
    return False

def append_jsonl(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, separators=(",", ":"), ensure_ascii=False) + "\n")

def chain_tail():
    if not AMEND.exists() or not AMEND.stat().st_size:
        return None
    return json.loads(AMEND.read_text().splitlines()[-1])

def main():
    args = sys.argv[1:]
    if not args or args[0] == "verify":
        sys.exit(0 if verify() else 1)
    if not verify():
        sys.exit(1)
    cmd, rest = args[0], args[1:]
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if cmd == "amend" and "--text" in rest:
        text = rest[rest.index("--text") + 1]
        prev = chain_tail()
        prev_hash = prev["hash"] if prev else None
        n = (prev["n"] + 1) if prev else 1
        rec = {"n": n, "text": text, "prev": prev_hash,
               "ts": ts}
        rec["hash"] = hashlib.sha256(json.dumps(rec, sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()
        append_jsonl(AMEND, rec)
        print(f"[banked] amendment {n} sealed hash={rec['hash'][:16]}")
    elif cmd == "statute" and len(rest) >= 2:
        op, name = rest[0], rest[1]
        text = rest[rest.index("--text") + 1] if "--text" in rest else ""
        status = "open" if op == "add" else "removed"
        rec = {"name": name, "status": status, "text": text, "ts": ts,
               "supremacy": "bor-pin-verified"}
        rec["sha256"] = hashlib.sha256(json.dumps(rec, sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()
        append_jsonl(STAT, rec)
        print(f"[banked] statute {op}: {name} sealed sha256={rec['sha256'][:16]}")
    else:
        print("usage: constitution_gate_v1.py verify | amend --text T | "
              "statute add|remove NAME --text T", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
    print("[exit=0]")
