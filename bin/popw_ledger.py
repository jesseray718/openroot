#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
"""POPW ledger: account tokens + joules for every model call.
RAPL microjoules when readable; TDP*walltime estimate fallback (tagged 'estimate',
never asserted as measured). Commands:
  call <stage> <model> [prompt words...] [--stdin]   # runs call, prints response + [POPW] line to stderr
  report                                             # per-stage + total tokens/joules, J per eval token
"""
import glob, json, os, sqlite3, sys, time, urllib.request

DB = "/home/jesse/openroot/data/popw_ledger.db"
OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
TDP_W = float(os.environ.get("POPW_TDP_W", "65"))  # OptiPlex 3060 CPU TDP fallback
TIMEOUT = int(os.environ.get("POPW_TIMEOUT", "400"))

def rapl_read():
    d = {}
    for p in sorted(glob.glob("/sys/class/powercap/intel-rapl*/energy_uj")):
        try:
            with open(p) as f: d[p] = int(f.read().strip())
        except OSError: pass
    return d

def delta_joules(b, a):
    t = 0.0
    for k, v in b.items():
        w = a.get(k)
        if w is None: continue
        t += (w - v) if w >= v else ((1 << 32) - v + w)  # wraparound
    return t / 1e6

def call(stage, model, prompt):
    b = rapl_read(); t0 = time.monotonic()
    req = urllib.request.Request(f"{OLLAMA}/api/generate",
        data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        resp = json.loads(r.read())
    wall = time.monotonic() - t0
    j = delta_joules(b, rapl_read()) if b else TDP_W * wall
    src = "rapl" if b else "estimate"
    db = sqlite3.connect(DB)
    db.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, ts TEXT, stage TEXT,
        model TEXT, prompt_tokens INT, eval_tokens INT, joules REAL, wall_s REAL, source TEXT)""")
    db.execute("INSERT INTO events(ts,stage,model,prompt_tokens,eval_tokens,joules,wall_s,source) VALUES(?,?,?,?,?,?,?,?)",
        (time.strftime("%Y-%m-%dT%H:%M:%S"), stage, model,
         resp.get("prompt_eval_count") or 0, resp.get("eval_count") or 0, j, wall, src))
    db.commit()
    return resp, j, src, wall

def main():
    a = sys.argv[1:]
    if a[:1] == ["report"]:
        db = sqlite3.connect(DB)
        try:
            rows = db.execute("SELECT stage,COUNT(*),SUM(prompt_tokens),SUM(eval_tokens),SUM(joules) FROM events GROUP BY stage").fetchall()
        except sqlite3.OperationalError:
            rows = []
        tt = tj = 0
        for st, n, pt, et, j in rows:
            print(f"[{st}] calls={n} prompt_tok={pt} eval_tok={et} joules={(j or 0):.0f}J")
            tt += et or 0; tj += j or 0
        if tt: print(f"[TOTAL] eval_tok={tt} J={tj:.0f} efficiency={tj/tt:.3f} J/eval_token (source tagged per-event)")
        else: print("[EMPTY] no events recorded yet")
        return
    if a[:1] == ["call"]:
        assert len(a) >= 3, "call <stage> <model> [prompt...] [--stdin]"
        stage, model = a[1], a[2]
        words = [x for x in a[3:] if x != "--stdin"]
        prompt = " ".join(words)
        if "--stdin" in a: prompt = (prompt + "\n" + sys.stdin.read()).strip()
        resp, j, src, wall = call(stage, model, prompt)
        print(resp.get("response", ""))
        print(f"[POPW] {resp.get('eval_count',0)} tok | {j:.1f} J ({src}) | {wall:.1f}s", file=sys.stderr)
        return
    print(__doc__)

if __name__ == "__main__": main()
