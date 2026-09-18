#!/usr/bin/env python3
# universal_unpack.py — consume unpack_list manifest: extract unique archives,
# hash every file, merge into the newest universal_index DB. Idempotent per archive.
# Jesse Ray / OpenRoot | v1.0 | pairs with universal_index_pipeline.py
import os, json, glob, sqlite3, hashlib, tarfile, zipfile, time, sys

OUT   = "/home/jesse/openroot/data/universal_index"
STAGE = os.path.join(OUT, "unpacked")

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# newest manifest + newest DB
manifests = sorted(glob.glob(os.path.join(OUT, "unpack_list_*.json")))
dbs       = sorted(glob.glob(os.path.join(OUT, "universal_index_*.db")))
if not manifests or not dbs:
    print("[held] no manifest or db yet — run universal_index_pipeline.py first")
    sys.exit(1)
manifest, db_path = manifests[-1], dbs[-1]

with open(manifest) as f:
    archives = json.load(f)

con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("SELECT detail FROM audit_log WHERE action='unpack'")
done = {r[0] for r in cur.fetchall()}
print(f"[canary] paste intact | mode: EXECUTE | manifest={os.path.basename(manifest)}")
print(f"[observe] archives in manifest: {len(archives)} | already unpacked: {len(done)}")
os.makedirs(STAGE, exist_ok=True)

n_new, n_files, n_dupe = 0, 0, 0
for arc in archives:
    ash, apath = arc["sha256"], arc["path"]
    if ash in done:
        continue
    dest = os.path.join(STAGE, ash[:16])
    try:
        if apath.endswith(".zip"):
            with zipfile.ZipFile(apath) as z:
                z.extractall(dest)
        else:
            with tarfile.open(apath, "r:*") as t:
                t.extractall(dest)
        n_new += 1
    except Exception as e:
        print(f"[hold] unpack failed {apath}: {e}")
        continue

    for root, _, files in os.walk(dest):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                fh = sha256_file(fp)
            except Exception:
                continue
            rel = os.path.relpath(fp, dest)
            row = cur.execute("SELECT original_paths FROM files WHERE sha256=?", (fh,)).fetchone()
            if row:
                paths = json.loads(row[0] or "[]")
                if rel not in paths:
                    paths.append(rel)
                cur.execute("UPDATE files SET original_paths=? WHERE sha256=?",
                            (json.dumps(paths), fh))
                n_dupe += 1
            else:
                cur.execute("INSERT INTO files VALUES (?,?,?,?,?,?,?,?)",
                            (fh, json.dumps([rel]), fn, os.path.getsize(fp),
                             None, None, fp, int(time.time())))
                n_files += 1
    cur.execute("INSERT OR REPLACE INTO audit_log VALUES (?,?,?,?)",
                (int(time.time()*1000), "unpack", ash, "ok"))
    con.commit()
    print(f"[banked] {os.path.basename(apath)} -> files={n_files} dupes={n_dupe}")

con.commit()
total = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
con.close()
print(f"\n[summary] archives newly unpacked: {n_new} | unique files indexed: {n_files} | dupe hits: {n_dupe}")
print(f"[summary] TOTAL rows in universal index: {total}")
print(f"[gate] next: query it — sqlite3 {db_path} 'SELECT COUNT(*) FROM files'")
