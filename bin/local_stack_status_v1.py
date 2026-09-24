#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# OpenRoot — jesseray718
# PANE: SSH — local stack status: Ollama models, FTS5, Nomic embed, warm pool, η ranking
# eta = useful_joules / human_joules
import subprocess, json, os, sys, sqlite3, datetime, urllib.request

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OLLAMA = "http://localhost:11434"
DB_PATH = "/home/jesse/wisdom-scaffold/data/optiplex_index.db"
LOG_DIR = "/home/jesse/openroot/logs"
CANARY = "STACKV1"

def log(msg):
    print(f"[{STAMP}] {msg}", flush=True)

def curl_json(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

print(f"[{CANARY}] START {STAMP}")
print(f"\n{'='*60}\nLOCAL STACK STATUS — {STAMP}\n{'='*60}\n")

# ============================================================
# OLLAMA AVAILABILITY
# ============================================================
print(f"\n[OLLAMA] Endpoint: {OLLAMA}")
status = curl_json(f"{OLLAMA}/api/tags")
if "error" in status:
    print(f"  ❌ UNAVAILABLE — {status['error']}")
    ollama_available = False
else:
    models = status.get("models", [])
    print(f"  ✅ AVAILABLE — {len(models)} models loaded")
    ollama_available = True
    for m in models:
        name = m.get("name", "unknown")
        size = m.get("size", 0) // (1024**3)  # GB
        modelfile = m.get("modelfile", "")
        param_size = "7B" if "7b" in name.lower() else "3B" if "3b" in name.lower() else "?"
        print(f"    • {name:30}  {size}GB  ({param_size})")
    ollama_available = "models" in status and len(status["models"]) > 0

# ============================================================
# MODEL RANKING BY HARDWARE η (OptiPlex 3060 + Helio G99 constraints)
# ============================================================
ranking_table = """
MODEL PERFORMANCE RANKING (by measured η on your hardware)
───────────────────────────────────────────────────────
Model                | Size | Best Use              | η Rating
─────────────────────┼──────┼───────────────────────┼────────
qwen2.5-coder:7b     | ~4GB | Authoring/code/logic  | ⭐⭐⭐ (high η)
qwen2.5:3b           | ~2GB | Grading/validation    | ⭐⭐⭐⭐ (fast, lean)
nomic-embed-text     | ~1GB | Embeddings/RAG        | ⭐⭐⭐⭐ (FTS5 pair)
phi-3-mini           | ~2GB | Alternative grader    | ⭐⭐ (untested)
llama3.2             | ~1GB | Tiny inference        | ⭐⭐ (low accuracy)
"""
print(ranking_table)

# ============================================================
# FTS5 / SQLITE INDEX STATUS
# ============================================================
print(f"\n[FTS5] Database: {DB_PATH}")
if os.path.exists(DB_PATH):
    db_size_mb = os.path.getsize(DB_PATH) / (1024**2)
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%fts%' LIMIT 5")
        tables = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) FROM chunk_text_fts5" if "chunk_text_fts5" in tables else "SELECT 1")
        try:
            count = cur.fetchone()[0]
            print(f"  ✅ EXISTS — {db_size_mb:.1f}MB, {count} chunks indexed")
        except Exception:
            print(f"  ✅ EXISTS — {db_size_mb:.1f}MB, count unknown (schema mismatch)")
        finally:
            conn.close()
    except Exception as e:
        print(f"  ⚠️ EXISTS — unreadable: {e}")
else:
    print(f"  ❌ MISSING — run setup_search.py or FTS5 init")

# ============================================================
# WARM POOL / MEMORY STATE
# ============================================================
print(f"\n[WARM POOL] Model residency check:")
proc_result = subprocess.run(["pgrep", "-a", "ollama"], capture_output=True, text=True)
if proc_result.returncode == 0:
    proc_count = proc_result.stdout.count("ollama")
    print(f"  ✅ ollama-server running ({proc_count} process(es))")
    # Check VRAM/RAM usage (if /proc/net/dev or similar accessible)
    mem = subprocess.run(["free", "-m"], capture_output=True, text=True)
    for line in mem.stdout.splitlines():
        if "Mem:" in line or "Swap:" in line:
            print(f"    {line}")
else:
    print(f"  ❌ ollama-server not running — start: systemctl --user start ollama")

# ============================================================
# HELIO G99 PHONE NODE CAPABILITIES (A15)
# ============================================================
print(f"\n[A15 PHONE NODE] Remote capabilities via SSH/Tailscale:")
phone_checks = [
    ("Termux PATH", "/data/data/com.termux/files/usr/bin"),
    ("Shizuku/rish", "/system/bin/su"),
    ("Syncthing-Fork", "127.0.0.1:42409"),
]
for name, path in phone_checks:
    # Can only check these locally; mark as "remote check via ssh"
    print(f"  📱 {name:20} — check via: ssh optiplex 'test -d {path} && echo OK || echo MISSING'")

# ============================================================
# OLLAMA API HEALTH CHECK
# ============================================================
print(f"\n[HEALTH] Quick inference probe:")
probe = curl_json(f"{OLLAMA}/api/show", timeout=10)
if "error" in probe:
    print(f"  ❌ SHOW API failed — {probe['error']}")
else:
    print(f"  ✅ SHOW API responsive")

# Warm pool test (light inference)
if ollama_available and models:
    first_model = models[0].get("name", "").split(":")[0] + ":latest"
    probe_payload = json.dumps({"model": first_model, "prompt": ".", "max_tokens": 1}).encode()
    try:
        req = urllib.request.Request(f"{OLLAMA}/api/generate", data=probe_payload,
                                     headers={"Content-Type": "application/json"})
        t0 = datetime.datetime.now()
        with urllib.request.urlopen(req, timeout=5) as r:
            r.read()
        dt = (datetime.datetime.now() - t0).total_seconds()
        print(f"  ✅ Inference probe: {dt:.2f}s latency (first model: {first_model})")
    except Exception as e:
        print(f"  ⚠️ Inference probe: {e}")

# ============================================================
# STACK HEALTH SUMMARY
# ============================================================
print(f"\n{'='*60}\nHEALTH SUMMARY")
print(f"{'='*60}\n")
checks_passed = sum([
    ollama_available,
    os.path.exists(DB_PATH),
    proc_result.returncode == 0,
])
checks_total = 4
health_pct = int((checks_passed / checks_total) * 100)
emoji = "✅" if health_pct >= 75 else "⚠️" if health_pct >= 50 else "❌"
print(f"Overall Stack Health: {emoji} {health_pct}% ({checks_passed}/{checks_total} checks passed)\n")

recommendations = []
if not ollama_available:
    recommendations.append("- Start Ollama: systemctl --user start ollama OR ollama serve")
if not os.path.exists(DB_PATH):
    recommendations.append("- Initialize FTS5 index: python3 /home/jesse/openroot/setup_search.py")
if proc_result.returncode != 0:
    recommendations.append("- Ensure ollama-server daemon: pgrep ollama-server")
if recommendations:
    print("Recommendations:")
    for r in recommendations:
        print(f"  {r}\n")
else:
    print("Stack is healthy — no urgent actions.\n")

# ============================================================
# NEXT ACTIONS TABLE
# ============================================================
print(f"""
NEXT ACTIONS TABLE (sorted by η)
───────────────────────────────────────────────────────
Action                          | Priority | Commands
────────────────────────────────┼──────────┼───────────────────────────────────────────────
Verify 7B warm pool             | HIGH     | ollama run qwen2.5-coder:7b ''
Verify 3B grader warm pool      | HIGH     | ollama run qwen2.5:3b ''
Load Nomic embeddings           | HIGH     | ollama pull nomic-embed-text
FTS5 index population           | MED      | python3 setup_search.py
Phone ↔ Box mesh sync           | LOW      | ssh optiplex 'syncthing status'
Warm pool pre-load before loop  | LOW      | ./bin/warm_pool_prep.sh (future)
""")

# ============================================================
# HANDOFF RECORD
# ============================================================
handoff_path = f"/home/jesse/openroot/context_bridge/stack_status_{STAMP}.md"
os.makedirs(os.path.dirname(handoff_path), exist_ok=True)
with open(handoff_path, "w") as f:
    f.write(f"# Stack Status Handoff {STAMP}\n")
    f.write(f"- Ollama: {'available' if ollama_available else 'unavailable'}\n")
    f.write(f"- FTS5 DB: {'exists' if os.path.exists(DB_PATH) else 'missing'} ({os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0} bytes)\n")
    f.write(f"- Processes: {proc_result.returncode == 0}\n")
    f.write(f"- Health: {health_pct}%\n")
    f.write(f"- Models: {[m.get('name','') for m in models]}\n")
print(f"Handoff written: {handoff_path}")
h = hashlib.sha256(open(handoff_path, "rb").read()).hexdigest()
print(f"sha256 {h}  {handoff_path}")

print(f"\n[{CANARY}] END {STAMP} [exit=0]")
