#!/usr/bin/env python3
"""
JouleLeverageAnalyzer: measures work (J) accomplished per human effort (J) to maximize systemic benefit per unit human input per OpenRoot directives.
Defaults to H-003 thermal cascade + Stirling (passive solar-thermal capture to mechanical work).
Integrates: thermal cascade (H-003) -> AE-GFRC/AR-GFRC material -> Stirling mechanical -> PoPW verification oracle -> ACRE token mint.
UNE nomenclature for tasks/systems. github.com/jesseray718/aerocement + openroot.
All metrics theoretical until physical validation with meters/logs. Assumptions: human 80-300W varies by intensity; convert real work to J; passive sets system_kwh=0.
"""

import argparse
import json
from datetime import datetime

def analyze_leverage(args):
    human_j = args.human_hours * 3600.0 * args.human_watts
    system_j = args.system_kwh * 3600.0 * 1000.0
    total_in_j = human_j + system_j
    work_j = args.work_kwh * 3600.0 * 1000.0 * args.cycles * args.lifetime
    
    amp = work_j / human_j if human_j > 0 else float('inf')
    eff = (work_j / total_in_j * 100.0) if total_in_j > 0 else 0.0
    
    amp_str = round(amp, 0) if amp != float('inf') else "infinite (passive marginal input)"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "task": args.task,
        "human_energy_input_mj": round(human_j / 1e6, 2),
        "system_energy_input_mj": round(system_j / 1e6, 2),
        "total_energy_input_mj": round(total_in_j / 1e6, 2),
        "work_output_gj": round(work_j / 1e9, 2),
        "amplification_x": amp_str,
        "efficiency_pct": round(eff, 1),
        "system_map": "H-003 thermal cascade node -> Stirling mechanical work node -> PoPW oracle -> ACRE token on verified kWh. AE-GFRC enables low-effort build. Replicate via UNE. github.com/jesseray718/aerocement",
        "assumptions": "Human watts vary by task intensity; convert all accomplished work (mech/thermal/elec/PE) to J; passive/ambient systems use system_kwh=0; validate with power meters, time logs, force sensors. Theoretical base until physical test.",
        "popw_note": "High amplification + verified output qualifies for PoPW mining and ACRE issuance proportional to proven physical work. Log JSON report for oracle submission."
    }
    
    print(f"Task: {report['task']}")
    print(f"Human input: {report['human_energy_input_mj']} MJ ({args.human_hours}h @ {args.human_watts}W avg)")
    print(f"System input: {report['system_energy_input_mj']} MJ (0 = passive thermodynamic/ambient)")
    print(f"Total input: {report['total_energy_input_mj']} MJ")
    print(f"Work output: {report['work_output_gj']} GJ over {args.lifetime} years / {args.cycles} cycles/yr")
    print(f"Amplification: {report['amplification_x']}x (work J per human J)")
    print(f"Efficiency: {report['efficiency_pct']}% (work / total input)")
    print(f"PoPW/ACRE: {report['popw_note']}")
    print(f"Map: {report['system_map']}")
    print(f"Assumptions: {report['assumptions']}")
    
    if args.report_file:
        with open(args.report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {args.report_file} for PoPW logging")
    
    if args.system_kwh < 0.01:
        print("Leverage status: MAX (passive thermal node H-003). Increase marginal yield by scaling collector area, improving insulation/labyrinth, or adding parallel cascades per specs. Verify discharge kWh for ACRE mint.")
    else:
        print("To increase leverage: migrate system energy input to passive solar-thermal (H-003 cascade) or ambient flows to approach infinite amplification. Minimize active fuel/electric chains. Use AE-GFRC for any build phase to cut human effort.")
    print("Next: edit params with your prototype logs or real measurements; re-run; submit high-amp verified reports to PoPW oracle. Rank all project tasks by this metric to compound infrastructure.")

def main():
    parser = argparse.ArgumentParser(description="JouleLeverageAnalyzer - max work per human input. Termux-native. Defaults model your H-003 passive case.")
    parser.add_argument("--task", default="H-003 thermal cascade + Stirling discharge", help="Task/system name (UNE compatible string)")
    parser.add_argument("--human_hours", type=float, default=180.0, help="Total human hours (build + operate + verify)")
    parser.add_argument("--human_watts", type=float, default=120.0, help="Average human metabolic power during effort (80-300 typical)")
    parser.add_argument("--work_kwh", type=float, default=24.89, help="Useful work accomplished per cycle (kWh mechanical/thermal/electrical)")
    parser.add_argument("--cycles", type=float, default=365.0, help="Cycles per year (e.g. nightly for thermal discharge)")
    parser.add_argument("--lifetime", type=float, default=25.0, help="Service lifetime in years")
    parser.add_argument("--system_kwh", type=float, default=0.0, help="Direct system energy input per cycle kWh (fuel/electric; set 0 for passive)")
    parser.add_argument("--report_file", default=None, help="Optional JSON report path e.g. $HOME/h003_report.json for oracle")
    args = parser.parse_args()
    analyze_leverage(args)

if __name__ == "__main__":
    main()
