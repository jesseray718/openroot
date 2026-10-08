# OpenRoot hash inspection

- Generated: `2026-09-28T14:33:45-05:00`
- Host: `optiplex3060`
- User: `jesse`
- Repo: `/home/jesse/openroot`
- Mode: read-only inspection; no hashing run, no manifest writes, no Git mutation, no process mutation.

## Existing hash scripts and operational files

```text
2026-09-13 12:34:09.0462029730 801 /home/jesse/openroot/attic/rescue_staging_vendor/0654_generate_manifest.py
2026-09-13 12:34:09.3022029730 4777 /home/jesse/openroot/attic/rescue_staging_vendor/0839_SHA256.py
2026-09-13 12:34:09.8982029730 884 /home/jesse/openroot/attic/rescue_staging_vendor/1320_generate_manifest.py
2026-09-13 12:34:13.3502029730 289163 /home/jesse/openroot/data/rescue_staging/MANIFEST.json
2026-09-14 03:28:00.2047906570 289163 /home/jesse/openroot/attic/rescue_staging_vendor/MANIFEST.json
2026-09-19 22:04:25.9699824690 12577 /home/jesse/openroot/outbox/agape_master_manifest.json
2026-09-20 00:21:13.9089341790 2210 /home/jesse/openroot/analysis/frp7_20260920_002113/bin_manifest.txt
2026-09-21 19:29:02.3988810200 7752 /home/jesse/openroot/data/manifest.txt
2026-09-23 19:42:44.9403486140 801 /home/jesse/openroot/bin/0654_generate_manifest.py
2026-09-23 19:42:45.0792393060 4777 /home/jesse/openroot/bin/0839_SHA256.py
2026-09-23 19:42:45.5887497650 884 /home/jesse/openroot/bin/1320_generate_manifest.py
2026-09-24 06:30:32.2114961390 34131 /home/jesse/openroot/data/mobile_sync_manifest.json
2026-09-26 22:25:27.1623829740 550 /home/jesse/openroot/designs/thermal-cascade/release-manifest.json
2026-09-27 22:43:06.9078274340 1247 /home/jesse/openroot/bin/__pycache__/0654_generate_manifest.cpython-312.pyc
2026-09-27 22:43:12.5740773960 5875 /home/jesse/openroot/bin/__pycache__/0839_SHA256.cpython-312.pyc
2026-09-27 22:43:28.0383319270 1441 /home/jesse/openroot/bin/__pycache__/1320_generate_manifest.cpython-312.pyc
2026-09-28 06:12:15.3938602250 6812 /home/jesse/openroot/hash_assign_v1.sh
2026-09-28 06:13:58.2535696780 20480 /home/jesse/openroot/data/hash_manifest_optiplex_smoke.db
2026-09-28 06:13:58.4375691000 2842 /home/jesse/openroot/logs/hash_assign_optiplex_smoke.log
2026-09-28 06:15:26.2852721040 7 /home/jesse/openroot/run/hash_assign_optiplex.launcher.pid
2026-09-28 06:15:26.2912720820 7 /home/jesse/openroot/run/hash_assign_optiplex.pid
2026-09-28 07:59:05.0978096870 403 /home/jesse/openroot/reports/local_loop_20260928T125901Z_678132_24052/hash_manifests.txt
2026-09-28 08:06:13.6614528810 403 /home/jesse/openroot/reports/local_loop_20260928T130610Z_698386_28407/hash_manifests.txt
2026-09-28 14:06:35.1908238660 1723 /home/jesse/openroot/reports/oshw_root_audit_20260928T190634Z/oshw_manifest.tsv
2026-09-28 14:08:19.6367170980 1723 /home/jesse/openroot/reports/oshw_root_audit_20260928T190819Z/oshw_manifest.tsv
2026-09-28 14:33:27.2821252410 109562 /home/jesse/openroot/logs/hash_assign_optiplex.log
2026-09-28 14:33:45.2800773150 616272 /home/jesse/openroot/logs/hash_assign_optiplex.nohup.log
2026-09-28 14:33:45.6000764480 57298944 /home/jesse/openroot/data/hash_manifest_optiplex.db
```

## Hash-related active processes

```text
 371069       1    08:18:19  2.5  0.0 S    bash /home/jesse/openroot/hash_assign_v1.sh
1840213  371069       00:00  0.0  0.0 D    sqlite3 -batch /home/jesse/openroot/data/hash_manifest_optiplex.db
```

## Hash manifest databases: integrity and schema

```text
--- db=/home/jesse/openroot/data/hash_manifest_a15.db ---
absent

--- db=/home/jesse/openroot/data/hash_manifest_optiplex.db ---
size=57298944 bytes
mtime=2026-09-28 14:33:45.924075570 -0500
mode=-rw-r--r--
integrity_check:
Error: in prepare, database is locked (5)
journal_mode:
Error: in prepare, database is locked (5)
tables:
Error: database is locked
manifest_schema:
Error: database is locked

--- db=/home/jesse/openroot/data/hash_manifest_a15_smoke.db ---
absent

--- db=/home/jesse/openroot/data/hash_manifest_optiplex_smoke.db ---
size=20480 bytes
mtime=2026-09-28 06:13:58.253569678 -0500
mode=-rw-r--r--
integrity_check:
ok
journal_mode:
wal
tables:
manifest
manifest_schema:
CREATE TABLE manifest (
  path        TEXT PRIMARY KEY,
  sha256      TEXT NOT NULL,
  size_bytes  INTEGER NOT NULL,
  mtime_ns    INTEGER NOT NULL,
  hashed_at   TEXT NOT NULL,
  host        TEXT NOT NULL,
  status      TEXT NOT NULL DEFAULT 'ok',
  error_text  TEXT
);
CREATE INDEX manifest_sha256_idx
ON manifest(sha256);
CREATE INDEX manifest_status_idx
ON manifest(status);

```
