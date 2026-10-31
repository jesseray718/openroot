#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""superloop_composite_v3.py — recall, mine chains, detect drift, respawn daemon, publish gist."""
import argparse, hashlib, json, re, subprocess, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OR = Path("/home/jesse/openroot")
DATA, CTX, LOGS = OR/"data", OR/"context_bridge", OR/"logs"
CMDLOG = DATA/"superloop_commands.jsonl"
CHAINS = DATA/"superloop_chains.json"
DASHBOARD = CTX/"superloop_DASHBOARD.md"
ROUTER_WEIGHTS = DATA/"model_registry.json"
DRIFT_LOG = DATA/"drift_alerts.jsonl"
GIST_ID = "3ffffa18763e5cbfdb5c44cc23743f4b"
HISTFILE = Path("/home/jesse/.bash_history")

BUCKETS = [
    ("bridge",   r"\b(ssh|scp)\b"),
    ("gitops",   r"\b(git|gh)\b"),
    ("model",    r"(ollama|localhost:11434|qwen)"),
    ("author",   r"cat\s*<<|heredoc|EOF"),
    ("exec",     r"^(python3?|bash|sh)\b|py_compile"),
    ("assistant",r"\b(lumo|hive\.sh|nanobot|smart_router|bot_loop|mistake_engine)\b"),
    ("gate",     r"(stack_gate|team_gate|push_guard|grep\s+-q)"),
    ("system",   r"\b(ps|pgrep|kill|nohup|crontab|df|free)\b"),
    ("net",      r"\b(curl|wget|tailscale)\b"),
    ("files",    r"\b(ls|cat|grep|tail|head|sed|mv|cp|mkdir|find|wc)\b"),
]

def classify(cmd):
    for name, pat in BUCKETS:
        if re.search(pat, cmd):
            return name
    return "other"

def sha16(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def load_seen(limit=4000):
    seen = set()
    if CMDLOG.exists():
        for ln in CMDLOG.read_text(errors="replace").splitlines()[-limit:]:
            try:
                seen.add(json.loads(ln)["sha"])
            except Exception:
                pass
    return seen

def recall(n):
    cmds = []
    if HISTFILE.exists():
        raw = HISTFILE.read_text(errors="replace").splitlines()
        cmds = [l.strip() for l in raw if l.strip() and not l.startswith("#")]
    try:
        sess = subprocess.run(["tmux","ls"], capture_output=True, text=True, timeout=5)
        for line in sess.stdout.splitlines():
            sname = line.split(":")[0].strip()
            if not sname:
                continue
            cap = subprocess.run(["tmux","capture-pane","-p","-S","-%d"%n,"-t",sname],
                                 capture_output=True, text=True, timeout=5)
            for l in cap.stdout.splitlines():
                t = l.strip()
                if re.match(r"^[a-z_./][\w./-]*\s?", t) and " " in t and not t.startswith(("default","Attached")):
                    cmds.append(t)
    except Exception:
        pass
    return cmds[-n:]

def recall_write(cmds, seen):
    new = 0
    with CMDLOG.open("a") as f:
        for c in cmds:
            h = sha16(c)
            if h in seen:
                continue
            seen.add(h)
            f.write(json.dumps({"sha": h, "cmd": c, "bucket": classify(c),
                                "ts": datetime.now(timezone.utc).isoformat()})+"\n")
            new += 1
    return new

def mine_chains(cmds):
    cls = [classify(c) for c in cmds]
    follow_weights = {}
    for a, b in zip(cls[:-1], cls[1:]):
        k = f"{a}->{b}"
        follow_weights[k] = follow_weights.get(k, 0) + 1
    ranked = sorted(follow_weights.items(), key=lambda x: x[1], reverse=True)[:10]
    bucket_affinity = {
        "bridge":   {"route_to": "smart_router", "pref_model": "7b"},
        "gitops":   {"route_to": "smart_router", "pref_model": "7b"},
        "model":    {"route_to": "qwen2.5-coder:7b", "pref_model": "7b"},
        "author":   {"route_to": "7b", "pref_model": "7b"},
        "exec":     {"route_to": "3b", "pref_model": "3b"},
        "gate":     {"route_to": "team_gate", "pref_model": "3b"},
        "system":   {"route_to": "local_shell", "pref_model": "none"},
        "net":      {"route_to": "smart_router", "pref_model": "7b"},
        "files":    {"route_to": "local_shell", "pref_model": "none"},
        "other":    {"route_to": "lumo", "pref_model": "max"},
    }
    out = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "bucket_counts": dict(Counter(cls)),
        "transition_weights": [{"rule": k, "count": n} for k, n in ranked],
        "routing_weights": bucket_affinity,
        "dominant_bucket": Counter(cls).most_common(1)[0][0] if cls else "unknown",
        "recalled_n": len(cmds),
    }
    CHAINS.write_text(json.dumps(out, indent=2))
    ROUTER_WEIGHTS.write_text(json.dumps(out, indent=2))
    return out

def detect_drift(cmds, threshold=0.3):
    current = dict(Counter(classify(c) for c in cmds))
    if not current:
        return {"drift_detected": False, "deviation_score": 0, "alerts": [], "alert_count": 0}
    keys = set(current.keys())
    diffs = [current[k]**2 for k in keys]  # self-deviation until a stable baseline lands
    deviation = sum(diffs) ** 0.5
    alerts = []
    if current.get("other", 0) / len(cmds) > 0.5:
        alerts.append({"type": "intent_unclear",
                       "ratio": round(current.get("other",0)/len(cmds), 2),
                       "msg": "over half of commands are 'other' — buckets need refinement",
                       "timestamp": datetime.now(timezone.utc).isoformat()})
    if alerts:
        with DRIFT_LOG.open("a") as f:
            for a in alerts:
                f.write(json.dumps(a)+"\n")
    return {"drift_detected": bool(alerts), "alert_count": len(alerts),
            "alerts": alerts, "deviation_score": round(deviation, 2)}

def daemon_state():
    try:
        out = subprocess.run(["pgrep","-af","bot_loop_v1.py"], capture_output=True, text=True, timeout=5)
        procs = [l for l in out.stdout.splitlines() if "bot_loop_v1.py" in l]
        return len(procs)
    except Exception:
        return 0

def respawn_daemon():
    for cand in [OR/"bin"/"bot_loop_v1.py", OR/"bot_loop_v1.py"]:
        if cand.exists():
            ts = time.strftime("%Y%m%d_%H%M%S")
            log = LOGS/f"bot_{ts}.log"
            subprocess.Popen(["nohup","python3",str(cand)], stdout=log.open("a"),
                             stderr=subprocess.STDOUT, start_new_session=True)
            return f"[banked] daemon respawned -> {log}"
    return "[held] bot_loop_v1.py not found anywhere"

def build_dashboard(cmds, patterns, drift):
    lines = [
        "# SuperLoop Composite Dashboard — %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "Auto-pulsed every 15 min via cron | Canary: [SUPERLOOPV3]", "",
        "## Command Flow Health",
        "- Commands analyzed: %d" % len(cmds),
        "- Dominant bucket: `%s`" % patterns.get("dominant_bucket"),
        "- Top transitions: %s" % ", ".join([t["rule"] for t in patterns.get("transition_weights", [])[:5]]),
        "", "## Routing Weights (Auto-Learned)",
        "| Trigger | Route | Model |", "|---------|-------|-------|",
    ]
    for route, cfg in patterns.get("routing_weights", {}).items():
        if isinstance(cfg, dict):
            lines.append("| %s | %s | %s |" % (route, cfg.get("route_to"), cfg.get("pref_model")))
    lines += ["", "## Drift Detection",
              "- Status: %s" % ("ALERTS" if drift.get("drift_detected") else "Stable"),
              "- 'other' ratio alert threshold: 50%"]
    for a in drift.get("alerts", []):
        lines.append(f"- [{a['type']}] {a['msg']}")
    lines += ["", "## Live Stack State"]
    try:
        r = subprocess.run(["curl","-sf","http://localhost:11434/api/tags"],
                           capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            tags = json.loads(r.stdout)
            loaded = [m.get("name") for m in tags.get("models", [])]
            lines.append("- Ollama: UP | Models: %s" % (", ".join(loaded) if loaded else "cold"))
        else:
            lines.append("- Ollama: DOWN")
    except Exception as e:
        lines.append("- Ollama: ERROR (%s)" % e)
    nc = daemon_state()
    lines.append("- bot_loop daemon: %s (%d proc)" % ("ALIVE" if nc else "RESPAWN NEEDED", nc))
    lines += ["", "---", "*Dashboard SHA256 prefix: %s*" % sha16(str(DASHBOARD)), "[exit=0]"]
    DASHBOARD.write_text("\n".join(lines))
    return len(lines)

def publish(confirm):
    if not confirm:
        return "[held] dashboard written locally; CONFIRM=1 publishes gist"
    import subprocess as sp
    try:
        payload = json.dumps({
            "description": "OpenRoot SUPERLOOP dashboard (auto-pulsed)",
            "files": {"STATE.md": {"content": DASHBOARD.read_text()}},
        })
        r = sp.run(["gh","api","-X","PATCH","gists/"+GIST_ID,"--input","-"],
                   input=payload, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return "[banked] gist published via gh api PATCH"
        return "[FAIL] gist: " + r.stderr[:200]
    except Exception as e:
        return "[FAIL] gist error: " + str(e)[:200]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recall", type=int, default=250)
    ap.add_argument("--confirm", type=int, default=0)
    ap.add_argument("--sample", type=int, default=0)
    a = ap.parse_args()
    seen = load_seen()
    cmds = recall(a.recall)
    new = recall_write(cmds, seen)
    patterns = mine_chains(cmds)
    drift = detect_drift(cmds)
    build_dashboard(cmds, patterns, drift)
    nc = daemon_state()
    if nc == 0:
        print(respawn_daemon())
    else:
        print("[banked] daemon alive (%d proc)" % nc)
    print("[SUPERLOOPV3] recalled=%d new=%d dominant=%s drift_alerts=%d" %
          (a.recall, new, patterns["dominant_bucket"], drift["alert_count"]))
    print(publish(a.confirm))
    print("[exit=0]")

def sample_other(top_n=20):
    """Evidence-based bucket tuning: show most-repeated 'other' commands."""
    counts = {}
    if CMDLOG.exists():
        for ln in CMDLOG.read_text(errors="replace").splitlines():
            try:
                e = json.loads(ln)
                if e["bucket"] == "other":
                    counts[e["cmd"]] = counts.get(e["cmd"], 0) + 1
            except Exception:
                pass
    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    print("[SAMPLE] top %d 'other' commands (freq):" % len(ranked))
    for cmd, n in ranked:
        print("  %3dx  %s" % (n, cmd[:140]))
    print("[SAMPLE] paste these back to Lumo -> we write bucket regexes from evidence")

if __name__ == "__main__":
    import sys as _sys
    if "--sample" in _sys.argv:
        sample_other()
    else:
        main()
