# Ghost Script Audit — 20261014T151519Z

## Referenced bin/ scripts that DO NOT exist on disk:
- `/home/jesse/openroot/bin/export_tasks_ics_v1.py`
- `/home/jesse/openroot/bin/local_task_queue_v1.py`
- `/home/jesse/openroot/bin/local_task_status_v1.py`
- `/home/jesse/openroot/bin/measure_thermal_v1.py`
- `/home/jesse/openroot/bin/superloop_composite_v3.py`

## Cron entries (crontab -l):
0 3 * * * /usr/bin/python3 /home/jesse/src/openroot-thesis/scripts/mesh_governor.py >> /home/jesse/src/openroot-thesis/audit_reports/mesh_governor.log 2>&1
15 3 * * * /usr/bin/python3 /home/jesse/github-audit/repo_loop.py >> /home/jesse/github-audit/repo-loop.log 2>&1
*/15 * * * * cd /home/jesse/openroot && python3 bin/superloop_composite_v3.py >> logs/superloop.log 2>&1
# OPENROOT BOTS [CRONBRIDGEV1]
0 * * * * cd /home/jesse/openroot && python3 bin/measure_thermal_v1.py --digest >> logs/cron_thermal.log 2>&1
0 6 * * * cd /home/jesse/openroot && bin/task_dispatch_v1.sh >> logs/cron_dispatch.log 2>&1
0 3 * * * cd /home/jesse/openroot && python3 bin/file_ledger_v2.py index && python3 bin/file_ledger_parallel_v1.py 2 && python3 bin/ecosystem_v2.py >> logs/nightly_ecosystem_$(date +\%Y\%m\%d).log 2>&1
*/10 * * * * /usr/bin/python3 /home/jesse/openroot/bin/lumo_ingest.py >> /home/jesse/openroot/logs/lumo_ingest.log 2>&1

## lumo_ingest schema check:
- /home/jesse/openroot/data/lumo_ingest.db: ingested columns = ['sha256', 'path', 'ts_utc', 'origin', 'size_bytes']
