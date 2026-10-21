#!/usr/bin/env python3
"""GH Copilot context bridge — one writer, small payload.

Reads compost outputs + PATH_INVENTORY.
Writes:
  /sdcard/openroot/context_bridge/LIVE.md          phone hot
  /sdcard/openroot/context_bridge/context.json     machine
  <repo>/context_bridge/LIVE.md                    if --repo given (Copilot @-include)

Copilot CLI will NOT load absolute or ~ paths in @-includes.
LIVE.md must live inside the repo Copilot has open.
Keep LIVE.md under ~4KB. Law stays in OPENROOT_COPILOT_OS.md.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

OPENROOT = Path(os.environ.get("OPENROOT_HOME", "/sdcard/openroot"))
SEED = OPENROOT / "session_seeds" / "current_seed.json"
REPORT = OPENROOT / "compost" / "report.json"
DOSSIER = OPENROOT / "compost" / "dossier.md"
INVENTORY = OPENROOT / "PATH_INVENTORY.yaml"
BRIDGE_DIR = OPENROOT / "context_bridge"
LIVE = BRIDGE_DIR / "LIVE.md"
CTX = BRIDGE_DIR / "context.json"
MAX_LIVE = 4000


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(p: Path) -> dict:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"_error": f"unreadable:{p}"}


def clip(text: str, n: int) -> str:
    text = text.strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def build() -> tuple[str, dict]:
    seed = load_json(SEED)
    report = load_json(REPORT)
    dossier_head = ""
    if DOSSIER.exists():
        dossier_head = "\n".join(DOSSIER.read_text(encoding="utf-8", errors="replace").splitlines()[:18])

    open_dot = seed.get("open_dot") or "none — run compost"
    wave = seed.get("wave_state") or report.get("wave_state") or "unknown"
    coh = seed.get("coherence") if seed.get("coherence") is not None else report.get("standing_wave_coherence")
    eta3 = seed.get("eta3")
    top = seed.get("top_gamma") or []
    latest = seed.get("latest_seeds") or []

    gamma_lines = []
    for g in top[:5]:
        key = str(g.get("key", ""))[:90]
        gamma_lines.append(f"- Γ={g.get('gamma')} n={g.get('n_sessions')} `{key}`")
    seed_lines = []
    for s in latest[:5]:
        seed_lines.append(f"- `{s.get('id', '')}` {clip(str(s.get('text', '')), 140)}")

    md = "\n".join([
        "# LIVE — Copilot context (generated, do not edit)",
        f"ts: {utcnow()}",
        f"writer: context_bridge/bridge.py",
        f"wave: {wave}  coherence: {coh}  eta3: {eta3}",
        f"open_dot: `{open_dot}`",
        "",
        "## Kernel (do not re-derive)",
        "η = useful_joules / human_joules. R=1.0 ⇒ C=0. Absolute paths. One atomic act.",
        "Serve lowest node first. Load OPENROOT_COPILOT_OS.md. No questions that Jesse must answer first.",
        "",
        "## Hardware",
        "Governor: Samsung A15 + Termux + Shizuku. Heavy: OptiPlex. Sync: Syncthing. Cold: SD /OpenRoot/cold.",
        "Hot tree: /sdcard/openroot   Termux: /data/data/com.termux/files/home",
        "",
        "## Cross-window Γ (the stitch)",
        *(gamma_lines or ["- none — compost has not seen two sessions yet"]),
        "",
        "## Latest seeds",
        *(seed_lines or ["- none"]),
        "",
        "## Dossier head",
        "```",
        clip(dossier_head, 900),
        "```",
        "",
        "## Next joule",
        "1. If open_dot is a path or CID, continue that thread. Do not start a parallel tree.",
        "2. Do not invent a fifth yield name. Seeds / Γ / η / cashpath / ash only.",
        "3. Do not dump logs into context. Read LIVE.md and current_seed.json only.",
        "",
    ])
    if len(md) > MAX_LIVE:
        md = md[: MAX_LIVE - 20] + "\n<!-- truncated -->\n"

    ctx = {
        "ts": utcnow(),
        "wave": wave,
        "coherence": coh,
        "eta3": eta3,
        "open_dot": open_dot,
        "seed_path": str(SEED),
        "live_path": str(LIVE),
        "inventory_path": str(INVENTORY),
        "bytes_live": len(md.encode("utf-8")),
    }
    return md, ctx


def write_pair(md: str, ctx: dict, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    live = dest_dir / "LIVE.md"
    live.write_text(md, encoding="utf-8")
    (dest_dir / "context.json").write_text(json.dumps(ctx, indent=2), encoding="utf-8")
    return live


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="", help="repo root that Copilot has open (relative LIVE lands here)")
    args = ap.parse_args()
    md, ctx = build()
    write_pair(md, ctx, BRIDGE_DIR)
    copied = []
    if args.repo:
        repo = Path(args.repo)
        copied.append(str(write_pair(md, ctx, repo / "context_bridge")))
    print(json.dumps({"wrote": str(LIVE), "bytes": ctx["bytes_live"], "open_dot": ctx["open_dot"], "repo_copies": copied}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
