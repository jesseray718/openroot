#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / "data" / "model_registry.json",
    ROOT / "model_registry.json",
    ROOT / "config" / "model_registry.json",
    ROOT / "context_bridge" / "model_registry.json",
]

path = next((candidate for candidate in CANDIDATES if candidate.is_file()), None)

if path is None:
    raise SystemExit("Registry missing: expected data/model_registry.json or a documented alternate path.")

try:
    data = json.loads(path.read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    raise SystemExit(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc

if not isinstance(data, dict):
    raise SystemExit(f"{path.relative_to(ROOT)} must contain a JSON object.")

models = data.get("models", data)

if not isinstance(models, (dict, list)):
    raise SystemExit(f"{path.relative_to(ROOT)}: 'models' must be an object or list.")

if isinstance(models, list):
    for index, item in enumerate(models):
        if not isinstance(item, dict):
            raise SystemExit(f"{path.relative_to(ROOT)}: models[{index}] must be an object.")

print(f"Registry valid: {path.relative_to(ROOT)}")
