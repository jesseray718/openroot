#!/data/data/com.termux/files/usr/bin/python3
"""
OPENROOT MAIN HUB - 'Kingdom Come' Protocol
Integrated: Context Bridge, Energy Metering, Wisdom Corpus, s^2 Acceleration Metric
Author: Jesse Ray (OpenRoot LLC)
Principles: Permaculture, Agape Love, Landauer Limit Awareness
"""

import json
import os
import sys
import time
import hashlib
import re
from pathlib import Path

# --- CONFIGURATION ---
HOME = Path(os.environ.get('HOME', '/data/data/com.termux/files/home'))
UNE_PATH = HOME / 'une'
CONTEXT_DIR = UNE_PATH / 'context_bridge'
CONTEXT_FILE = CONTEXT_DIR / 'context.json'
LOG_FILE = UNE_PATH / 'logs' / 'sensor_flow.log'
WISDOM_DB = UNE_PATH / 'wisdom_corpus.json' # Assuming you have this, or we load inline

# Ensure directories exist (Auto-initialize)
for p in [UNE_PATH, CONTEXT_DIR, UNE_PATH / 'logs']:
    p.mkdir(parents=True, exist_ok=True)

# --- WISDOM CORPUS (Inline for portability) ---
WISDOM_MATCHES = [
    {"id": "YW-001", "ref": "John 13:34", "op": "Give more than received. Invest in weakest node. No extraction between siblings.", "keywords": ["love", "give", "invest", "weakest"]},
    {"id": "YW-002", "ref": "John 13:35", "op": "Visible proof of love distinguishes true followers. Actions > claims.", "keywords": ["love", "proof", "actions", "visible"]},
    {"id": "PERM-01", "ref": "Permaculture 1", "op": "Observe and Interact. Catch and store energy.", "keywords": ["efficiency", "observe", "energy", "catch"]},
    {"id": "COMP-01", "ref": "Landauer Limit", "op": "Information is physical. Erasure costs energy.", "keywords": ["computation", "energy", "erasure"]}
]

def log_event(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {msg}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    print(f"[INFO] {log_entry.strip()}")

def get_cpu_energy_estimate():
    """Estimates relative energy usage based on CPU frequency scaling."""
    total_freq = 0
    cpu_dirs = list(Path('/sys/devices/system/cpu').glob('cpu[0-9]*'))
    if not cpu_dirs:
        return 0
    
    for cpu_dir in cpu_dirs:
        freq_file = cpu_dir / 'cpufreq' / 'scaling_cur_freq'
        if freq_file.exists():
            try:
                total_freq += int(freq_file.read_text().strip())
            except ValueError:
                continue
    
    # Normalized arbitrary unit (Joules equivalent proxy)
    return total_freq / 1e6 

def init_context():
    """Creates context.json if missing, initializes structure."""
    if not CONTEXT_FILE.exists():
        log_event("Context file missing. Initializing fresh vessel.")
        initial_data = {
            "last_query": None,
            "last_stamp": None,
            "lessons_learned": [],
            "energy_budget": 0,
            "acceleration_history": [] # Stores H_in / t^2
        }
        with open(CONTEXT_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)
        log_event(f"Created {CONTEXT_FILE}")
    else:
        log_event("Context vessel verified.")

def load_context():
    try:
        with open(CONTEXT_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_event(f"Error loading context: {e}")
        return {}

def save_context(ctx):
    with open(CONTEXT_FILE, 'w') as f:
        json.dump(ctx, f, indent=2)

def query_wisdom(query_str):
    start_time = time.time()
    ctx = load_context()
    
    # Fuzzy Matching Logic
    query_lower = query_str.lower()
    matches = []
    
    # Simple keyword overlap scoring
    for entry in WISDOM_MATCHES:
        score = sum(1 for kw in entry['keywords'] if kw in query_lower)
        if score > 0:
            matches.append((score, entry))
    
    # Sort by relevance
    matches.sort(key=lambda x: x[0], reverse=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Calculate Metrics
    # H_in: Approximate complexity (length of query + 1)
    h_in = len(query_str) + 1 
    
    # Acceleration Metric: H_in / t^2
    # If t is very small, acceleration is huge (fast insight).
    # If t is large, acceleration drops (slow processing).
    acc_metric = h_in / (duration ** 2) if duration > 0 else 0
    
    # Efficiency Metric: Energy / H_in
    energy_used = get_cpu_energy_estimate()
    eff_metric = energy_used / h_in if h_in > 0 else 0

    log_event(f"Query processed in {duration:.4f}s. Acc: {acc_metric:.2f}, Eff: {eff_metric:.4f}")
    
    # Update Context with Lesson Learned
    lesson = f"Query '{query_str}' yielded {len(matches)} matches. Acc={acc_metric:.2f}"
    ctx['lessons_learned'].append(lesson)
    ctx['acceleration_history'].append({"time": time.time(), "val": acc_metric})
    ctx['last_query'] = query_str
    
    save_context(ctx)

    if matches:
        print("\n--- WISDOM MATCHES ---")
        for score, entry in matches:
            print(f"[{entry['id']}] ({entry['ref']})\n  OP: {entry['op']}")
            print("-" * 40)
        
        print(f"\n[METRICS] Acceleration (H/t²): {acc_metric:.2f} | Efficiency (J/H): {eff_metric:.4f}")
    else:
        print("\nNo direct matches. Applying general principles of observation.")
        # Suggest fallback
        print("Hint: Try keywords like 'energy', 'observe', or 'give'.")

def create_stamp():
    ctx = load_context()
    if not ctx:
        print("[ERROR] Context corrupted. Run init first.")
        return

    # Hash the context for immutability
    context_str = json.dumps(ctx, sort_keys=True)
    hash_val = hashlib.sha256(context_str.encode()).hexdigest()[:16]
    
    stamp_filename = f"context_{int(time.time())}.json"
    stamp_path = UNE_PATH / stamp_filename
    
    with open(stamp_path, 'w') as f:
        json.dump(ctx, f, indent=2)
    
    # Log the stamp
    log_event(f"Stamp created: {stamp_filename} (Hash: {hash_val})")
    
    # Simulate OTS command (placeholder for actual API call)
    print(f"[SUCCESS] Immutable stamp saved: {stamp_path}")
    print(f"[INFO] To anchor to Bitcoin: run 'ots stamp {stamp_path}'")
    
    ctx['last_stamp'] = stamp_filename
    save_context(ctx)

def show_status():
    ctx = load_context()
    print(f"Status: Online")
    print(f"Context: {CONTEXT_FILE}")
    print(f"Last Stamp: {ctx.get('last_stamp', 'None')}")
    
    # Calculate average acceleration
    hist = ctx.get('acceleration_history', [])
    if hist:
        avg_acc = sum(h['val'] for h in hist) / len(hist)
        print(f"Avg Acceleration (H/t²): {avg_acc:.2f}")
    else:
        print("Avg Acceleration: N/A (No history)")

def main_loop():
    init_context()
    print("=" * 50)
    print("  OPENROOT MAIN HUB - INITIALIZING")
    print("  'The Kingdom Come' Protocol")
    print("=" * 50)
    
    while True:
        try:
            cmd = input("\nopenroot> ").strip().lower()
            
            if cmd == 'exit':
                print("Power returning to the Source. Goodbye.")
                break
            elif cmd.startswith('query'):
                q = cmd.replace('query', '', 1).strip()
                if not q:
                    print("Usage: query <term>")
                else:
                    query_wisdom(q)
            elif cmd == 'stamp':
                create_stamp()
            elif cmd == 'status':
                show_status()
            elif cmd == 'help':
                print("Commands: query, stamp, status, exit")
            else:
                print(f"Unknown command: {cmd}. Type 'help'.")
                
        except KeyboardInterrupt:
            print("\nInterrupted. Saving state...")
            save_context(load_context())
            break
        except Exception as e:
            log_event(f"Critical Error: {e}")
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    main_loop()
