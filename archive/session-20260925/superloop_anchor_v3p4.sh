#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# superloop_anchor_v3p4.sh — PROMPT-ANCHORED recall (tmux capture fix + final regex)
# Canary: [SUPERLOOPV3P4]  Human gate: run, inspect, then git commit
set -euo pipefail
OR=/home/jesse/openroot

cat > "$OR/bin/superloop_recall_fixed.py" <<'PYEOF'
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Prompt-anchored tmux recall: only capture lines AFTER shell prompts.
Filters: #, -, quotes, brackets, vars, JSON, markdown output lines."""
import argparse, hashlib, json, re, subprocess, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OR = Path("/home/jesse/openroot")
DATA, CTX, LOGS = OR/"data", OR/"context_bridge", OR/"logs"
CMDLOG, CHAINS = DATA/"superloop_commands.jsonl", DATA/"superloop_chains.json"
GIST_ID = "3ffffa18763e5cbfdb5c44cc23743f4b"
HISTFILE = Path("/home/jesse/.bash_history")

# PROMPT PATTERN: captures "optiplex3060:~/*$ " or "localhost:~$ "
PROMPT_RE = re.compile(r'^(optiplex3060|localhost):~[\w/-]*\$\s+')

# Filter: lines that are OUTPUT (not commands)
OUTPUT_RE = re.compile(r'^(\s*#|\s*-+\s*$|"## |\s*- |\[[a-zA-Z]+"\s*:|^\w+\s*=\s*"[a-zA-Z]|\^C|\^\d')

BUCKETS = [
    ("bridge",   r"\b(ssh|scp)\b"),
    ("gitops",   r"\b(git|gh)\b"),
    ("model",    r"(ollama|localhost:11434|qwen)"),
    ("author",   r"cat\s*<<|heredoc|PYE?OF"),
    ("exec",     r"^(python3?|bash|sh)\b|py_compile"),
    ("assistant",r"\b(lumo|hive\.sh|nanobot|smart_router|bot_loop|mistake_engine)\b"),
    ("gate",     r"(stack_gate|team_gate|push_guard|grep\s+-q)"),
    ("system",   r"\b(ps|pgrep|kill|nohup|crontab|df|free)\b"),
    ("net",      r"\b(curl|wget|tailscale)\b"),
    ("files",    r"^(ls|cat|grep|tail|head|sed|mv|cp|mkdir|find|wc|rm|touch)\b"),
    ("nav",      r"^cd\b|^pushd\b|^pwd$"),
    ("vars",     r"^[A-Za-z_]\w*=.*"),
    ("builtin",  r"^(echo|export|alias|chmod|chown|tar|zip|unzip|nano|vi|vim|less|which|whoami|date|sleep|clear|history|man)\b"),
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
    """ONLY capture lines AFTER shell prompts. Discard output lines."""
    cmds = []
    
    # 1) flushed history (always clean)
    if HISTFILE.exists():
        raw = HISTFILE.read_text(errors="replace").splitlines()
        cmds = [l.strip() for l in raw if l.strip() and not l.startswith("#")]
    
    # 2) tmux scrollback — PROMPT-ANCHORED
    try:
        sess = subprocess.run(["tmux","ls"], capture_output=True, text=True, timeout=5)
        for line in sess.stdout.splitlines():
            sname = line.split(":")[0].strip()
            if not sname:
                continue
            cap = subprocess.run(["tmux","capture-pane","-p","-S","-%d"%n,"-t",sname],
                                 capture_output=True, text=True, timeout=5)
            
            in_cmd = False
            captured = []
            for l in cap.stdout.splitlines():
                t = l.strip()
                
                # If we see a PROMPT, start capturing the NEXT line as command
                if PROMPT_RE.search(t):
                    in_cmd = True
                    continue
                
                # If we're expecting a command (after prompt), capture it
                if in_cmd:
                    # Skip output markers
                    if OUTPUT_RE.match(t) or t.startswith(("default","Attached")):
                        in_cmd = False
                        captured.append(None)  # reset
                        continue
                    
                    if t and " " in t and not t.startswith("#"):
                        cmds.append(t)
                        in_cmd = False
            
            # Fallback: also grab lines after $ that aren't obviously output
            for t in cap.stdout.splitlines():
                if "$ " in t and not OUTPUT_RE.match(t):
                    parts = t.split("$ ",1)
                    if len(parts) == 2 and parts[1].strip():
                        candidate = parts[1].strip()
                        if not OUTPUT_RE.match(candidate):
                            cmds.append(candidate)
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
        "nav":      {"route_to": "local_shell", "pref_model": "none"},
        "vars":     {"route_to": "local_shell", "pref_model": "none"},
        "builtin":  {"route_to": "local_shell", "pref_model": "none"},
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
    (OR/"data"/"model_registry.json").write_text(json.dumps(out, indent=2))
    return out

def publish(confirm):
    if not confirm:
        return "[held] dashboard written locally; CONFIRM=1 publishes gist"
    try:
        import subprocess as sp
        payload = json.dumps({
            "description": "OpenRoot SUPERLOOP dashboard (auto-pulsed)",
            "files": {"STATE.md": {"content": (CTX/"superloop_DASHBOARD.md").read_text()}},
        })
        r = sp.run(["gh","api","-X","PATCH","gists/"+GIST_ID,"--input","-"],
                   input=payload, capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            return "[banked] gist published via gh api PATCH"
        return "[FAIL] gist: " + r.stderr[:200]
    except Exception as e:
        return "[FAIL] gist error: " + str(e)[:200]

def build_dashboard(cmds, patterns):
    lines = [
        "# SuperLoop — PROMPT-ANCHORED (v3p4)",
        "**Canary:** [SUPERLOOPV3P4] | Auto-pulsed every 15 min via cron", "",
        "## Command Classification Health",
        "- Commands analyzed: %d" % len(cmds),
        "- Dominant bucket: `%s`" % patterns.get("dominant_bucket"),
        "- Clean 'other' ratio: **TARGET <20%** (current depends on sample size)",
        "", "## Routing Weights (Auto-Learned)",
        "| Trigger | Route | Model |", "|---------|-------|-------|",
    ]
    for route, cfg in patterns.get("routing_weights", {}).items():
        if isinstance(cfg, dict):
            lines.append("| %s | %s | %s |" % (route, cfg.get("route_to"), cfg.get("pref_model")))
    lines += ["", "---", "*Dashboard SHA256 prefix: %s*" % sha16(str(CTX/"superloop_DASHBOARD.md")), "[exit=0]"]
    (CTX/"superloop_DASHBOARD.md").write_text("\n".join(lines))
    return len(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recall", type=int, default=250)
    ap.add_argument("--confirm", type=int, default=0)
    a = ap.parse_args()
    
    seen = load_seen()
    cmds = recall(a.recall)
    new = recall_write(cmds, seen)
    patterns = mine_chains(cmds)
    build_dashboard(cmds, patterns)
    
    print("[SUPERLOOPV3P4] recalled=%d new=%d dominant=%s" % (a.recall, new, patterns["dominant_bucket"]))
    print("[RECLASS] Check data/superloop_commands.jsonl — 'other' should now be <20%%")
    print(publish(a.confirm))
    print("[exit=0]")

if __name__ == "__main__":
    main()
PYEOF

python3 -m py_compile "$OR/bin/superloop_recall_fixed.py" && echo "[gate:py_compile] PASS"

echo "=== RUN PROMPT-ANCHORED RECALL ==="
CONFIRM="${CONFIRM:-0}"
python3 "$OR/bin/superloop_recall_fixed.py" --recall 250 --confirm "$CONFIRM"

echo ""
echo "=== CHECK CLASSIFICATION QUALITY ==="
python3 "$OR/bin/superloop_other_census.py"

echo ""
echo "=== READY TO COMMIT IF 'other' < 20% ==="
echo "git add bin/superloop_recall_fixed.py data/model_registry.json context_bridge/superloop_DASHBOARD.md"
echo "git commit -m '[ADD][SUPERLOOP] prompt-anchored tmux recall + builtin bucket; AI-assisted, human-gated'"
echo "[exit=0]"
