import os, time, sqlite3, hashlib, sys

DB = sys.argv[1]
SKIP = {'/proc', '/sys', '/dev', '/run', '/snap', os.path.dirname(DB)}
db = sqlite3.connect(DB)
db.executescript('''
CREATE TABLE IF NOT EXISTS files(
  path TEXT PRIMARY KEY, sha256 TEXT, size INTEGER, mtime REAL, scanned_at TEXT);
CREATE INDEX IF NOT EXISTS idx_sha ON files(sha256);
''')
done = {p: (s, m) for p, s, m in db.execute(
    'SELECT path, size, mtime FROM files WHERE sha256 IS NOT NULL')}
print(f'[banked] resume state: {len(done)} files', flush=True)

hashed = skipped = errors = 0
t0 = time.time()
for dirpath, dirnames, filenames in os.walk('/', followlinks=False, topdown=True):
    if dirpath in SKIP:
        dirnames[:] = []
        continue
    dirnames[:] = [d for d in dirnames if os.path.join(dirpath, d) not in SKIP]
    for fn in filenames:
        fp = os.path.join(dirpath, fn)
        try:
            st = os.stat(fp)
            if not os.path.isfile(fp):
                continue
            if fp in done and done[fp] == (st.st_size, int(st.st_mtime)):
                skipped += 1
                continue
            h = hashlib.sha256()
            with open(fp, 'rb') as fh:
                for chunk in iter(lambda: fh.read(1024*1024), b''):
                    h.update(chunk)
            db.execute('INSERT OR REPLACE INTO files VALUES (?,?,?,?,?)',
                       (fp, h.hexdigest(), st.st_size, int(st.st_mtime),
                        time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
            hashed += 1
        except OSError:
            errors += 1
            continue
        if hashed % 5000 == 0:
            db.commit()
            print(f'[gate] progress: hashed={hashed} skipped={skipped} errors={errors} '
                  f'rate={hashed/max(time.time()-t0,1):.0f} files/s', flush=True)
db.commit()
rows, distinct = db.execute('SELECT COUNT(*), COUNT(DISTINCT sha256) FROM files').fetchone()
print(f'[banked] OPTIPLEX SCAN COMPLETE: rows={rows} distinct={distinct} '
      f'errors={errors} elapsed={(time.time()-t0)/60:.0f}min', flush=True)
