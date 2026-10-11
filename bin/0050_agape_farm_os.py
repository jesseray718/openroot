#!/usr/bin/env python3
"""
AGAPE FARM OS - Offline Voice + Synergetic Thermal Cascade Calculator
Operator: Jesse McMillen (OpenRoot LLC) - Sikeston, MO
Core: Whisper -> Constitution -> Thermal Cascade -> Ledger -> ACRE
"""
import os, sys, json, math, hashlib, time, subprocess
from datetime import datetime
from pathlib import Path

BASE = Path(os.path.expanduser("~/agapenet"))
LEDGER = BASE / "ledger" / "thermo_ledger.jsonl"
CONST = BASE / "docs" / "00_MASTER_CONSTITUTION.md"
FARM_LOG = BASE / "ledger" / "farm_cascade.jsonl"

for d in ["ledger", "docs"]:
    (BASE / d).mkdir(parents=True, exist_ok=True)

# --- PHYSICS ---
C = 299792458
K = 1.380649e-23
PHI = (1 + math.sqrt(5)) / 2

# --- 46656 LANGUAGE ENCODER (36^3) ---
SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
def encode_agape(text):
    """Encode text into 3-symbol Agape language."""
    codes = []
    for ch in text.upper():
        if ch in SYMBOLS:
            idx = SYMBOLS.index(ch)
            d1 = idx // 36
            d2 = (idx % 36) // 6
            d3 = idx % 6
            codes.append(f"{SYMBOLS[d1]}{SYMBOLS[d2]}{SYMBOLS[d3]}")
    return codes

def decode_agape(codes):
    """Decode 3-symbol Agape language back to text."""
    result = ""
    for code in codes:
        if len(code) == 3:
            d1 = SYMBOLS.index(code[0])
            d2 = SYMBOLS.index(code[1])
            d3 = SYMBOLS.index(code[2])
            idx = d1 * 36 + d2 * 6 + d3
            if idx < len(SYMBOLS):
                result += SYMBOLS[idx]
    return result

# --- VOICE CAPTURE (multiple fallbacks) ---
def capture_voice():
    """Try termux-speech-to-text, then whisper, then simulated."""
    # Method 1: termux-speech-to-text (requires Termux:API app)
    try:
        r = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True, text=True, timeout=20
        )
        text = r.stdout.strip()
        if text:
            print(f"[VOICE] termux-speech-to-text: \"{text}\"")
            return text
    except Exception:
        pass

    # Method 2: ffmpeg recording + whisper (if installed)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "avfoundation", "-i", ":0",
             "-t", "5", "-ar", "16000", "/tmp/voice.wav"],
            capture_output=True, timeout=10
        )
        import whisper
        model = whisper.load_model("tiny")
        result = model.transcribe("/tmp/voice.wav")
        text = result["text"].strip()
        if text:
            print(f"[VOICE] whisper offline: \"{text}\"")
            return text
    except Exception:
        pass

    # Method 3: Text input fallback
    print("[VOICE] Speech unavailable. Type your amendment:")
    try:
        text = input("> ").strip()
        if text:
            return text
    except EOFError:
        pass

    print("[VOICE] Using simulated input.")
    return "Amendment H-005: Thermal cascade calibrated at 0.98 efficiency"

# --- SYNERGISTIC THERMAL CASCADE CALCULATOR ---
def calculate_thermal_cascade(
    ambient_temp_c=37.8,      # Sikeston summer high
    ground_temp_c=15.0,       # Subterranean stable temp
    labyrinth_depth_m=3.0,    # Depth of thermal labyrinth
    labyrinth_length_m=30.0,  # Length of cooling tunnel
    tank_volume_m3=50.0,      # Ferro-cement water battery volume
    greenhouse_area_m2=200.0, # Greenhouse footprint
    insulation_r_value=30.0,  # Aerocement insulation
    solar_gain_w_m2=800.0,    # Peak solar irradiance
    hours_sunlight=6.0,       # Winter day sunlight
    bubble_diameter_mm=0.3    # Aerocement bubble size
):
    """
    Calculate passive thermal energy cascade.
    Models: ground coupling, water battery, solar gain, cascade compounding.
    """
    # Daily solar energy harvest (Joules)
    daily_solar_j = solar_gain_w_m2 * greenhouse_area_m2 * hours_sunlight * 3600

    # Water battery thermal mass (4.186 J/g/K = 4.186 MJ/m3/K)
    water_mass_kg = tank_volume_m3 * 1000
    water_thermal_capacity = water_mass_kg * 4186  # J/K
    delta_t_water = abs(ambient_temp_c - ground_temp_c)
    water_battery_j = water_thermal_capacity * delta_t_water

    # Labyrinth cooling: air through ground-coupled tunnel
    air_flow_m3_s = 2.0  # natural convection estimate
    air_heat_capacity = 1.005  # kJ/kg/K
    air_density = 1.225  # kg/m3
    labyrinth_cooling_w = (
        air_flow_m3_s * air_density * air_heat_capacity * 1000 *
        (ambient_temp_c - ground_temp_c)
    )

    # Aerocement insulation efficiency (smaller bubbles = better)
    bubble_efficiency = 1.0 / (1.0 + bubble_diameter_mm)
    heat_loss_w = (
        (ambient_temp_c - ground_temp_c) *
        greenhouse_area_m2 / insulation_r_value * 5.678  # R to W/m2K
    )
    heat_loss_w *= (1.0 - bubble_efficiency * 0.3)

    # Cascade compounding: PHI-weighted time multiplier
    # Each day the system retains energy, next day compounds
    daily_net_energy_j = daily_solar_j - (heat_loss_w * 24 * 3600)
    cascade_multiplier = 1.0
    total_compounded_j = 0
    daily_log = []

    for day in range(1, 31):
        total_compounded_j += daily_net_energy_j * cascade_multiplier
        cascade_multiplier = min(cascade_multiplier * (1.0 + 0.001 * PHI), PHI)
        daily_log.append({
            "day": day,
            "net_energy_j": round(daily_net_energy_j * cascade_multiplier, 2),
            "cumulative_j": round(total_compounded_j, 2),
            "cascade_mult": round(cascade_multiplier, 6)
        })

    # Useful energy per human joule (eta)
    human_joules = 5000.0  # estimated daily human labor in J
    eta = total_compounded_j / max(human_joules, 1)

    # ACRE equivalent (1 ACRE = 1000 J useful)
    acre_minted = total_compounded_j / 1000

    return {
        "location": "Sikeston, MO",
        "daily_solar_harvest_j": round(daily_solar_j, 2),
        "water_battery_capacity_j": round(water_battery_j, 2),
        "labyrinth_cooling_w": round(labyrinth_cooling_w, 2),
        "heat_loss_w": round(heat_loss_w, 2),
        "daily_net_energy_j": round(daily_net_energy_j, 2),
        "30_day_compounded_j": round(total_compounded_j, 2),
        "cascade_peak_multiplier": round(cascade_multiplier, 6),
        "eta_efficiency": round(eta, 4),
        "acre_minted_30d": round(acre_minted, 2),
        "bubble_efficiency": round(bubble_efficiency, 4),
        "daily_log": daily_log
    }

# --- PREDICTION ENGINE ---
def predict_outcomes(cascade_data, amendment_text):
    """Multiple simultaneous predictions based on cascade + amendment."""
    predictions = []

    # Prediction 1: Food output scaling
    base_kg_day = 50.0  # kg food per day at current scale
    eta = cascade_data["eta_efficiency"]
    food_pred = base_kg_day * (1 + eta * 0.01)
    predictions.append({
        "type": "FOOD_OUTPUT",
        "prediction": f"{food_pred:.1f} kg/day",
        "basis": "eta efficiency multiplier on base yield"
    })

    # Prediction 2: Energy independence timeline
    daily_net = cascade_data["daily_net_energy_j"]
    energy_autonomy_days = 365 if daily_net > 0 else -1
    predictions.append({
        "type": "ENERGY_AUTONOMY",
        "prediction": f"{'ACHIEVED' if daily_net > 0 else 'NOT YET'} (net={daily_net:.0f} J/day)",
        "basis": "positive net energy = autonomy"
    })

    # Prediction 3: ACRE minting rate
    acre_day = cascade_data["acre_minted_30d"] / 30
    predictions.append({
        "type": "ACRE_MINT_RATE",
        "prediction": f"{acre_day:.2f} ACRE/day",
        "basis": "30-day compounded thermal cascade"
    })

    # Prediction 4: Risk assessment
    risk = "LOW" if eta > 1.0 else ("MODERATE" if eta > 0.5 else "HIGH")
    predictions.append({
        "type": "RISK",
        "prediction": risk,
        "basis": f"eta={eta:.4f}"
    })

    return predictions

# --- MAIN WORKFLOW ---
def run_farm_os():
    print("="*60)
    print("AGAPE FARM OS v1.0 | OpenRoot LLC")
    print("Sikeston, MO | Offline Voice + Thermal Cascade")
    print("="*60)

    # 1. Voice/text input
    print("\n[1/6] CAPTURING INPUT...")
    voice_text = capture_voice()

    # 2. Agape encoding
    print("\n[2/6] ENCODING TO AGAPE LANGUAGE...")
    encoded = encode_agape(voice_text)
    print(f"  Original: {voice_text[:60]}")
    print(f"  Encoded: {' '.join(encoded[:8])}...")
    print(f"  Symbols: {len(encoded)} triples from {len(voice_text)} chars")

    # 3. Constitutional parse
    print("\n[3/6] PARSING CONSTITUTION...")
    keywords = ["amendment","right","justice","restoration","seed","energy",
                "thermal","aerocement","farm","mesh","agape","acre"]
    hits = [k for k in keywords if k in voice_text.lower()]
    agape_score = len(hits)*10 + len(voice_text.split())*0.5
    print(f"  Keywords: {hits}")
    print(f"  Agape Score: {agape_score:.1f}")

    # 4. Thermal cascade calculation
    print("\n[4/6] CALCULATING THERMAL CASCADE...")
    cascade = calculate_thermal_cascade()
    print(f"  Daily Solar Harvest: {cascade['daily_solar_harvest_j']:.0f} J")
    print(f"  Water Battery: {cascade['water_battery_capacity_j']:.0f} J")
    print(f"  Labyrinth Cooling: {cascade['labyrinth_cooling_w']:.1f} W")
    print(f"  Heat Loss: {cascade['heat_loss_w']:.1f} W")
    print(f"  Net Daily Energy: {cascade['daily_net_energy_j']:.0f} J")
    print(f"  30-Day Compounded: {cascade['30_day_compounded_j']:.0f} J")
    print(f"  Cascade Multiplier: {cascade['cascade_peak_multiplier']:.6f}")
    print(f"  ETA: {cascade['eta_efficiency']:.4f}")
    print(f"  ACRE (30d): {cascade['acre_minted_30d']:.2f}")

    # 5. Predictions
    print("\n[5/6] RUNNING SIMULTANEOUS PREDICTIONS...")
    preds = predict_outcomes(cascade, voice_text)
    for p in preds:
        print(f"  [{p['type']}] {p['prediction']}")
        print(f"    basis: {p['basis']}")

    # 6. Ledger entry
    print("\n[6/6] WRITING TO THERMODYNAMIC LEDGER...")
    entry = {
        "id": f"FARM_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "operator": "jesse_mcmillen_openroot_llc",
        "location": "Sikeston_MO",
        "type": "FARM_CASCADE_AMENDMENT",
        "input_raw": voice_text,
        "input_encoded": encoded[:20],
        "agape_score": agape_score,
        "cascade": {
            "daily_solar_j": cascade["daily_solar_harvest_j"],
            "water_battery_j": cascade["water_battery_capacity_j"],
            "net_daily_j": cascade["daily_net_energy_j"],
            "compounded_30d_j": cascade["30_day_compounded_j"],
            "eta": cascade["eta_efficiency"],
            "acre_30d": cascade["acre_minted_30d"]
        },
        "predictions": preds,
        "physics_bridge": {
            "landauer_j": len(voice_text)*8*K*300*math.log(2),
            "mass_equiv_kg": (len(voice_text)*8*K*300*math.log(2))/(C**2)
        },
        "hash": hashlib.sha256(
            (voice_text + str(cascade["30_day_compounded_j"]) +
             str(time.time())).encode()
        ).hexdigest()
    }

    with open(LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    with open(FARM_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"  Ledger: {LEDGER}")
    print(f"  Farm Log: {FARM_LOG}")
    print(f"  Hash: {entry['hash'][:32]}...")

    # Verdict
    if cascade["eta_efficiency"] > 1.0:
        verdict = "SYSTEM IS NET POSITIVE. AMPLIFYING."
    elif cascade["daily_net_energy_j"] > 0:
        verdict = "SYSTEM IS BREAKING EVEN. TUNING."
    else:
        verdict = "SYSTEM NEEDS CALIBRATION. ADJUSTING."

    print(f"\n[VERDICT] {verdict}")
    print("[DONE] Agape Farm OS cycle complete.")

if __name__ == "__main__":
    try:
        run_farm_os()
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
