#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
BRIDGE = Path("/sdcard/openroot/context_bridge")
SEED   = Path("/sdcard/openroot/session_seeds")
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["seed", "show", "status"])
    ap.add_argument("--input", default=str(SEED / "current_seed.json"))
    args = ap.parse_args()
    if args.cmd == "seed":
        src = Path(args.input)
        if not src.exists():
            print(f"missing {src}"); sys.exit(1)
        data = json.loads(src.read_text())
        (BRIDGE / "context.json").write_text(json.dumps(data, indent=2))
        print(f"bridged {src} → context.json")
    elif args.cmd == "show":
        p = BRIDGE / "context.json"
        print(p.read_text() if p.exists() else "no context yet")
    elif args.cmd == "status":
        for f in ["context.json", "agape_context_bridge.json"]:
            p = BRIDGE / f
            print(f"{f}: {'present' if p.exists() else 'missing'}")
if __name__ == "__main__":
    main()
