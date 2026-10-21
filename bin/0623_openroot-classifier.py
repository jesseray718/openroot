#!/usr/bin/env python3
"""
OpenRoot Security Classifier v2
Classify pane, classify path, admit or refuse, then touch the bus.
No third state. No network. No mutation.

v1 was policy-correct and mesh-wrong:
  - hardcoded /home/jesse while PATH_INVENTORY.yaml says /home/optiplex
  - treated all of /storage/emulated/0 as the bus
  - defined COLD_SSH and BUS_SUBDIRS then never enforced them
  - -q still printed debug
  - prefix-matched /home/jessefoo as BOX
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ============= ENUMS =============

class Pane(Enum):
    SSH = "SSH"          # OptiPlex heavy spoke
    A15 = "A15"          # Samsung A15 Termux governor
    UNKNOWN = "UNKNOWN"


class PathClass(Enum):
    BOX = "BOX"          # OptiPlex home tree
    PHONE = "PHONE"      # Android shared storage / Termux tree
    MESH = "MESH"        # declared Syncthing share roots
    BUS = "BUS"          # inbox/ outbox/ dump/ under a mesh root
    COLD = "COLD"        # models, archive — read maybe, mutate no
    CLONE = "CLONE"      # git working copy that is NOT the live mesh
    RELATIVE = "RELATIVE"
    OTHER = "OTHER"


# ============= CANONICAL TREE (dual-accept until identity lock) =============
# Source of truth: jesseray718/PATH_INVENTORY.yaml v1.4
# Plus the live classifier constants you already use on the box.
# Accept BOTH jesse and optiplex homes. Refuse everything else on the box.

BOX_HOMES = [
    "/home/jesse",
    "/home/optiplex",
]

MESH_ROOTS = [
    "/home/jesse/openroot",
    "/home/optiplex/openroot",
    "/storage/emulated/0/openroot",
    "/sdcard/openroot",
    "/storage/emulated/0/Syncthing/openroot",
]

# Git clone on the phone is not the mesh share.
CLONE_ROOTS = [
    "/data/data/com.termux/files/home/openroot",
    "/data/data/com.termux/files/home/src/openroot-foundation",
]

COLD_ROOTS = [
    "/home/jesse/archive",
    "/home/jesse/models",
    "/home/optiplex/archive",
    "/home/optiplex/models",
    "/home/optiplex/agape_kb",
]

PHONE_ROOTS = [
    "/data/data/com.termux",
    "/storage/emulated/0",
    "/sdcard",
]

BUS_SUBDIRS = ("inbox", "outbox", "dump")

SSH_HOSTS = {
    "optiplex3060",
    "optiplex-3060",
    "optiplex3060sff",
    "optiplex",
}

SYNCTHING_ID_WIPES = frozenset({
    "--wipe-id",
    "--reset-database",
    "--reset-deltas",
    "--force-rescan",
    "--generate",
    "reset-database",
    "wipe-id",
})

WRITEISH = frozenset({
    "cp", "mv", "rm", "rmdir", "mkdir", "touch", "ln",
    "tee", "install", "rsync", "dd", "truncate",
    "sed", "awk", "python", "python3", "bash", "sh",
    "git", "syncthing",
})


def _add_unique(seq: list, value: str) -> None:
    if value and value not in seq:
        seq.append(value)


def _read_kv(path: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        return {}
    return out


def load_identity() -> Dict[str, str]:
    """
    Load etc/identity.env if present. Stdlib only. First file wins extras,
    all files may add roots. This is the map the valve actually obeys.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.environ.get("OPENROOT_IDENTITY", ""),
        os.path.join(here, "..", "etc", "identity.env"),
        "/home/jesse/openroot/etc/identity.env",
        "/home/optiplex/openroot/etc/identity.env",
        "/storage/emulated/0/openroot/etc/identity.env",
        "/sdcard/openroot/etc/identity.env",
        os.path.expanduser("~/openroot/etc/identity.env"),
    ]
    merged: Dict[str, str] = {}
    for c in candidates:
        if not c:
            continue
        kv = _read_kv(os.path.normpath(c))
        if not kv:
            continue
        for k, v in kv.items():
            merged.setdefault(k, v)
        home = kv.get("BOX_HOME")
        if home:
            _add_unique(BOX_HOMES, home)
            _add_unique(MESH_ROOTS, home.rstrip("/") + "/openroot")
            _add_unique(COLD_ROOTS, home.rstrip("/") + "/models")
            _add_unique(COLD_ROOTS, home.rstrip("/") + "/archive")
        mesh = kv.get("MESH_BOX") or kv.get("MESH_ROOT")
        if mesh:
            _add_unique(MESH_ROOTS, mesh)
        phone_mesh = kv.get("MESH_PHONE")
        if phone_mesh:
            _add_unique(MESH_ROOTS, phone_mesh)
        st = kv.get("MESH_ST")
        if st:
            _add_unique(MESH_ROOTS, st)
        host = kv.get("BOX_HOST")
        if host:
            SSH_HOSTS.add(host.strip().lower().split(".")[0])
    return merged


IDENTITY = load_identity()


# ============= PATH HELPERS =============

def norm(path: str) -> str:
    if not path:
        return ""
    return os.path.normpath(path.replace("\\", "/"))


def is_under(path: str, root: str) -> bool:
    """True iff path is root or a child. No /home/jessefoo false-positive."""
    p = norm(path)
    r = norm(root)
    if p == r:
        return True
    return p.startswith(r + "/")


def under_any(path: str, roots: Iterable[str]) -> Optional[str]:
    for r in roots:
        if is_under(path, r):
            return r
    return None


def bus_subdir_of(path: str) -> Optional[str]:
    """Return inbox|outbox|dump if path sits in that folder under a mesh root."""
    mesh = under_any(path, MESH_ROOTS)
    if not mesh:
        return None
    rest = norm(path)[len(norm(mesh)):].lstrip("/")
    if not rest:
        return None
    first = rest.split("/", 1)[0]
    if first in BUS_SUBDIRS:
        return first
    return None


# ============= CLASSIFIERS =============

def classify_pane(env: dict, prompt_hostname: Optional[str] = None) -> Pane:
    """
    Prompt hostname wins over cwd. PWD on the phone does not make you SSH.
    Conflict => UNKNOWN. No third operating state that pretends it is safe.
    """
    home = env.get("HOME", "") or ""
    prefix = env.get("PREFIX", "") or ""
    user = env.get("USER") or env.get("LOGNAME") or ""
    host_raw = env.get("HOSTNAME") or env.get("HOST") or ""
    try:
        if not host_raw:
            host_raw = socket.gethostname()
    except OSError:
        host_raw = ""
    host = host_raw.strip().lower().split(".")[0]

    prompt_host = ""
    if prompt_hostname:
        prompt_host = prompt_hostname.strip().lower().split(".")[0]
        if "@" in prompt_host:
            prompt_host = prompt_host.split("@", 1)[1]

    ssh_hits = [
        user in ("jesse", "optiplex"),
        host in SSH_HOSTS,
        prompt_host in SSH_HOSTS,
        any(home == h or home.startswith(h + "/") for h in BOX_HOMES),
    ]
    a15_hits = [
        user.startswith("u0_a"),
        home.startswith("/data/data/com.termux"),
        prefix.startswith("/data/data/com.termux"),
        home.startswith("/storage/emulated/0"),
    ]

    ssh = any(ssh_hits)
    a15 = any(a15_hits)

    if ssh and a15:
        return Pane.UNKNOWN
    if ssh:
        if home.startswith("/data/data/com.termux"):
            return Pane.UNKNOWN
        return Pane.SSH
    if a15:
        return Pane.A15
    return Pane.UNKNOWN


def classify_path(path: str, cwd: str) -> Tuple[PathClass, str]:
    """
    Classify without following symlinks.
    Returns (class, resolved_or_original).
    Relative stays RELATIVE until resolve_relative is called by the gate.
    """
    if not path:
        return PathClass.OTHER, path
    if not path.startswith("/"):
        return PathClass.RELATIVE, path

    p = norm(path)

    if under_any(p, COLD_ROOTS):
        return PathClass.COLD, p
    if bus_subdir_of(p):
        return PathClass.BUS, p
    if under_any(p, MESH_ROOTS):
        return PathClass.MESH, p
    if under_any(p, CLONE_ROOTS):
        return PathClass.CLONE, p
    if under_any(p, BOX_HOMES):
        return PathClass.BOX, p
    if under_any(p, PHONE_ROOTS):
        return PathClass.PHONE, p
    return PathClass.OTHER, p


def resolve_relative(path: str, cwd: str) -> str:
    if path.startswith("/"):
        return norm(path)
    return norm(os.path.join(cwd or ".", path))


# ============= LEGALITY =============

# Who may even SEE which class.
LEGAL_SEE = frozenset({
    (Pane.SSH, PathClass.BOX),
    (Pane.SSH, PathClass.MESH),
    (Pane.SSH, PathClass.BUS),
    (Pane.SSH, PathClass.COLD),
    (Pane.SSH, PathClass.RELATIVE),
    (Pane.A15, PathClass.PHONE),
    (Pane.A15, PathClass.MESH),
    (Pane.A15, PathClass.BUS),
    (Pane.A15, PathClass.CLONE),
    (Pane.A15, PathClass.RELATIVE),
})

# Who may WRITE. COLD never. MESH root itself never (only bus subdirs).
# CLONE is git-only, not a Syncthing share.
LEGAL_WRITE = frozenset({
    (Pane.SSH, PathClass.BUS),
    (Pane.A15, PathClass.BUS),
    (Pane.A15, PathClass.CLONE),  # local git work, not mesh
})


def looks_writeish(command: Optional[str], args: Sequence[str]) -> bool:
    if not command:
        return False
    base = os.path.basename(command)
    if base in WRITEISH:
        return True
    joined = " ".join(args)
    if any(tok in args for tok in ("-i", ">", ">>")):
        return True
    if "serve" in args or "--generate" in args:
        return True
    if joined:
        pass
    return False


def check_cwd_consistency(pane: Pane, cwd: str) -> Optional[str]:
    """Physical mount, not refined class. A phone mesh root is still a phone mount."""
    if pane == Pane.A15 and under_any(cwd, BOX_HOMES):
        return "REFUSE cwd is BOX path on A15"
    if pane == Pane.SSH and under_any(cwd, PHONE_ROOTS):
        return "REFUSE cwd is PHONE path on SSH"
    if pane == Pane.SSH and under_any(cwd, CLONE_ROOTS):
        return "REFUSE cwd is CLONE path on SSH"
    return None


def check_syncthing_identity_mutate(command: Optional[str], args: Sequence[str], folder_state: str) -> Optional[str]:
    if not command:
        return None
    base = os.path.basename(command)
    tokens = [base, *args]
    hit = any(t in SYNCTHING_ID_WIPES for t in tokens)
    if not hit:
        return None
    if folder_state != "UP_TO_DATE":
        return "no unique-ID wipe unless folder_state=UP_TO_DATE"
    return None


def check_fork_serve(pane: Pane, command: Optional[str], args: Sequence[str]) -> Optional[str]:
    """A15 runs Syncthing-Fork UI. CLI `syncthing serve` forks a second identity."""
    if pane != Pane.A15 or not command:
        return None
    base = os.path.basename(command)
    if base == "syncthing" and (not args or args[0] == "serve" or "serve" in args):
        return "syncthing serve forbidden on A15 — Fork app only"
    if command == "syncthing serve":
        return "syncthing serve forbidden on A15 — Fork app only"
    return None


# ============= MAIN GATE =============

def run_classifier(
    prompt: str,
    env: Optional[dict] = None,
    command: Optional[str] = None,
    args: Optional[List[str]] = None,
    folder_state: str = "UNKNOWN",
    quiet: bool = False,
    bus_only: bool = False,
) -> Tuple[str, Optional[str]]:
    if env is None:
        env = dict(os.environ)
    if args is None:
        args = []

    prompt_hostname = None
    if prompt and "@" in prompt:
        try:
            right = prompt.split("@", 1)[1]
            prompt_hostname = right.replace(":", " ").split()[0]
        except IndexError:
            prompt_hostname = None

    pane = classify_pane(env, prompt_hostname)
    if pane == Pane.UNKNOWN:
        return "REFUSE", "Unknown pane — cannot determine execution context"

    cwd = env.get("PWD") or os.getcwd()

    if not quiet:
        print(f"[CLASSIFIER] pane={pane.value}")
        print(f"[CLASSIFIER] user={env.get('USER') or 'unknown'}")
        print(f"[CLASSIFIER] host={env.get('HOSTNAME') or socket.gethostname()}")
        print(f"[CLASSIFIER] HOME={env.get('HOME', 'N/A')}")
        print(f"[CLASSIFIER] CWD={cwd}")
        print(f"[CLASSIFIER] PREFIX={env.get('PREFIX', 'unset')}")
        print(f"[CLASSIFIER] cmd={command or '-'}")

    cwd_error = check_cwd_consistency(pane, cwd)
    if cwd_error:
        return "REFUSE", cwd_error

    fork_err = check_fork_serve(pane, command, args)
    if fork_err:
        return "REFUSE", fork_err

    id_err = check_syncthing_identity_mutate(command, args, folder_state)
    if id_err:
        return "REFUSE", id_err

    writing = looks_writeish(command, args) or bus_only
    paths_to_check = list(args) if args else [cwd]

    notes: List[str] = []
    for raw in paths_to_check:
        # skip flags
        if raw.startswith("-") and raw not in (".", ".."):
            continue
        path_class, _ = classify_path(raw, cwd)
        if path_class == PathClass.RELATIVE:
            resolved = resolve_relative(raw, cwd)
            final_class, resolved = classify_path(resolved, cwd)
        else:
            resolved = norm(raw) if raw.startswith("/") else resolve_relative(raw, cwd)
            final_class, resolved = classify_path(resolved, cwd)

        if not quiet:
            print(f"[CLASSIFIER] path={raw} -> {resolved} class={final_class.value}")

        if (pane, final_class) not in LEGAL_SEE:
            return "REFUSE", f"wrong pane: {pane.value} cannot open {final_class.value} path {raw}"

        if writing and (pane, final_class) not in LEGAL_WRITE:
            if final_class == PathClass.MESH:
                return "REFUSE", f"mesh root is read-mostly; write only inbox/outbox/dump: {resolved}"
            if final_class == PathClass.COLD:
                return "REFUSE", f"cold storage is not the bus: {resolved}"
            if final_class == PathClass.PHONE and pane == Pane.A15:
                return "REFUSE", f"PHONE is the continent, not the bus: {resolved}"
            if final_class == PathClass.BOX and pane == Pane.SSH:
                return "REFUSE", f"BOX home is not the bus: {resolved}"
            return "REFUSE", f"write forbidden: {pane.value} -> {final_class.value} {resolved}"

        if pane == Pane.A15 and final_class == PathClass.CLONE:
            notes.append("TERMUX_CLONE_ONLY — not mesh")
        if final_class == PathClass.MESH:
            notes.append("standing on mesh root")
        if final_class == PathClass.BUS:
            notes.append(f"bus={bus_subdir_of(resolved)}")

    if not quiet:
        for n in notes:
            print(f"[NOTE] {n}")

    return "ADMIT", None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="OpenRoot Security Classifier — Admit or Refuse before bus touch"
    )
    parser.add_argument("-p", "--prompt", default="", help="Prompt string e.g. jesse@optiplex3060")
    parser.add_argument("--command", default=None, help="Command being executed")
    parser.add_argument("paths", nargs="*", help="Paths to classify")
    parser.add_argument(
        "--folder-state",
        default="UNKNOWN",
        choices=["UP_TO_DATE", "OUT_OF_DATE", "UNKNOWN"],
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument(
        "--bus-only",
        action="store_true",
        help="Treat this invocation as a write to the bus (strict)",
    )
    ns = parser.parse_args()

    result, reason = run_classifier(
        prompt=ns.prompt,
        env=dict(os.environ),
        command=ns.command,
        args=ns.paths,
        folder_state=ns.folder_state,
        quiet=ns.quiet,
        bus_only=ns.bus_only,
    )

    if not ns.quiet:
        print("\n=== RESULT ===")

    if result == "ADMIT":
        print("ADMIT")
        sys.exit(0)
    print(f"REFUSE: {reason}")
    sys.exit(2)


if __name__ == "__main__":
    main()
