#!/usr/bin/env python3
import os, sys, json, datetime

PATH = sys.argv[sys.argv.index("--path") + 1] if "--path" in sys.argv else "/sdcard/openroot"
VIOLATIONS = []
WARNINGS = []

ALLOWED = {"cycle.sh", "relay_exec.sh", "sys_snapshot.sh", "wealth_log.sh",
           "run_hourly.sh", "agape_autostart.sh", "immortal_context.py"}

for root, dirs, files in os.walk(PATH):
    if "/.git" in root or "/relay/out_" in root:
        continue
    for fname in files:
        fpath = os.path.join(root, fname)
        if not fname.endswith((".py", ".sh")):
            continue
        try:
            with open(fpath, "r") as f:
                content = f.read()
            if "/sdcard/openroot" in content and fname not in ALLOWED and fname != "structure_enforcer.py":
                WARNINGS.append(f"hardcoded_path:{fpath}")
            if len(content.strip()) == 0:
                VIOLATIONS.append(f"empty_file:{fpath}")
        except Exception as e:
            WARNINGS.append(f"read_error:{fpath}:{e}")

report = {
    "stamp": datetime.datetime.now().isoformat(),
    "violations": VIOLATIONS,
    "warnings": WARNINGS,
    "checked_path": PATH,
}
rp = os.path.join(PATH, "logs", "enforcer_report.json")
os.makedirs(os.path.dirname(rp), exist_ok=True)
with open(rp, "w") as f:
    json.dump(report, f, indent=2)

if VIOLATIONS:
    print(f"ENFORCER: {len(VIOLATIONS)} violations, {len(WARNINGS)} warnings")
    sys.exit(1)
print(f"ENFORCER: clean ({len(WARNINGS)} warnings)")
