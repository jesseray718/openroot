#!/usr/bin/env python3
"""Rescue: back up canonical files that exist ONLY on this A15 to the OptiPlex."""
import sys, os, sqlite3, tarfile, subprocess, warnings
from pathlib import Path

warnings.simplefilter("ignore", SyntaxWarning)  # silence legacy-string noise
sys.path.insert(0, os.path.expanduser("~/openroot/bin"))

DB = os.path.expanduser("~/openroot/data/mesh_index.db")
STAGING = Path(os.path.expanduser("~/openroot/data/rescue_staging"))
TARBALL = Path(os.path.expanduser("~/openroot/data/a15_only_canonical.tar.gz"))

conn = sqlite3.connect(DB)
c = conn.cursor()

# canonical a15 files whose hash appears NOWHERE on optiplex
rows = c.execute("""
    SELECT path FROM files
    WHERE is_canonical=1 AND node='a15'
    AND hash NOT IN (SELECT hash FROM files WHERE node='optiplex')
""").fetchall()
paths = [Path(r[0]) for r in rows]
print(f"[rescue] {len(paths)} canonical files exist ONLY on this A15")

if not paths:
    print("[rescue] nothing to rescue — full mesh redundancy achieved")
    sys.exit(0)

# stage copies (flat manifest in case of name collisions)
manifest = []
STAGING.mkdir(parents=True, exist_ok=True)
for i, p in enumerate(paths):
    if not p.exists():
        continue
    dest = STAGING / f"{i:04d}_{p.name}"
    dest.write_bytes(p.read_bytes())
    manifest.append({"orig": str(p), "staged": str(dest)})
print(f"[rescue] staged {len(manifest)} files in {STAGING}")

# tarball from staging + write manifest alongside
with tarfile.open(TARBALL, "w:gz") as tar:
    for m in manifest:
        tar.add(m["staged"], arcname=os.path.basename(m["staged"]))
    man_path = STAGING / "MANIFEST.json"
    import json
    man_path.write_text(json.dumps(manifest, indent=2))
    tar.add(man_path, arcname="MANIFEST.json")
size_mb = TARBALL.stat().st_size / 1e6
print(f"[rescue] tarball: {TARBALL} ({size_mb:.1f} MB)")

# push to OptiPlex (phone->optiplex SSH is your reliable direction)
r = subprocess.run(["scp", str(TARBALL), "optiplex:/home/jesse/openroot/data/"],
                   capture_output=True, text=True, timeout=300)
if r.returncode == 0:
    print("[rescue] pushed to optiplex:/home/jesse/openroot/data/ — "
          "at-risk corpus now has 2-node redundancy")
else:
    print(f"[warn] scp failed: {r.stderr.strip()[:200]}")
    print(f"[gate] tarball is safe at {TARBALL} — push manually when SSH cooperates")
