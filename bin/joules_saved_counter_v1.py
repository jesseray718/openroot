# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
"""Rolling joules-saved counter — computes energy saved by cache-hit skips."""
import json, hashlib, datetime
from pathlib import Path
from collections import defaultdict

REPO = "/home/jesse/openroot"
RECEIPTS = Path(REPO + "/ledger/unified/run_receipts.jsonl")
OUT = Path(REPO + "/data/joules_saved.json")

def main():
    if not RECEIPTS.exists():
        print("[held] no receipts yet — run agape_thermo_merge_v2.py first")
        return
    by_fp = defaultdict(list)
    for line in RECEIPTS.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            by_fp[r["input_fingerprint"]].append(r)
    saved = 0.0
    runs_fresh = runs_cached = 0
    for fp, runs in by_fp.items():
        fresh = [r["joules"] for r in runs if not r["cache_hit"]]
        if not fresh:
            continue
        baseline = sum(fresh) / len(fresh)
        for r in runs:
            if r["cache_hit"]:
                saved += max(0.0, baseline - r["joules"])
                runs_cached += 1
            else:
                runs_fresh += 1
    rec = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "saved_joules": round(saved, 6),
        "runs_fresh": runs_fresh,
        "runs_cached": runs_cached,
        "receipts_source": "ledger/unified/run_receipts.jsonl",
        "method": "baseline=mean fresh joules per fingerprint; saved=max(0,baseline-cached)",
    }
    rec["sha256"] = hashlib.sha256(
        json.dumps(rec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(f"[accounting] saved_joules={saved:.3f}J (fresh={runs_fresh} cached={runs_cached})")
    print(f"[banked] sealed {OUT} sha256={rec['sha256'][:16]}")

if __name__ == "__main__":
    main()
    print("[exit=0]")
