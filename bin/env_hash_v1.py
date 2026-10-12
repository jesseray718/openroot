#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""env_hash_v1.py — environment fingerprint; composite excludes timestamp."""
import hashlib, json, os, platform, subprocess, time
OUT = "/home/jesse/openroot/data/env_hash.json"

def sh(cmd, timeout=30):
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip() if p.returncode == 0 else ""
    except Exception:
        return ""

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

def fingerprint():
    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": platform.python_version(),
        "kernel": platform.release(),
        "distro": sh(". /etc/os-release && echo $PRETTY_NAME"),
        "cpu": platform.processor() or platform.machine(),
        "ollama_models_sha": h(sh("ollama list 2>/dev/null")),
        "pip_freeze_sha": h(sh("python3 -m pip freeze 2>/dev/null | sort")),
        "locale_env_sha": h("|".join("%s=%s" % (k, os.environ.get(k, ""))
                        for k in ("LANG", "LC_ALL", "TZ"))),
        "hostname": platform.node(),
    }

if __name__ == "__main__":
    fp = fingerprint()
    stable = {k: v for k, v in fp.items() if k != "ts"}
    composite = h(json.dumps(stable, sort_keys=True))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"env_hash": composite, "components": fp}, f, indent=2, sort_keys=True)
    print("[banked] env_hash=%s" % composite)
