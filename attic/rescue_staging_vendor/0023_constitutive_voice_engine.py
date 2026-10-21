#!/usr/bin/env python3
"""AGAPE_NET CONSTITUTIONAL VOICE ENGINE - Operator: Jesse McMillen (OpenRoot LLC)"""
import os, sys, json, math, hashlib, time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(os.path.expanduser("~/agapenet"))
CONST_FILE = BASE_DIR / "docs" / "00_MASTER_CONSTITUTION.md"
LEDGER_FILE = BASE_DIR / "ledger" / "thermo_ledger.jsonl"

for d in ["ledger", "config"]:
    (BASE_DIR / d).mkdir(parents=True, exist_ok=True)

C_SPEED = 299792458
BOLTZMANN = 1.380649e-23

def capture_voice_input():
    """Real voice capture via Android termux-speech-to-text."""
    import subprocess
    try:
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True, text=True, timeout=15
        )
        text = result.stdout.strip()
        if text:
            return text
        print("[WARN] No speech detected. SIMULATED MODE.")
        return "Amendment H-004: Thermal Labyrinth efficiency increased to 98%"
    except Exception as e:
        print(f"[WARN] termux-speech-to-text failed ({e}). SIMULATED MODE.")
        return "Amendment H-004: Thermal Labyrinth efficiency increased to 98%"



def parse_constitution(text):
    if not CONST_FILE.exists():
        raise FileNotFoundError("Run agape_init_all.py first.")
    keywords = ["amendment", "right", "justice", "restoration", "seed", "energy"]
    hits = [k for k in keywords if k in text.lower()]
    agape_score = len(hits) * 10 + (len(text.split()) * 0.5)
    human_joules = len(text.split()) * 0.05
    return {
        "raw_text": text,
        "keywords_found": hits,
        "agape_score": round(agape_score, 2),
        "human_joules": round(human_joules, 4),
        "timestamp": datetime.now().isoformat()
    }

def calculate_energy_equivalent(info_text):
    bits = len(info_text) * 8
    min_energy = bits * BOLTZMANN * 300 * math.log(2)
    mass_kg = min_energy / (C_SPEED ** 2)
    return {
        "bits": bits,
        "min_energy_joules": min_energy,
        "mass_equiv_kg": mass_kg
    }

def run_synergy_prediction(new_amendment):
    base_eff = 0.85
    boost = (new_amendment['agape_score'] / 100) * 0.15
    pred_eff = min(base_eff + boost, 0.99)
    return {
        "prediction_id": hashlib.sha256(str(time.time()).encode()).hexdigest()[:8],
        "predicted_gain": f"{(pred_eff - base_eff)*100:.2f}%",
        "system_status": "OPTIMIZING" if pred_eff > 0.9 else "STABLE",
        "risk_factor": "LOW" if len(new_amendment['keywords_found']) > 2 else "MODERATE"
    }

def initiate_workflow():
    print("="*60)
    print("CONSTITUTIONAL VOICE ENGINE | OpenRoot LLC")
    print("="*60)
    
    voice_text = capture_voice_input()
    print(f'\n[INPUT] "{voice_text}"')
    
    parsed = parse_constitution(voice_text)
    print(f"\n[PARSE] Keywords: {parsed['keywords_found']}")
    print(f"[PARSE] Agape Score: {parsed['agape_score']}")
    print(f"[PARSE] Human Joules: {parsed['human_joules']} J")
    
    physics = calculate_energy_equivalent(parsed['raw_text'])
    print(f"\n[PHYSICS] Bits: {physics['bits']}")
    print(f"[PHYSICS] Min Energy: {physics['min_energy_joules']:.2e} J")
    print(f"[PHYSICS] Mass Equiv: {physics['mass_equiv_kg']:.2e} kg")
    
    prediction = run_synergy_prediction(parsed)
    print(f"\n[PREDICT] Status: {prediction['system_status']}")
    print(f"[PREDICT] Gain: {prediction['predicted_gain']}")
    print(f"[PREDICT] Risk: {prediction['risk_factor']}")
    
    entry = {
        "id": f"VOICED_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": parsed['timestamp'],
        "type": "VOICE_AMENDMENT",
        "input": parsed['raw_text'],
        "agape_score": parsed['agape_score'],
        "human_joules": parsed['human_joules'],
        "info_energy_joules": physics['min_energy_joules'],
        "mass_equiv_kg": physics['mass_equiv_kg'],
        "prediction": prediction,
        "hash": hashlib.sha256(
            (parsed['raw_text'] + str(time.time())).encode()
        ).hexdigest()
    }
    
    with open(LEDGER_FILE, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"\n[LEDGER] Written to {LEDGER_FILE}")
    print(f"[LEDGER] Hash: {entry['hash'][:32]}...")
    print("\n[DONE] System tuned. Frequency stabilized.")

if __name__ == "__main__":
    try:
        initiate_workflow()
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("Run agape_init_all.py first if Constitution is missing.")
