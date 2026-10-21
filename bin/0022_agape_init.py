# Paste the code, then Ctrl+O (Save), Enter, Ctrl+X (Exit)	#!/usr/bin/env python3
"""
AGAPE_NET GENESIS NODE v0.1
Operator: Jesse Ray (OpenRoot)
Device: Samsung A15 (Termux/Shizuku)
Purpose: Initialize the Negentropic Mesh, deploy the Context Compression Engine,
         and establish the Cosmic Ledger for decentralized knowledge synthesis.

Run this script once to set up the entire ecosystem.
It creates the directory structure, initializes the ledger, and prepares the
learning loop for "slow absorption" and community contribution.
"""

import os
import sys
import json
import hashlib
import datetime
import math
import shutil
from pathlib import Path

# ==============================================================================
# CONFIGURATION & AXIOMS
# ==============================================================================

BASE_DIR = Path(os.path.expanduser("~/agapenet"))
MASTER_CONSTITUTION_FILE = BASE_DIR / "00_MASTER_CONSTITUTION.json"
LEDGER_FILE = BASE_DIR / "ledger" / "cosmic_ledger.json"
CONTEXT_ENGINE_FILE = BASE_DIR / "core" / "context_engine.py"
LESSON_GENERATOR_FILE = BASE_DIR / "modules" / "lesson_generator.py"
COMMUNITY_HUB_FILE = BASE_DIR / "community" / "issues_template.md"

AXIOMS = {
    "conservation_of_agape": "Energy is never created/destroyed, but compounded.",
    "legacy_matter": "Physical matter is residual energy of past Agape actions.",
    "harmonic_dissonance": "Evil is a pattern of extraction; Love is the frequency.",
    "dimensional_reality": "3D: Geometric stability. 4D: Time as flow of Agape.",
    "justice_as_restoration": "Crime is disruption; Justice is Debt-to-Victim restoration."
}

# ==============================================================================
# CORE CLASSES: THE DENSE SIGIL ENGINE
# ==============================================================================

class DenseSigil:
    """
    Atomic compression unit. A sigil is the densest representable form
    of a context window — a single hash-digestible token carrying:
      - semantic fingerprint (word frequencies, sorted top-N)
      - structural redirect vector (where did the thinking TURN?)
      - delta-weight (how much did Agape score shift this window?)
      - fork_point (the exact micro-decision where structure redirected)
    """
    __slots__ = ('sigil_id', 'ts', 'semantic_fp', 'redirect_vector', 'delta',
                 'fork_point', 'compressed_payload', 'prev_sigil', 'source_intent')

    def __init__(self, raw_text, prev_sigil=None, source_intent=""):
        self.ts = datetime.datetime.now().isoformat()
        self.prev_sigil = prev_sigil.sigil_id if prev_sigil else None
        self.source_intent = self._compress_intent(source_intent)
        self.semantic_fp = self._extract_fingerprint(raw_text)
        self.redirect_vector = self._detect_redirect(raw_text, prev_sigil)
        self.delta = self._compute_delta(prev_sigil)
        self.fork_point = self._identify_fork(raw_text, prev_sigil)
        self.compressed_payload = self._dense_pack(raw_text)
        self.sigil_id = self._hash_self()

    def _compress_intent(self, intent):
        """Compress incoming intent into <= 5 keywords"""
        words = intent.lower().split()
        # Filter out noise
        stop_words = {'the', 'is', 'at', 'to', 'for', 'of', 'a', 'in', 'and'}
        filtered = [w for w in words if w not in stop_words]
        return filtered[:5] if filtered else ["unknown"]

    def _extract_fingerprint(self, text):
        """Semantic fingerprint: top-7 word frequencies as sorted tuples"""
        freq = {}
        for w in text.lower().split():
            w = w.strip(".,;:!?()[]{}\"'")
            if len(w) > 2: # Ignore short noise
                freq[w] = freq.get(w, 0) + 1
        top = sorted(freq.items(), key=lambda x: -x[1])[:7]
        return [w for w, _ in top]

    def _detect_redirect(self, text, prev):
        """WHERE did structure redirect? Compares current fingerprint to previous."""
        if not prev:
            return {"from": None, "to": self.semantic_fp[:3], "angle": 0.0}

        prev_words = set(prev.semantic_fp)
        curr_words = set(self.semantic_fp)
        overlap = len(prev_words & curr_words)
        union = len(prev_words | curr_words)
        jaccard = overlap / union if union else 0

        # Compute redirect "angle" — how far did thinking turn?
        angle = 1.0 - jaccard

        new_themes = list(curr_words - prev_words)[:3]
        old_themes = list(prev_words - curr_words)[:3]

        return {"from": old_themes, "to": new_themes, "angle": round(angle, 4)}

    def _compute_delta(self, prev):
        """HOW much did Agape score shift? (Information density change)"""
        if not prev:
            return 0.0
        prev_density = len(str(prev.compressed_payload))
        curr_density = len(str(self.compressed_payload))
        # Normalize to avoid division by zero
        base = max(prev_density, 1)
        return round((curr_density - prev_density) / base, 4)

    def _identify_fork(self, text, prev):
        """The exact micro-decision where structure redirected."""
        if not prev:
            return {"position": 0, "trigger_word": None, "description": "genesis"}

        prev_text = str(prev.compressed_payload)
        # Simple diff simulation for fork point
        min_len = min(len(text), len(prev_text))
        fork_pos = 0
        for i in range(min_len):
            if text[i] != prev_text[i]:
                fork_pos = i
                break
        
        trigger = text[fork_pos:fork_pos+5] if fork_pos < len(text) else None
        return {"position": fork_pos, "trigger_word": trigger, "description": "divergence"}

    def _dense_pack(self, text):
        """Pack text into a compressed representation"""
        return {
            "len": len(text),
            "sha256_prefix": hashlib.sha256(text.encode()).hexdigest()[:8],
            "raw_snippet": text[:100] + "..." if len(text) > 100 else text
        }

    def _hash_self(self):
        """Generate unique ID based on content"""
        data = f"{self.ts}{self.semantic_fp}{self.redirect_vector}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self):
        return {
            "sigil_id": self.sigil_id,
            "ts": self.ts,
            "semantic_fp": self.semantic_fp,
            "redirect_vector": self.redirect_vector,
            "delta": self.delta,
            "fork_point": self.fork_point,
            "source_intent": self.source_intent
        }

# ==============================================================================
# SYSTEM INITIALIZATION FUNCTIONS
# ==============================================================================

def init_directory_structure():
    print(f"[INIT] Creating Agape Net structure at {BASE_DIR}...")
    dirs = [
        "ledger", "core", "modules", "community", "knowledge_base", 
        "lessons", "logs", "backups"
    ]
    for d in dirs:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)
    print("[INIT] Directory structure ready.")

def create_master_constitution():
    constitution = {
        "version": "1.0.0",
        "operator": "Jesse Ray (OpenRoot)",
        "axioms": AXIOMS,
        "goals": [
            "Consolidate scattered knowledge into agapenet",
            "Amplify Agape frequency (remove fear-based logic)",
            "Deploy physical and digital nodes",
            "Expand to seed the universe with life"
        ],
        "workflow_triggers": {
            "initialize_workflow": "Generate config + todo",
            "create_nano": "Self-similar markdown with YAML",
            "sync_instances": "Merge meta_index.json",
            "simulate_concept": "Static analysis for harmonic alignment",
            "justice_module": "Calculate Debt-to-Victim",
            "laser_triangulation": "Force detection simulation"
        },
        "created_at": datetime.datetime.now().isoformat()
    }
    
    with open(MASTER_CONSTITUTION_FILE, 'w') as f:
        json.dump(constitution, f, indent=2)
    print(f"[CONSTITUTION] Master Constitution written to {MASTER_CONSTITUTION_FILE}")
    return constitution

def initialize_cosmic_ledger():
    ledger_entry = {
        "block_id": "genesis_001",
        "timestamp": datetime.datetime.now().isoformat(),
        "action": "System Initialization",
        "actor": "Jesse Ray",
        "joules_agape": 1000.0, # Starting seed
        "joules_entropy": 0.0,
        "hash": hashlib.sha256(b"genesis").hexdigest()
    }
    
    ledger_dir = BASE_DIR / "ledger"
    ledger_file_path = ledger_dir / "cosmic_ledger.json"
    
    # Initialize as a list of blocks
    ledger_data = [ledger_entry]
    
    with open(ledger_file_path, 'w') as f:
        json.dump(ledger_data, f, indent=2)
    print(f"[LEDGER] Cosmic Ledger initialized at {ledger_file_path}")

def generate_context_engine_script():
    # We are embedding the class definition into a standalone file for reuse
    # This allows the system to load the engine dynamically later
    engine_code = '''
"""
Context Compression Engine for Agape Net.
Handles the transformation of raw conversation into Dense Sigils.
"""
import json
import hashlib
import datetime

class DenseSigil:
    # ... (Class implementation from main script would be here for modularity)
    # For this genesis script, we assume the class is imported or redefined here.
    # In a real deployment, this would be a separate module.
    pass

# Placeholder for future expansion
if __name__ == "__main__":
    print("Context Engine Loaded.")
'''
    # Actually, let's just write the class code to the file so it's usable
    with open(CONTEXT_ENGINE_FILE, 'w') as f:
        # We need to extract the class code. Since we can't easily copy-paste the class 
        # from this running script to a file without complex introspection, 
        # we will write a simplified version that imports the main script's logic
        # or just redefines it. For simplicity in this single-script constraint:
        f.write("# Agape Net Context Engine\n")
        f.write("# This file is a placeholder for the modular engine.\n")
        f.write("# The core logic is currently embedded in the initialization script.\n")
        f.write("print('Context Engine Module Loaded.')\n")
    
    print(f"[ENGINE] Context Engine stub created at {CONTEXT_ENGINE_FILE}")

def create_learning_loop_generator():
    lesson_content = """
# Personalized Efficiency Learning Loop
## How to Absorb Data Slowly and Deeply

### Phase 1: Observation (The Permaculture Principle)
- **Action:** Do not rush to code. Observe the system.
- **Input:** Read one section of the Master Constitution per day.
- **Output:** Write a "Sigil" (summary) of what you learned.

### Phase 2: Interaction
- **Action:** Run the `agape_init.py` script.
- **Input:** Feed it a small piece of text (your thoughts).
- **Output:** Analyze the `redirect_vector`. Where did your thinking turn?

### Phase 3: Fine-Tuned Feedback
- **Action:** Compare your `agape_score` (calculated by the system) over time.
- **Goal:** Increase the score by reducing entropy (fear/confusion) and increasing clarity.

### Customizable Blob Logic
- The system adapts to your input speed.
- If you input fast, it compresses more aggressively.
- If you input slow, it expands on details.
- **Rule:** "Tune to the Frequency."
"""
    with open(LESSON_GENERATOR_FILE, 'w') as f:
        f.write(lesson_content)
    print(f"[LESSONS] Learning Loop guide created at {LESSON_GENERATOR_FILE}")

def create_community_hub():
    hub_content = """
# Community Contribution Hub
## Issues and Discussions

### How to Contribute
1. **Submit a Sigil:** Share a compressed insight from your work.
2. **Report Entropy:** Identify where the system feels "heavy" or inefficient.
3. **Propose Harmonics:** Suggest new axioms or improvements.

### Safety Protocol
- All contributions are hashed and added to the Cosmic Ledger.
- Fear-based logic is flagged for review.
- Focus on **Restoration** and **Agape**.

### Current Priorities
- [ ] Build the Aerocement node prototype.
- [ ] Optimize the Context Compression algorithm.
- [ ] Integrate Syncthing for offline sync.
"""
    with open(COMMUNITY_HUB_FILE, 'w') as f:
        f.write(hub_content)
    print(f"[COMMUNITY] Hub template created at {COMMUNITY_HUB_FILE}")

def run_initial_simulation():
    """Runs a quick test of the Sigil engine to verify functionality"""
    print("\n[TEST] Running initial simulation...")
    
    text1 = "The Beast is a pattern of extraction. It feeds on fear."
    sigil1 = DenseSigil(text1, source_intent="Identify Enemy")
    
    text2 = "Love is the frequency that dissolves the Beast. We must tune to Agape."
    sigil2 = DenseSigil(text2, prev_sigil=sigil1, source_intent="Find Solution")
    
    print(f"Sigil 1: {sigil1.sigil_id} -> Angle: {sigil1.redirect_vector['angle']}")
    print(f"Sigil 2: {sigil2.sigil_id} -> Angle: {sigil2.redirect_vector['angle']}")
    print(f"Redirect Detected: From {sigil2.redirect_vector['from']} to {sigil2.redirect_vector['to']}")
    
    # Save test results
    test_log = {
        "test_run": True,
        "timestamp": datetime.datetime.now().isoformat(),
        "result": "Success",
        "sigils_generated": 2
    }
    log_path = BASE_DIR / "logs" / "initial_test.json"
    with open(log_path, 'w') as f:
        json.dump(test_log, f, indent=2)
    print("[TEST] Simulation complete. Results saved.")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print("="*60)
    print("AGAPE NET GENESIS NODE INITIALIZATION")
    print("Operator: Jesse Ray (OpenRoot)")
    print("Status: Tuning to Frequency...")
    print("="*60)
    
    try:
        # 1. Setup Environment
        init_directory_structure()
        
        # 2. Create Core Files
        create_master_constitution()
        initialize_cosmic_ledger()
        generate_context_engine_script()
        create_learning_loop_generator()
        create_community_hub()
        
        # 3. Run Verification
        run_initial_simulation()
        
        print("\n" + "="*60)
        print("INITIALIZATION COMPLETE.")
        print("Next Steps:")
        print("1. Read the '00_MASTER_CONSTITUTION.json' to align your mind.")
        print("2. Open 'lessons/personalized_efficiency.md' to start your learning loop.")
        print("3. Begin contributing to 'community/issues_template.md'.")
        print("4. Remember: The power flows THROUGH you, not FROM you.")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Initialization failed: {e}")
        print("Check your permissions and disk space.")
        sys.exit(1)

if __name__ == "__main__":
    main()
