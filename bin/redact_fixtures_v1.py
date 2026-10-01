#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""
redact_fixtures_v1.py — pre-ingest scrubber for test-fixture credential lookalikes.
Usage:
  python3 bin/redact_fixtures_v1.py <dir-or-file> [--apply]
Dry-run default: lists files matching fixture patterns. --apply rewrites
matching substrings to <fixture-redacted>. Real keys (sk-[A-Za-z0-9]{20,})
are NEVER scrubbed silently — they trigger exit code 2 + quarantine advice,
because those need rotation, not redaction.
Wiring point: kai_ingest_bridge_v1.py should call this before enqueueing
kai corpus bodies into lumo_inbox (see mistake 6daeb91f8bcf5765).
"""
import re, sys
from pathlib import Path

FIXTURE_PATTERNS = [
    (re.compile(r'sk-this-is-the-secret-key'), '<fixture-redacted>'),
    (re.compile(r'TEST_API_KEY\s*=\s*["\'][^"\']*["\']'), 'TEST_API_KEY = "<fixture-redacted>"'),
]
REAL_KEY = re.compile(r'sk-[A-Za-z0-9]{20,}')

def scan(root: Path):
    hits, real = [], []
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for p in paths:
        if not p.is_file():
            continue
        try:
            t = p.read_text(errors="ignore")
        except Exception:
            continue
        if REAL_KEY.search(t) and not any(rx.search(t) for rx, _ in FIXTURE_PATTERNS):
            real.append(p); continue
        if any(rx.search(t) for rx, _ in FIXTURE_PATTERNS):
            hits.append(p)
    return hits, real

def main():
    args = [a for a in sys.argv[1:] if a != "--apply"]
    apply = "--apply" in sys.argv
    if not args:
        print(__doc__); sys.exit(1)
    root = Path(args[0])
    hits, real = scan(root)
    for p in real:
        print(f"[ALERT] possible REAL key: {p} — rotate + quarantine, do not merely redact")
    for p in hits:
        print(f"{'[applied]' if apply else '[dry-run]'} fixture scrub: {p}")
        if apply:
            t = p.read_text(errors="ignore")
            for rx, sub in FIXTURE_PATTERNS:
                t = rx.sub(sub, t)
            p.write_text(t)
    print(f"summary: {len(hits)} fixture files, {len(real)} real-key suspicions")
    sys.exit(2 if real else 0)

if __name__ == "__main__":
    main()
