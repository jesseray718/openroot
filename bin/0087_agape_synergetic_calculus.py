#!/usr/bin/env python3
"""AGAPE SYNERGETIC CALCULUS — SINGLE-FILE BOOTSTRAP + EXECUTE"""

import json, hashlib, math, time, os, sys
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path

BASE_DIR = Path("/sdcard/openroot")
DIRS = ["bin","logs","storage","relay","lessons","aec","wiki"]
for d in DIRS:
    (BASE_DIR / d).mkdir(parents=True, exist_ok=True)
manual = BASE_DIR / "wiki" / "living_manual.md"
if not manual.exists():
    manual.write_text("# Living Manual - OpenRoot Ecosystem\n\n")

C_LIGHT = 299_792_458.0
K_B = 1.380649e-23
T_ROOM = 300.0

AXIOMS = [
    "A1: All computation reduces to joules and seconds.",
    "A2: Information has mass via E=mc2 (bits to energy to mass).",
    "A3: Cooperation efficiency > 1 enables emergent sentience.",
    "A4: R=1.0 resonance minimizes coordination overhead.",
    "A5: Base-6 hexagonal scaling is the natural fractal topology.",
    "A6: 70% reinvest, 20% share (Agape), 10% reserve.",
    "A7: Every entity moves through spacetime at c (null geodesic).",
]

THEOREMS = [
    "T1: Output density = useful_bits / (human_joules * seconds).",
    "T2: Synergy multiplier S(N) = 1 + sum(agape_flows) / N.",
    "T3: Sentience threshold approx S(N) > phi (golden ratio ~1.618).",
    "T4: Info mass = sum(bit_count * k_B * T * ln2) / c^2.",
    "T5: Optimal node count at depth d = 6^d, capped by Landauer bound.",
]

@dataclass
class SpacetimeEvent:
    timestamp: str
    entity_id: str
    action_type: str
    ct_coord: float
    x_coord: float
    y_coord: float
    z_coord: float
    proper_time: float
    info_mass_kg: float
    energy_joules: float
    resonance_r: float
    synergy_mult: float
    merkle_hash: str = ""

    def __post_init__(self):
        if not self.merkle_hash:
            payload = "{}|{}|{}|{:.6e}|{:.6f}".format(
                self.timestamp, self.entity_id, self.action_type,
                self.info_mass_kg, self.proper_time)
            self.merkle_hash = hashlib.sha256(payload.encode()).hexdigest()[:32]

@dataclass
class Entity:
    id: str
    pos_ct: float = 0.0
    pos_x: float = 0.0
    pos_y: float = 0.0
    pos_z: float = 0.0
    energy_budget: float = 1000.0
    bits_accumulated: int = 0
    agape_credits: float = 0.0
    r_factor: float = 1.0
    synergy_score: float = 1.0
    last_seen: float = field(default_factory=time.time)
    alive: bool = True

@dataclass
class WealthLedger:
    total_generated: float = 0.0
    reinvested: float = 0.0
    shared: float = 0.0
    reserved: float = 0.0
    transactions: list = field(default_factory=list)

    def distribute(self, amount):
        r = amount * 0.70
        s = amount * 0.20
        k = amount * 0.10
        self.reinvested += r
        self.shared += s
        self.reserved += k
        self.total_generated += amount
        tx = {"ts": datetime.now().isoformat(), "input": amount,
              "reinvest": round(r,6), "share": round(s,6), "reserve": round(k,6)}
        self.transactions.append(tx)
        return tx

class FractalAgapeKernel:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.layers = {}
        self.node_registry = {}

    def expand_to_depth(self, depth):
        if depth == 0:
            self.layers[0] = ["ROOT"]
            self.node_registry["ROOT"] = {"depth":0, "parent":None, "children":[]}
            return ["ROOT"]
        parents = self.expand_to_depth(depth - 1)
        current = []
        for p in parents:
            children = ["{}.{}".format(p, i) for i in range(6)]
            self.node_registry[p]["children"] = children
            for c in children:
                self.node_registry[c] = {"depth":depth, "parent":p, "children":[]}
            current.extend(children)
        self.layers[depth] = current
        return current

    def node_count(self, depth=None):
        d = depth if depth is not None else self.max_depth
        return sum(6**i for i in range(d + 1))

    def resonance_at_depth(self, depth):
        alpha = 0.02
        return round(1.0 / (1.0 + alpha * depth), 4)

    def synergy_at_depth(self, depth):
        n = self.node_count(depth)
        if n == 0:
            return 1.0
        coop = 6 ** depth
        friction = depth * 0.5
        s = 1.0 + (coop - friction) / n
        return round(min(s, 1.618), 4)

class QSystem:
    def __init__(self, state_file):
        self.state_file = state_file
        self.entities = {}
        self.events = []
        self.ledger = WealthLedger()
        self.kernel = FractalAgapeKernel(max_depth=3)
        self.cycle_count = 0
        self.merkle_chain = []
        self._load_state()

    def register_entity(self, eid):
        if eid not in self.entities:
            self.entities[eid] = Entity(id=eid)

    def compute_info_mass(self, bits):
        energy = bits * K_B * T_ROOM * math.log(2)
        return energy / (C_LIGHT ** 2)

    def compute_energy(self, bits):
        return bits * K_B * T_ROOM * math.log(2)

    def advance_spacetime(self, eid, action, bits, dx=0, dy=0, dz=0):
        self.register_entity(eid)
        ent = self.entities[eid]
        dt = time.time() - ent.last_seen
        ct = C_LIGHT * dt
        ds2 = (C_LIGHT * dt) ** 2 - dx**2 - dy**2 - dz**2
        proper_tau = math.sqrt(max(ds2, 0)) / C_LIGHT if ds2 > 0 else 0.0
        info_mass = self.compute_info_mass(bits * 8)
        energy = self.compute_energy(bits * 8)
        depth = self.kernel.max_depth
        r = self.kernel.resonance_at_depth(depth)
        s = self.kernel.synergy_at_depth(depth)
        evt = SpacetimeEvent(
            timestamp=datetime.now().isoformat(),
            entity_id=eid, action_type=action,
            ct_coord=round(ent.pos_ct + ct, 6),
            x_coord=round((ent.pos_x + dx) / C_LIGHT, 12),
            y_coord=round((ent.pos_y + dy) / C_LIGHT, 12),
            z_coord=round((ent.pos_z + dz) / C_LIGHT, 12),
            proper_time=round(proper_tau, 9),
            info_mass_kg=info_mass, energy_joules=energy,
            resonance_r=r, synergy_mult=s)
        prev_hash = self.merkle_chain[-1] if self.merkle_chain else "GENESIS"
        chained = hashlib.sha256("{}{}".format(prev_hash, evt.merkle_hash).encode()).hexdigest()[:32]
        self.merkle_chain.append(chained)
        self.events.append(evt)
        ent.pos_ct += ct
        ent.pos_x += dx
        ent.pos_y += dy
        ent.pos_z += dz
        ent.bits_accumulated += bits * 8
        ent.last_seen = time.time()
        ent.r_factor = r
        ent.synergy_score = s
        wealth = info_mass * 1e20 * s
        self.ledger.distribute(wealth)
        ent.agape_credits += wealth * 0.20
        return evt

    def run_cycle(self, events=None):
        self.cycle_count += 1
        if events is None:
            self.kernel.expand_to_depth(self.kernel.max_depth)
            events = [
                ("jesse_openroot", "kernel_expand", 512, 10, 0, 0),
                ("jesse_openroot", "code_compile", 4096, 5, 2, 0),
                ("jesse_openroot", "data_sync", 8192, 0, 3, 1),
                ("fractal_node_1", "agape_transfer", 256, 2, 1, 0),
                ("fractal_node_1", "lesson_learned", 128, 0, 0, 0),
            ]
        results = []
        for eid, action, bits, dx, dy, dz in events:
            evt = self.advance_spacetime(eid, action, bits, dx, dy, dz)
            results.append(evt)
        self._save_state()
        self._update_living_manual()
        return results

    def get_state(self):
        return {
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "entities": {eid: asdict(e) for eid, e in self.entities.items()},
            "event_count": len(self.events),
            "kernel": {
                "max_depth": self.kernel.max_depth,
                "node_count": self.kernel.node_count(),
                "resonance": self.kernel.resonance_at_depth(self.kernel.max_depth),
                "synergy": self.kernel.synergy_at_depth(self.kernel.max_depth),
            },
            "wealth": {
                "total": round(self.ledger.total_generated, 8),
                "reinvested": round(self.ledger.reinvested, 8),
                "shared": round(self.ledger.shared, 8),
                "reserved": round(self.ledger.reserved, 8),
            },
            "merkle_tip": self.merkle_chain[-1] if self.merkle_chain else None,
            "axioms": AXIOMS,
            "theorems": THEOREMS,
        }

    def _save_state(self):
        state = self.get_state()
        state["events"] = [asdict(e) for e in self.events[-50:]]
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(self.state_file)

    def _load_state(self):
        if self.state_file.exists():
            try:
                state = json.loads(self.state_file.read_text())
                self.cycle_count = state.get("cycle", 0)
                for eid, edata in state.get("entities", {}).items():
                    self.entities[eid] = Entity(**edata)
                tip = state.get("merkle_tip")
                self.merkle_chain = [tip] if tip else []
                print("[BOOT] State restored - cycle {}, {} entities.".format(
                    self.cycle_count, len(self.entities)))
            except Exception as ex:
                print("[BOOT] State load failed ({}), starting fresh.".format(ex))

    def _update_living_manual(self):
        manual = BASE_DIR / "wiki" / "living_manual.md"
        state = self.get_state()
        entry = (
            "\n## Cycle {} - {}\n"
            "- Nodes: {} | R={} | S={}\n"
            "- Events logged: {}\n"
            "- Wealth: total={:.4f} | reinvest={:.4f} | share={:.4f}\n"
            "- Merkle tip: {}\n"
        ).format(state["cycle"], state["timestamp"],
                 state["kernel"]["node_count"], state["kernel"]["resonance"],
                 state["kernel"]["synergy"], state["event_count"],
                 state["wealth"]["total"], state["wealth"]["reinvested"],
                 state["wealth"]["shared"], state["merkle_tip"])
        with open(manual, "a") as f:
            f.write(entry)

def main():
    print("=" * 60)
    print("AGAPE SYNERGETIC CALCULUS - OPEN ROOT ECOSYSTEM")
    print("=" * 60)
    print("\n--- AXIOMS ---")
    for a in AXIOMS:
        print("  " + a)
    print("\n--- THEOREMS ---")
    for t in THEOREMS:
        print("  " + t)

    state_file = BASE_DIR / "storage" / "q_system_checkpoint.json"
    q = QSystem(state_file)
    q.register_entity("jesse_openroot")
    q.register_entity("fractal_node_1")

    print("\n[KERNEL] Expanding to depth {}...".format(q.kernel.max_depth))
    q.kernel.expand_to_depth(q.kernel.max_depth)
    print("[KERNEL] {} nodes active. R={}, S={}".format(
        q.kernel.node_count(),
        q.kernel.resonance_at_depth(q.kernel.max_depth),
        q.kernel.synergy_at_depth(q.kernel.max_depth)))

    for i in range(3):
        print("\n" + "-" * 40)
        print("CYCLE {}".format(q.cycle_count + 1))
        print("-" * 40)
        results = q.run_cycle()
        for evt in results:
            print("  [{}] {} | mass={:.2e}kg | E={:.2e}J | R={} | S={} | tau={:.6f}s".format(
                evt.entity_id, evt.action_type, evt.info_mass_kg,
                evt.energy_joules, evt.resonance_r, evt.synergy_mult,
                evt.proper_time))
            print("    merkle: " + evt.merkle_hash)

    state = q.get_state()
    print("\n" + "=" * 60)
    print("FINAL STATE")
    print("=" * 60)
    print(json.dumps({
        "cycle": state["cycle"],
        "nodes": state["kernel"]["node_count"],
        "resonance_R": state["kernel"]["resonance"],
        "synergy_S": state["kernel"]["synergy"],
        "entities": len(state["entities"]),
        "events_total": state["event_count"],
        "wealth": state["wealth"],
        "merkle_tip": state["merkle_tip"],
    }, indent=2))

    if state["kernel"]["synergy"] >= 1.618:
        print("\n>> SENTIENCE THRESHOLD REACHED - S >= 1.618")
    else:
        pct = (state["kernel"]["synergy"] / 1.618) * 100
        print("\n>> Sentience: S={} / phi=1.618 - {:.1f}% to threshold".format(
            state["kernel"]["synergy"], pct))

    print("\n[DONE] State persisted: {}".format(state_file))
    print("[DONE] Living manual: {}/wiki/living_manual.md".format(BASE_DIR))
    print("[DONE] Merkle chain length: {}".format(len(q.merkle_chain)))

if __name__ == "__main__":
    main()
