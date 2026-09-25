#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""lesson_ingest.py — idempotent lesson chain ingest. Usage:
lesson_ingest.py "<mistake>" "<root_cause>" "<correction>" [domain]
Removes the ssh-heredoc quoting fragility that ate two ingest attempts."""
import sqlite3, hashlib, sys, os
from datetime import datetime, timezone
if len(sys.argv) < 4:
    sys.exit(__doc__)
mistake, root_cause, correction = sys.argv[1:4]
domain = sys.argv[4] if len(sys.argv) > 4 else "infra"
DB = os.path.expanduser("~/openroot/data/lessons.db")
c = sqlite3.connect(DB)
msha = hashlib.sha256(mistake.encode()).hexdigest()[:16]
ssha = hashlib.sha256(correction.encode()).hexdigest()[:16]
lsha = hashlib.sha256((msha + ssha).encode()).hexdigest()[:16]
if c.execute("SELECT 1 FROM lessons WHERE link_sha=?", (lsha,)).fetchone():
    print("[IDEMPOTENT-HIT]", lsha); sys.exit(0)
c.execute("""INSERT INTO lessons
    (ts, domain, mistake, root_cause, correction, verified,
     mistake_sha, solution_sha, link_sha) VALUES (?,?,?,?,?,?,?,?,?)""",
    (datetime.now(timezone.utc).isoformat(), domain, mistake,
     root_cause, correction, "verified", msha, ssha, lsha))
c.commit()
print("[INGESTED]", lsha, "| chain length:",
      c.execute("SELECT COUNT(*) FROM lessons").fetchone()[0])
