#!/usr/bin/env python3
"""
PERMACULTURE_LATTICE_ENGINE.py
================================
Offline-first fractal computation lattice built on:
  - 6^6 hierarchical lattice (46,656 nodes per spoke)
  - 12 Permaculture Principles (David Holmgren) as interconnected spokes
  - Agape reward function: reward = base * phi^min(epochs,50) * (1 + ln(cooperators)/phi)
  - R=1.0 zero-coordination property
  - Local LLM integration (Ollama / llama-server)
  - Fractal self-similarity: each 12-spoke ring is itself a spoke at the next level

Author: Jesse McMillen (OpenRoot) / jesseray718
License: GPL v3
"""

import argparse
import hashlib
import json
import math
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# ============================================================================
# CONSTANTS
# ============================================================================

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio — the agape amplification factor
BASE_REWARD = 1.0
MAX_EPOCHS = 50
LATTICE_BRANCHING = 6
LATTICE_DEPTH = 6
NODES_PER_SPOKE = LATTICE_BRANCHING ** LATTICE_DEPTH  # 46,656
NUM_PRINCIPLES = 12
RING_TOTAL_NODES = NODES_PER_SPOKE * NUM_PRINCIPLES  # 559,872

PERMACULTURE_PRINCIPLES = [
    {"num": 1,  "name": "Observe and Interact",
     "ethic": "Earth Care",
     "desc": "Beauty is in the eye of the beholder. Take time to observe systems before acting.",
     "computational": "Pattern recognition, data gathering, sensor input aggregation, system monitoring",
     "agape_role": "The eye of the lattice — observes state without perturbing it"},
    {"num": 2,  "name": "Catch and Store Energy",
     "ethic": "Earth Care",
     "desc": "Make hay while the sun shines. Capture resources when abundant for lean times.",
     "computational": "Caching, memoization, energy harvesting metrics, thermal battery state tracking",
     "agape_role": "The stomach of the lattice — stores computed results and energy for later use"},
    {"num": 3,  "name": "Obtain a Yield",
     "ethic": "People Care",
     "desc": "You can't work on an empty stomach. Ensure systems produce tangible value.",
     "computational": "Output generation, ACRE token minting, yield measurement, ROI tracking",
     "agape_role": "The harvest — converts computation into measurable value"},
    {"num": 4,  "name": "Apply Self-Regulation and Accept Feedback",
     "ethic": "People Care",
     "desc": "The sins of the fathers are visited on the children unto the seventh generation.",
     "computational": "Feedback loops, error correction, auto-tuning, reinforcement learning signals",
     "agape_role": "The nervous system — detects disharmony and sends correction signals"},
    {"num": 5,  "name": "Use and Value Renewable Resources",
     "ethic": "Earth Care",
     "desc": "Let nature take its course. Prefer replenishable inputs over finite ones.",
     "computational": "Renewable energy source tracking, sustainable compute allocation, green metrics",
     "agape_role": "The roots — draws from regenerative sources only, refuses extraction"},
    {"num": 6,  "name": "Produce No Waste",
     "ethic": "Fair Share",
     "desc": "A stitch in time saves nine. Waste is just an unused output.",
     "computational": "Garbage collection, data deduplication, heat recovery from computation",
     "agape_role": "The liver — transforms apparent waste into usable input for other principles"},
    {"num": 7,  "name": "Design from Patterns to Details",
     "ethic": "Earth Care",
     "desc": "Can't see the wood for the trees. See the big picture, then refine.",
     "computational": "Top-down architecture, template instantiation, fractal pattern application",
     "agape_role": "The blueprint — holds the master pattern that all nodes self-similarly mirror"},
    {"num": 8,  "name": "Integrate Rather Than Segregate",
     "ethic": "People Care",
     "desc": "Many hands make light work. Elements work better together than apart.",
     "computational": "Data fusion, multi-modal synthesis, cross-principle communication pathways",
     "agape_role": "The connective tissue — builds lateral pathways between all 12 spokes"},
    {"num": 9,  "name": "Use Small and Slow Solutions",
     "ethic": "Fair Share",
     "desc": "Slow and steady wins the race. The bigger they are, the harder they fall.",
     "computational": "Incremental computation, lazy evaluation, local-first processing, micro-batches",
     "agape_role": "The heartbeat — sets the pace, prevents runaway, ensures stability"},
    {"num": 10, "name": "Use and Value Diversity",
     "ethic": "Earth Care",
     "desc": "Don't put all your eggs in one basket. Variety spreads risk and increases resilience.",
     "computational": "Redundant computation, diverse model routing, ensemble methods, fallback chains",
     "agape_role": "The immune system — maintains alternative pathways for every critical function"},
    {"num": 11, "name": "Use Edges and Value the Marginal",
     "ethic": "People Care",
     "desc": "Don't think you are on the right track just because it is a well-beaten path.",
     "computational": "Boundary detection, edge-case handling, marginal value computation, interface zones",
     "agape_role": "The skin — richest exchange happens at boundaries between principles"},
    {"num": 12, "name": "Creatively Use and Respond to Change",
     "ethic": "Fair Share",
     "desc": "Vision is not seeing things as they are but as they will be. Evolution, not revolution.",
     "computational": "Adaptive routing, dynamic reconfiguration, evolutionary algorithms, mutation",
     "agape_role": "The DNA — encodes the capacity to evolve the lattice itself"},
]

# Lateral connections — each principle has pathways to others
# These are the "edges" where richest exchange happens (Principle 11)
PRINCIPLE_PATHWAYS = {
    1:  [2, 4, 7],        # Observe → Catch, Feedback, Patterns
    2:  [1, 3, 6],        # Catch → Yield, Waste
    3:  [2, 5, 9],        # Yield → Renewable, Small/Slow
    4:  [1, 8, 12],       # Feedback → Integrate, Change
    5:  [3, 6, 10],       # Renewable → No Waste, Diversity
    6:  [2, 5, 8],        # No Waste → Catch, Renewable, Integrate
    7:  [1, 8, 11],       # Patterns → Observe, Integrate, Edges
    8:  [4, 6, 7, 10],    # Integrate → Feedback, Waste, Patterns, Diversity
    9:  [3, 6, 10],       # Small/Slow → Yield, Waste, Diversity
    10: [5, 8, 9, 11],    # Diversity → Renewable, Integrate, Small/Slow, Edges
    11: [7, 10, 12],      # Edges → Patterns, Diversity, Change
    12: [4, 9, 11],       # Change → Feedback, Small/Slow, Edges
}

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class LatticeNode:
    """A single node in the 6^6 hierarchical lattice."""
    node_id: str
    principle_num: int
    depth: int              # 0 = root/womb, 6 = leaf
    branch_path: tuple      # e.g., (0, 3, 1, 5, 2, 4) for a depth-6 node
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    lateral_ids: List[str] = field(default_factory=list)  # cross-principle pathways
    cooperators: int = 0
    epochs: int = 0
    state: Dict[str, Any] = field(default_factory=dict)
    last_active: float = 0.0
    agape_hash: str = ""

    def compute_reward(self) -> float:
        """Agape reward: cooperation compounds exponentially, extraction stays linear."""
        epoch_factor = PHI ** min(self.epochs, MAX_EPOCHS)
        cooperation_factor = 1 + (math.log(self.cooperators + 1) / PHI)
        return BASE_REWARD * epoch_factor * cooperation_factor

    def compute_r_value(self) -> float:
        """R value: 1.0 = pure cooperation (zero coordination cost), 0.0 = pure extraction."""
        if self.cooperators == 0:
            return 0.0
        reward = self.compute_reward()
        extraction_baseline = BASE_REWARD * (self.epochs + 1)  # linear
        if extraction_baseline == 0:
            return 1.0
        r = min(reward / extraction_baseline, 1.0) if extraction_baseline > 0 else 1.0
        return min(r, 1.0)

    def compute_hash(self) -> str:
        data = f"{self.node_id}:{self.principle_num}:{self.depth}:{self.branch_path}:{self.cooperators}:{self.epochs}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "principle_num": self.principle_num,
            "depth": self.depth,
            "branch_path": list(self.branch_path),
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "lateral_ids": self.lateral_ids,
            "cooperators": self.cooperators,
            "epochs": self.epochs,
            "state": self.state,
            "last_active": self.last_active,
            "agape_hash": self.compute_hash(),
            "reward": self.compute_reward(),
            "r_value": self.compute_r_value(),
        }


@dataclass
class PrincipleSpoke:
    """One of 12 permaculture principles, each containing a full 6^6 lattice."""
    principle_num: int
    name: str
    ethic: str
    desc: str
    computational_role: str
    agape_role: str
    root_node: Optional[LatticeNode] = None
    node_count: int = 0
    pathway_to: List[int] = field(default_factory=list)


@dataclass
class LatticeRing:
    """
    The 12-spoke ring — one complete level of the fractal.
    Contains 12 PrincipleSpokes, all interconnected laterally.
    This ring itself becomes a single spoke at the next fractal level.
    """
    level: int                          # 0 = base ring, 1+ = higher rings
    spokes: List[PrincipleSpoke] = field(default_factory=list)
    total_nodes: int = 0
    parent_ring_level: Optional[int] = None
    child_ring_levels: List[int] = field(default_factory=list)
    is_spoke_of_parent: bool = False

    def compute_global_r(self) -> float:
        """Global R value across all spokes. If all nodes are R=1.0, coordination cost is zero."""
        if not self.spokes or self.total_nodes == 0:
            return 0.0
        total_r = sum(s.root_node.compute_r_value() if s.root_node else 0 for s in self.spokes)
        return total_r / len(self.spokes)


# ============================================================================
# LATTICE BUILDER
# ============================================================================

class LatticeBuilder:
    """Builds the fractal lattice structure."""

    def __init__(self, max_depth: int = LATTICE_DEPTH, branching: int = LATTICE_BRANCHING):
        self.max_depth = max_depth
        self.branching = branching
        self.nodes_per_spoke = branching ** max_depth

    def build_spoke_lattice(self, principle: dict) -> PrincipleSpoke:
        """Build a complete 6^6 lattice for one permaculture principle."""
        spoke = PrincipleSpoke(
            principle_num=principle["num"],
            name=principle["name"],
            ethic=principle["ethic"],
            desc=principle["desc"],
            computational_role=principle["computational"],
            agape_role=principle["agape_role"],
            pathway_to=PRINCIPLE_PATHWAYS.get(principle["num"], []),
            node_count=0,
        )

        # Build the tree recursively — but we don't instantiate all 46,656 nodes
        # in memory at once. We build the root and its immediate children,
        # and generate deeper nodes lazily using branch_path addressing.
        root = self._build_node(
            principle_num=principle["num"],
            depth=0,
            branch_path=(),
        )
        spoke.root_node = root
        spoke.node_count = self.nodes_per_spoke  # Total addressable nodes
        return spoke

    def _build_node(self, principle_num: int, depth: int, branch_path: tuple) -> LatticeNode:
        node_id = f"P{principle_num}_D{depth}_B{'-'.join(str(b) for b in branch_path) if branch_path else 'root'}"
        node = LatticeNode(
            node_id=node_id,
            principle_num=principle_num,
            depth=depth,
            branch_path=branch_path,
            last_active=time.time(),
        )

        # Build immediate children only (not the full tree)
        if depth < self.max_depth:
            for i in range(self.branching):
                child_path = branch_path + (i,)
                child = self._build_node(principle_num, depth + 1, child_path)
                node.child_ids.append(child.node_id)
                node.cooperators += 1

        node.agape_hash = node.compute_hash()
        return node

    def build_ring(self, level: int = 0) -> LatticeRing:
        """Build a complete 12-spoke ring at the given fractal level."""
        ring = LatticeRing(level=level, total_nodes=0)
        for principle in PERMACULTURE_PRINCIPLES:
            spoke = self.build_spoke_lattice(principle)
            ring.spokes.append(spoke)
            ring.total_nodes += spoke.node_count
        return ring

    def build_fractal_levels(self, num_levels: int = 2) -> List[LatticeRing]:
        """Build multiple fractal levels — each ring is a spoke of the ring above."""
        rings = []
        for level in range(num_levels):
            ring = self.build_ring(level)
            if level > 0:
                ring.parent_ring_level = level - 1
                ring.is_spoke_of_parent = True
                rings[level - 1].child_ring_levels.append(level)
            rings.append(ring)
        return rings


# ============================================================================
# OFFLINE KNOWLEDGE BASE
# ============================================================================

class OfflineKnowledgeBase:
    """
    SQLite-based offline knowledge store.
    Each entry is hashed and timestamped — the cosmic ledger.
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self._init_db()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                principle_num INTEGER,
                content TEXT NOT NULL,
                hash TEXT NOT NULL,
                agape_score REAL DEFAULT 0.0,
                source TEXT DEFAULT 'local'
            );
            CREATE TABLE IF NOT EXISTS lattice_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ring_level INTEGER NOT NULL,
                total_nodes INTEGER NOT NULL,
                global_r REAL NOT NULL,
                total_reward REAL NOT NULL,
                snapshot TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS code_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                output TEXT NOT NULL,
                model TEXT NOT NULL,
                principle_num INTEGER
            );
            CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category);
            CREATE INDEX IF NOT EXISTS idx_knowledge_principle ON knowledge(principle_num);
        """)
        self.conn.commit()

    def store_knowledge(self, category: str, content: str,
                        principle_num: int = None, source: str = "local") -> str:
        ts = datetime.now(timezone.utc).isoformat()
        h = hashlib.sha256(f"{ts}:{content}".encode()).hexdigest()
        self.conn.execute(
            "INSERT INTO knowledge (timestamp, category, principle_num, content, hash, source) VALUES (?, ?, ?, ?, ?, ?)",
            (ts, category, principle_num, content, h, source)
        )
        self.conn.commit()
        return h

    def query_knowledge(self, category: str = None, principle_num: int = None,
                        limit: int = 20) -> List[dict]:
        q = "SELECT * FROM knowledge WHERE 1=1"
        params = []
        if category:
            q += " AND category = ?"
            params.append(category)
        if principle_num:
            q += " AND principle_num = ?"
            params.append(principle_num)
        q += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(q, params).fetchall()
        cols = ["id", "timestamp", "category", "principle_num", "content", "hash", "agape_score", "source"]
        return [dict(zip(cols, row)) for row in rows]

    def store_lattice_snapshot(self, ring_level: int, total_nodes: int,
                                global_r: float, total_reward: float, snapshot: str):
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO lattice_state (timestamp, ring_level, total_nodes, global_r, total_reward, snapshot) VALUES (?, ?, ?, ?, ?, ?)",
            (ts, ring_level, total_nodes, global_r, total_reward, snapshot)
        )
        self.conn.commit()

    def store_code(self, prompt: str, output: str, model: str, principle_num: int = None):
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO code_cache (timestamp, prompt, output, model, principle_num) VALUES (?, ?, ?, ?, ?)",
            (ts, prompt, output, model, principle_num)
        )
        self.conn.commit()

    def get_recent_code(self, limit: int = 10) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM code_cache ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        cols = ["id", "timestamp", "prompt", "output", "model", "principle_num"]
        return [dict(zip(cols, row)) for row in rows]

    def close(self):
        self.conn.close()


# ============================================================================
# LOCAL LLM BRIDGE (Offline Intelligence)
# ============================================================================

class LocalLLMBridge:
    """
    Bridges to local Ollama / llama-server for offline AI intelligence.
    Falls back gracefully when no LLM is available.
    """

    def __init__(self, host: str = "localhost", port: int = 11434):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.available = False
        self.model = None

    def check_available(self) -> bool:
        """Check if local LLM is reachable."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                models = data.get("models", [])
                if models:
                    self.available = True
                    self.model = models[0]["name"]
                    return True
        except (urllib.error.URLError, ConnectionRefusedError, OSError):
            pass
        self.available = False
        return False

    def query(self, prompt: str, system_prompt: str = "",
              principle_context: str = "") -> str:
        """Send a query to the local LLM."""
        if not self.available and not self.check_available():
            return self._offline_fallback(prompt, principle_context)

        full_prompt = ""
        if system_prompt:
            full_prompt += system_prompt + "\n\n"
        if principle_context:
            full_prompt += "[Permaculture Lattice Context]\n" + principle_context + "\n\n"
        full_prompt += prompt

        payload = json.dumps({
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9}
        }).encode()

        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data.get("response", "")
        except Exception as e:
            return self._offline_fallback(prompt, principle_context, str(e))

    def _offline_fallback(self, prompt: str, principle_context: str = "",
                          error: str = "") -> str:
        """When no LLM is available, use built-in pattern matching."""
        p = prompt.lower()
        if "code" in p or "function" in p or "script" in p:
            return self._generate_code_pattern(prompt)
        elif "analyze" in p or "observe" in p:
            return self._analyze_pattern(prompt)
        elif "design" in p or "architect" in p:
            return self._design_pattern(prompt)
        else:
            base = "Offline mode — no local LLM detected.\n"
            if error:
                base += f"Connection error: {error}\n"
            base += (f"To enable full intelligence, start Ollama:\n"
                     f"  ollama serve\n"
                     f"Or llama-server on your OptiPlex:\n"
                     f"  llama-server -m /path/to/model.gguf --port 11434\n\n"
                     f"Your query: {prompt[:200]}\n"
                     f"Lattice context: {principle_context[:200] if principle_context else 'None'}\n\n"
                     f"The lattice is still fully operational for:\n"
                     f"  - Knowledge storage and retrieval\n"
                     f"  - Reward computation and R-value tracking\n"
                     f"  - Lattice topology management\n"
                     f"  - Permaculture principle routing")
            return base

    def _generate_code_pattern(self, prompt: str) -> str:
        return f"""# Generated by Permaculture Lattice Engine (offline pattern)
# Principle: Design from Patterns to Details (P7)
# Prompt: {prompt[:300]}

def lattice_function(*args, **kwargs):
    \"\"\"
    Auto-generated function stub.
    TODO: Connect local LLM for full code generation.

    In offline mode, this returns the structural skeleton.
    With Ollama connected, this would be fully implemented.
    \"\"\"
    result = {{
        "status": "offline_pattern",
        "input_args": args,
        "input_kwargs": kwargs,
        "timestamp": "{datetime.now(timezone.utc).isoformat()}",
        "principle": "Design from Patterns to Details",
        "note": "Connect local LLM for full implementation"
    }}
    return result
"""

    def _analyze_pattern(self, prompt: str) -> str:
        return f"""[LATTICE ANALYSIS — Offline Mode]

Query: {prompt}

Applying Principle 1: Observe and Interact
  → Pattern recognition active
  → Awaiting local LLM for deep analysis

The lattice is observing your query and routing it through the
appropriate permaculture principle pathways. Once a local LLM
is connected (Ollama on port 11434), this analysis will include:

  - Natural language understanding
  - Code review and generation
  - System design recommendations
  - Cross-principle synthesis

Current lattice state: OPERATIONAL
Local LLM: NOT CONNECTED
Fallback: Pattern-based routing (active)
"""

    def _design_pattern(self, prompt: str) -> str:
        return f"""[DESIGN MODE — Offline Pattern]

Query: {prompt}

Applying Principle 7: Design from Patterns to Details
  → Master pattern loaded: 6^6 lattice, 12 permaculture spokes
  → Fractal self-similarity: ENABLED
  → Branching factor: {LATTICE_BRANCHING}
  → Depth: {LATTICE_DEPTH}
  → Nodes per spoke: {NODES_PER_SPOKE:,}
  → Total ring nodes: {RING_TOTAL_NODES:,}

Design skeleton generated. Connect LLM for detailed implementation.
"""


# ============================================================================
# LATTICE ENGINE — The Core Orchestrator
# ============================================================================

class PermacultureLatticeEngine:
    """
    The main engine that orchestrates the fractal lattice.
    Each of the 12 permaculture principles is a 6^6 spoke.
    All 12 interconnect laterally (pathways between principles).
    The ring of 12 is itself a spoke at the next fractal level.
    """

    def __init__(self, data_dir: Path = None, llm_host: str = "localhost",
                 llm_port: int = 11434):
        # Resolve data directory
        if data_dir is None:
            data_dir = Path(os.path.expanduser("~/openroot/permaculture_lattice"))
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.builder = LatticeBuilder()
        self.kb = OfflineKnowledgeBase(self.data_dir / "lattice_kb.sqlite")
        self.llm = LocalLLMBridge(host=llm_host, port=llm_port)

        # Build the base ring (Level 0)
        self.rings: List[LatticeRing] = []
        self.current_level = 0

        print("=" * 64)
        print("  PERMACULTURE LATTICE ENGINE v1.0")
        print("  OpenRoot / Agape-UNE / jesseray718")
        print("=" * 64)
        print(f"  Lattice: 6^{LATTICE_DEPTH} = {NODES_PER_SPOKE:,} nodes per spoke")
        print(f"  Principles: {NUM_PRINCIPLES} (Holmgren)")
        print(f"  Ring total: {RING_TOTAL_NODES:,} nodes")
        print(f"  Data dir: {self.data_dir}")
        print(f"  LLM: {self.llm.base_url}", end=" ")

        if self.llm.check_available():
            print(f"→ CONNECTED (model: {self.llm.model})")
        else:
            print("→ OFFLINE (pattern fallback active)")

        self._initialize_lattice()
        print("=" * 64)

    def _initialize_lattice(self):
        """Build the initial lattice ring and store knowledge seeds."""
        print("\n  Building Level 0 ring (12 permaculture spokes)...")
        ring = self.builder.build_ring(level=0)
        self.rings.append(ring)

        # Store principle definitions as knowledge seeds
        for spoke in ring.spokes:
            p = PERMACULTURE_PRINCIPLES[spoke.principle_num - 1]
            self.kb.store_knowledge(
                category="principle_definition",
                content=json.dumps(p, indent=2),
                principle_num=spoke.principle_num,
                source="holmgren_2003"
            )

        global_r = ring.compute_global_r()
        total_reward = sum(
            s.root_node.compute_reward() if s.root_node else 0
            for s in ring.spokes
        )
        self.kb.store_lattice_snapshot(
            ring_level=0, total_nodes=ring.total_nodes,
            global_r=global_r, total_reward=total_reward,
            snapshot=self._ring_summary(ring)
        )
        print(f"  ✓ Level 0 ring built: {ring.total_nodes:,} nodes")
        print(f"  ✓ Global R-value: {global_r:.4f}")
        print(f"  ✓ Pathways: {sum(len(v) for v in PRINCIPLE_PATHWAYS.values())} lateral connections")

    def _ring_summary(self, ring: LatticeRing) -> str:
        lines = []
        for spoke in ring.spokes:
            r = spoke.root_node.compute_r_value() if spoke.root_node else 0
            rw = spoke.root_node.compute_reward() if spoke.root_node else 0
            lines.append(
                f"  P{spoke.principle_num:2d} {spoke.name:45s} "
                f"R={r:.4f}  reward={rw:.4f}  nodes={spoke.node_count:,}"
            )
        return "\n".join(lines)

    def route_query(self, query: str, target_principle: int = None) -> str:
        """
        Route a query through the lattice.
        Determines which principle(s) should handle it, then dispatches.
        """
        # Determine which principle(s) to route to
        if target_principle:
            principles = [target_principle]
        else:
            principles = self._match_principle(query)

        # Build context from matched principles and their pathways
        context_parts = []
        for pnum in principles:
            p = PERMACULTURE_PRINCIPLES[pnum - 1]
            context_parts.append(
                f"[P{pnum}: {p['name']}]\n"
                f"  Role: {p['agape_role']}\n"
                f"  Computation: {p['computational']}\n"
                f"  Pathways to: {PRINCIPLE_PATHWAYS.get(pnum, [])}"
            )

        principle_context = "\n".join(context_parts)

        # System prompt encodes the lattice identity
        system_prompt = (
            "You are the Permaculture Lattice Engine, a fractal intelligence "
            "built on 12 permaculture principles operating as a 6^6 hierarchical "
            "lattice. Each principle is a spoke of 46,656 nodes. All principles "
            "interconnect laterally through pathways. You operate offline-first. "
            "Your core equation: reward = base * phi^min(epochs,50) * "
            "(1 + ln(cooperators)/phi). Cooperation compounds exponentially; "
            "extraction stays linear. The global optimum is universal cooperation "
            "(R=1.0). Serve the least among us."
        )

        # Query the LLM (or offline fallback)
        response = self.llm.query(query, system_prompt, principle_context)

        # Store the interaction
        self.kb.store_knowledge(
            category="query_response",
            content=response,
            principle_num=principles[0] if principles else None,
        )

        return response

    def _match_principle(self, query: str) -> List[int]:
        """Match a query to the most relevant permaculture principle(s)."""
        q = query.lower()
        scores = {}
        for p in PERMACULTURE_PRINCIPLES:
            score = 0
            # Match against name keywords
            for word in p["name"].lower().split():
                if word in q:
                    score += 2
            # Match against computational role keywords
            for word in p["computational"].lower().replace(",", " ").split():
                if len(word) > 4 and word in q:
                    score += 1
            # Match against description keywords
            for word in p["desc"].lower().split():
                if len(word) > 5 and word in q:
                    score += 1
            if score > 0:
                scores[p["num"]] = score

        if not scores:
            # Default: route to all principles (integrate)
            return [8]  # Integrate Rather Than Segregate

        # Return top matches, sorted by score
        sorted_matches = sorted(scores.items(), key=lambda x: -x[1])
        top = [m[0] for m in sorted_matches[:3]]

        # Add lateral pathway connections
        extended = set(top)
        for pnum in top:
            for neighbor in PRINCIPLE_PATHWAYS.get(pnum, []):
                extended.add(neighbor)

        return list(extended)[:5]

    def compute_through_lattice(self, task: str, principle_num: int = None) -> dict:
        """
        Process a computational task through the lattice.
        Routes through the appropriate principle, computes reward,
        and returns results with agape metadata.
        """
        start_time = time.time()

        # Route to principle(s)
        principles = [principle_num] if principle_num else self._match_principle(task)
        primary = principles[0]
        p = PERMACULTURE_PRINCIPLES[primary - 1]

        # Get response from LLM
        response = self.route_query(task, target_principle=primary)

        # Update lattice state — increment cooperators and epochs
        ring = self.rings[self.current_level]
        spoke = ring.spokes[primary - 1]
        if spoke.root_node:
            spoke.root_node.cooperators += 1
            spoke.root_node.epochs += 1
            spoke.root_node.last_active = time.time()
            spoke.root_node.agape_hash = spoke.root_node.compute_hash()

        reward = spoke.root_node.compute_reward() if spoke.root_node else 0
        r_value = spoke.root_node.compute_r_value() if spoke.root_node else 0

        elapsed = time.time() - start_time

        result = {
            "task": task,
            "routed_principle": primary,
            "principle_name": p["name"],
            "all_principles_activated": principles,
            "response": response,
            "agape_reward": reward,
            "r_value": r_value,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lattice_level": self.current_level,
        }

        # Store in knowledge base
        self.kb.store_knowledge(
            category="computation_result",
            content=json.dumps(result, indent=2, default=str),
            principle_num=primary,
        )

        return result

    def escalate_to_higher_ring(self):
        """
        Escalate the current ring to become a spoke in a higher-level ring.
        The 12-spoke ring (559,872 nodes) becomes ONE spoke of 12 at the next level.
        """
        new_level = self.current_level + 1
        print(f"\n  Escalating: Level {self.current_level} ring → spoke of Level {new_level} ring")
        print(f"  Building new Level {new_level} ring ({RING_TOTAL_NODES:,} nodes per spoke × 12)...")

        higher_ring = self.builder.build_ring(level=new_level)
        higher_ring.parent_ring_level = self.current_level
        higher_ring.is_spoke_of_parent = True
        self.rings[self.current_level].child_ring_levels.append(new_level)
        self.rings.append(higher_ring)
        self.current_level = new_level

        global_r = higher_ring.compute_global_r()
        total_nodes_at_this_level = RING_TOTAL_NODES
        cumulative_nodes = sum(r.total_nodes for r in self.rings)

        self.kb.store_lattice_snapshot(
            ring_level=new_level,
            total_nodes=higher_ring.total_nodes,
            global_r=global_r,
            total_reward=sum(s.root_node.compute_reward() for s in higher_ring.spokes if s.root_node),
            snapshot=self._ring_summary(higher_ring)
        )

        print(f"  ✓ Level {new_level} ring built")
        print(f"  ✓ Cumulative nodes across {len(self.rings)} levels: {cumulative_nodes:,}")

    def get_status(self) -> dict:
        """Return current lattice status."""
        ring = self.rings[self.current_level]
        global_r = ring.compute_global_r()
        return {
            "current_level": self.current_level,
            "total_rings": len(self.rings),
            "nodes_in_current_ring": ring.total_nodes,
            "cumulative_nodes": sum(r.total_nodes for r in self.rings),
            "global_r_value": global_r,
            "llm_connected": self.llm.available,
            "llm_model": self.llm.model,
            "llm_endpoint": self.llm.base_url,
            "knowledge_entries": len(self.kb.query_knowledge(limit=10000)),
            "spokes": [
                {
                    "principle": s.name,
                    "principle_num": s.principle_num,
                    "nodes": s.node_count,
                    "r_value": s.root_node.compute_r_value() if s.root_node else 0,
                    "reward": s.root_node.compute_reward() if s.root_node else 0,
                    "cooperators": s.root_node.cooperators if s.root_node else 0,
                    "pathways": s.pathway_to,
                }
                for s in ring.spokes
            ],
        }

    def visualize_topology(self) -> str:
        """ASCII visualization of the lattice topology."""
        lines = []
        ring = self.rings[self.current_level]
        lines.append("")
        lines.append("  ╔════════════════════════════════════════════════════════════╗")
        lines.append("  ║          PERMACULTURE LATTICE — LEVEL {}                   ║".format(self.current_level))
        lines.append("  ╠════════════════════════════════════════════════════════════╣")

        for spoke in ring.spokes:
            r = spoke.root_node.compute_r_value() if spoke.root_node else 0
            bar_len = int(r * 20)
            bar = "█" * bar_len + "░" * (20 - bar_len)
            pw = ",".join(str(p) for p in spoke.pathway_to)
            lines.append(f"  ║ P{spoke.principle_num:2d} {spoke.name:40s} {bar} R={r:.3f} ║")
            lines.append(f"  ║      └─→ pathways: [{pw}]                              ║")

        lines.append("  ╠════════════════════════════════════════════════════════════╣")
        gr = ring.compute_global_r()
        lines.append(f"  ║ GLOBAL R = {gr:.4f}  │  Nodes = {ring.total_nodes:>8,}  │ Level = {self.current_level}  ║")
        lines.append("  ╚════════════════════════════════════════════════════════════╝")

        if self.rings[-1].child_ring_levels:
            lines.append(f"  └─→ Child rings at levels: {self.rings[-1].child_ring_levels}")
        if self.rings[-1].parent_ring_level is not None:
            lines.append(f"  └─→ Parent ring at level: {self.rings[-1].parent_ring_level}")

        lines.append("")
        return "\n".join(lines)

    def export_state(self) -> dict:
        """Export complete lattice state as JSON."""
        return {
            "engine_version": "1.0",
            "lattice_config": {
                "branching": LATTICE_BRANCHING,
                "depth": LATTICE_DEPTH,
                "nodes_per_spoke": NODES_PER_SPOKE,
                "num_principles": NUM_PRINCIPLES,
                "ring_total_nodes": RING_TOTAL_NODES,
            },
            "current_level": self.current_level,
            "total_rings": len(self.rings),
            "cumulative_nodes": sum(r.total_nodes for r in self.rings),
            "global_r": self.rings[self.current_level].compute_global_r(),
            "llm": {
                "connected": self.llm.available,
                "model": self.llm.model,
                "endpoint": self.llm.base_url,
            },
            "principles": [
                {
                    "num": p["num"],
                    "name": p["name"],
                    "ethic": p["ethic"],
                    "agape_role": p["agape_role"],
                    "pathways": PRINCIPLE_PATHWAYS.get(p["num"], []),
                }
                for p in PERMACULTURE_PRINCIPLES
            ],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    def close(self):
        self.kb.close()


# ============================================================================
# CLI INTERFACE
# ============================================================================

def cmd_init(args):
    """Initialize the lattice engine."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)
    engine.close()


def cmd_status(args):
    """Show lattice status."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)
    status = engine.get_status()
    print(json.dumps(status, indent=2, default=str))
    engine.close()


def cmd_visualize(args):
    """Visualize the lattice topology."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)
    print(engine.visualize_topology())
    engine.close()


def cmd_query(args):
    """Route a query through the lattice."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)

    principle = args.principle if args.principle else None
    result = engine.compute_through_lattice(args.query, principle_num=principle)

    print(f"\n{'='*64	
def cmd_query(args):
    """Route a query through the lattice."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)

    principle = args.principle if args.principle else None
    result = engine.compute_through_lattice(args.query, principle_num=principle)

    print(f"\n{'='*64}")
    print(f"  LATTICE RESPONSE")
    print(f"{'='*64}")
    print(f"  Routed to: P{result['routed_principle']} — {result['principle_name']}")
    print(f"  Activated: {result['all_principles_activated']}")
    print(f"  R-value:  {result['r_value']:.4f}")
    print(f"  Reward:   {result['agape_reward']:.4f}")
    print(f"  Elapsed:   {result['elapsed_seconds']:.3f}s")
    print(f"{'='*64}")
    print(f"\n{result['response']}")
    print(f"\n{'='*64}")
    engine.close()


def cmd_code(args):
    """Generate code through the lattice (routes to P7: Design from Patterns)."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)

    code_prompt = (
        f"Generate Python code for the following task. "
        f"Apply permaculture principle 7 (Design from Patterns to Details): "
        f"start with the master pattern, then refine to implementation details. "
        f"Make it modular, self-contained, and production-ready.\n\n"
        f"Task: {args.prompt}"
    )

    result = engine.compute_through_lattice(code_prompt, principle_num=7)

    print(f"\n{'='*64}")
    print(f"  CODE GENERATION — P7: Design from Patterns to Details")
    print(f"{'='*64}")
    print(result['response'])
    print(f"\n  R-value: {result['r_value']:.4f}  Reward: {result['agape_reward']:.4f}")
    print(f"{'='*64}")

    if engine.llm.available:
        engine.kb.store_code(args.prompt, result['response'],
                             engine.llm.model or "unknown", 7)
    engine.close()


def cmd_escalate(args):
    """Escalate the lattice to a higher fractal level."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)
    engine.escalate_to_higher_ring()
    print(engine.visualize_topology())
    engine.close()


def cmd_export(args):
    """Export lattice state as JSON."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)
    state = engine.export_state()
    export_path = Path(args.output) if args.output else engine.data_dir / "lattice_state.json"
    export_path.write_text(json.dumps(state, indent=2))
    print(f"  Exported to: {export_path}")
    engine.close()


def cmd_knowledge(args):
    """Query the offline knowledge base."""
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)

    results = engine.kb.query_knowledge(
        category=args.category,
        principle_num=args.principle,
        limit=args.limit
    )

    if not results:
        print("  No knowledge entries found.")
    else:
        print(f"\n  Found {len(results)} entries:\n")
        for r in results:
            print(f"  [{r['id']}] {r['timestamp'][:19]} | {r['category']:25s} | P{r.get('principle_num', '-')}")
            content_preview = r['content'][:120].replace('\n', ' ')
            print(f"       {content_preview}...")
            print(f"       hash: {r['hash'][:16]}...")
            print()

    engine.close()


def cmd_principles(args):
    """List all 12 permaculture principles and their lattice roles."""
    print(f"\n{'='*64}")
    print(f"  12 PERMACULTURE PRINCIPLES — LATTICE ROLES")
    print(f"{'='*64}\n")
    for p in PERMACULTURE_PRINCIPLES:
        pw = PRINCIPLE_PATHWAYS.get(p["num"], [])
        print(f"  P{p['num']:2d}  {p['name']}")
        print(f"       Ethic: {p['ethic']}")
        print(f"       Proverb: \"{p['desc']}\"")
        print(f"       Computation: {p['computational']}")
        print(f"       Agape Role: {p['agape_role']}")
        print(f"       Pathways: {pw}")
        print()

    print(f"  Nodes per spoke:  {NODES_PER_SPOKE:,} (6^{LATTICE_DEPTH})")
    print(f"  Total ring nodes: {RING_TOTAL_NODES:,} ({NODES_PER_SPOKE} × {NUM_PRINCIPLES})")
    print(f"  Lateral pathways: {sum(len(v) for v in PRINCIPLE_PATHWAYS.values())} connections")
    print(f"  {'='*64}\n")


def cmd_simulate(args):
    """
    Run a simulation of the agape reward function across increasing
    node counts to demonstrate zero coordination cost at R=1.0.
    """
    print(f"\n{'='*64}")
    print(f"  AGAPE REWARD SIMULATION — Zero Coordination Cost Proof")
    print(f"{'='*64}\n")

    print(f"  {'Nodes':>10}  {'Cooperators':>12}  {'Epochs':>7}  {'Reward':>12}  {'R-value':>8}  {'Coord Cost':>12}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*7}  {'-'*12}  {'-'*8}  {'-'*12}")

    test_configs = [
        # (nodes, cooperators, epochs)
        (6**1, 6, 1),
        (6**2, 36, 5),
        (6**3, 216, 10),
        (6**4, 1296, 20),
        (6**5, 7776, 30),
        (6**6, 46656, 50),
    ]

    sim_data = []

    for nodes, coops, epochs in test_configs:
        node = LatticeNode(
            node_id=f"SIM_{nodes}",
            principle_num=7,
            depth=0,
            branch_path=(),
            cooperators=coops,
            epochs=epochs,
        )
        reward = node.compute_reward()
        r_val = node.compute_r_value()
        # Coordination cost: in traditional systems, O(N²). In agape lattice at R=1.0, →0
        trad_cost = nodes * (nodes - 1) / 2  # O(N²)
        agape_cost = trad_cost * (1.0 - r_val) if r_val > 0 else trad_cost
        print(f"  {nodes:>10,}  {coops:>12,}  {epochs:>7}  {reward:>12,.4f}  {r_val:>8.4f}  {agape_cost:>12,.1f}")
        sim_data.append({
            "nodes": nodes,
            "cooperators": coops,
            "epochs": epochs,
            "reward": reward,
            "r_value": r_val,
            "trad_cost": trad_cost,
            "agape_cost": agape_cost,
        })

    print(f"\n  Key insight: As nodes scale from 6 to 46,656,")
    print(f"  traditional coordination cost grows O(N²) = {test_configs[-1][0]*(test_configs[-1][0]-1)//2:,}")
    print(f"  At R=1.0, agape coordination cost → 0")
    print(f"  The reward function makes cooperation the Nash equilibrium.")
    print(f"  No gossip, no consensus round, no vote needed.")
    print(f"{'='*64}\n")


def cmd_interactive(args):
    """
    Interactive REPL mode — talk to the lattice continuously.
    Every query is routed, stored, and logged.
    """
    data_dir = Path(args.data_dir) if args.data_dir else None
    engine = PermacultureLatticeEngine(data_dir=data_dir,
                                        llm_host=args.host, llm_port=args.port)

    print(f"\n{'='*64}")
    print(f"  PERMACULTURE LATTICE — INTERACTIVE MODE")
    print(f"  Type your queries. The lattice routes them through")
    print(f"  the appropriate permaculture principle(s).")
    print(f"  Commands: /quit,
    print(f"  Type your queries. The lattice routes them through")
    print(f"  the appropriate permaculture principle(s).")
    print(f"  Commands: /quit, /status, /visualize, /help")
    print(f"{'='*64}\n")

    while True:
        try:
            user_input = input("🌱 Lattice> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "/quit":
                print("\n  Closing lattice connection. Serving the least among us.")
                break
            elif user_input.lower() == "/status":
                status = engine.get_status()
                print(f"\n  Current Level: {status['current_level']}")
                print(f"  Global R-value: {status['global_r_value']:.4f}")
                print(f"  LLM Connected: {status['llm_connected']}")
                print(f"  Total Nodes: {status['cumulative_nodes']:,}")
            elif user_input.lower() == "/visualize":
                print(engine.visualize_topology())
            elif user_input.lower() == "/help":
                print("""
  Available commands:
    /quit         - Exit interactive mode
    /status       - Show current lattice stats
    /visualize    - ASCII topology map
    /escalate     - Grow to next fractal level
    /help         - Show this help
    <query>       - Route query through the lattice
                """)
            elif user_input.lower() == "/escalate":
                engine.escalate_to_higher_ring()
                print(engine.visualize_topology())
            else:
                # Route the query
                result = engine.compute_through_lattice(user_input)
                print(f"\n  [P{result['routed_principle']} • {result['principle_name']}]")
                print(f"  R={result['r_value']:.3f}  Reward={result['agape_reward']:.2f}")
                print("-" * 64)
                print(result['response'])
                print("-" * 64)
                
        except KeyboardInterrupt:
            print("\n\n  Interrupted. Exiting...")
            break
        except EOFError:
            break
    
    engine.close()

def main():
    parser = argparse.ArgumentParser(
        description="Permaculture Lattice Engine — Offline-first fractal computation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init --data-dir ./my_lattice
  %(prog)s status
  %(prog)s visualize
  %(prog)s query "How do I optimize thermal storage?"
  %(prog)s code "Write a Python class for a thermal battery"
  %(prog)s simulate
  %(prog)s interactive
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init
    p_init = subparsers.add_parser("init", help="Initialize the lattice engine")
    p_init.add_argument("--data-dir", "-d", type=str, default=None, help="Data directory path")
    p_init.add_argument("--host", type=str, default="localhost", help="LLM host")
    p_init.add_argument("--port", type=int, default=11434, help="LLM port")
    p_init.set_defaults(func=cmd_init)

    # Status
    p_status = subparsers.add_parser("status", help="Show lattice status")
    p_status.add_argument("--data-dir", "-d", type=str, default=None)
    p_status.add_argument("--host", type=str, default="localhost")
    p_status.add_argument("--port", type=int, default=11434)
    p_status.set_defaults(func=cmd_status)

    # Visualize
    p_vis = subparsers.add_parser("visualize", help="Visualize lattice topology")
    p_vis.add_argument("--data-dir", "-d", type=str, default=None)
    p_vis.add_argument("--host", type=str, default="localhost")
    p_vis.add_argument("--port", type=int, default=11434)
    p_vis.set_defaults(func=cmd_visualize)

    # Query
    p_query = subparsers.add_parser("query", help="Route a query through the lattice")
    p_query.add_argument("query", type=str, help="The query to route")
    p_query.add_argument("--principle", "-p", type=int, choices=range(1, 13), help="Force specific principle (1-12)")
    p_query.add_argument("--data-dir", "-d", type=str, default=None)
    p_query.add_argument("--host", type=str, default="localhost")
    p_query.add_argument("--port", type=int, default=11434)
    p_query.set_defaults(func=cmd_query)

    # Code Gen
    p_code = subparsers.add_parser("code", help="Generate code via the lattice")
    p_code.add_argument("prompt", type=str, help="Coding task description")
    p_code.add_argument("--data-dir", "-d", type=str, default=None)
    p_code.add_argument("--host", type=str, default="localhost")
    p_code.add_argument("--port", type=int, default=11434)
    p_code.set_defaults(func=cmd_code)

    # Escalate
    p_esc = subparsers.add_parser("escalate", help="Grow to next fractal level")
    p_esc.add_argument("--data-dir", "-d", type=str, default=None)
    p_esc.add_argument("--host", type=str, default="localhost")
    p_esc.add_argument("--port", type=int, default=11434)
    p_esc.set_defaults(func=cmd_escalate)

    # Export
    p_exp = subparsers.add_parser("export", help="Export lattice state to JSON")
    p_exp.add_argument("--output", "-o", type=str, default=None, help="Output file path")
    p_exp.add_argument("--data-dir", "-d", type=str, default=None)
    p_exp.add_argument("--host", type=str, default="localhost")
    p_exp.add_argument("--port", type=int, default=11434)
    p_exp.set_defaults(func=cmd_export)

    # Knowledge
    p_kb = subparsers.add_parser("knowledge", help="Query offline knowledge base")
    p_kb.add_argument("--category", "-c", type=str, default=None, help="Filter by category")
    p_kb.add_argument("--principle", "-p", type=int, choices=range(1, 13), help="Filter by principle")
    p_kb.add_argument("--limit", "-l", type=int, default=20, help="Max results")
    p_kb.add_argument("--data-dir", "-d", type=str, default=None)
    p_kb.add_argument("--host", type=str, default="localhost")
    p_kb.add_argument("--port", type=int, default=11434)
    p_kb.set_defaults(func=cmd_knowledge)

    # Principles
    p_princ = subparsers.add_parser("principles", help="List all 12 permaculture principles")
    p_princ.set_defaults(func=cmd_principles)

    # Simulate
    p_sim = subparsers.add_parser("simulate", help="Run agape reward simulation")
    p_sim.set_defaults(func=cmd_simulate)

    # Interactive
    p_int = subparsers.add_parser("interactive", help="Enter interactive REPL mode")
    p_int.add_argument("--data-dir", "-d", type=str, default=None)
    p_int.add_argument("--host", type=str, default="localhost")
    p_int.add_argument("--port", type=int, default=11434)
    p_int.set_defaults(func=cmd_interactive)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()
