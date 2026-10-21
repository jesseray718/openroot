#!/usr/bin/env python3
"""Write RMH comparison next to this repo. Works on OptiPlex and A15 mesh."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.openroot_optimizer.rmh_labyrinth_model import compare_current_vs_rmh_lab

OUT = ROOT / "reports" / "RMH_LABYRINTH_COMPARISON.md"
BOX = ROOT / "reports" / "RMH_LABYRINTH_COMPARISON_BOX.md"
JSON_OUT = ROOT / "reports" / "rmh_compare.json"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = compare_current_vs_rmh_lab()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = [
        "# RMH + labyrinth comparison",
        "generated: " + now,
        "root: " + str(ROOT),
        "N14: model output, not pad measurement.",
        "CSV trial.A1.sample is a 3-row fixture. Do not publish as a hang.",
        "",
        "```json",
        json.dumps(data, indent=2, default=str),
        "```",
        "",
    ]
    text = "\n".join(body)
    OUT.write_text(text, encoding="utf-8")
    BOX.write_text(text, encoding="utf-8")
    JSON_OUT.write_text(json.dumps({"generated": now, "root": str(ROOT), "n14": "model", "data": data}, indent=2, default=str) + "\n", encoding="utf-8")
    print("wrote", OUT)
    print("wrote", BOX)
    print("wrote", JSON_OUT)


if __name__ == "__main__":
    main()
