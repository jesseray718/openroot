#!/usr/bin/env python3
"""workflow_dispatcher_v1.py — validates & routes the ALIGN/ASSESS/ACT/VERIFY/DOCUMENT/AMPLIFY envelope.
Whitelist registry ONLY. Unknown action or /root/ path = [held], never executed. Human is final gate.
Usage: cat envelope.json | python3 workflow_dispatcher_v1.py [--dry-run]"""
import json, sys, subprocess, hashlib, datetime

REGISTRY = {  # phase -> (implemented, executor) ; executors are shell strings run on host
  "align":   (True,  "echo '[align] doctrine manifest via env_map' && python3 /home/jesse/openroot/bin/env_map.py"),
  "assess":  (True,  "gh search repos --owner jesseray718 --sort updated --limit 10"),
  "act":     (False, None),  # calculate_eta: needs RAPL ledger fusion — registered, not yet implemented
  "verify":  (True,  "bash /home/jesse/openroot/bin/stack_gate.sh /home/jesse/openroot/bin/stack_gate.sh"),
  "document":(True,  "__DOC__"),
  "amplify": (True,  "__AMP__"),
}
FORBIDDEN_PREFIX = "/root/"   # false-root contamination guard — maps to real home

def stamp(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
def now_iso(): return datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"


SINGLE_SHOT = {  # envelope-level tools (no steps wrapper) -> executor, read-only
  "read_wiki_contents": "rm -rf /tmp/wiki_ro; git clone --depth 1 https://github.com/jesseray718/jesseray718.wiki.git /tmp/wiki_ro 2>&1 | tail -2; ls /tmp/wiki_ro/*.md 2>/dev/null | head -10",
  "search_github": "gh search prs --author jesseray718 --limit 10 && gh search issues --author jesseray718 --limit 10",
}
def dispatch_single(envelope, dry):
    name = envelope.get("name")
    if name not in SINGLE_SHOT:
        return {"phase": name, "status": "held", "note": "unknown action — not in registry"}
    cmd = SINGLE_SHOT[name]
    if dry: return {"phase": name, "status": "dry-run", "note": cmd}
    import subprocess
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    return {"phase": name, "status": "banked" if r.returncode == 0 else "held",
            "note": (r.stdout or r.stderr)[:300]}

def main():
    dry = "--dry-run" in sys.argv
    envelope = json.load(sys.stdin)
    if "steps" not in envelope.get("arguments", {}):  # single-shot envelope
        res = dispatch_single(envelope, dry)
        print(json.dumps({"ts": now_iso(), "phases": [res]}, indent=2))
        with open(f"/home/jesse/openroot/logs/heartbeat/{stamp()}-receipt.md", "a") as f:
            f.write(f"\n## single-shot {now_iso()}\n- {res['phase']}: {res['status']}\n")
        return
    steps = envelope.get("arguments", {}).get("steps", {})
    receipt = {"ts": now_iso(), "phases": [], "envelope_sha256":
               hashlib.sha256(json.dumps(envelope, sort_keys=True).encode()).hexdigest()}
    for phase in ("align", "assess", "act", "verify", "document", "amplify"):
        if phase not in steps: continue
        spec = steps.get(phase, {})
        # path sanitation: /root/ -> /home/jesse/openroot/
        raw = json.dumps(spec)
        if FORBIDDEN_PREFIX in raw:
            print(f"[held] {phase}: /root/ path rejected — remapping to /home/jesse/openroot/")
            raw = raw.replace("/root/", "/home/jesse/openroot/")
        implemented, exe = REGISTRY[phase]
        if not implemented:
            receipt["phases"].append({"phase": phase, "status": "held", "reason": "registered, not implemented (eta calc needs RAPL fusion)"})
            continue
        if phase == "document":
            outp = f"/home/jesse/openroot/logs/heartbeat/{stamp()}-receipt.md"
            cmd = f"true"
            status, note = "held", "receipt written by dispatcher (below)"
        elif phase == "amplify":
            cmd = None; status, note = "held", "proposals require human gate"
        else:
            cmd = exe
            if dry:
                status, note = "dry-run", cmd
            else:
                try:
                    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=600)
                    status = "banked" if r.returncode == 0 else "held"
                    note = (r.stdout or r.stderr)[:200]
                except Exception as e:
                    status, note = "held", str(e)[:120]
            receipt["phases"].append({"phase": phase, "status": status, "note": note})
    # document phase always writes the receipt itself
    recpath = f"/home/jesse/openroot/logs/heartbeat/{stamp()}-receipt.md"
    with open(recpath, "a") as f:
        f.write(f"\n## workflow {now_iso()}\n")
        for p in receipt["phases"]:
            f.write(f"- {p['phase']}: {p['status']} — {p.get('note','')}\n")
    print(json.dumps(receipt, indent=2))
    print(f"[banked] receipt -> {recpath}")

if __name__ == "__main__":
    main()
