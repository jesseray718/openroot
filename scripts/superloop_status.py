#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "context_bridge" / "superloop_DASHBOARD.md"

def run(*args):
    try:
        return subprocess.check_output(
            args,
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except Exception as exc:
        return f"unavailable: {exc}"

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def status_summary():
    raw = run("git", "status", "--porcelain")
    if not raw:
        return "clean"
    changed = len(raw.splitlines())
    return f"{changed} changed/untracked path(s); details intentionally omitted"

registry_candidates = [
    ROOT / "data" / "model_registry.json",
    ROOT / "model_registry.json",
    ROOT / "config" / "model_registry.json",
    ROOT / "context_bridge" / "model_registry.json",
]
registry = next((candidate for candidate in registry_candidates if candidate.is_file()), None)

lines = [
    "<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->",
    "# OpenRoot Superloop Dashboard",
    "",
    f"- Generated UTC: `{datetime.now(timezone.utc).isoformat()}`",
    f"- Branch: `{run('git', 'branch', '--show-current')}`",
    f"- HEAD: `{run('git', 'rev-parse', '--short=12', 'HEAD')}`",
    f"- Working tree: `{status_summary()}`",
    f"- Last commit: `{run('git', 'log', '-1', '--pretty=%h %ad %s', '--date=iso-strict')}`",
    "",
    "## Command Flow Health",
    "",
    "- Source: sanitized local superloop state; no raw command history is emitted here.",
    "- Drift review compares categorized activity with `MASTER_TODO` and accepted work.",
    "",
    "## Routing Evidence",
]

if registry:
    try:
        payload = json.loads(registry.read_text(encoding="utf-8"))
        models = payload.get("models", payload) if isinstance(payload, dict) else None
        count = len(models) if isinstance(models, (dict, list)) else 0
        lines.extend([
            f"- Registry: `{registry.relative_to(ROOT)}`",
            f"- Registry SHA-256: `{sha256(registry)}`",
            f"- Registry entries: `{count}`",
        ])
    except Exception as exc:
        lines.append(f"- Registry parse status: `error: {exc}`")
else:
    lines.append("- Registry: `not found`")

lines.extend([
    "",
    "## Local AI Boundary",
    "",
    "- FTS5/Git retrieval provides bounded evidence.",
    "- A local small model may classify or summarize evidence.",
    "- A local coder may propose a minimal patch and tests.",
    "- No model output is applied, committed, pushed, tagged, released, or deployed without human review.",
    "",
    "## Publication Boundary",
    "",
    "- Never publish tokens, secrets, raw prompts, raw command history, private paths, private IPs, databases, or telemetry.",
    "- The public status pulse is a redacted summary, not a source of authority.",
    "",
])

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUT)
