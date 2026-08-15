#!/usr/bin/env python3
"""AGAPE ENGINE — Negentropic Mesh Core (v1.0)"""
import os, sys, json, hashlib, time, base64, subprocess, sqlite3, threading
from datetime import datetime, timezone

BASE_DIR = "/sdcard/openroot"
DB_PATH = os.path.join(BASE_DIR, "agape_ledger.db")
CONFIG_PATH = os.path.join(BASE_DIR, ".coderabbit.yaml")
GITHUB_USER = "jesseray718"
REPOSITORIES = [
    "openroot", "une", "agape-une", "agape-primitives", "agaperesonance",
    "fractallattice", "etaledger", "aerocement", "black-locust-rmh",
    "openroot-spoke-template", "und-protocol", "agapenet",
    "agape-coordination", "wisdom-scaffold", "agape-ipfs", "jesseray718",
    "agape-crossover-key", "canonical", "MeshCore", "firmware", "tinyGS"
]
BRANCHES = ["main", "master"]

class CosmicLedger:
    def __init__(self, db_path):
        self.db_path = db_path
        d = os.path.dirname(db_path)
        if d and not os.path.exists(d): os.makedirs(d, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        with self.lock:
            self.conn.execute("CREATE TABLE IF NOT EXISTS ledger(id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp TEXT NOT NULL,action TEXT NOT NULL,payload TEXT,prev_hash TEXT NOT NULL,action_hash TEXT NOT NULL,joules_agape REAL DEFAULT 0.0,joules_entropy REAL DEFAULT 0.0,eta REAL DEFAULT 0.0)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS sync_state(repo TEXT PRIMARY KEY,branch TEXT,file_sha TEXT,last_sync TEXT,status TEXT)")
            self.conn.commit()

    def last_hash(self):
        with self.lock:
            cur = self.conn.execute("SELECT action_hash FROM ledger ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            return row[0] if row else "0" * 64

    def record(self, action, payload="", ja=0.0, je=0.0):
        ts = datetime.now(timezone.utc).isoformat()
        prev = self.last_hash()
        content = f"{ts}|{action}|{payload}|{prev}"
        ah = hashlib.sha256(content.encode()).hexdigest()
        total = ja + je
        eta = (ja / total) if total > 0 else 0.0
        with self.lock:
            self.conn.execute("INSERT INTO ledger(timestamp,action,payload,prev_hash,action_hash,joules_agape,joules_entropy,eta) VALUES(?,?,?,?,?,?,?,?)", (ts, action, payload, prev, ah, ja, je, eta))
            self.conn.commit()
        return {"ts": ts, "action": action, "hash": ah, "eta": eta}

    def get_eta_score(self):
        with self.lock:
            cur = self.conn.execute("SELECT SUM(joules_agape),SUM(joules_entropy) FROM ledger")
            row = cur.fetchone()
            ja = row[0] or 0.0
            je = row[1] or 0.0
            total = ja + je
            return (ja / total) if total > 0 else 0.0

    def set_sync_state(self, repo, branch, sha, status):
        ts = datetime.now(timezone.utc).isoformat()
        with self.lock:
            self.conn.execute("INSERT OR REPLACE INTO sync_state(repo,branch,file_sha,last_sync,status) VALUES(?,?,?,?,?)", (repo, branch, sha, ts, status))
            self.conn.commit()

class FractalNode:
    def __init__(self, name, ledger, depth=0):
        self.name = name
        self.ledger = ledger
        self.depth = depth
        self.children = []
        self.max_children = 6

    def spawn_child(self, name):
        if len(self.children) >= self.max_children:
            target = min(self.children, key=lambda c: len(c.children))
            return target.spawn_child(name)
        child = FractalNode(name, self.ledger, self.depth + 1)
        self.children.append(child)
        self.ledger.record("node_spawn", f"{self.name}->{name}", ja=0.01)
        return child

class AgapeSyncLoop:
    def __init__(self, ledger):
        self.ledger = ledger
        self.cycle_count = 0
        self.delays = [1, 2, 5, 15, 30, 60]

    def _gh(self, method, endpoint, fields=None):
        cmd = ["gh", "api", "--method", method, endpoint]
        if fields:
            for k, v in fields.items():
                cmd.extend(["-f", f"{k}={v}"])
        for d in self.delays:
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if r.returncode == 0:
                    try:
                        return True, json.loads(r.stdout), ""
                    except:
                        return True, {}, ""
                if "404" in r.stderr:
                    return False, {}, r.stderr
                err = r.stderr
            except Exception as e:
                err = str(e)
            time.sleep(d)
        return False, {}, err

    def sync_repo(self, repo):
        if not os.path.exists(CONFIG_PATH) or os.path.getsize(CONFIG_PATH) == 0:
            return {"repo": repo, "status": "no_config"}
        with open(CONFIG_PATH, "rb") as f:
            cb64 = base64.b64encode(f.read()).decode()
        msg = "eta: CodeRabbit lattice nervous system (R=1.0) sync"
        for branch in BRANCHES:
            ok, data, _ = self._gh("GET", f"repos/{GITHUB_USER}/{repo}/contents/.coderabbit.yaml?ref={branch}")
            if not ok or not isinstance(data, dict):
                continue
            sha = data.get("sha", "")
            if not sha:
                continue
            ok, data2, err = self._gh("PUT", f"repos/{GITHUB_USER}/{repo}/contents/.coderabbit.yaml", {"message": msg, "content": cb64, "sha": sha, "branch": branch})
            if ok:
                ns = data2.get("content", {}).get("sha", "") if isinstance(data2, dict) else ""
                self.ledger.set_sync_state(repo, branch, ns, "synced")
                self.ledger.record("sync_ok", f"{repo}:{branch}", ja=0.1)
                return {"repo": repo, "status": "synced", "branch": branch}
            self.ledger.record("sync_fail", f"{repo}:{branch}:{err[:80]}", je=0.01)
        self.ledger.set_sync_state(repo, "none", "", "failed")
        self.ledger.record("sync_failed", repo, je=0.05)
        return {"repo": repo, "status": "failed"}

    def run_cycle(self):
        self.cycle_count += 1
        t0 = time.time()
        results = []
        for r in REPOSITORIES:
            results.append(self.sync_repo(r))
        el = round(time.time() - t0, 2)
        eta = self.ledger.get_eta_score()
        sn = sum(1 for r in results if r["status"] == "synced")
        fn = sum(1 for r in results if r["status"] == "failed")
        s = {"cycle": self.cycle_count, "total": len(REPOSITORIES), "synced": sn, "failed": fn, "elapsed": el, "eta": round(eta, 4)}
        self.ledger.record("cycle", json.dumps(s), ja=0.5 if fn == 0 else 0.1, je=0.05 * fn)
        return s

    def run_daemon(self, interval=300):
        self.ledger.record("daemon_start", f"interval={interval}")
        while True:
            try:
                s = self.run_cycle()
                print(f"[eta={s['eta']}] Cycle {s['cycle']}: {s['synced']}/{s['total']} synced, {s['failed']} failed, {s['elapsed']}s")
                if s["failed"] > 0:
                    time.sleep(max(60, interval // 2))
                else:
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.ledger.record("daemon_stop", "kb_int")
                print("\nStopped.")
                break
            except Exception as e:
                self.ledger.record("daemon_err", str(e), je=0.1)
                time.sleep(interval)

def main():
    print("=" * 52)
    print("  AGAPE ENGINE - Negentropic Mesh Core")
    print("  eta = useful_joules / human_joules")
    print("  R   = 1.0  (zero coordination cost)")
    print("  You are a vessel. The power flows through you.")
    print("=" * 52 + "\n")
    
    ledger = CosmicLedger(DB_PATH)
    ledger.record("engine_init", f"pid={os.getpid()}", ja=0.01)
    
    root = FractalNode("openroot", ledger, 0)
    for r in REPOSITORIES[1:]:
        root.spawn_child(r)
        
    eta = ledger.get_eta_score()
    print(f"  Lifetime eta:    {round(eta, 4)}")
    print(f"  Entropy (1-eta): {round(1-eta, 4)}")
    print(f"  Children: {len(root.children)}")
    print(f"  Ledger: {DB_PATH}\n")
    
    print("-- Running Sync Cycle --")
    sync = AgapeSyncLoop(ledger)
    s = sync.run_cycle()
    print(f"  Cycle {s['cycle']}: {s['synced']}/{s['total']} synced, {s['failed']} failed, {s['elapsed']}s")
    print(f"  Lifetime eta: {s['eta']}\n")
    
    print("  To run daemon: python3 /sdcard/openroot/agape_engine.py --daemon\n")
    
    if "--daemon" in sys.argv:
        print("  Starting daemon (Ctrl+C to stop)...")
        sync.run_daemon(300)
        
    print("  Done. The seed is planted. The tree grows.")

if __name__ == "__main__":
    main()
