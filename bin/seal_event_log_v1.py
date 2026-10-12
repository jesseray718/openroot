#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""seal_event_log_v1.py — HMAC-signed append-only event log.
Usage: seal_event_log_v1.py append '<json>' | validate | status"""
import hmac, hashlib, json, os, secrets, sys, time
KEY = os.path.expanduser("~/.openroot_receipt_key")
LOG = "/home/jesse/openroot/data/receipt_events.jsonl"

def load_key():
    if not os.path.exists(KEY):
        with open(KEY, "w") as f:
            f.write(secrets.token_hex(32))
        os.chmod(KEY, 0o600)
    return open(KEY).read().strip().encode()

def canon(ev):
    core = {k: ev[k] for k in sorted(ev) if k != "sig"}
    return json.dumps(core, sort_keys=True, separators=(",", ":")).encode()

def rows():
    if not os.path.exists(LOG):
        return []
    with open(LOG) as f:
        return [json.loads(l) for l in f if l.strip()]

def cmd_append(payload):
    ev = json.loads(payload)
    ev.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    ev["sig"] = hmac.new(load_key(), canon(ev), hashlib.sha256).hexdigest()
    with open(LOG, "a") as f:
        f.write(json.dumps(ev, sort_keys=True) + "\n")
    print("[banked] event sealed sig=%s" % ev["sig"][:12])
    return 0

def cmd_validate():
    rs, ok, bad = rows(), 0, []
    for i, ev in enumerate(rs):
        try:
            expect = hmac.new(load_key(), canon(ev), hashlib.sha256).hexdigest()
            if ev.get("sig") == expect:
                ok += 1
            else:
                bad.append((i, "SIG_MISMATCH"))
        except Exception as e:
            bad.append((i, "PARSE:%s" % e))
    print("rows=%d valid=%d bad=%d" % (len(rs), ok, len(bad)))
    for i, r in bad:
        print("[held] row %d %s" % (i, r))
    return 1 if bad else 0

def cmd_status():
    rs = rows()
    last = rs[-1]["ts"] if rs else "-"
    print("events=%d last_ts=%s key=%s" % (
        len(rs), last, "present" if os.path.exists(KEY) else "missing"))

if __name__ == "__main__":
    cmds = {"append": cmd_append, "validate": cmd_validate, "status": cmd_status}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit("usage: append '<json>'|validate|status")
    sys.exit(cmds[sys.argv[1]](*sys.argv[2:]))
