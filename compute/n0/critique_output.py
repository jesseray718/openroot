#!/usr/bin/env python3
import sys, json
from datetime import datetime
sys.path.insert(0, "$HOME/openroot/compute/n0")
from llm_inference_hook import get_critique

text = sys.stdin.read() if not sys.stdin.isatty() else " ".join(sys.argv[1:])
state = {
    "keywords_matched": any(k in text.lower() for k in ["solar", "thermal", "passive", "capture"]),
    "joules": 0
}
result = get_critique(state)
result["node"] = "N0_critique_output"
print(json.dumps(result, indent=2))
