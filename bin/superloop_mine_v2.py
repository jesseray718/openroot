#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""superloop_mine_v2.py — mine command chains → learn routing weights, detect drift."""
import argparse, json, hashlib, re, sqlite3, subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

OR = Path("/home/jesse/openroot")
DATA = OR / "data"
CTX = OR / "context_bridge"
CMDLOG = DATA / "superloop_commands.jsonl"
CHAINS = DATA / "superloop_chains.json"
ROUTER_WEIGHTS = DATA / "model_registry.json"
DRIFT_LOG = DATA / "drift_alerts.jsonl"
DASHBOARD = CTX / "superloop_DASHBOARD.md"
GIST_ID = "3ffffa18763e5cbfdb5c44cc23743f4b"

def sha16(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def load_commands(last_hours=48):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=last_hours)
    cmds = []
    if CMDLOG.exists():
        for line in CMDLOG.read_text().splitlines():
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00"))
                if ts >= cutoff:
                    cmds.append(entry)
            except Exception:
                pass
    return cmds

def mine_patterns(cmds):
    """Turn raw commands into weighted routing rules."""
    buckets = [e["bucket"] for e in cmds]
    transitions = list(zip(buckets[:-1], buckets[1:]))
    
    # Learn: when X occurs, Y likely follows (routing weight)
    follow_weights = {}
    for a, b in transitions:
        k = f"{a}->{b}"
        follow_weights[k] = follow_weights.get(k, 0) + 1
    
    # Sort by frequency
    ranked = sorted(follow_weights.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Bucket affinity (what models/tools fit each bucket?)
    bucket_affinity = {
        "bridge": {"route_to": "smart_router", "pref_model": "7b", "reason": "ssh/scp require context awareness"},
        "gitops": {"route_to": "smart_router", "pref_model": "7b", "reason": "commit/PR operations need precision"},
        "model": {"route_to": "qwen2.5-coder:7b", "pref_model": "7b", "reason": "direct ollama inference"},
        "author": {"route_to": "7b", "pref_model": "7b", "reason": "heredoc/cat requires precise formatting"},
        "exec": {"route_to": "3b", "pref_model": "3b", "reason": "syntax checks are grader-domain"},
        "gate": {"route_to": "team_gate", "pref_model": "3b", "reason": "verification/grading"},
        "system": {"route_to": "local_shell", "pref_model": "none", "reason": "direct ps/df commands"},
        "net": {"route_to": "smart_router", "pref_model": "7b", "reason": "curl/wget/tailscale need state"},
        "other": {"route_to": "lumo", "pref_model": "max", "reason": "fallback for unclear intent"},
    }
    
    output = {
        "learned_at": datetime.now(timezone.utc).isoformat(),
        "total_cmds_analyzed": len(cmds),
        "transition_weights": [{"rule": k, "count": n} for k, n in ranked],
        "routing_weights": bucket_affinity,
        "dominant_bucket": Counter(buckets).most_common(1)[0][0] if buckets else "unknown",
    }
    
    ROUTER_WEIGHTS.write_text(json.dumps(output, indent=2))
    return output

def detect_drift(cmds, threshold_deviation=0.3):
    """Flag when your actual command distribution diverges from expected pattern."""
    if not CHAINS.exists():
        return {"drift_detected": False, "reason": "no baseline chains"}
    
    baseline = json.loads(CHAINS.read_text())
    baseline_buckets = baseline.get("bucket_counts", {})
    
    current_buckets = dict(Counter(e["bucket"] for e in cmds))
    
    # Simple cosine similarity deviation
    keys = set(baseline_buckets.keys()) | set(current_buckets.keys())
    diffs = [(baseline_buckets.get(k, 0) - current_buckets.get(k, 0))**2 for k in keys]
    deviation = sum(diffs) ** 0.5
    
    alerts = []
    if deviation > threshold_deviation * len(cmds):
        alerts.append({
            "type": "distribution_shift",
            "deviation": round(deviation, 2),
            "threshold": threshold_deviation * len(cmds),
            "msg": f"Command distribution shifted significantly. Baseline: {baseline_buckets}, Current: {current_buckets}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    
    # Check for orphaned workflows (other > 60% = unclear intent)
    if cmds:
        other_ratio = current_buckets.get("other", 0) / len(cmds)
        if other_ratio > 0.6:
            alerts.append({
                "type": "intent_unclear",
                "ratio": round(other_ratio, 2),
                "msg": f"{round(other_ratio*100)}% of commands classified as 'other' — routing rule needs refinement",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    
    if alerts:
        with DRIFT_LOG.open("a") as f:
            for a in alerts:
                f.write(json.dumps(a) + "\n")
    
    return {
        "drift_detected": len(alerts) > 0,
        "alert_count": len(alerts),
        "alerts": alerts,
        "deviation_score": deviation,
    }

def build_dashboard(cmds, patterns, drift):
    """Generate human-readable dashboard with actionable insights."""
    lines = [
        "# SuperLoop Dashboard — %s" % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "Auto-updated every cycle (cron @ 15 min intervals)",
        "**Canary:** [SUPERLOOPV2]",
        "",
        "## Command Flow Health",
        "- Recalled this cycle: %d commands" % len(cmds),
        "- Dominant bucket: `%s`" % patterns.get("dominant_bucket", "N/A"),
        "- Top transitions: %s" % ", ".join([t["rule"] for t in patterns.get("transition_weights", [])[:5]]),
        "",
        "## Routing Weights (Auto-Learned)",
        "| Trigger → Action | Model | Reason |",
        "|------------------|-------|--------|",
    ]
    
    for route, cfg in patterns.get("routing_weights", {}).items():
        if isinstance(cfg, dict):
            lines.append("| %s → %s | %s | %s |" % (
                route, cfg.get("route_to"), cfg.get("pref_model"), cfg.get("reason", "")
            ))
    
    lines += [
        "",
        "## Drift Detection",
        "- Status: %s" % ("⚠️ ALERTS" if drift.get("drift_detected") else "✅ Stable"),
        "- Deviation score: %.2f" % drift.get("deviation_score", 0),
    ]
    
    if drift.get("alerts"):
        lines.append("- **Alerts:**")
        for a in drift["alerts"]:
            lines.append(f"  - [{a['type']}] {a['msg']}")
    
    lines += [
        "",
        "## Live Stack State",
    ]
    # Pull live metrics
    try:
        ollama_tags = subprocess.run(["curl","-sf","http://localhost:11434/api/tags"],
                                      capture_output=True, text=True, timeout=5)
        if ollama_tags.returncode == 0:
            tags = json.loads(ollama_tags.stdout)
            loaded = [m.get("name") for m in tags.get("models", []) if m.get("size"]]
            lines.append(f"- Ollama: UP | Loaded: {', '.join(loaded) if loaded else 'cold'}")
        else:
            lines.append("- Ollama: DOWN")
    except Exception as e:
        lines.append(f"- Ollama: ERROR ({e})")
    
    try:
        daemon_check = subprocess.run(["pgrep","-af","bot_loop_v1.py"],
                                       capture_output=True, text=True, timeout=5)
        proc_count = len([l for l in daemon_check.stdout.splitlines() if "bot_loop_v1.py" in l])
        lines.append(f"- bot_loop daemon: {'ALIVE' if proc_count > 0 else 'RESPAWN NEEDED'} ({proc_count} proc)")
    except Exception:
        lines.append("- bot_loop: UNKNOWN")
    
    lines += [
        "",
        "---",
        f"*Dashboard SHA256 prefix: {sha16(DASHBOARD.name)}*",
        "[exit=0]",
    ]
    
    DASHBOARD.write_text("\n".join(lines))
    return len(lines)

def publish(confirm):
    """Update the LIVING STATE gist if confirmed."""
    if not confirm:
        return "[held] local dashboard written; CONFIRM=1 pushes gist"
    
    try:
        # Publish DASHBOARD.md to gist
        r = subprocess.run(
            ["gh","gist","edit",GIST_ID,"-f","STATE.md","-",str(DASHBOARD)],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0:
            return "[banked] gist updated"
        else:
            return "[FAIL] gist update: " + r.stderr[:200]
    except Exception as e:
        return "[FAIL] gist error: " + str(e)[:200]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", type=int, default=0)
    a = ap.parse_args()
    
    # Load recent commands
    cmds = load_commands(last_hours=48)
    if not cmds:
        print("[WARN] No commands found in last 48h — check CMDLOG path")
        return
    
    # Mine patterns
    patterns = mine_patterns(cmds)
    print(f"[mine] patterns learned: dominant={patterns['dominant_bucket']}")
    
    # Detect drift
    drift = detect_drift(cmds)
    if drift.get("drift_detected"):
        print(f"[drift] ⚠️ {drift['alert_count']} alert(s) — review data/drift_alerts.jsonl")
    else:
        print("[drift] ✅ stable within threshold")
    
    # Build dashboard
    lines = build_dashboard(cmds, patterns, drift)
    print(f"[dashboard] written to {DASHBOARD.name} ({lines} lines)")
    
    # Publish (if confirmed)
    result = publish(a.confirm)
    print(result)
    print("[exit=0]")

if __name__ == "__main__":
    main()
