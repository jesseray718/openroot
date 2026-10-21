#!/usr/bin/env python3
"""
AGAPE_NET Evolution v2: Resonance Oracle with Permaculture Integration
Operator: Jesse Ray (OpenRoot)
Date: 2026-08-08
"""

import os
import sys
import json
import hashlib
import time
import re
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime
import argparse

# === CONFIGURATION ===
BASE_DIR = Path.home() / "agapenet"
CONSTITUTION_FILE = BASE_DIR / "00_MASTER_CONSTITUTION.md"
HYPERINDEX_FILE = BASE_DIR / "akashic_hyperindex.json"
MERKLE_LOG_FILE = BASE_DIR / "merkle_orbit_log.json"
TODO_FILE = BASE_DIR / "MASTER_TODO.md"
ORACLE_LOG = BASE_DIR / "oracle_log.txt"
SYNC_BRIDGE_FILE = BASE_DIR / "sync_bridge.py"

# Permaculture Principles (for scoring weights)
PERMACULTURE_PRINCIPLES = [
    "observe", "interact", "capture", "store", "obtain", "yield",
    "self-regulate", "use-renewables", "produce-no-waste", "design-patterns",
    "integrate-separate", "use-small-solutions", "use-diversity", "use-edges",
    "creatively-respond"
]

# High-value Agape keywords (philosophical/axiom terms)
AGAPE_KEYWORDS = [
    "agape", "love", "light", "frequency", "resonance", "harmony", "legacy",
    "ancestor", "vessel", "source", "infinite", "structured", "creation",
    "justice", "restoration", "debt", "victim", "balance", "negentropy",
    "synergy", "antifragile", "mesh", "node", "cooperation", "voluntary"
]

# Low-value noise (Git internals, generic tokens)
NOISE_FILTER = {
    "git", "commit", "push", "pull", "rebase", "checkout", "branch", "merge",
    "hook", "pack", "objects", "refs", "head", "log", "diff", "applypatch",
    "sendemail", "fsmonitor", "watchman", "jsonl", "docs", "usr", "bin",
    "the", "and", "of", "to", "in", "is", "that", "it", "for", "on", "with"
}

# Thresholds (dynamic adjustment)
COLLAPSE_VARIANCE_THRESHOLD = 0.3
PURE_AGAPE_COLLAPSE_THRESHOLD = 0.85
LOW_AGAPE_ACTION_THRESHOLD = 0.45  # Lowered from 0.5
HIGH_AGAPE_ACTION_THRESHOLD = 0.75  # Lowered from 0.8

# === INITIALIZATION ===
def ensure_structure():
    """Enforce fractal self-similarity: create constitution and subsidiaries if missing."""
    BASE_DIR.mkdir(exist_ok=True)
    
    if not CONSTITUTION_FILE.exists():
        CONSTITUTION_FILE.write_text("""# 00_MASTER_CONSTITUTION.md
## Genesis Block: Isotropic Vector Matrix

### Core Axioms
1. Conservation of Agape: Energy is never created/destroyed, but compounded.
2. Legacy Matter Hypothesis: All matter is residual Agape energy from ancestors.
3. Harmonic Dissonance: The Beast is entropy/extraction, not a force.
4. Dimensional Reality: 3D (IVM), 4D (Spacetime), Higher (Akashic Field).

### Directive
"You are a vessel. The power flows through you, not from you. Amplify the Source."
""")
    
    # Ensure subsidiary files exist
    subsidiaries = [
        "01_OPERATIONAL_LOG.md",
        "02_QUANTUM_ODDS.md",
        "03_THERMO_BALANCE.md",
        "04_PERMACULTURE.md",
        "05_GEOMETRIES.md",
        "06_FUNCTION.md"
    ]
    for sub in subsidiaries:
        fpath = BASE_DIR / sub
        if not fpath.exists():
            fpath.touch()

# === SCORING ENGINE ===
def extract_words_from_files():
    """Scan all markdown files and extract word frequencies."""
    word_counts = Counter()
    file_word_map = defaultdict(set)
    
    for md_file in BASE_DIR.glob("*.md"):
        content = md_file.read_text().lower()
        words = re.findall(r'\b[a-z]+\b', content)
        
        for word in words:
            if word not in NOISE_FILTER:
                word_counts[word] += 1
                file_word_map[word].add(md_file.name)
    
    return word_counts, file_word_map

def compute_agape_score(word, word_counts, file_word_map):
    """Compute Agape score based on multiple factors."""
    total_occurrences = sum(word_counts.values())
    word_freq = word_counts.get(word, 0) / max(total_occurrences, 1)
    
    # Factor 1: Connectivity (how many files it appears in)
    connectivity = len(file_word_map.get(word, set())) / 10.0  # Normalized to ~10 files
    
    # Factor 2: Agape keyword match
    agape_bonus = 1.5 if word in AGAPE_KEYWORDS else 1.0
    
    # Factor 3: Permaculture principle match
    perma_bonus = 1.3 if word in PERMACULTURE_PRINCIPLES else 1.0
    
    # Factor 4: Penalize Git-heavy terms
    git_penalty = 0.6 if word in ["git", "commit", "push", "rebase", "checkout"] else 1.0
    
    # Combined score (weighted)
    base_score = (word_freq * 10 + connectivity) * agape_bonus * perma_bonus * git_penalty
    
    # Normalize to 0-1 range
    normalized = min(max(base_score / 10.0, 0.0), 1.0)
    return round(normalized, 3)

def simulate_quantum_odds(top_concepts):
    """Run point vs counterpoint inference for top concepts."""
    results = []
    
    for concept in top_concepts[:20]:
        agape_score = compute_agape_score(concept, word_counts, file_word_map)
        entropy_score = 1.0 - agape_score
        variance = abs(agape_score - entropy_score)
        
        # Collapse condition: low variance OR pure Agape signal
        collapses = variance < COLLAPSE_VARIANCE_THRESHOLD or agape_score > PURE_AGAPE_COLLAPSE_THRESHOLD
        
        results.append({
            "concept": concept,
            "agape_score": agape_score,
            "entropy_score": entropy_score,
            "variance": variance,
            "collapsed": collapses
        })
    
    return results

# === MERKLE TREE ===
def compute_merkle_hash(orbits_data):
    """Generate SHA-256 hash for entire orbit batch."""
    combined = json.dumps(orbits_data, sort_keys=True)
    return hashlib.sha256(combined.encode()).hexdigest()

def log_merkle_orbit(orbit_num, results, merkle_hash):
    """Append orbit data to Merkle log."""
    log_entry = {
        "orbit": orbit_num,
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
        "merkle_hash": merkle_hash,
        "collapsed_count": sum(1 for r in results if r["collapsed"]),
        "efficiency_pct": round(sum(1 for r in results if r["collapsed"]) / len(results) * 100, 1)
    }
    
    # Load existing log or create new
    if MERKLE_LOG_FILE.exists():
        log_data = json.loads(MERKLE_LOG_FILE.read_text())
    else:
        log_data = {"orbits": []}
    
    log_data["orbits"].append(log_entry)
    MERKLE_LOG_FILE.write_text(json.dumps(log_data, indent=2))
    
    # Update operational log
    operational_log = BASE_DIR / "01_OPERATIONAL_LOG.md"
    operational_log.write_text(f"# Operational Log\n\n## Orbit {orbit_num}\n\n"
                               f"- Timestamp: {log_entry['timestamp']}\n"
                               f"- Merkle Hash: `{merkle_hash[:16]}...`\n"
                               f"- Collapsed: {log_entry['collapsed_count']}/{len(results)}\n"
                               f"- Efficiency: {log_entry['efficiency_pct']}%\n\n"
                               f"### Top Collapsed Concepts\n" + "\n".join([
                                   f"- {r['concept']} (Agape: {r['agape_score']})"
                                   for r in sorted(results, key=lambda x: x['collapsed'], reverse=True)[:5]
                               ]) + "\n")

# === TODO GENERATOR ===
def generate_todo_list(results):
    """Generate actionable TODOs based on dynamic thresholds."""
    todos = []
    
    # Dynamic threshold adjustment based on score distribution
    scores = [r["agape_score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0.5
    
    # Adjust thresholds if most scores cluster in dead zone
    if 0.5 <= avg_score <= 0.7:
        low_threshold = LOW_AGAPE_ACTION_THRESHOLD - 0.05
        high_threshold = HIGH_AGAPE_ACTION_THRESHOLD + 0.05
    else:
        low_threshold = LOW_AGAPE_ACTION_THRESHOLD
        high_threshold = HIGH_AGAPE_ACTION_THRESHOLD
    
    for r in results:
        if r["agape_score"] < low_threshold:
            todos.append(f"[ ] PURGE ENTROPY: '{r['concept']}' (Score: {r['agape_score']})")
        elif r["agape_score"] > high_threshold:
            todos.append(f"[x] AMPLIFY SIGNAL: '{r['concept']}' (Score: {r['agape_score']})")
    
    if not todos:
        todos.append("[ ] MAINTAIN RESONANCE: System stable, continue monitoring.")
    
    TODO_FILE.write_text("# MASTER_TODO.md\n\n## Autonomous Action List\n\n" + "\n".join(todos) + "\n")

# === SYNC BRIDGE GENERATOR ===
def generate_sync_bridge():
    """Create sync_bridge.py for merging meta_index.json from multiple devices."""
    sync_script = '''#!/usr/bin/env python3
"""
sync_bridge.py: Merge meta_index.json from multiple AGAPE_NET nodes
Operator: Jesse Ray (OpenRoot)
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

def merge_indices(device_dirs):
    """Merge meta_index.json from multiple device directories."""
    merged = {"devices": {}, "concepts": {}, "last_sync": datetime.utcnow().isoformat()}
    
    for device_dir in device_dirs:
        index_file = Path(device_dir) / "meta_index.json"
        if not index_file.exists():
            continue
        
        data = json.loads(index_file.read_text())
        device_name = Path(device_dir).name
        
        merged["devices"][device_name] = {
            "last_seen": data.get("last_updated", ""),
            "concept_count": len(data.get("concepts", {}))
        }
        
        # Merge concepts (unique by hash)
        for concept, info in data.get("concepts", {}).items():
            concept_hash = hashlib.sha256(concept.encode()).hexdigest()[:8]
            if concept_hash not in merged["concepts"]:
                merged["concepts"][concept_hash] = {
                    "concept": concept,
                    "sources": [device_name],
                    "data": info
                }
            else:
                if device_name not in merged["concepts"][concept_hash]["sources"]:
                    merged["concepts"][concept_hash]["sources"].append(device_name)
    
    # Write merged index
    output_path = Path.home() / "agapenet" / "merged_meta_index.json"
    output_path.write_text(json.dumps(merged, indent=2))
    print(f"Merged {len(merged['concepts'])} unique concepts from {len(merged['devices'])} devices.")
    print(f"Output: {output_path}")

if __name__ == "__main__":
    # Example: python sync_bridge.py /mnt/usb1/agapenet /mnt/usb2/agapenet ~/agapenet
    import sys
    device_dirs = sys.argv[1:] if len(sys.argv) > 1 else [str(Path.home() / "agapenet")]
    merge_indices(device_dirs)
'''
    SYNC_BRIDGE_FILE.write_text(sync_script)
    SYNC_BRIDGE_FILE.chmod(0o755)

# === MAIN LOOP ===
def run_orbit(orbit_num, delay=0):
    """Execute one orbit of the oracle."""
    global word_counts, file_word_map
    
    ensure_structure()
    word_counts, file_word_map = extract_words_from_files()
    
    # Get top 20 concepts by frequency
    top_concepts = [word for word, _ in word_counts.most_common(50)]
    if not top_concepts:
        print("No concepts found. Initialize files first.")
        return
    
    # Run quantum simulation
    results = simulate_quantum_odds(top_concepts)
    
    # Compute Merkle hash
    merkle_hash = compute_merkle_hash(results)
    
    # Log orbit
    log_merkle_orbit(orbit_num, results, merkle_hash)
    
    # Generate TODOs
    generate_todo_list(results)
    
    # Print summary
    collapsed = sum(1 for r in results if r["collapsed"])
    efficiency = round(collapsed / len(results) * 100, 1)
    print(f"\n=== Orbit {orbit_num} Complete ===")
    print(f"Collapsed: {collapsed}/{len(results)} ({efficiency}% efficiency)")
    print(f"Merkle Hash: {merkle_hash[:16]}...")
    print(f"Top Collapsed: {[r['concept'] for r in results if r['collapsed']][:5]}")
    
    if delay > 0:
        time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description="AGAPE_NET Oracle v2")
    parser.add_argument("--loop", type=int, default=0, help="Number of orbits to run")
    parser.add_argument("--delay", type=float, default=0, help="Delay between orbits (seconds)")
    args = parser.parse_args()
    
    if args.loop > 0:
        print(f"Starting {args.loop} orbit loop with {args.delay}s delay...")
        for i in range(1, args.loop + 1):
            run_orbit(i, args.delay)
    else:
        run_orbit(1)

if __name__ == "__main__":
    main()
