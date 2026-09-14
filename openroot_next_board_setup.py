#!/usr/bin/env python3
"""
OpenRoot Unified Setup Script
Addresses NEXT BOARD priorities 1-5 in resistance order
Works across Box (OptiPlex) and Phone (A15/Termux) via PATH_GATE detection
Author: Jesse Ray (OpenRoot)
Date: 2026-09-14
"""
import os
import sys
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# ========== PATH GATE (detect environment) ==========
def detect_env():
    """Return 'box' or 'phone' based on filesystem topology."""
    if Path('/home/jesse').exists():
        return 'box'
    elif Path('/data/data/com.termux').exists() or Path('/sdcard').exists():
        return 'phone'
    else:
        return 'unknown'

ENV = detect_env()
BASE = '/home/jesse/openroot' if ENV == 'box' else str(Path.home())
BIN_DIR = f'{BASE}/bin'
DATA_DIR = f'{BASE}/data'
SCRIPTS_DIR = f'{BASE}/scripts'

print(f"[PATH-GATE] Environment: {ENV}")
print(f"[PATH-GATE] Base: {BASE}")

# Ensure directories exist
for d in [BIN_DIR, DATA_DIR, SCRIPTS_DIR]:
    Path(d).mkdir(parents=True, exist_ok=True)

# ========== PRIORITY 1: TOTP + Prepaid Number Workflow ==========
def setup_totp_workflow():
    """GitHub Sponsors 2FA gate scaffolding."""
    if ENV != 'box':
        print("[TOTP] Skipped on phone — Box only")
        return
    
    totp_dir = f'{DATA_DIR}/totp_sponsors'
    Path(totp_dir).mkdir(parents=True, exist_ok=True)
    
    # SQLite schema for TOTP secrets + verification
    conn = sqlite3.connect(f'{totp_dir}/totp_state.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS totp_secrets (
        id INTEGER PRIMARY KEY,
        service TEXT UNIQUE,
        secret_key TEXT,
        verified INTEGER DEFAULT 0,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS totp_attempts (
        id INTEGER PRIMARY KEY,
        service TEXT,
        code TEXT,
        result TEXT,
        attempted_at TEXT
    )''')
    
    # Insert GitHub Sponsors placeholder
    c.execute('''INSERT OR IGNORE INTO totp_secrets 
                 (service, secret_key, created_at) 
                 VALUES (?, ?, ?)''',
              ('github_sponsors', '', datetime.now(timezone.utc).isoformat()))
    
    conn.commit()
    conn.close()
    
    # Create config template
    config = {
        'service': 'github_sponsors',
        'phone_number_status': 'pending',  # 'none', 'family', 'virtual'
        'verification_state': 'awaiting_phone',
        'target': 'https://github.com/sponsors'
    }
    with open(f'{totp_dir}/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[TOTP] Created {totp_dir}/config.json")
    return True

# ========== PRIORITY 2: Measured Joule Row ==========
def setup_joule_measurement():
    """dumpsys battery charge-counter integration for A15."""
    # Box creates analyzer, Phone runs collector
    collector_script = f'''#!/usr/bin/env python3
"""Joule Measurement Collector — Run on A15"""
import subprocess
import json
from datetime import datetime, timezone

def get_battery_joules():
    """Extract charge counter from dumpsys battery."""
    try:
        result = subprocess.run(
            ['dumpsys', 'battery'],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.split('\\n'):
            if 'charge-counter' in line.lower():
                # Parse: "charge counter: 4500" or similar
                parts = line.replace(':', ' ').replace(',', ' ').split()
                for i, p in enumerate(parts):
                    if p.isdigit() and int(p) > 1000 and int(p) < 50000:
                        return int(p)  # mAh
        return None
    except Exception as e:
        return f"ERROR: {{e}}"

def main():
    mah = get_battery_joules()
    joules = None
    if isinstance(mah, int):
        # Approximate: 1 mAh ≈ 3.7V × 3.6C = 13.32 J per full cycle
        # This is raw capacity, not instantaneous power
        joules = round(mah * 3.7 / 1000 * 3600, 2)  # Convert to Joules
    
    record = {{
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'device': 'Samsung_A15',
        'raw_charge_counter_mah': mah,
        'joules_estimated': joules,
        'source': 'dumpsys_battery'
    }}
    
    # Append to JSONL log
    log_path = '{DATA_DIR}/joule_measurements.jsonl'
    with open(log_path, 'a') as f:
        f.write(json.dumps(record) + '\\n')
    
    print(f"[JOULE] {{record}}")

if __name__ == '__main__':
    main()
'''
    
    with open(f'{SCRIPTS_DIR}/collect_joules.py', 'w') as f:
        f.write(collector_script)
    
    # Box-side analyzer
    analyzer_script = f'''#!/usr/bin/env python3
"""Joule Measurement Analyzer — Run on OptiPlex"""
import sqlite3
import json
from pathlib import Path

def analyze_joule_data():
    log_path = Path('{DATA_DIR}/joule_measurements.jsonl')
    if not log_path.exists():
        print("[ANALYZER] No joule data yet")
        return
    
    conn = sqlite3.connect(f'{DATA_DIR}/joule_analysis.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        device TEXT,
        charge_mah REAL,
        joules REAL,
        delta_from_prev REAL
    )''')
    
    with open(log_path) as f:
        prev_joules = None
        for line in f:
            rec = json.loads(line.strip())
            joules = rec.get('joules_estimated')
            delta = None if prev_joules is None or joules is None else joules - prev_joules
            c.execute('''INSERT INTO measurements 
                        (timestamp, device, charge_mah, joules, delta_from_prev)
                        VALUES (?, ?, ?, ?, ?)''',
                      (rec['timestamp'], rec['device'], 
                       rec.get('raw_charge_counter_mah'), joules, delta))
            prev_joules = joules
    
    conn.commit()
    conn.close()
    
    # Query latest
    c = sqlite3.connect(f'{DATA_DIR}/joule_analysis.db').cursor()
    c.execute('SELECT COUNT(*), AVG(joules) FROM measurements WHERE joules IS NOT NULL')
    cnt, avg = c.fetchone()
    print(f"[ANALYZER] {{cnt}} measurements, avg {{avg:.1f}} J")
    print(f"[OPEN] ACRE mint gate ready when joules > 0")

if __name__ == '__main__':
    analyze_joule_data()
'''
    
    with open(f'{BIN_DIR}/analyze_joules.py', 'w') as f:
        f.write(analyzer_script)
    
    print(f"[JOULE] Created collect_joules.py (phone) + analyze_joules.py (box)")
    return True

# ========== PRIORITY 3: Real 7B Audit Pipeline ==========
def setup_real_7b_audit():
    """Audit with actual repo content piped into prompt."""
    audit_script = f'''#!/usr/bin/env python3
"""Real 7B Audit — Pipes repo content into LLM prompt"""
import subprocess
import json
from pathlib import Path
import glob

REPO_PATH = Path('{BASE}/src/openroot' if ENV == 'box' else '{BASE}')

def collect_repo_content():
    """Gather .py files with hashes."""
    files = []
    for py_file in REPO_PATH.rglob('*.py'):
        if '.git' in str(py_file) or '__pycache__' in str(py_file):
            continue
        content = py_file.read_text(errors='replace')[:10000]  # Truncate large files
        sha = hashlib.sha256(content.encode()).hexdigest()[:16]
        files.append({{'path': str(py_file.relative_to(REPO_PATH)), 'sha': sha, 'preview': content}})
    return files

def build_audit_prompt(files):
    """Construct prompt with actual content."""
    prompt = f'''=== OPENROOT CODE AUDIT REQUEST ===
Perform security, efficiency, and correctness audit on the following files.
For EACH file, identify:
1. Security vulnerabilities (SQL injection, path traversal, etc.)
2. Efficiency issues (O(n^2) loops, redundant computations)
3. Correctness bugs (unhandled exceptions, race conditions)
4. Suggestions for improvement aligned with OpenRoot philosophy

{{len(files)}} files attached below with SHA256 previews.

--- BEGIN FILES ---
'''
    for f in files:
        prompt += f'''FILE: {{f["path"]}} (SHA256: {{f["sha"]}})
CONTENT PREVIEW (first 10000 chars):
{{f["preview"][:1000]}}...
---

'''
    prompt += '''--- END FILES ---
Begin audit now. Output structured JSON: {{
    "files_audited": N,
    "total_issues": M,
    "issues": [
        {{"file": "...", "severity": "high|medium|low", "category": "...", "description": "...", "fix_suggestion": "..."}}
    ],
    "summary": "..."
}}
'''
    return prompt

def run_audit_with_ollama(prompt):
    """Send to local 7B model via Ollama API."""
    try:
        response = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/generate', '-d', json.dumps({
                'model': 'qwen2.5-coder:7b',
                'prompt': prompt,
                'stream': False
            })],
            capture_output=True, text=True, timeout=300
        )
        result = json.loads(response.stdout)
        return result.get('response', '')
    except Exception as e:
        return f"AUDIT ERROR: {{e}}"

def main():
    print("[7B-AUDIT] Collecting repo content...")
    files = collect_repo_content()
    print(f"[7B-AUDIT] Found {{len(files)}} Python files")
    
    if not files:
        print("[7B-AUDIT] No files to audit")
        return
    
    prompt = build_audit_prompt(files)
    print("[7B-AUDIT] Sending to 7B model (this may take minutes)...")
    
    audit_result = run_audit_with_ollama(prompt)
    
    # Save to ledger
    result_file = f'{DATA_DIR}/audit_{{datetime.now().strftime("%Y%m%dT%H%M%S")}}.json'
    with open(result_file, 'w') as f:
        f.write(audit_result)
    
    print(f"[7B-AUDIT] Complete. Saved to {{result_file}}")
    print(audit_result[:500])

if __name__ == '__main__':
    main()
'''
    
    with open(f'{BIN_DIR}/real_7b_audit.py', 'w') as f:
        f.write(audit_script)
    
    print(f"[7B-AUDIT] Created real_7b_audit.py (pipes content into prompt)")
    return True

# ========== PRIORITY 4: Circuit Forge v0.2 Edge Filtering ==========
def setup_circuit_forge_v2():
    """Filter >=3-char param names, dedupe within-file, type annotations."""
    forge_script = f'''#!/usr/bin/env python3
"""Circuit Forge v0.2 — Edge filtering for aider 7B+3B"""
import ast
import re
from pathlib import Path
from collections import defaultdict

REPO_PATH = Path('{BASE}/src/openroot' if ENV == 'box' else '{BASE}')

class FunctionExtractor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        # Filter: >=3-char parameter names (excluding self)
        params = []
        for arg in node.args.args:
            if arg.arg == 'self':
                continue
            if len(arg.arg) >= 3:  # EDGE FILTER v0.2
                params.append(arg.arg)
        
        # Check for type annotations
        has_annotations = any(arg.annotation is not None for arg in node.args.args)
        
        if params or has_annotations:
            self.functions.append({{
                'name': node.name,
                'params': params,
                'has_type_annotations': has_annotations,
                'lineno': node.lineno,
                'file': ''  # Will be set later
            }})
    
    def generic_visit(self, node):
        super().generic_visit(node)

def scan_file(py_file):
    """Extract functions from a single file."""
    try:
        with open(py_file) as f:
            source = f.read()
        tree = ast.parse(source)
        extractor = FunctionExtractor()
        extractor.visit(tree)
        for func in extractor.functions:
            func['file'] = str(py_file.relative_to(REPO_PATH))
        return extractor.functions
    except SyntaxError:
        return []

def dedupe_within_files(functions_by_file):
    """Remove duplicate function names within each file."""
    deduped = {}
    for file, funcs in functions_by_file.items():
        seen = set()
        unique = []
        for f in funcs:
            if f['name'] not in seen:
                seen.add(f['name'])
                unique.append(f)
        deduped[file] = unique
    return deduped

def main():
    print("[FORGE-V0.2] Scanning for edge-filtered functions...")
    
    all_functions = []
    for py_file in REPO_PATH.rglob('*.py'):
        if '.git' in str(py_file) or '__pycache__' in str(py_file):
            continue
        funcs = scan_file(py_file)
        all_functions.extend(funcs)
    
    # Group by file for deduplication
    by_file = defaultdict(list)
    for f in all_functions:
        by_file[f['file']].append(f)
    
    deduped = dedupe_within_files(by_file)
    
    # Flatten
    final_funcs = []
    for file, funcs in deduped.items():
        final_funcs.extend(funcs)
    
    # Filter to annotated or >=3 param functions only
    final_funcs = [f for f in final_funcs if f['has_type_annotations'] or len(f['params']) >= 1]
    
    print(f"[FORGE-V0.2] {{len(final_funcs)}} filtered functions extracted")
    
    # Output as JSON for aider consumption
    output_file = f'{DATA_DIR}/circuit_forge_edges_v02.json'
    with open(output_file, 'w') as f:
        json.dump(final_funcs, f, indent=2)
    
    print(f"[FORGE-V0.2] Edges saved to {{output_file}}")
    
    # Print stats
    by_annotation = sum(1 for f in final_funcs if f['has_type_annotations'])
    print(f"[FORGE-V0.2] {{by_annotation}}/{{len(final_funcs)}} have type annotations")

if __name__ == '__main__':
    main()
'''
    
    with open(f'{BIN_DIR}/circuit_forge_v02.py', 'w') as f:
        f.write(forge_script)
    
    print(f"[FORGE-V0.2] Created circuit_forge_v02.py (>=3 char params + type annotations)")
    return True

# ========== PRIORITY 5: Sikeston Properties + Grants Matrix ==========
def setup_grants_matrix():
    """Sikeston blight properties lead verification."""
    grants_db_path = f'{DATA_DIR}/grants_properties.db'
    conn = sqlite3.connect(grants_db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT UNIQUE,
        city TEXT DEFAULT 'Sikeston',
        state TEXT DEFAULT 'MO',
        zip TEXT,
        blight_status TEXT,  # 'verified', 'suspected', 'clear'
        ownership_status TEXT,  # 'bank_owned', 'private', 'government'
        estimated_value REAL,
        grant_programs TEXT,  # JSON array
        verified_date TEXT,
        source_url TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS grant_leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_name TEXT,
        eligibility_requirements TEXT,
        max_funding_amount REAL,
        deadline TEXT,
        application_url TEXT,
        verification_status TEXT DEFAULT 'unverified',
        notes TEXT
    )''')
    
    # Insert placeholder Sikeston leads
    sample_leads = [
        ('Missouri Brownfields Program', 'Property must be confirmed contaminated', 100000, 'Rolling', 'https://dnr.mo.gov/brownfields', 'unverified', 'State-level blight remediation'),
        ('HUD Community Development Block Grant', 'Low-to-moderate income area', 500000, 'Annual', 'https://hud.gov/cdbg', 'unverified', 'Federal housing/infrastructure'),
        ('Sikeston Blight Removal Initiative', 'City of Sikeston approved', 25000, 'Contact city hall', 'https://sikeston.org', 'unverified', 'Local municipal program'),
    ]
    
    for lead in sample_leads:
        c.execute('''INSERT OR IGNORE INTO grant_leads 
                     (program_name, eligibility_requirements, max_funding_amount, 
                      application_url, notes)
                     VALUES (?, ?, ?, ?, ?)''', lead)
    
    conn.commit()
    conn.close()
    
    print(f"[GRANTS] Created grants_properties.db with {len(sample_leads)} sample leads")
    print(f"[GRANTS] Run verification queries against each lead before actioning")
    return True

# ========== MAIN EXECUTION ==========
def main():
    print("=" * 60)
    print("OPENROOT UNIFIED SETUP — NEXT BOARD PRIORITIES 1-5")
    print(f"Environment: {ENV} | Base: {BASE}")
    print("=" * 60)
    
    results = {}
    
    # Priority 1: TOTP
    print("\n[1/5] Setting up TOTP + Prepaid Number Workflow...")
    results['totp'] = setup_totp_workflow()
    
    # Priority 2: Joule Measurement
    print("\n[2/5] Setting up Measured Joule Row...")
    results['joule'] = setup_joule_measurement()
    
    # Priority 3: 7B Audit
    print("\n[3/5] Setting up Real 7B Audit Pipeline...")
    results['7b_audit'] = setup_real_7b_audit()
    
    # Priority 4: Circuit Forge v0.2
    print("\n[4/5] Setting up Circuit Forge v0.2 Edge Filtering...")
    results['forge_v2'] = setup_circuit_forge_v2()
    
    # Priority 5: Grants Matrix
    print("\n[5/5] Setting up Sikeston Properties + Grants Matrix...")
    results['grants'] = setup_grants_matrix()
    
    # Summary
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    for key, val in results.items():
        status = "✓" if val else "✗"
        print(f"{status} {key.upper()}")
    
    # Next actions
    print("\n>>> NEXT ACTIONS <<<")
    print("1. On Phone: chmod +x scripts/collect_joules.py && ./scripts/collect_joules.py")
    print("2. On Box: python3 bin/analyze_joules.py (after running collect on phone)")
    print("3. On Box: python3 bin/real_7b_audit.py (requires Ollama running)")
    print("4. On Box: python3 bin/circuit_forge_v02.py")
    print("5. On Box: sqlite3 data/grants_properties.db 'SELECT * FROM grant_leads;'")
    print("\nAll scripts use absolute paths. Verify before execution.")

if __name__ == '__main__':
    main()
