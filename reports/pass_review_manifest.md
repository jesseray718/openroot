# OpenRoot Automation Pass Manifest
**Execution Mode:** ACTIVE EXECUTION
**Host:** OptiPlex 3060 (`jesse@optiplex3060`)
**LLM Endpoint:** `http://127.0.0.1:8080/v1`

## System Topology & State
- **OptiPlex:** Workspace host, local 7B inference engine, git orchestrator.
- **A15 Phone:** Mobile operator terminal via SSH.
- **GitHub:** Remote repository mirror (`jesseray718`).

## Output Deliverables
1. Audit JSON: `/home/jesse/openroot/reports/audit_summary.json`
2. Generated Fix Scripts: `/home/jesse/openroot/reports/pr_fixes/`

To execute active modifications: `python3 /home/jesse/openroot/kit/bin/openroot_loop.py --execute`
