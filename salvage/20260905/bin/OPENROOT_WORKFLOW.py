#!/usr/bin/env python3
"""
OPENROOT WORKFLOW MANAGER v2.1 — OptiPlex Native
Jesse Ray McMillen | GOVERNOR-01 spoke
η = useful_joules / human_joules
Absolute paths only. No tilde. Serve lowest node.
"""

import os
import sys
import json
import hashlib
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

# ── Absolute path configuration (OptiPlex) ──────────────────────────
HOME = Path("/home/jesse")
OPENROOT = HOME / "openroot"
AGAPE_KB = OPENROOT / "agape_kb"
LOG_DIR = OPENROOT / "logs"
SEED_DIR = OPENROOT / "session_seeds"
BL_RMH = OPENROOT / "black-locust-rmh"
SSH_DIR = HOME / ".ssh"

PRIORITY = {
    "A": [
        "black_locust_rmh_alpine_ssh_bridge",
        "purge_assumed_saxton_tokens",
    ],
    "B": [
        "first_measured_eta_entry",
        "stand_up_optiplex_llama_server",
        "agape_kernel_load_check",
    ],
    "C": [
        "syncthing_mesh_phone_optiplex",
        "duns_mercury_only_after_live",
    ],
}

def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def sha256_file(p: Path) -> str:
    if not p.exists():
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd: list, timeout: int = 15) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def ensure_dirs():
    for d in [OPENROOT, AGAPE_KB, LOG_DIR, SEED_DIR, BL_RMH, SSH_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def log_eta(task: str, priority: str, eta: float, merkle: str, note: str = ""):
    entry = {
        "ts": utcnow(),
        "task": task,
        "priority": priority,
        "eta": round(eta, 6),
        "merkle": merkle[:32],
        "note": note,
        "host": platform.node(),
    }
    log_path = LOG_DIR / "workflow_eta.jsonl"
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"  [{priority}] {task}  η={eta:.4f}  {note}")

# ── Priority A ──────────────────────────────────────────────────────
def task_A1_black_locust():
    print("\n[A1] black-locust-rmh Alpine SSH bridge status")
    start = datetime.now(timezone.utc).timestamp()
    note = []
    # Check if Alpine container / chroot or SSH key exists
    key = SSH_DIR / "black-locust-rmh"
    if key.exists():
        note.append("ed25519 key present")
    else:
        note.append("NO key — generate with: ssh-keygen -t ed25519 -f /home/jesse/.ssh/black-locust-rmh -N ''")
    # Check for alpine binary or container
    rc, out, _ = run(["which", "alpine"])
    note.append("alpine binary" if rc == 0 else "alpine not installed")
    rc2, out2, _ = run(["systemctl", "is-active", "ssh"])
    note.append(f"sshd={out2 or 'unknown'}")
    end = datetime.now(timezone.utc).timestamp()
    human_j = max(0.001, (end - start) * 80)
    eta = 40.0 / human_j
    merkle = sha256_str(f"A1:{start}:{end}:{';'.join(note)}")
    log_eta("black_locust_rmh_alpine_ssh_bridge", "A", eta, merkle, " | ".join(note))
    return eta

def task_A2_purge_saxton():
    print("\n[A2] Purge assumed Saxton tokens")
    start = datetime.now(timezone.utc).timestamp()
    hits = []
    for root, _, files in os.walk(OPENROOT):
        for fn in files:
            if fn.endswith((".md", ".py", ".txt", ".json")):
                p = Path(root) / fn
                try:
                    txt = p.read_text(errors="ignore")
                    if "Saxton" in txt or "saxton" in txt:
                        hits.append(str(p))
                except Exception:
                    pass
    note = f"{len(hits)} hits" if hits else "CLEAN"
    if hits:
        note += " → " + ", ".join(hits[:3])
    end = datetime.now(timezone.utc).timestamp()
    human_j = max(0.001, (end - start) * 80)
    eta = 25.0 / human_j
    merkle = sha256_str(f"A2:{start}:{end}:{note}")
    log_eta("purge_assumed_saxton_tokens", "A", eta, merkle, note)
    return eta

# ── Priority B ──────────────────────────────────────────────────────
def task_B1_first_eta():
    print("\n[B1] First measured η entry (Standing Wave)")
    start = datetime.now(timezone.utc).timestamp()
    axiom = AGAPE_KB / "STANDING_WAVE_AXIOM.md"
    if not axiom.exists():
        axiom.write_text(
            f"# STANDING_WAVE_AXIOM\n\nCreated {utcnow()}\nη = useful_joules / human_joules\nR=1.0\n",
            encoding="utf-8",
        )
        note = "axiom created"
    else:
        size = axiom.stat().st_size
        lines = len(axiom.read_text().splitlines())
        note = f"exists {size}B / {lines} lines"
    end = datetime.now(timezone.utc).timestamp()
    human_j = max(0.001, (end - start) * 80)
    eta = 15.0 / human_j
    merkle = sha256_str(f"B1:{start}:{end}:{note}")
    log_eta("first_measured_eta_entry", "B", eta, merkle, note)
    return eta

def task_B2_llama_server():
    print("\n[B2] OptiPlex llama-server status")
    start = datetime.now(timezone.utc).timestamp()
    note = []
    rc, out, _ = run(["which", "llama-server"])
    if rc == 0:
        note.append(f"binary={out}")
    else:
        note.append("llama-server NOT in PATH")
    # Check common service names
    for svc in ["llama-server", "llama", "ollama"]:
        rc2, st, _ = run(["systemctl", "is-active", svc])
        if st:
            note.append(f"{svc}={st}")
    # Port check
    rc3, ports, _ = run(["ss", "-tlnp"])
    if "8080" in ports or "11434" in ports:
        note.append("listening port found")
    else:
        note.append("no 8080/11434 listener")
    end = datetime.now(timezone.utc).timestamp()
    human_j = max(0.001, (end - start) * 80)
    eta = 120.0 / human_j   # high value if this is the real stand-up
    merkle = sha256_str(f"B2:{start}:{end}:{';'.join(note)}")
    log_eta("stand_up_optiplex_llama_server", "B", eta, merkle, " | ".join(note))
    return eta

def task_B3_kernel_check():
    print("\n[B3] Agape kernel presence check")
    start = datetime.now(timezone.utc).timestamp()
    kernel = OPENROOT / "agape-bible-kernel"
    note = "kernel dir present" if kernel.exists() else "kernel dir MISSING"
    end = datetime.now(timezone.utc).timestamp()
    human_j = max(0.001, (end - start) * 80)
    eta = 10.0 / human_j
    merkle = sha256_str(f"B3:{start}:{end}:{note}")
    log_eta("agape_kernel_load_check", "B", eta, merkle, note)
    return eta

# ── Priority C ──────────────────────────────────────────────────────
def task_C1_syncthing():
    print("\n[C1] Syncthing mesh status")
    start = datetime.now(timezone.utc).timestamp()
    rc, out, _ = run(["which", "syncthing"])
    note = f"binary={out}" if rc == 0 else "syncthing NOT installed"
    rc2, st, _ = run(["systemctl", "is-active", "syncthing@jesse"])
    if st:
        note += f" | service={st}"
    end = datetime.now(timezone.utc).timestamp()
    human_j = max(0.001, (end - start) * 80)
    eta = 60.0 / human_j
    merkle = sha256_str(f"C1:{start}:{end}:{note}")
    log_eta("syncthing_mesh_phone_optiplex", "C", eta, merkle, note)
    return eta

def task_C2_duns():
    print("\n[C2] DUNS + Mercury deferred")
    log_eta("duns_mercury_only_after_live", "C", 0.0, "DEFERRED", "A+B must be live first")
    return 0.0

# ── Main ────────────────────────────────────────────────────────────
def main():
    print("=" * 72)
    print("  OPENROOT WORKFLOW MANAGER v2.1 — OptiPlex Native")
    print("  η = useful_joules / human_joules   R=1.0")
    print("=" * 72)
    ensure_dirs()
    total = 0.0
    total += task_A1_black_locust()
    total += task_A2_purge_saxton()
    total += task_B1_first_eta()
    total += task_B2_llama_server()
    total += task_B3_kernel_check()
    total += task_C1_syncthing()
    total += task_C2_duns()
    print("\n" + "=" * 72)
    print(f"  TOTAL η this pass: {total:.4f}")
    print(f"  Log: {LOG_DIR / 'workflow_eta.jsonl'}")
    print("=" * 72)
    print("\nNEXT PHYSICAL ACTIONS (highest leverage):")
    print("  1. ssh-keygen -t ed25519 -f /home/jesse/.ssh/black-locust-rmh -N ''")
    print("  2. Finish Alpine SSH bridge on black-locust-rmh")
    print("  3. Install + enable llama-server 7-8B Q4 on this box")
    print("  4. syncthing phone ↔ /home/jesse/openroot")
    print("=" * 72)

if __name__ == "__main__":
    sys.exit(main() or 0)
