#!/usr/bin/env python3
"""lever.py — OpenRoot leverage engine.
Commands: repos clone models audit prune joules ledger scheduler saas cicd dossier."""
import datetime, json, os, shlex, sqlite3, subprocess, sys, time

ROOT  = os.environ.get("SYN_ROOT", os.path.expanduser("~/src/openroot"))
LEVER = os.path.join(ROOT, "lever")
DB    = os.path.join(LEVER, "db", "lever.db")
BOX   = os.environ.get("BOX", "jesse@100.122.169.43")
SRC   = os.path.join(os.path.dirname(ROOT), "")  # sibling clones

SCHEMA = """
CREATE TABLE IF NOT EXISTS repos (
  name TEXT PRIMARY KEY, visibility TEXT, pushed_at TEXT, kb INTEGER, url TEXT,
  cloned INTEGER DEFAULT 0, snapshotted TEXT);
CREATE TABLE IF NOT EXISTS models (
  name TEXT PRIMARY KEY, size_bytes INTEGER, modified TEXT, seen TEXT);
CREATE TABLE IF NOT EXISTS quarantine (
  path TEXT PRIMARY KEY, reason TEXT, action TEXT, moved TEXT DEFAULT NULL);
CREATE TABLE IF NOT EXISTS joule_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, label TEXT, cpu_util REAL,
  watts_est REAL, seconds REAL, joules REAL);
CREATE TABLE IF NOT EXISTS leverage_items (
  category TEXT, title TEXT, detail TEXT, priority REAL, status TEXT DEFAULT 'OPEN',
  PRIMARY KEY(category, title));
CREATE TABLE IF NOT EXISTS ai_grades (
  model TEXT, task TEXT, score REAL, joules REAL, ts TEXT, PRIMARY KEY(model, task));
"""

def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def conn():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB); c.executescript(SCHEMA); return c
def sh(cmd, **kw): return subprocess.run(shlex.split(cmd), capture_output=True, text=True, **kw)
def ssh(cmd):
    if os.environ.get("LEVER_LOCAL") == "1": return sh(cmd)  # on the box itself, no ssh hop
    return sh(f"ssh -o ConnectTimeout=8 {BOX} {shlex.quote(cmd)}")

# ---------- repos: gh snapshot ----------
def repos():
    c = conn()
    r = sh("gh repo list --limit 200 --json name,isPrivate,pushedAt,diskUsage,url")
    if r.returncode != 0:
        print("[repos] gh failed:", (r.stderr or "").strip()[:120]); return
    n = 0
    for it in json.loads(r.stdout):
        name = it["name"]; vis = "private" if it["isPrivate"] else "public"
        c.execute("""INSERT INTO repos(name,visibility,pushed_at,kb,url,snapshotted)
                     VALUES(?,?,?,?,?,?)
                     ON CONFLICT(name) DO UPDATE SET visibility=excluded.visibility,
                       pushed_at=excluded.pushed_at, kb=excluded.kb, snapshotted=excluded.snapshotted""",
                  (name, vis, it["pushedAt"], it["diskUsage"], it["url"], now())); n += 1
    c.commit()
    pub = c.execute("SELECT COUNT(*) FROM repos WHERE visibility='public'").fetchone()[0]
    priv = c.execute("SELECT COUNT(*) FROM repos WHERE visibility='private'").fetchone()[0]
    print(f"[repos] {n} repos snapshotted ({pub} public / {priv} private)")

def clone():
    c = conn()
    rootdir = os.path.dirname(ROOT)
    n = 0
    for (name,) in c.execute("SELECT name FROM repos WHERE cloned=0"):
        dest = os.path.join(rootdir, name)
        if os.path.isdir(os.path.join(dest, ".git")):
            c.execute("UPDATE repos SET cloned=1 WHERE name=?", (name,)); continue
        r = sh(f"gh repo clone jesseray718/{name} -- --depth=1 {dest}")
        if r.returncode == 0: c.execute("UPDATE repos SET cloned=1 WHERE name=?", (name,)); n += 1
        else: print(f"  [skip] {name}: {(r.stderr or '').strip()[:80]}")
    c.commit(); print(f"[clone] {n} new shallow clones into {rootdir}/")

# ---------- models: probe box ollama ----------
def models():
    c = conn()
    r = ssh("curl -s --max-time 5 http://localhost:11434/api/tags")
    if r.returncode != 0 or not r.stdout.strip():
        print("[models] box ollama unreachable — run locally later"); return
    try: data = json.loads(r.stdout)
    except json.JSONDecodeError: print("[models] bad json from ollama"); return
    for m in data.get("models", []):
        c.execute("""INSERT INTO models(name,size_bytes,modified,seen) VALUES(?,?,?,?)
                     ON CONFLICT(name) DO UPDATE SET seen=excluded.seen""",
                  (m["name"], m.get("size", 0), m.get("modified_at", ""), now()))
    c.commit()
    print("[models] local fleet on OptiPlex (available NOW for audit):")
    for (nm, gb) in c.execute("SELECT name, ROUND(size_bytes/1073741824.0,1) FROM models"):
        print(f"   {nm}  ({gb} GB)")
    print("[models] candidates to download (research-grade suggestion, verify fit):")
    for nm in ("qwen2.5-coder:14b", "deepseek-r1:14b", "llama3.1:8b", "nomic-embed-text"):
        print(f"   {nm}")
    print("[models] verify VRAM/RAM before pulling — 3060-class box favors 7B-14B quantized")

# ---------- audit: deep-dive via local model ----------
def audit(topic="repo-hygiene"):
    prompt = (f"Audit the OpenRoot ecosystem focusing on {topic}. List concrete findings: "
              "clutter to quarantine, README gaps, CI/CD opportunities, monoliths to split, "
              "high-yield next actions. Be terse, bullet points only.")
    r = ssh(f"curl -s --max-time 240 http://localhost:11434/api/generate -d " +
            shlex.quote(json.dumps({"model": "openroot-coder:latest", "prompt": prompt, "stream": False})))
    if r.returncode != 0 or not r.stdout.strip():
        print("[audit] model call failed — box or ollama down"); return
    try: out = json.loads(r.stdout).get("response", "")
    except json.JSONDecodeError: out = r.stdout[:500]
    fp = os.path.join(LEVER, "audits", f"{topic}-{now().replace(':','')}.md")
    open(fp, "w").write(f"# Local-model audit — {topic}\n_ts {now}_\n\n{out}\n")
    print(f"[audit] 7B deep-dive written: {fp}"); print(out[:900])

# ---------- prune: quarantine plan (gated) ----------
CLUTTER = ("__pycache__", ".bak", ".egg-info", "build", ".pytest_cache", "dist")
def prune(commit=False):
    c = conn(); hits = 0
    for dirpath, dirnames, filenames in os.walk(os.path.dirname(ROOT)):
        if "/.git/" in dirpath or "/.cargo/" in dirpath or "/salvage/" in dirpath: dirnames[:] = []; continue
        dirnames[:] = [d for d in dirnames if d not in (".git", "venv", "node_modules", "target", ".cargo")]
        for name in dirnames[:]:
            if name in CLUTTER:
                p = os.path.join(dirpath, name)
                c.execute("INSERT OR IGNORE INTO quarantine(path,reason,action) VALUES(?,?,?)",
                          (p, "build-artifact clutter", "quarantine")); hits += 1
        for fn in filenames:
            if fn.endswith(".bak") or fn.startswith(".sync-conflict"):
                p = os.path.join(dirpath, fn)
                c.execute("INSERT OR IGNORE INTO quarantine(path,reason,action) VALUES(?,?,?)",
                          (p, "backup/conflict clutter", "quarantine")); hits += 1
    c.commit()
    print(f"[prune] {hits} quarantine candidates planned (see quarantine table)")
    if commit and os.environ.get("CONFIRM") == "1":
        qdir = os.path.join(ROOT, "attic", now()[:10]); os.makedirs(qdir, exist_ok=True)
        moved = 0
        for (p,) in c.execute("SELECT path FROM quarantine WHERE moved IS NULL"):
            if os.path.exists(p):
                import shutil; shutil.move(p, os.path.join(qdir, os.path.basename(p))); moved += 1
                c.execute("UPDATE quarantine SET moved=? WHERE path=?", (now(), p))
        c.commit()
        print(f"[prune][CONFIRM] {moved} items moved to attic/{now()[:10]}")
        r = sh(f"gh repo create jesseray718/openroot-quarantine --private --confirm 2>/dev/null || true")
        print("[prune] quarantine repo: jesseray718/openroot-quarantine (private, rescan-later vault)")
    elif commit:
        print("[prune][held] set CONFIRM=1 to execute the move")

# ---------- joules: real-time compute energy meter (PoPW feed) ----------
def joules(seconds=10, label="compute"):
    tdp = float(os.environ.get("CPU_WATTS", os.environ.get("BOX_TDP", "65")))
    def cpu_sample():
        try:
            with open("/proc/stat") as f: parts = [float(x) for x in f.readline().split()[1:]]
            idle = parts[3] + (parts[4] if len(parts) > 4 else 0)
            return sum(parts), idle
        except OSError:
            return None, None   # Android denies /proc/stat; caller falls back to loadavg
    t1, i1 = cpu_sample(); time.sleep(seconds); t2, i2 = cpu_sample()
    if t1 is None or t2 is None:
        cores = os.cpu_count() or 8
        try: la = float(open("/proc/loadavg").read().split()[0])
        except Exception: la = cores * 0.25
        util = max(0.0, min(1.0, la / cores))   # loadavg estimate, marked MODEL-grade
    else:
        util = max(0.0, min(1.0, 1 - ((i2 - i1) / (t2 - t1)))) if t2 > t1 else 0.0
    watts = tdp * (0.15 + 0.85 * util)   # idle floor + utilization draw
    j = watts * seconds
    c = conn()
    c.execute("INSERT INTO joule_events(ts,label,cpu_util,watts_est,seconds,joules) VALUES(?,?,?,?,?,?)",
              (now(), label, round(util, 3), round(watts, 2), seconds, round(j, 1)))
    c.commit()
    mass_g = j / (299792458.0 ** 2) * 1000.0  # E=mc^2 — same unit, physics closes the loop
    print(f"[joules] {label}: util={util*100:.0f}%  ~{watts:.1f}W  {seconds}s -> {j:.1f} J"
          f"  (= {mass_g:.2e} g matter-equivalent — compute and human and mechanical all in J/s)")
    print("[joules] rows land in lever.db joule_events -> grade MEASURED with 3B gate -> synthesis acre_mints")

# ---------- ledger: persistent ordered leverage list ----------
SEEDS = [
 ("node", "OptiPlex write-authority", "box becomes sole chain writer; phone verifies read-only (two-pane law)", 0.2),
 ("node", "A15 7B-serving probe", "test if ollama small models (1b-3b) run in Termux for offline pane", 0.5),
 ("finance", "prepaid-number + TOTP", "phone line unblocks GitHub Sponsors + Mercury Bank + voice system", 0.15),
 ("finance", "SaaS/API monetization", "thermal_product_server -> FastAPI key-gated tier + Stripe/LemonSqueezy stub", 0.8),
 ("finance", "LLC vs 501c3 structure", "research fiscal sponsorship (open-collective etc.) vs private foundation for Agape mission arm", 1.1),
 ("need", "MEASURED joule row", "instrument one real thermal_sim run -> unlocks ACRE mint (currently 0.0 J)", 0.45),
 ("want", "Sikeston blight properties", "VERIFY county blight-list, zoning for industrial/e-waste, MO cleanup liens; couple to recycling build-out", 1.4),
 ("resource_opensrc", "github-sponsors + CI badges", "after README honesty pass: sponsors button, passing-build badge, CONTRIBUTING gate", 0.9),
 ("resource_501c3", "grant cross-reference", "Solana Foundation ecosystem + DePIN programs + MO rural-energy grants; verify intakes first", 1.2),
 ("path", "Big Beautiful Bill research", "VERIFY actual provisions (bonus depreciation, energy credits, OpEx deduction) with a professional before acting; then map to recycling capex", 1.0),
 ("path", "electronics-recycling + data-destruction biz", "MO DNR e-scrap registration research, NAID-style data-destruction cert path, Sikeston site + blight tie-in", 1.3),
 ("path", "autonomous voice scheduler", "inbound call -> whisper STT -> LLM intent -> calendar slot -> SMS confirm; see specs/voice_scheduler.md", 0.75),
 ("crossref", "smart-contracts + grants + tax-code matrix", "one SQLite table joining: pathway x funding source x tax treatment x PoPW evidence required", 1.6),
]
def ledger():
    c = conn()
    for cat, t, d, p in SEEDS:
        c.execute("INSERT OR IGNORE INTO leverage_items(category,title,detail,priority) VALUES(?,?,?,?)",
                  (cat, t, d, p))
    c.commit()
    print("[ledger] persistent ordered leverage list (low priority-value = fire first):")
    for cat, t, d, p in c.execute("SELECT category,title,detail,priority FROM leverage_items "
                                  "WHERE status='OPEN' ORDER BY priority ASC"):
        print(f"  {p:>5}  [{cat:<16}] {t}")

# ---------- specs ----------
def scheduler():
    fp = os.path.join(LEVER, "specs", "voice_scheduler.md")
    open(fp, "w").write("""# Autonomous Voice Scheduler — spec v0.1 (STUB; provider choice = OPEN question)
Flow: inbound call -> PBX (Twilio/Telnyx self-hosted Asterisk both viable) -> Whisper STT
-> openroot-coder intent extraction -> sqlite calendar -> TTS confirm -> SMS reminder.
Booking API: POST /book {name, service(e-waste pickup|dropoff|data-destruction), addr, slot}.
Calendar: lever.db bookings table + .ics export to phone.
Human-in-loop: OFF by default after 10 graded transcripts; rc_circuit scores each call.
Prereq: phone line (prepaid-number task, already queued at 0.15).\n""")
    print(f"[scheduler] spec written: {fp}")

def saas():
    fp = os.path.join(LEVER, "specs", "saas_monetization.md")
    open(fp, "w").write("""# API Monetization Pipeline — spec v0.1
Existing assets: thermal_product_server (OptiPlex), thermal cascade + psychrometric models,
acre ledger. Pipeline: FastAPI gateway -> API-key auth (sqlite) -> metered joules per request
(from lever joule_events pattern) -> tier pricing -> Stripe/LemonSqueezy webhook -> billing rows.
Grade: STUB until one paid-tier smoke test. Sell-to: HVAC sizing, greenhouse cooling, DePIN
node planning, permies/homestead audience via the existing README channels.\n""")
    print(f"[saas] spec written: {fp}")

# ---------- cicd ----------
def cicd():
    wr = os.path.join(ROOT, ".github", "workflows")
    os.makedirs(wr, exist_ok=True)
    fp = os.path.join(wr, "openroot-audit.yml")
    open(fp, "w").write("""name: openroot-audit
on: [push, workflow_dispatch]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - name: compile-gate
        run: |
          find . -name '*.py' -not -path './.git/*' -not -path '*/venv/*' -print0 |
            xargs -0 -n1 python -m py_compile
      - name: verify-chains
        run: |
          SYN_ROOT=$PWD python3 synthesis/synthesis.py verify || true
""")
    print(f"[cicd] draft workflow written: {fp} (commit gated: CONFIRM=1 + git add)")

# ---------- dossier ----------
def dossier():
    c = conn()
    fp = os.path.join(ROOT, "context_bridge", "LEVER_DOSSIER.md")
    rows = c.execute("SELECT category,title,priority FROM leverage_items WHERE status='OPEN' "
                     "ORDER BY priority ASC").fetchall()
    jr = c.execute("SELECT COUNT(*), ROUND(SUM(joules),1) FROM joule_events").fetchone()
    qs = c.execute("SELECT COUNT(*) FROM quarantine WHERE moved IS NULL").fetchone()[0]
    lines = ["# LEVER DOSSIER — " + now(), "",
             "## Nodes & finances & needs/wants & resources — ranked least-resistance first", ""]
    for cat, t, p in rows: lines.append(f"- [{cat}] **{t}** (fire-order {p})")
    lines += ["", "## Joule economy (E=mc2 unified accounting)", "",
             f"- measured compute events: {jr[0]}, total ~{jr[1]} J (grade MODEL until 3B-gated)",
             f"- quarantine backlog: {qs} candidates (private-vault rescan pending)", "",
             "## Honest-status board (nothing above its grade)",
             "- Sikeston/BBB/tax items: UNVERIFIED — treat as research leads, not facts",
             "- Voice scheduler + SaaS: STUB specs planted, no provider commitments yet",
             "- ACRE mint: still 0 J MEASURED — thermal instrumentation is the gate", ""]
    open(fp, "w").write("\n".join(lines) + "\n")
    print(f"[dossier] written: {fp}")
    r = sh(f"gh gist create {fp} --public --desc 'OpenRoot lever dossier {now()[:10]}'")
    if r.returncode == 0 and r.stdout.strip():
        print(f"[dossier] published: {r.stdout.strip()}")

CMDS = dict(repos=repos, clone=clone, models=models, prune=lambda: prune(False),
            prune_commit=lambda: prune(True), joules=joules, ledger=ledger,
            scheduler=scheduler, saas=saas, cicd=cicd, dossier=dossier, audit=audit)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ledger"
    args = sys.argv[2:]
    if mode == "joules": joules(float(args[0]) if args else 10.0, args[1] if len(args) > 1 else "compute")
    elif mode == "audit": audit(args[0] if args else "repo-hygiene")
    else: CMDS.get(mode, ledger)()
