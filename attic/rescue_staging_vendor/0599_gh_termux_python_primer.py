#!/usr/bin/env python3
from pathlib import Path
import json, os, shutil, subprocess, sys, time

def run(cmd, timeout=20):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except FileNotFoundError:
        return 127, "", "not found: " + cmd[0]
    except Exception as e:
        return 1, "", str(e)

home = Path("/data/data/com.termux/files/home")
report = {
    "t": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "cwd": str(Path.cwd()),
    "python": sys.version.split()[0],
    "bins": {n: shutil.which(n) for n in ("git", "gh", "python3", "rish")},
    "git_name": run(["git", "config", "--get", "user.name"])[1] or None,
    "git_email": run(["git", "config", "--get", "user.email"])[1] or None,
    "code_tree": str(home / "code/openroot"),
    "src_tree": str(home / "src/openroot"),
    "code_exists": (home / "code/openroot/.git").exists(),
    "src_exists": (home / "src/openroot/.git").exists(),
    "mesh_exists": Path("/storage/emulated/0/openroot").exists(),
    "canon": (home / "openroot/canon/src/canon.py").exists(),
}
rc, out, err = run(["gh", "auth", "status"])
report["gh_auth_ok"] = "Logged in" in (out + err)
print(json.dumps(report, indent=2))
