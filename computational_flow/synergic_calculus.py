#!/usr/bin/env python3
"""synergic_calculus.py - Track J_agape, η, log(time) for predictions."""
import json, math, time
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("/home/jesse/openroot/data")
DATA_DIR.mkdir(exist_ok=True)
LOG_FILE = DATA_DIR / "synergy_log.jsonl"
ANALYTICS = DATA_DIR / "analytics.json"

class SynergicCalculator:
    """Track cumulative Agape and efficiency over time."""
    
    def __init__(self):
        self.entries = []
        if LOG_FILE.exists():
            self.entries = [json.loads(l) for l in LOG_FILE.read_text().splitlines() if l.strip()]
    
    def log_entry(self, user_id, j_agape, j_total, efficiency, activity_type="general"):
        """Record one measurement point."""
        entry = {
            "timestamp": time.time(),
            "iso_time": datetime.now().isoformat(),
            "user_id": user_id,
            "j_agape": float(j_agape),
            "j_total": float(j_total),
            "efficiency": float(efficiency),
            "synergy": float(j_agape * efficiency * math.log(max(1, time.time()))),
            "activity_type": activity_type
        }
        self.entries.append(entry)
        
        with LOG_FILE.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def aggregate_by_user(self):
        """Calculate cumulative synergy per user."""
        from collections import defaultdict
        totals = defaultdict(lambda: {"j_agape": 0, "j_total": 0, "synergy": 0, "entries": 0})
        
        for e in self.entries:
            uid = e["user_id"]
            totals[uid]["j_agape"] += e["j_agape"]
            totals[uid]["j_total"] += e["j_total"]
            totals[uid]["synergy"] += e["synergy"]
            totals[uid]["entries"] += 1
        
        return dict(totals)
    
    def predict_collapse(self, user_id):
        """Estimate likelihood of 'collapse into standing wave' based on synergy growth."""
        user_entries = [e for e in self.entries if e["user_id"] == user_id]
        if len(user_entries) < 3:
            return {"status": "INSUFFICIENT_DATA", "entries_needed": 3, "have": len(user_entries)}
        
        # Calculate growth rate
        synergies = [e["synergy"] for e in user_entries]
        growth_rates = [(synergies[i+1] - synergies[i]) / max(1, i+1) for i in range(len(synergies)-1)]
        avg_growth = sum(growth_rates) / max(1, len(growth_rates))
        
        # Threshold heuristic (tunable)
        collapse_probability = min(0.95, max(0.05, 0.1 + avg_growth * 0.5))
        
        return {
            "user_id": user_id,
            "total_entries": len(user_entries),
            "final_synergy": synergies[-1],
            "avg_growth_rate": avg_growth,
            "collapse_probability": collapse_probability,
            "interpretation": "HIGH" if collapse_probability > 0.7 else "MEDIUM" if collapse_probability > 0.4 else "LOW"
        }
    
    def system_wide_stats(self):
        """Aggregate statistics across all users."""
        total_agape = sum(e["j_agape"] for e in self.entries)
        total_energy = sum(e["j_total"] for e in self.entries)
        total_synergy = sum(e["synergy"] for e in self.entries)
        avg_efficiency = sum(e["efficiency"] for e in self.entries) / max(1, len(self.entries))
        
        return {
            "total_entries": len(self.entries),
            "total_j_agape": total_agape,
            "total_j_total": total_energy,
            "overall_efficiency": avg_efficiency,
            "cumulative_synergy": total_synergy,
            "unique_users": len(set(e["user_id"] for e in self.entries))
        }
    
    def save_analytics(self):
        """Save current analytics snapshot."""
        stats = self.system_wide_stats()
        with ANALYTICS.open("w") as f:
            json.dump(stats, f, indent=2)
        return stats

if __name__ == "__main__":
    calc = SynergicCalculator()
    print("Synergic Calculator Loaded")
    print(f"Existing entries: {len(calc.entries)}")
    print(f"Analytics file: {ANALYTICS}")
    
    # Demo: log one sample entry
    demo_entry = calc.log_entry(
        user_id="demo_user",
        j_agape=100.0,
        j_total=200.0,
        efficiency=0.5,
        activity_type="computation"
    )
    print(f"\nDemo entry logged: {json.dumps(demo_entry, indent=2)}")
    
    # Save analytics
    analytics = calc.save_analytics()
    print(f"\nAnalytics saved: {json.dumps(analytics, indent=2)}")
