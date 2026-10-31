#!/usr/bin/env python3
# CANARY:OPENROOT-ESTATE-TOPOLOGY-V1
"""Survey what's built, what's wired, what's orphaned. Emits JSON + MD report."""
import os, json, hashlib, sqlite3, subprocess, datetime, re, glob

ROOT = "/home/jesse/openroot"
BIN = os.path.join(ROOT, "bin")
DATA = os.path.join(ROOT, "data")
BRIDGE = os.path.join(ROOT, "context_bridge")
TS = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

# ---------- [STAGE 1] inventory ----------
components = []  # {id, path, kind, sha256, size}
for pat, kind in [(f"{BIN}/*", "script"), (f"{DATA}/*", "ledger"),
                  (f"{BRIDGE}/*", "bridge")]:
    for p in sorted(glob.glob(pat)):
        if not os.path.isfile(p):
            continue
        components.append({"id": os.path.basename(p), "path": p,
                           "kind": kind if kind != "bridge" else
                           ("bridge-dir-file" if p.endswith((".md", ".txt")) else "bridge-other"),
                           "sha256": sha(p), "bytes": os.path.getsize(p)})

# ---------- [STAGE 2] wiring graph ----------
refs = {}  # script -> list of components it references
comp_names = [c["id"] for c in components]
for c in components:
    if c["kind"] not in ("script",):
        continue
    try:
        txt = open(c["path"], encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    hits = set()
    for other in comp_names:
        if other == c["id"]:
            continue
        if other in txt:
            hits.add(other)
    # also common DB paths referenced by bare name
    for db in ["file_ledger.db", "thermo_ledger.jsonl", "harvest_receipts.jsonl",
               "corpus_goal_index.db", "team_gate.db", "repo_drift.db",
               "canonical_index.db", "state.json", "acre_wallet.jsonl"]:
        if db in txt and db not in hits and any(x["id"] == db for x in components):
            hits.add(db)
    refs[c["id"]] = sorted(hits)

# ---------- [STAGE 3] scheduler consumers ----------
consumers = set()
try:
    cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True).read()
    consumers |= set(re.findall(r"[\w./-]+\.(?:sh|py)", cron))
except Exception:
    pass
for cf in glob.glob("/etc/cron.d/*"):
    try:
        txt = open(cf, encoding="utf-8", errors="replace").read()
        consumers |= {m for m in re.findall(r"[\w./-]+\.(?:sh|py)", txt) if "openroot" in txt or "/home/jesse" in txt}
    except OSError:
        pass
for unit in glob.glob("/etc/systemd/system/*.service") + glob.glob(
        os.path.expanduser("~/.config/systemd/user/*.service")):
    try:
        txt = open(unit, encoding="utf-8", errors="replace").read()
        consumers |= set(re.findall(r"[\w./-]+\.(?:sh|py)", txt))
    except OSError:
        pass
consumer_paths = {os.path.basename(c) for c in consumers}

# ---------- [STAGE 4] classification ----------
wired, islands, producers = [], [], []
for c in components:
    name = c["id"]
    referenced_by = [s for s, tgt in refs.items() if name in tgt]
    scheduled = name in consumer_paths
    calls_out = refs.get(name, [])
    if referenced_by or scheduled or calls_out:
        wired.append({**c, "referenced_by": referenced_by,
                      "scheduled": scheduled, "calls": calls_out})
    else:
        islands.append(c)
    if c["kind"] == "ledger":
        producers.append(c["id"])

# ---------- [STAGE 5] emission ----------
report = {
    "ts": TS, "canary": "OPENROOT-ESTATE-TOPOLOGY-V1",
    "counts": {"scripts": sum(1 for c in components if c["kind"] == "script"),
               "ledgers": len(producers), "total": len(components),
               "wired": len(wired), "islands": len(islands)},
    "wired": wired, "islands": islands, "scheduler_consumers": sorted(consumer_paths),
}
jp = os.path.join(DATA, f"estate_topology_{TS}.json")
json.dump(report, open(jp, "w"), indent=2)

md = [f"# Estate Wiring Report {TS}",
      f"- components: {len(components)} (wired: {len(wired)}, islands: {len(islands)})",
      f"- scheduler consumers: {', '.join(sorted(consumer_paths)) or 'NONE FOUND'}",
      "", "## WIRED (chained or scheduled)", ""]
for w in wired:
    md.append(f"- `{w['id']}` ({w['kind']}) <- {w['referenced_by'] or '-'} "
              f"{'[scheduled]' if w['scheduled'] else ''} calls: {w['calls'] or '-'}")
md += ["", "## ISLANDS (built, unwired — incorporation candidates)", ""]
md += [f"- `{c['id']}` ({c['kind']}, {c['bytes']} bytes)" for c in islands]
md += ["", "## MISSING COMPONENTS (declared but not found)", ""]
for expect in ["harvest_lumo_seed_v2.sh", "GOALS.md", "MASTER_TODO.md",
               "onepass_v3.sh", "stack_gate.sh", "team_gate_v2.sh",
               "agent.sh", "push_guard.py", "heartbeat_engine.sh",
               "corpus_goal_index.db", "file_ledger.db"]:
    found = any(c["id"] == expect for c in components) or os.path.exists(os.path.join(ROOT, expect)) \
        or os.path.exists(os.path.join(BIN, expect)) or os.path.exists(os.path.join(DATA, expect))
    md.append(f"- `{expect}`: {'[banked] present' if found else '[held] ABSENT'}")
mp = os.path.join(BRIDGE, f"estate_wiring_{TS}.md")
open(mp, "w").write("\n".join(md))

recv = os.path.join(DATA, "topology_receipts.jsonl")
open(recv, "a").write(json.dumps({
    "ts": TS, "report_sha256": sha(jp), "md_sha256": sha(mp),
    "wired": len(wired), "islands": len(islands),
    "scheduler_consumers": len(consumer_paths)}) + "\n")
print(f"[banked] survey: {len(components)} components, "
      f"{len(wired)} wired, {len(islands)} islands")
print(f"[banked] report: {mp}")
print(f"[banked] json:   {jp}")
