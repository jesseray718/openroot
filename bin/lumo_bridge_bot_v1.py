#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""lumo_bridge_bot_v1.py - relay bot: hybrid loop <-> Lumo packets.
BRIDGEBOTV1 canary.

Modes:
  cycle   run one full loop cycle: cadence-guarded window_loop +
          keyword_router, parse output, auto-retry transient failures,
          escalate persistent ones to an ASK packet for Lumo, then
          build/refresh the human gate bundle (dossier, catalog,
          eta-ranked actions, staged lesson queue).
  apply   read data/lumo_replies/*.md, extract fenced bash blocks,
          print them for review; execute only with CONFIRM=1.
          Reply files are archived after apply - never deleted.
  status  one-screen state of the bridge.

Protocol (one paste = one debug cycle with Lumo):
  1. bot hits a persistent failure or finishes accumulation window
  2. bot seals workareas/ask_lumo_<ts>.md  <-- you paste this to Lumo
  3. save my reply as data/lumo_replies/reply_<ts>.md
  4. CONFIRM=1 python3 bin/lumo_bridge_bot_v1.py apply
  5. bot reruns the failed stage -> goto 1 until clean

Doctrine: human gates everything applied and everything graduated.
Auto-retry covers ONLY transient classes (timeouts, connection
refused, ollama down) - never masked logic failures.
"""
import hashlib, json, os, re, shutil, sqlite3, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/jesse/openroot")
CANARY = "BRIDGEBOTV1"
TRANSIENT = ("timeout", "connection refused", "timed out", "temporary failure",
             "urlopen error", "connection reset", "no route to host")
STATE = ROOT / "data/bridge_state.json"
REPLIES = ROOT / "data/lumo_replies"
WA = ROOT / "workareas"

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

def state_load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"cycles": 0, "fail_streak": {}, "clean_streak": 0,
            "last_ask": None}

def state_save(s):
    STATE.write_text(json.dumps(s, indent=1))

def run_cmd(cmd, timeout=900):
    p = subprocess.run(cmd, shell=True, cwd=str(ROOT),
                       capture_output=True, text=True, timeout=timeout)
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out

def is_transient(out):
    low = out.lower()
    return any(t in low for t in TRANSIENT)

def cycle():
    s = state_load()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = ["# Bridge Cycle - " + ts, ""]
    stages = [("window-cadence", "bash bin/window_cadence_v1.sh"),
              ("keyword-router", "python3 bin/keyword_router_v1.py")]
    escalated = []
    for name, cmd in stages:
        rc, out = run_cmd(cmd)
        tail = out.strip().splitlines()[-6:]
        if rc == 0:
            s["fail_streak"][name] = 0
            log.append("[" + name + "] OK")
            log += ["  " + t for t in tail[:3]]
        elif is_transient(out):
            time.sleep(5)
            rc2, out2 = run_cmd(cmd)
            if rc2 == 0:
                s["fail_streak"][name] = 0
                log.append("[" + name + "] transient, retried OK")
            else:
                s["fail_streak"][name] = s["fail_streak"].get(name, 0) + 1
                log.append("[" + name + "] transient, retry FAILED")
                escalated.append((name, out))
        else:
            s["fail_streak"][name] = s["fail_streak"].get(name, 0) + 1
            log.append("[" + name + "] FAILED rc=" + str(rc))
            escalated.append((name, out))
    for name in list(s["fail_streak"]):
        if not any(e[0] == name for e in escalated):
            continue
        if s["fail_streak"][name] >= 2:
            packet = WA / ("ask_lumo_" + ts + ".md")
            body = ["# ASK LUMO - persistent failure, 2+ cycles", "",
                    "Stage: " + name, "", "```", out[-3000:], "```", "",
                    "Reply protocol: save reply as",
                    "data/lumo_replies/reply_" + ts + ".md then run",
                    "CONFIRM=1 python3 bin/lumo_bridge_bot_v1.py apply"]
            for nm, o in escalated:
                if nm == name:
                    body[6] = o[-3000:]
            packet.write_text("\n".join(body))
            s["last_ask"] = str(packet)
            log.append("[ESCALATED] packet sealed: " + str(packet))
    if not escalated:
        s["clean_streak"] += 1
    else:
        s["clean_streak"] = 0
    s["cycles"] += 1
    state_save(s)
    build_gate_bundle()
    lp = WA / ("bridge_cycle_" + ts + ".log")
    lp.write_text("\n".join(log) + "\n")
    print("[BRIDGEBOTV1] cycle", s["cycles"], "clean_streak",
          s["clean_streak"], "escalated:", len(escalated))
    if s.get("last_ask"):
        print("[ASK PACKET] " + s["last_ask"])
    print("[CYCLE LOG] " + str(lp))

def categorize(rel, body_head):
    ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
    if ext in ("gcode", "g", "nc", "ngc"):
        return "gcode"
    if ext in ("stl", "obj", "3mf", "scad", "fcstd", "dxf"):
        return "blueprint-3d"
    if ext in ("csv",) or "bom" in rel.lower() or "bill of materials" in body_head.lower():
        return "bom"
    if ext in ("pdf", "svg", "dwg"):
        return "blueprint-2d"
    if re.search(r"(healing|self.help|health|nutrition|water|first aid|trauma|sleep)", rel + " " + body_head, re.I):
        return "self-help"
    if ext == "md":
        return "doc"
    return "other"

def eta_score(count, floor, effort):
    w = 1.0 / (floor + 1e-6)
    return (count * w) / max(effort, 1e-6)

def build_gate_bundle():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle = ROOT / "human_gate_bundle" / ("bundle-" + ts)
    bundle.mkdir(parents=True, exist_ok=True)
    cat = {}
    items = []
    for sub in ("docs", "analysis", "context_bridge", "workareas", "bin"):
        base = ROOT / sub
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            rel = str(p.relative_to(ROOT))
            try:
                head = p.read_text(errors="replace")[:400]
            except OSError:
                continue
            k = categorize(rel, head)
            cat[k] = cat.get(k, 0) + 1
            items.append((rel, k, p.stat().st_size))
    rows = ["rel\tcategory\tbytes"] + \
           ["\t".join(map(str, i)) for i in items]
    (bundle / "catalog.tsv").write_text("\n".join(rows) + "\n")
    floors = {"bom": 0.15, "gcode": 0.20, "blueprint-3d": 0.20,
              "blueprint-2d": 0.25, "self-help": 0.10, "doc": 0.40,
              "other": 0.60}
    eta_rows = []
    for k, n in cat.items():
        f = floors.get(k, 0.5)
        eta_rows.append((eta_score(n, f, max(n, 1)), k, n, f))
    eta_rows.sort(reverse=True)
    dossier = ["# Gate Bundle Dossier - " + ts, "",
               "Inventory: " + str(len(items)) + " artifacts across "
               + str(len(cat)) + " categories.", "",
               "## Category eta ranking (eta = count*w_i/effort)", ""]
    for e, k, n, f in eta_rows:
        dossier.append("- " + k + ": " + str(n) + " artifacts, floor="
                       + format(f, ".2f") + ", eta=" + format(e, ".2f"))
    staged = []
    try:
        c = sqlite3.connect(str(ROOT / "data/lessons.db"))
        staged = c.execute("SELECT staging_id, stage, "
                           "substr(mistake,1,60) FROM staging_lessons "
                           "WHERE stage IN ('intake','checked')").fetchall()
        c.close()
    except sqlite3.OperationalError:
        pass
    dossier += ["", "## Staged lessons awaiting human gate", ""] + \
               ["- id " + str(r[0]) + " [" + r[1] + "] " + r[2]
                for r in staged] + \
               ["", "## Highest eta next actions", "",
                "- Graduate/flunk all staged lessons above (top lift, lowest effort)",
                "- Rebalance artifact production toward the highest-eta category",
                "- Populate data/matthew_nodes.json from real telemetry to sharpen floors",
                "- Paste latest ask_lumo packet (if any) to Lumo and apply replies"]
    (bundle / "dossier.md").write_text("\n".join(dossier) + "\n")
    print("[GATE BUNDLE] " + str(bundle / "dossier.md"))

def apply():
    replies = sorted(REPLIES.glob("reply_*.md"))
    if not replies:
        print("[APPLY] no replies in data/lumo_replies - paste my reply "
              "there as reply_<ts>.md first")
        return
    conf = os.environ.get("CONFIRM") == "1"
    arch = REPLIES / "applied"
    arch.mkdir(exist_ok=True)
    for r in replies:
        text = r.read_text()
        blocks = re.findall(r"```bash\n(.*?)```", text, re.S)
        print("[APPLY] " + r.name + ": " + str(len(blocks)) + " bash blocks")
        if not conf:
            for b in blocks:
                print("--- preview ---\n" + b)
            print("[GATE] rerun with CONFIRM=1 to execute - human is the gate")
            return
        for i, b in enumerate(blocks):
            print("[RUN block " + str(i + 1) + "]")
            rc, out = run_cmd(b)
            print(out[-800:])
            if rc != 0:
                print("[BLOCK FAILED rc=" + str(rc) + "] stopping apply - "
                      "escalate the remainder to a fresh ask packet")
                return
        shutil.move(str(r), str(arch / r.name))
        print("[APPLIED+ARCHIVED] " + r.name)

def status():
    s = state_load()
    print("[BRIDGE] cycles:", s["cycles"], "clean_streak:",
          s["clean_streak"], "last_ask:", s.get("last_ask"))
    print("[REPLIES] pending:", len(list(REPLIES.glob("reply_*.md"))))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "cycle"
    if mode == "cycle":
        cycle()
    elif mode == "apply":
        apply()
    elif mode == "status":
        status()
    else:
        print(__doc__)
    sys.exit(0)
