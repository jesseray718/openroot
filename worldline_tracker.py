#!/usr/bin/env python3
"""worldline_tracker.py - Track individual observer trajectories and timeline branches."""
import json, time, hashlib
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path("/home/jesse/openroot/data")
WORLDLINE_FILE = DATA_DIR / "worldlines.jsonl"
BRANCH_FILE = DATA_DIR / "branches.json"

class WorldlineTracker:
    """Track observer worldlines and branching timelines."""
    
    def __init__(self):
        self.worldlines = []
        self.branches = []
        if WORLDLINE_FILE.exists():
            self.worldlines = [json.loads(l) for l in WORLDLINE_FILE.read_text().splitlines() if l.strip()]
        if BRANCH_FILE.exists():
            self.branches = json.load(open(BRANCH_FILE))
    
    def record_observation(self, observer_id, event_type, coordinates, timestamp=None):
        """Record one point on an observer's worldline."""
        ts = timestamp or time.time()
        obs = {
            "observer_id": observer_id,
            "event_type": event_type,
            "coordinates": coordinates,
            "timestamp": ts,
            "hash": hashlib.sha256(f"{observer_id}:{event_type}:{ts}".encode()).hexdigest()[:16]
        }
        self.worldlines.append(obs)
        
        with WORLDLINE_FILE.open("a") as f:
            f.write(json.dumps(obs) + "\n")
        
        return obs
    
    def get_worldline(self, observer_id):
        """Return all observations for one observer."""
        return [o for o in self.worldlines if o["observer_id"] == observer_id]
    
    def create_branch(self, parent_observer, decision_point, outcome):
        """Record a timeline branch at decision point."""
        branch = {
            "branch_id": hashlib.sha256(f"{parent_observer}:{decision_point}".encode()).hexdigest()[:16],
            "parent_observer": parent_observer,
            "decision_point": decision_point,
            "outcome": outcome,
            "timestamp": time.time()
        }
        self.branches.append(branch)
        
        with open(BRANCH_FILE, "w") as f:
            json.dump(self.branches, f, indent=2)
        
        return branch
    
    def detect_interference(self, observer_a, observer_b):
        """Check if two observers' worldlines show interference patterns."""
        wa = self.get_worldline(observer_a)
        wb = self.get_worldline(observer_b)
        
        if not wa or not wb:
            return {"status": "INSUFFICIENT_DATA"}
        
        # Check for correlated events (same timestamps within tolerance)
        tol = 1.0  # second tolerance
        correlations = []
        for a in wa:
            for b in wb:
                if abs(a["timestamp"] - b["timestamp"]) < tol:
                    correlations.append({
                        "observer_a": a["event_type"],
                        "observer_b": b["event_type"],
                        "time_diff": abs(a["timestamp"] - b["timestamp"])
                    })
        
        return {
            "correlations_found": len(correlations),
            "sample": correlations[:5] if correlations else []
        }
    
    def standing_wave_analysis(self):
        """Analyze overall pattern as standing wave."""
        if not self.worldlines:
            return {"status": "NO_DATA"}
        
        # Aggregate by timestamp
        by_ts = defaultdict(list)
        for obs in self.worldlines:
            ts_bucket = int(obs["timestamp"] / 60)  # minute buckets
            by_ts[ts_bucket].append(obs)
        
        # Check periodicity
        counts = sorted([(ts, len(obs)) for ts, obs in by_ts.items()], key=lambda x: x[0])
        
        return {
            "total_observations": len(self.worldlines),
            "time_buckets": len(by_ts),
            "avg_per_minute": len(self.worldlines) / max(1, len(by_ts)),
            "pattern": "periodic" if len(counts) > 3 else "insufficient_data"
        }

if __name__ == "__main__":
    wt = WorldlineTracker()
    print("Worldline Tracker Loaded")
    print(f"Stored observations: {len(wt.worldlines)}")
    print(f"Branches recorded: {len(wt.branches)}")
    
    # Demo
    obs = wt.record_observation("demo_observer", "computation_event", {"x": 1, "y": 2, "t": time.time()})
    print(f"\nSample observation: {json.dumps(obs, indent=2)}")
    
    analysis = wt.standing_wave_analysis()
    print(f"\nStanding wave analysis: {json.dumps(analysis, indent=2)}")
