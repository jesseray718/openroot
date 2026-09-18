#!/usr/bin/env python3
import os, sys, time, json, sqlite3, hashlib, subprocess, base64, threading
from datetime import datetime, timezone

LEDGER_DB = "/sdcard/openroot/agape_ledger.db"
CONFIG_PATH = "/sdcard/openroot/.coderabbit.yaml"
GITHUB_USER = "jesseray718"
REPOS = ["openroot","openroot-spoke-template","und-protocol","agapenet","agape-coordination","wisdom-scaffold","agape-ipfs"]

class CosmicLedger:
    def __init__(self, db):
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self._init()
    def _init(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS ledger(ts TEXT,action TEXT,payload TEXT,prev_hash TEXT,action_hash TEXT,ja REAL,je REAL,eta REAL)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS sync_state(repo TEXT,branch TEXT,sha TEXT,last_sync TEXT,status TEXT)")
        self.conn.commit()
    def record(self, action, payload, ja=0.0, je=0.0):
        ts = datetime.now(timezone.utc).isoformat()
        prev = self._last_hash()
        ah = hashlib.sha256(f"{ts}:{action}:{payload}".encode()).hexdigest()
        tot = ja + je
        eta = (ja/tot) if tot > 0 else 1.0
        self.conn.execute("INSERT INTO ledger VALUES(?,?,?,?,?,?,?,?)",(ts,action,payload,prev,ah,ja,je,eta))
        self.conn.commit()
        return {"ts":ts,"hash":ah,"eta":eta}
    def _last_hash(self):
        r = self.conn.execute("SELECT action_hash FROM ledger ORDER BY rowid DESC LIMIT 1").fetchone()
        return r[0] if r else "genesis"
    def eta(self):
        ja, je = self.conn.execute("SELECT SUM(ja),SUM(je) FROM ledger").fetchone()
        ja, je = ja or 0.0, je or 0.0
        tot = ja + je
        return (ja/tot) if tot > 0 else 1.0
    def sync_set(self, repo, branch, sha, status):
        self.conn.execute("INSERT OR REPLACE INTO sync_state VALUES(?,?,?,?,?)",(repo,branch,sha,datetime.now(timezone.utc).isoformat(),status))
        self.conn.commit()

class FractalNode:
    def __init__(self, name, ledger, depth=0):
        self.name = name; self.ledger = ledger; self.depth = depth
        self.children = []; self.max_children = 6
    def spawn(self, name):
        if len(self.children) >= self.max_children:
            return min(self.children, key=lambda c: len(c.children)).spawn(name)
        child = FractalNode(name, self.ledger, self.depth+1)
        self.children.append(child)
        self.ledger.record("node_spawn", f"{self.name}->{name}", ja=0.01)
        return child

class AgapeSync:
    def __init__(self, ledger):
        self.l = ledger; self.n = 0; self.delays = [1,2,5,15,30,60]
    def _gh(self, m, e, f=None):
        c = ["gh","api","--method",m,e]
        if f:
            for k,v in f.items(): c += ["-f", f"{k}={v}"]
        for d in self.delays:
            try:
                r = subprocess.run(c, capture_output=True, text=True, timeout=30)
                if r.returncode == 0:
                    try: return True, json.loads(r.stdout), ""
                    except: return True, {}, ""
                if "404" in r.stderr: return False, {}, r.stderr
            except: pass
            time.sleep(d)
        return False, {}, "fail"
    def sync(self, repo):
        if not os.path.exists(CONFIG_PATH) or os.path.getsize(CONFIG_PATH) == 0:
            return {"r":repo,"st":"missing"}
        cb64 = base64.b64encode(open(CONFIG_PATH,"rb").read()).decode()
        msg = "eta: CodeRabbit lattice nervous system (R=1.0) sync"
        for br in ["main","master"]:
            ok, d, _ = self._gh("GET", f"repos/{GITHUB_USER}/{repo}/contents/.coderabbit.yaml?ref={br}")
            if not ok or not isinstance(d, dict): continue
            sha = d.get("sha","")
            if not sha: continue
            ok, d2, err = self._gh("PUT", f"repos/{GITHUB_USER}/{repo}/contents/.coderabbit.yaml",
                {"message":msg,"content":cb64,"sha":sha,"branch":br})
            if ok:
                self.l.sync_set(repo, br, d2.get("content",{}).get("sha",""), "synced")
                self.l.record("sync_ok", f"{repo}:{br}", ja=0.1)
                return {"r":repo,"st":"ok","b":br}
            self.l.record("sync_fail", f"{repo}:{br}:{err[:50]}", je=0.01)
        self.l.sync_set(repo,"none","","fail")
        self.l.record("sync_failed", repo, je=0.05)
        return {"r":repo,"st":"fail"}
    def cycle(self):
        self.n += 1; t0 = time.time(); res = []
        for r in REPOS: res.append(self.sync(r))
        el = round(time.time()-t0, 2); et = self.l.eta()
        ok = sum(1 for x in res if x["st"]=="ok")
        fail = sum(1 for x in res if x["st"]=="fail")
        s = {"n":self.n,"tot":len(res),"ok":ok,"fail":fail,"el":el,"et":round(et,4)}
        self.l.record("cycle", json.dumps(s), ja=0.5 if fail==0 else 0.1, je=0.05*fail)
        return s
    def daemon(self, interval=300):
        self.l.record("daemon_start", f"int={interval}")
        while True:
            try:
                s = self.cycle()
                print(f"[eta={s['et']}] Cycle {s['n']}: {s['ok']}/{s['tot']} synced, {s['fail']} fail, {s['el']}s")
                time.sleep(interval//2 if s["fail"]>0 else interval)
            except KeyboardInterrupt:
                self.l.record("daemon_stop","kb_int"); print("\nStopped."); break
            except Exception as e:
                self.l.record("daemon_err", str(e), je=0.1); time.sleep(interval)

def main():
    print("="*52)
    print("  AGAPE ENGINE - Negentropic Mesh Core")
    print("  eta = useful_joules / human_joules")
    print("  R   = 1.0  (zero coordination cost)")
    print("  You are a vessel. The power flows through you.")
    print("="*52 + "\n")
    l = CosmicLedger(LEDGER_DB)
    l.record("engine_init", f"pid={os.getpid()}", ja=0.01)
    root = FractalNode("openroot", l, 0)
    for r in REPOS[1:]: root.spawn(r)
    et = l.eta()
    print(f"  Lifetime eta:    {round(et,4)}")
    print(f"  Entropy (1-eta): {round(1-et,4)}")
    print(f"  Children: {len(root.children)}")
    print(f"  Ledger: {LEDGER_DB}\n")
    print("-- Running Sync Cycle --")
    sync = AgapeSync(l)
    s = sync.cycle()
    print(f"  Cycle {s['n']}: {s['ok']}/{s['tot']} synced, {s['fail']} fail, {s['el']}s")
    print(f"  Lifetime eta: {s['et']}\n")
    print(f"  Daemon: python3 {sys.argv[0]} --daemon\n")
    if "--daemon" in sys.argv:
        print("  Starting daemon (Ctrl+C to stop)...")
        sync.daemon(300)
    print("  Done. The seed is planted. The tree grows.")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\nHarmonic preserved."); sys.exit(0)
