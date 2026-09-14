#!/usr/bin/env python3
"""rc_circuit.py — RC low-pass + McCulloch-Pitts gate task-selection circuit."""
import hashlib, json, os, time

ROOT   = os.environ.get("RC_ROOT", "/home/jesse/src/openroot")
SEALS  = os.path.join(ROOT, "circuits", "seals")
LEDGER = os.path.join(SEALS, "rc_circuit_seals.jsonl")
TODAY  = time.strftime("%Y-%m-%d")

TASKS = [
    dict(id="rotate_scrub",  desc="read + rotate + scrub uri_credentials", r=0.188, ent=3, age=1,   cl=1.0),
    dict(id="prepaid_totp",  desc="prepaid-number + TOTP",                  r=0.200, ent=1, age=30,  cl=0.8),
    dict(id="spec_pay_demo", desc="spec machine-to-machine payment demo",  r=0.444, ent=1, age=7,   cl=0.7),
    dict(id="lock_four",     desc="lock four sentences",                    r=0.500, ent=1, age=3,   cl=0.9),
    dict(id="builder_apps",  desc="builder-program applications",           r=0.750, ent=1, age=14,  cl=0.5),
    dict(id="acre_devnet",   desc="ACRE hello-world on devnet",             r=1.333, ent=0, age=60,  cl=0.4),
    dict(id="sim_script",    desc="simulation script",                      r=2.400, ent=1, age=90,  cl=0.3),
]

def rc_lowpass(raw, dt=1.0, tau=4.0, prior=None):
    v = prior if prior is not None else raw
    return v + (dt / tau) * (raw - v)

def mp_gate(inputs, weights, theta):
    z = sum(i * w for i, w in zip(inputs, weights))
    return (1, z) if z >= theta else (0, z)

def fire_gates(t):
    feat = [t["r"], t["ent"], min(t["age"], 90) / 90.0, t["cl"]]
    urgency, _zu = mp_gate(feat, [-2.0, 0.0, 1.5, 0.0], -0.25)
    clarity, _zc = mp_gate(feat, [0.0, 0.0, 0.0, 1.8], 0.9)
    energy,  _ze = mp_gate(feat, [-0.8, -0.5, 0.0, 0.0], -0.5)
    return urgency, clarity, energy

def gated_resistance(t):
    u, c, e = fire_gates(t)
    smooth = rc_lowpass(t["r"])
    discount = 0.85 ** (u + c + e)
    return smooth * discount, (u, c, e)

def load_ledger():
    os.makedirs(SEALS, exist_ok=True)
    prev, done_today = "GENESIS", set()
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                prev = rec.get("seal", prev)
                if rec.get("date") == TODAY:
                    done_today.add(rec.get("task"))
    return prev, done_today

def seal(prev, payload):
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev + blob).encode()).hexdigest()

def main():
    t0, ops = time.time(), 0
    prev, done_today = load_ledger()

    scored = []
    for t in TASKS:
        gr, gates = gated_resistance(t)
        scored.append((gr, t, gates))
        ops += 6
    scored.sort(key=lambda s: s[0])

    ranked, chosen = [], None
    for gr, t, gates in scored:
        skipped = t["id"] in done_today
        ranked.append((t["id"], round(gr, 4), "SKIP(done-today)" if skipped else "live"))
        if chosen is None and not skipped:
            chosen = t

    if chosen is None:
        print("[circuit] all tasks sealed today — nothing to fire.")
        return

    gr = dict((s[1]["id"], s[0]) for s in scored)[chosen["id"]]
    payload = dict(date=TODAY, task=chosen["id"], desc=chosen["desc"],
                   gated_resistance=round(gr, 4), raw_resistance=chosen["r"], prev=prev)
    s = seal(prev, payload)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(dict(payload, seal=s)) + "\n")

    dt = time.time() - t0
    print("[circuit] RC+MP winner-take-all ranking (lower = less resistance):")
    for tid, g, stat in ranked:
        mark = " <- FIRE" if tid == chosen["id"] else ""
        print("   {:>8.4f}  {:<14} {}{}".format(g, tid, stat, mark))
    print("[seal-chain] prev={}... new={}...".format(prev[:12], s[:16]))
    print("[ledger] " + LEDGER)
    print("[perf] {} ops in {:.4f}s = {:,.0f} ops/s".format(ops, dt, ops / max(dt, 1e-9)))
    print("[next-move] " + chosen["desc"])

if __name__ == "__main__":
    main()
