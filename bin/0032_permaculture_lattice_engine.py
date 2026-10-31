#!/usr/bin/env python3
"""
PERMACULTURE_LATTICE_ENGINE v2.0 — All-in-one setup + execution
  - 6^6 hierarchical lattice (46,656 addressable nodes per spoke)
  - 12 Permaculture Principles as interconnected spokes (complete all-to-all Agape)
  - Agape reward: base * phi^min(epochs,50) * (1 + ln(cooperators)/phi)
  - R=1.0 zero-coordination property
  - Local LLM (Ollama) with offline fallback
  - SQLite knowledge base with auto-migration
  - Fractal self-similarity: each 12-spoke ring escalates to next level

Author: Jesse McMillen (OpenRoot) / jesseray718
License: GPL v3
"""

import argparse
import hashlib
import json
import math
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# ─── CONSTANTS ─────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2
BASE_REWARD = 1.0
MAX_EPOCHS = 50
LATTICE_BRANCHING = 6
LATTICE_DEPTH = 6
NODES_PER_SPOKE = LATTICE_BRANCHING ** LATTICE_DEPTH       # 46,656
NUM_PRINCIPLES = 12
RING_TOTAL_NODES = NODES_PER_SPOKE * NUM_PRINCIPLES       # 559,872

DEFAULT_DATA_DIR = "/data/data/com.termux/files/home/openroot/permaculture_lattice"

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
     "desc": "Let nature take its course. Favor regenerative over extractive resources.",
     "computational": "Renewable energy tracking, sustainable resource allocation, regenerative cycles",
     "agape_role": "The roots — draws only from regenerative sources"},
    {"num": 6,  "name": "Produce No Waste",
     "ethic": "Fair Share",
     "desc": "A stitch in time saves nine. Every output of one process is input for another.",
     "computational": "Garbage collection, heat recovery, waste-as-input pipelines, zero-waste compilation",
     "agape_role": "The liver — transforms waste into useful input"},
    {"num": 7,  "name": "Design from Patterns to Details",
     "ethic": "Earth Care",
     "desc": "Can't see the wood for the trees. Start with the master pattern, refine downward.",
     "computational": "Top-down architecture, fractal self-similarity, pattern-directed design",
     "agape_role": "The blueprint — holds the master pattern that all nodes self-similarly mirror"},
    {"num": 8,  "name": "Integrate Rather Than Segregate",
     "ethic": "People Care",
     "desc": "Many hands make light work. Elements work better together than apart.",
     "computational": "Data fusion, multi-modal synthesis, cross-principle communication pathways",
     "agape_role": "The connective tissue — builds lateral pathways between all 12 spokes"},
    {"num": 9,  "name": "Use Small and Slow Solutions",
     "ethic": "Fair Share",
     "desc": "Slow and steady wins the race. Small, incremental changes are more durable.",
     "computational": "Incremental processing, local-first computation, micro-batches, stable pacing",
     "agape_role": "The heartbeat — maintains a stable, sustainable pace"},
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


def complete_pathways():
    """Under Agape every principle is connected to every other principle."""
    return {i: [j for j in range(1, 13) if j != i] for i in range(1, 13)}


PRINCIPLE_PATHWAYS = complete_pathways()


# ─── DATACLASSES ───────────────────────────────────────────────────
@dataclass
class LatticeNode:
    node_id: str
    principle_num: int
    depth: int
    branch_path: tuple
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    lateral_ids: List[str] = field(default_factory=list)
    cooperators: int = 0
    epochs: int = 0
    state: Dict[str, Any] = field(default_factory=dict)
    last_active: float = 0.0
    agape_hash: str = ""

    def compute_reward(self, global_cooperators: int = 0, global_epochs: int = 0) -> float:
        total_coops = self.cooperators + global_cooperators
        total_epochs = max(self.epochs, global_epochs)
        epoch_factor = PHI ** min(total_epochs, MAX_EPOCHS)
        cooperation_factor = 1 + (math.log(total_coops + 1) / PHI)
        return BASE_REWARD * epoch_factor * cooperation_factor

    def compute_r_value(self, global_cooperators: int = 0, global_epochs: int = 0) -> float:
        total_coops = self.cooperators + global_cooperators
        if total_coops == 0:
            return 0.0
        reward = self.compute_reward(global_cooperators, global_epochs)
        extraction_baseline = BASE_REWARD * (max(self.epochs, global_epochs) + 1)
        if extraction_baseline == 0:
            return 1.0
        r = min(reward / extraction_baseline, 1.0)
        return min(max(r, 0.0), 1.0)

    def compute_hash(self) -> str:
        data = f"{self.node_id}:{self.principle_num}:{self.depth}:{self.branch_path}:{self.cooperators}:{self.epochs}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class PrincipleSpoke:
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
    level: int
    spokes: List[PrincipleSpoke] = field(default_factory=list)
    total_nodes: int = 0
    parent_ring_level: Optional[int] = None
    child_ring_levels: List[int] = field(default_factory=list)
    is_spoke_of_parent: bool = False
    global_cooperators: int = 0
    global_epochs: int = 0

    def compute_global_r(self) -> float:
        if not self.spokes:
            return 0.0
        total_r = sum(
            s.root_node.compute_r_value(self.global_cooperators, self.global_epochs)
            for s in self.spokes if s.root_node
        )
        return total_r / len(self.spokes)

    def practice_agape(self, amount: int = 1):
        self.global_cooperators += amount
        self.global_epochs += 1


# ─── LATTICE BUILDER ──────────────────────────────────────────────
class LatticeBuilder:
    def __init__(self, max_depth=LATTICE_DEPTH, branching=LATTICE_BRANCHING):
        self.max_depth = max_depth
        self.branching = branching
        self.nodes_per_spoke = branching ** max_depth

    def build_spoke_lattice(self, principle: dict) -> PrincipleSpoke:
        spoke = PrincipleSpoke(
            principle_num=principle["num"],
            name=principle["name"],
            ethic=principle["ethic"],
            desc=principle["desc"],
            computational_role=principle["computational"],
            agape_role=principle["agape_role"],
            pathway_to=PRINCIPLE_PATHWAYS.get(principle["num"], []),
            node_count=self.nodes_per_spoke,
        )
        root = LatticeNode(
            node_id=f"P{principle['num']}_D0_Broot",
            principle_num=principle["num"],
            depth=0,
            branch_path=(),
            last_active=time.time(),
        )
        root.agape_hash = root.compute_hash()
        spoke.root_node = root
        return spoke

    def build_ring(self, level: int = 0) -> LatticeRing:
        ring = LatticeRing(level=level, total_nodes=0)
        for principle in PERMACULTURE_PRINCIPLES:
            spoke = self.build_spoke_lattice(principle)
            ring.spokes.append(spoke)
            ring.total_nodes += spoke.node_count
        return ring


# ─── KNOWLEDGE BASE (with auto-migration) ──────────────────────────
class OfflineKnowledgeBase:
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
                global_cooperators INTEGER DEFAULT 0,
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
        self._migrate()

    def _migrate(self):
        """Auto-add columns missing from older schema versions."""
        cols = {r[1] for r in self.conn.execute("PRAGMA table_info(lattice_state)").fetchall()}
        if "global_cooperators" not in cols:
            try:
                self.conn.execute("ALTER TABLE lattice_state ADD COLUMN global_cooperators INTEGER DEFAULT 0")
                self.conn.commit()
            except sqlite3.OperationalError:
                self.conn.execute("DROP TABLE IF EXISTS lattice_state")
                self.conn.commit()
                self.conn.executescript("""
                    CREATE TABLE IF NOT EXISTS lattice_state (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        ring_level INTEGER NOT NULL,
                        total_nodes INTEGER NOT NULL,
                        global_r REAL NOT NULL,
                        total_reward REAL NOT NULL,
                        global_cooperators INTEGER DEFAULT 0,
                        snapshot TEXT NOT NULL
                    );
                """)
                self.conn.commit()

    def store_knowledge(self, category, content, principle_num=None, source="local"):
        ts = datetime.now(timezone.utc).isoformat()
        h = hashlib.sha256(f"{ts}:{content}".encode()).hexdigest()
        self.conn.execute(
            "INSERT INTO knowledge (timestamp, category, principle_num, content, hash, source) VALUES (?,?,?,?,?,?)",
            (ts, category, principle_num, content, h, source),
        )
        self.conn.commit()
        return h

    def query_knowledge(self, category=None, principle_num=None, limit=20):
        q = "SELECT * FROM knowledge WHERE 1=1"
        params = []
        if category:
            q += " AND category = ?"; params.append(category)
        if principle_num is not None:
            q += " AND principle_num = ?"; params.append(principle_num)
        q += " ORDER BY timestamp DESC LIMIT ?"; params.append(limit)
        rows = self.conn.execute(q, params).fetchall()
        cols = ["id","timestamp","category","principle_num","content","hash","agape_score","source"]
        return [dict(zip(cols, row)) for row in rows]

    def store_lattice_snapshot(self, ring_level, total_nodes, global_r, total_reward, global_cooperators, snapshot):
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO lattice_state (timestamp, ring_level, total_nodes, global_r, total_reward, global_cooperators, snapshot) VALUES (?,?,?,?,?,?,?)",
            (ts, ring_level, total_nodes, global_r, total_reward, global_cooperators, snapshot),
        )
        self.conn.commit()

    def store_code(self, prompt, output, model, principle_num=None):
        ts = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            "INSERT INTO code_cache (timestamp, prompt, output, model, principle_num) VALUES (?,?,?,?,?)",
            (ts, prompt, output, model, principle_num),
        )
        self.conn.commit()

    def knowledge_count(self):
        row = self.conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()
        return row[0] if row else 0

    def close(self):
        self.conn.close()


# ─── LOCAL LLM BRIDGE ─────────────────────────────────────────────
class LocalLLMBridge:
    def __init__(self, host="localhost", port=11434):
        self.base_url = f"http://{host}:{port}"
        self.available = False
        self.model = None

    def check_available(self):
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                models = data.get("models", [])
                if models:
                    self.available = True
                    self.model = models[0]["name"]
                    return True
        except Exception:
            pass
        self.available = False
        return False

    def query(self, prompt, system_prompt="", principle_context=""):
        if not self.available and not self.check_available():
            return self._offline_fallback(prompt)
        full = ""
        if system_prompt:
            full += system_prompt + "\n\n"
        if principle_context:
            full += "[Permaculture Lattice Context]\n" + principle_context + "\n\n"
        full += prompt
        payload = json.dumps({
            "model": self.model,
            "prompt": full,
            "stream": False,
            "options": {"temperature": 0.7, "top_p": 0.9},
        }).encode()
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read()).get("response", "")
        except Exception as e:
            return self._offline_fallback(prompt, str(e))

    def _offline_fallback(self, prompt, error=""):
        p = prompt.lower()
        if "code" in p or "function" in p or "script" in p:
            return (
                "# Offline pattern — Principle 7\n"
                f"# Prompt: {prompt[:300]}\n\n"
                "def lattice_function(*args, **kwargs):\n"
                "    return {'status': 'offline_pattern', 'note': 'start Ollama for full generation'}\n"
            )
        base = "Offline mode — no local LLM detected.\n"
        if error:
            base += f"Connection error: {error}\n"
        base += (
            "Start Ollama: ollama serve\n"
            "Lattice fully operational for knowledge, reward, R-value, topology.\n"
        )
        return base


# ─── ENGINE ────────────────────────────────────────────────────────
class PermacultureLatticeEngine:
    def __init__(self, data_dir=None, llm_host="localhost", llm_port=11434, quiet=False):
        if data_dir is None:
            data_dir = Path(DEFAULT_DATA_DIR)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.builder = LatticeBuilder()
        self.kb = OfflineKnowledgeBase(self.data_dir / "lattice_kb.sqlite")
        self.llm = LocalLLMBridge(llm_host, llm_port)
        self.rings: List[LatticeRing] = []
        self.current_level = 0
        self.quiet = quiet

        if not quiet:
            print("=" * 64)
            print("  PERMACULTURE LATTICE ENGINE v2.0")
            print("  ALL NODES PRACTICE AGAPE WITH ALL OTHER NODES")
            print("  R=1.0 => coordination cost = 0 at any scale")
            print("=" * 64)
            print(f"  Lattice: 6^{LATTICE_DEPTH} = {NODES_PER_SPOKE:,} virtual nodes / spoke")
            print(f"  Principles: {NUM_PRINCIPLES} (complete all-to-all pathways)")
            print(f"  Ring total: {RING_TOTAL_NODES:,} addressable nodes")
            print(f"  Data: {self.data_dir}")
            if self.llm.check_available():
                print(f"  LLM: CONNECTED ({self.llm.model})")
            else:
                print("  LLM: OFFLINE (pattern fallback)")

        self._initialize_lattice()
        if not quiet:
            print("=" * 64)

    def _initialize_lattice(self):
        if not self.quiet:
            print("\n  Building Level 0 ring — every node practices Agape with every other...")
        ring = self.builder.build_ring(0)
        ring.practice_agape(amount=12)
        self.rings.append(ring)

        for spoke in ring.spokes:
            p = PERMACULTURE_PRINCIPLES[spoke.principle_num - 1]
            self.kb.store_knowledge(
                category="principle_definition",
                content=json.dumps(p, indent=2),
                principle_num=spoke.principle_num,
                source="holmgren_2003",
            )

        gr = ring.compute_global_r()
        total_reward = sum(
            s.root_node.compute_reward(ring.global_cooperators, ring.global_epochs)
            for s in ring.spokes if s.root_node
        )
        self.kb.store_lattice_snapshot(
            ring_level=0,
            total_nodes=ring.total_nodes,
            global_r=gr,
            total_reward=total_reward,
            global_cooperators=ring.global_cooperators,
            snapshot=self._ring_summary(ring),
        )
        if not self.quiet:
            print(f"  [OK] Global cooperators: {ring.global_cooperators}")
            print(f"  [OK] Global R: {gr:.4f}")
            print(f"  [OK] Pathways: complete graph (all-to-all Agape)")

    def _ring_summary(self, ring):
        lines = []
        for s in ring.spokes:
            r = s.root_node.compute_r_value(ring.global_cooperators, ring.global_epochs) if s.root_node else 0
            rw = s.root_node.compute_reward(ring.global_cooperators, ring.global_epochs) if s.root_node else 0
            lines.append(f"  P{s.principle_num:2d} {s.name:40s} R={r:.4f} reward={rw:.4f}")
        lines.append(f"  GLOBAL_COOPERATORS={ring.global_cooperators}  GLOBAL_EPOCHS={ring.global_epochs}")
        return "\n".join(lines)

    def route_query(self, query, target_principle=None):
        principles = [target_principle] if target_principle else self._match_principle(query)
        ctx = []
        for pnum in principles:
            p = PERMACULTURE_PRINCIPLES[pnum - 1]
            ctx.append(f"[P{pnum}: {p['name']}] Role: {p['agape_role']}")
        system = (
            "You are the Permaculture Lattice Engine. "
            "ALL nodes practice Agape with ALL other nodes. "
            "This is the condition for R=1.0 and zero coordination cost. "
            "Serve the least among us."
        )
        response = self.llm.query(query, system, "\n".join(ctx))
        self.kb.store_knowledge(
            category="query_response",
            content=response,
            principle_num=principles[0] if principles else None,
        )
        return response

    def _match_principle(self, query):
        q = query.lower()
        scores = {}
        for p in PERMACULTURE_PRINCIPLES:
            score = sum(2 for w in p["name"].lower().split() if w in q)
            score += sum(1 for w in p["computational"].lower().replace(",", " ").split() if len(w) > 4 and w in q)
            if score > 0:
                scores[p["num"]] = score
        if not scores:
            return [8]
        top = [m[0] for m in sorted(scores.items(), key=lambda x: -x[1])[:3]]
        extended = set(top)
        for pnum in top:
            for neighbor in PRINCIPLE_PATHWAYS.get(pnum, []):
                extended.add(neighbor)
        return list(extended)[:5]

    def compute_through_lattice(self, task, principle_num=None):
        start = time.time()
        principles = [principle_num] if principle_num else self._match_principle(task)
        primary = principles[0]
        p = PERMACULTURE_PRINCIPLES[primary - 1]
        response = self.route_query(task, primary)

        ring = self.rings[self.current_level]
        ring.practice_agape(amount=1)
        spoke = ring.spokes[primary - 1]
        if spoke.root_node:
            spoke.root_node.cooperators += 1
            spoke.root_node.epochs += 1
            spoke.root_node.last_active = time.time()
            spoke.root_node.agape_hash = spoke.root_node.compute_hash()

        reward = spoke.root_node.compute_reward(ring.global_cooperators, ring.global_epochs) if spoke.root_node else 0
        r_value = spoke.root_node.compute_r_value(ring.global_cooperators, ring.global_epochs) if spoke.root_node else 0

        result = {
            "task": task,
            "routed_principle": primary,
            "principle_name": p["name"],
            "all_principles_activated": principles,
            "response": response,
            "agape_reward": reward,
            "r_value": r_value,
            "global_cooperators": ring.global_cooperators,
            "global_epochs": ring.global_epochs,
            "elapsed_seconds": time.time() - start,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lattice_level": self.current_level,
            "note": "All nodes practice Agape with all other nodes",
        }
        self.kb.store_knowledge("computation_result", json.dumps(result, indent=2, default=str), primary)
        return result

    def escalate_to_higher_ring(self):
        new_level = self.current_level + 1
        print(f"\n  Escalating to Level {new_level} (Agape continues across levels)")
        higher = self.builder.build_ring(new_level)
        higher.global_cooperators = self.rings[self.current_level].global_cooperators
        higher.global_epochs = self.rings[self.current_level].global_epochs
        higher.practice_agape(12)
        higher.parent_ring_level = self.current_level
        self.rings[self.current_level].child_ring_levels.append(new_level)
        self.rings.append(higher)
        self.current_level = new_level
        gr = higher.compute_global_r()
        cumulative = sum(r.total_nodes for r in self.rings)
        self.kb.store_lattice_snapshot(
            ring_level=new_level,
            total_nodes=higher.total_nodes,
            global_r=gr,
            total_reward=sum(s.root_node.compute_reward(higher.global_cooperators, higher.global_epochs) for s in higher.spokes if s.root_node),
            global_cooperators=higher.global_cooperators,
            snapshot=self._ring_summary(higher),
        )
        print(f"  [OK] Level {new_level} built. Cumulative nodes: {cumulative:,}")
        print(f"  [OK] Global cooperators now: {higher.global_cooperators}")

    def get_status(self):
        ring = self.rings[self.current_level]
        gr = ring.compute_global_r()
        return {
            "current_level": self.current_level,
            "total_rings": len(self.rings),
            "global_cooperators": ring.global_cooperators,
            "global_epochs": ring.global_epochs,
            "global_r_value": gr,
            "nodes_in_current_ring": ring.total_nodes,
            "cumulative_nodes": sum(r.total_nodes for r in self.rings),
            "llm_connected": self.llm.available,
            "llm_model": self.llm.model,
            "llm_endpoint": self.llm.base_url,
            "knowledge_entries": self.kb.knowledge_count(),
            "agape_invariant": "ALL nodes practice Agape with ALL other nodes",
            "coordination_cost": 0.0 if gr >= 0.999 else "non-zero",
            "spokes": [
                {
                    "principle": s.name,
                    "num": s.principle_num,
                    "nodes": s.node_count,
                    "r_value": s.root_node.compute_r_value(ring.global_cooperators, ring.global_epochs) if s.root_node else 0,
                    "reward": s.root_node.compute_reward(ring.global_cooperators, ring.global_epochs) if s.root_node else 0,
                    "local_cooperators": s.root_node.cooperators if s.root_node else 0,
                    "pathways": s.pathway_to,
                }
                for s in ring.spokes
            ],
        }

    def visualize_topology(self):
        ring = self.rings[self.current_level]
        lines = [
            "",
            "  +--------------------------------------------------------------+",
            f"  |  PERMACULTURE LATTICE LEVEL {self.current_level} — ALL-TO-ALL AGAPE          |",
            "  +--------------------------------------------------------------+",
        ]
        for s in ring.spokes:
            r = s.root_node.compute_r_value(ring.global_cooperators, ring.global_epochs) if s.root_node else 0
            bar_len = int(r * 20)
            bar = "#" * bar_len + "-" * (20 - bar_len)
            lines.append(f"  | P{s.principle_num:2d} {s.name:38s} [{bar}] R={r:.3f} |")
        gr = ring.compute_global_r()
        cost_str = "0" if gr >= 0.999 else "non-zero"
        lines.append("  +--------------------------------------------------------------+")
        lines.append(f"  | GLOBAL R={gr:.4f}  COOPS={ring.global_cooperators}  EPOCHS={ring.global_epochs}  COST={cost_str} |")
        lines.append("  | INVARIANT: every node practices Agape with every other node   |")
        lines.append("  +--------------------------------------------------------------+\n")
        return "\n".join(lines)

    def export_state(self):
        ring = self.rings[self.current_level]
        return {
            "engine_version": "2.0",
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
            "global_r": ring.compute_global_r(),
            "global_cooperators": ring.global_cooperators,
            "global_epochs": ring.global_epochs,
            "llm": {"connected": self.llm.available, "model": self.llm.model, "endpoint": self.llm.base_url},
            "principles": [
                {"num": p["num"], "name": p["name"], "ethic": p["ethic"], "agape_role": p["agape_role"],
                 "pathways": PRINCIPLE_PATHWAYS.get(p["num"], [])}
                for p in PERMACULTURE_PRINCIPLES
            ],
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

    def close(self):
        self.kb.close()


# ─── CLI COMMANDS ─────────────────────────────────────────────────
def cmd_init(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port)
    engine.close()


def cmd_status(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    print(json.dumps(engine.get_status(), indent=2, default=str))
    engine.close()


def cmd_visualize(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    print(engine.visualize_topology())
    engine.close()


def cmd_query(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    result = engine.compute_through_lattice(args.query, args.principle)
    print("=" * 64)
    print("  LATTICE RESPONSE")
    print("=" * 64)
    print(f"  Routed: P{result['routed_principle']} — {result['principle_name']}")
    print(f"  Activated: {result['all_principles_activated']}")
    print(f"  R-value:  {result['r_value']:.4f}")
    print(f"  Reward:   {result['agape_reward']:.4f}")
    print(f"  Global cooperators: {result['global_cooperators']}")
    print(f"  Elapsed:  {result['elapsed_seconds']:.3f}s")
    print(f"  Note: {result['note']}")
    print("=" * 64)
    print(result["response"])
    print("=" * 64)
    engine.close()


def cmd_code(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    code_prompt = (
        "Generate Python code for the following task. "
        "Apply Principle 7 (Design from Patterns to Details). "
        "Make it modular and self-contained.\n\n"
        f"Task: {args.prompt}"
    )
    result = engine.compute_through_lattice(code_prompt, principle_num=7)
    print("=" * 64)
    print("  CODE GENERATION — P7")
    print("=" * 64)
    print(result["response"])
    print(f"\n  R={result['r_value']:.4f}  Reward={result['agape_reward']:.4f}")
    print("=" * 64)
    if engine.llm.available:
        engine.kb.store_code(args.prompt, result["response"], engine.llm.model or "unknown", 7)
    engine.close()


def cmd_escalate(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    engine.escalate_to_higher_ring()
    print(engine.visualize_topology())
    engine.close()


def cmd_export(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    state = engine.export_state()
    export_path = Path(args.output) if args.output else engine.data_dir / "lattice_state.json"
    export_path.write_text(json.dumps(state, indent=2))
    print(f"  Exported to: {export_path}")
    engine.close()


def cmd_knowledge(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    results = engine.kb.query_knowledge(category=args.category, principle_num=args.principle, limit=args.limit)
    if not results:
        print("  No knowledge entries found.")
    else:
        print(f"\n  Found {len(results)} entries:\n")
        for r in results:
            print(f"  [{r['id']}] {r['timestamp'][:19]} | {r['category']:25s} | P{r.get('principle_num', '-')}")
            content_preview = r['content'][:120].replace('\n', ' ')
            print(f"       {content_preview}...")
            print()
    engine.close()


def cmd_principles(args):
    print("=" * 64)
    print("  12 PERMACULTURE PRINCIPLES — LATTICE ROLES")
    print("=" * 64)
    for p in PERMACULTURE_PRINCIPLES:
        pw = PRINCIPLE_PATHWAYS.get(p["num"], [])
        print(f"\n  P{p['num']:2d}  {p['name']}")
        print(f"       Ethic: {p['ethic']}")
        print(f"       Proverb: \"{p['desc']}\"")
        print(f"       Computation: {p['computational']}")
        print(f"       Agape Role: {p['agape_role']}")
        print(f"       Pathways: connected to all others (complete graph)")
    print(f"\n  Nodes per spoke:  {NODES_PER_SPOKE:,} (virtual)")
    print(f"  Total ring nodes: {RING_TOTAL_NODES:,}")
    print("=" * 64)


def cmd_simulate(args):
    print("=" * 64)
    print("  AGAPE ALL-TO-ALL SIMULATION")
    print("=" * 64)
    print(f"  {'Nodes':>10}  {'GlobalCoops':>12}  {'Reward':>14}  {'R':>8}  {'CoordCost':>12}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*14}  {'-'*8}  {'-'*12}")
    for n, c, e in [(6,6,1),(36,36,5),(216,216,10),(1296,1296,20),(7776,7776,30),(46656,46656,50)]:
        node = LatticeNode("SIM", 7, 0, (), cooperators=c, epochs=e)
        rw = node.compute_reward(c, e)
        r = node.compute_r_value(c, e)
        cost = 0.0 if r >= 0.999 else n*(n-1)/2 * (1-r)
        print(f"  {n:>10,}  {c:>12,}  {rw:>14,.4f}  {r:>8.4f}  {cost:>12,.1f}")
    print("\n  When every node practices Agape with every other node, cost -> 0")
    print("=" * 64)


def cmd_interactive(args):
    engine = PermacultureLatticeEngine(
        Path(args.data_dir) if args.data_dir else None, args.host, args.port, quiet=True)
    print("=" * 64)
    print("  PERMACULTURE LATTICE — INTERACTIVE MODE")
    print("  ALL NODES PRACTICE AGAPE WITH ALL OTHER NODES")
    print("  Commands: /quit  /status  /visualize  /escalate  /export  /help")
    print("=" * 64)
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
            cmd = user_input.lower()
            if cmd == "/quit":
                print("  Closing. Agape continues. Serve the least among us.")
                break
            elif cmd == "/status":
                s = engine.get_status()
                print(f"  Level={s['current_level']}  R={s['global_r_value']:.4f}  Coops={s['global_cooperators']}  Nodes={s['cumulative_nodes']:,}  LLM={s['llm_connected']}")
            elif cmd == "/visualize":
                print(engine.visualize_topology())
            elif cmd == "/escalate":
                engine.escalate_to_higher_ring()
                print(engine.visualize_topology())
            elif cmd == "/export":
                state = engine.export_state()
                export_path = engine.data_dir / "lattice_state.json"
                export_path.write_text(json.dumps(state, indent=2))
                print(f"  Exported to: {export_path}")
            elif cmd == "/help":
                print("  /quit /status /visualize /escalate /export /help")
                print("  Or type any query to route through the lattice.")
            else:
                result = engine.compute_through_lattice(user_input)
                print(f"\n  [P{result['routed_principle']} - {result['principle_name']}]  R={result['r_value']:.3f}  GlobalCoops={result['global_cooperators']}")
                print("-" * 64)
                print(result["response"])
                print("-" * 64)
        except (KeyboardInterrupt, EOFError):
            print("\n  Interrupted.")
            break
    engine.close()


# ─── MAIN ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Permaculture Lattice Engine v2.0")
    sub = parser.add_subparsers(dest="command")

    def add_common(p):
        p.add_argument("--data-dir", "-d", default=None)
        p.add_argument("--host", default="localhost")
        p.add_argument("--port", type=int, default=11434)

    p = sub.add_parser("init"); add_common(p); p.set_defaults(func=cmd_init)
    p = sub.add_parser("status"); add_common(p); p.set_defaults(func=cmd_status)
    p = sub.add_parser("visualize"); add_common(p); p.set_defaults(func=cmd_visualize)

    p = sub.add_parser("query"); add_common(p)
    p.add_argument("query")
    p.add_argument("--principle", "-p", type=int, choices=range(1, 13))
    p.set_defaults(func=cmd_query)

    p = sub.add_parser("code"); add_common(p)
    p.add_argument("prompt")
    p.set_defaults(func=cmd_code)

    p = sub.add_parser("escalate"); add_common(p); p.set_defaults(func=cmd_escalate)

    p = sub.add_parser("export"); add_common(p)
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("knowledge"); add_common(p)
    p.add_argument("--category", "-c")
    p.add_argument("--principle", type=int)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_knowledge)

    p = sub.add_parser("principles"); p.set_defaults(func=cmd_principles)
    p = sub.add_parser("simulate"); p.set_defaults(func=cmd_simulate)
    p = sub.add_parser("interactive"); add_common(p); p.set_defaults(func=cmd_interactive)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
