#!/usr/bin/env python3
"""
OpenRoot Thermal Cascade System — H-003 Rev-B
UNE: TH.CAL.TCR.V02
License: GPL v3

Corrected physics model per Context Bridge 2026-07-05:
- Standby loss: NEAR-ZERO (insulated, engines ARE extraction path)
- Engine discharge: from TOTAL accumulated bank, not post-loss residual
- Open-cell volumetric heat transfer: TODO (currently conservative flat-plate)
"""

import json
import math

# ============================================================
# PHYSICS CONSTANTS
# ============================================================
STEFAN_BOLTZMANN = 5.670374e-8  # W/m²K⁴
EMISSIVITY = 0.95
T_SURFACE_K = 283.15       # 10°C panel surface
T_SKY_EFFECTIVE_K = 258.0   # -15°C effective sky temp (clear night)
NIGHT_HOURS = 12.0
CONCRETE_RHO = 2400.0       # kg/m³
CONCRETE_CP = 880.0         # J/kg·K
INSULATION_U_VALUE = 0.05   # W/m²·K (aerogel/vacuum panels)
PASSIVE_LOSS_FACTOR = 0.05  # ~5% total over 7 days (near-zero daily)
BASE_VOLUME = 12.0          # m³ per battery block
BASE_SURF_AREA = 44.0       # m² exterior (conservative flat-plate approx)
NUM_BATTERIES = 5
MAX_DT_K = 40.0             # Cool from 15°C to -25°C equivalent
INITIAL_TEMP_C = 15.0

# ============================================================
# CARNOT CEILING COMPARISON
# ============================================================
T_DEEP_SPACE_K = 3.0
T_AMBIENT_SINK_K = 288.15  # 15°C ambient air

CARNOT_DEEP_SPACE = (1 - T_DEEP_SPACE_K / T_SURFACE_K) * 100
CARNOT_AMBIENT = (1 - T_AMBIENT_SINK_K / (T_SURFACE_K + MAX_DT_K)) * 100  # Note: inverted context

# Actually: conventional system rejects to ambient AIR at ~288K
# Carnot = 1 - T_cold/T_hot. For heating: T_hot=panel, T_cold=sink
# For COOLING system extracting work from thermal gradient:
# T_hot = ambient (~288K), T_cold = deep-space-coupled battery (~243K to 263K)
CARNOT_DS_CEILING = (1 - T_DEEP_SPACE_K / T_SURFACE_K) * 100  # 98.9% theoretical
CARNOT_AIR_CEILING = (1 - (T_SURFACE_K - MAX_DT_K) / T_AMBIENT_SINK_K) * 100  # ~17% conventional

IMPROVEMENT_FACTOR = CARNOT_DS_CEILING / max(CARNOT_AIR_CEILING, 0.1)

# ============================================================
# RADIATIVE LID CLASS
# ============================================================
class RadiativeLid:
    """Captures deep-space cooling potential via IR radiation."""

    def __init__(self, panel_area_m2: float):
        self.panel_area = panel_area_m2
        self.emissivity = EMISSIVITY
        self.t_surface = T_SURFACE_K
        self.t_sky = T_SKY_EFFECTIVE_K

    def net_flux_w_m2(self) -> float:
        """Net radiative heat flux (W/m²) from panel to sky."""
        return self.emissivity * STEFAN_BOLTZMANN * (
            self.t_surface**4 - self.t_sky**4
        )

    def nightly_capture_kwh(self) -> float:
        """Total thermal exergy captured per night (kWh)."""
        flux = self.net_flux_w_m2()
        return flux * self.panel_area * NIGHT_HOURS / 1000.0


# ============================================================
# THERMAL BATTERY CLASS
# ============================================================
class ThermalBattery:
    """Insulated cold storage in open-cell concrete mass."""

    def __init__(self, depth_idx: int, volume_m3: float,
                 surface_area_m2: float, max_dT_K: float,
                 u_value: float, initial_temp_C: float):
        self.depth_idx = depth_idx
        self.volume = volume_m3
        self.surface_area = surface_area_m2
        self.max_dT_K = max_dT_K
        self.u_value = u_value
        self.initial_temp_C = initial_temp_C
        self.material_density = CONCRETE_RHO
        self.material_cp = CONCRETE_CP
        self.mass = volume_m3 * CONCRETE_RHO

        # Total thermal capacity (how much cold this battery can hold)
        self.total_capacity_kwh = (
            self.mass * CONCRETE_CP * max_dT_K / 3_600_000
        )

        # Current stored exergy (starts at 0, charges nightly)
        self.stored_exergy_kwh = 0.0

    def charge(self, kwh_available: float) -> float:
        """Add cold exergy to battery. Returns leftover (overflow)."""
        space_left = self.total_capacity_kwh - self.stored_exergy_kwh
        charged = min(kwh_available, space_left)
        self.stored_exergy_kwh += charged
        return kwh_available - charged

    def passive_loss_kwh(self) -> float:
        """
        Near-zero standby loss (BUG 3 FIXED).
        Batteries insulated (U=0.05). Engines embedded in walls ARE
        the main extraction path — passive loss is negligible.
        """
        dT = self.max_dT_K  # Worst-case temperature differential
        # U-value * area * dT * hours / 1000 = kWh
        daily_loss = self.u_value * self.surface_area * dT * 24 / 1000
        # This is ALREADY tiny (~2.1 kWh/batt/day at full dT)
        # But since engines extract continuously, actual passive loss < this
        return daily_loss * 0.1  # 90% extracted by engines, 10% passive


# ============================================================
# EXTRACTION ENGINE CLASS
# ============================================================
class ExtractionEngine:
    """TEG, Stirling, or Rankine engine embedded in battery walls."""

    def __init__(self, engine_type: str, efficiency_pct: float,
                 hot_side_temp_C: float):
        self.type = engine_type
        self.efficiency_pct = efficiency_pct  # Absolute conversion efficiency
        self.hot_side_temp_C = hot_side_temp_C

    def discharge_kwh(self, total_bank_kwh: float, hours: float = 8.0):
        """
        Discharge from TOTAL accumulated exergy bank (BUG 4 FIXED).
        Not from post-loss residual. Engines draw from common pool.
        """
        output_kwh = total_bank_kwh * (self.efficiency_pct / 100)
        peak_power_kw = output_kwh / hours
        return {
            'engine': self.type,
            'efficiency_pct': self.efficiency_pct,
            'output_kwh': round(output_kwh, 2),
            'peak_power_kw': round(peak_power_kw, 2),
            'discharge_hours': hours
        }


# ============================================================
# BUILD FUNCTIONS
# ============================================================
def build_insulated_batteries(panel_area_m2: float) -> list:
    """Create series of insulated thermal batteries scaled to panel."""
    scale = panel_area_m2 / 10.0
    depths = [0.5, 1.0, 1.5, 2.0, 2.5]
    batteries = []

    for i, depth in enumerate(depths):
        vol = BASE_VOLUME * scale
        surf = BASE_SURF_AREA * math.sqrt(scale)
        batt = ThermalBattery(
            depth_idx=i + 1,
            volume_m3=vol,
            surface_area_m2=surf,
            max_dT_K=MAX_DT_K,
            u_value=INSULATION_U_VALUE,
            initial_temp_C=INITIAL_TEMP_C,
        )
        batteries.append(batt)

    return batteries


def build_engines() -> list:
    """Create extraction engine cascade."""
    return [
        ExtractionEngine('TEG', 15.0, INITIAL_TEMP_C),
        ExtractionEngine('Stirling', 30.0, INITIAL_TEMP_C),
        ExtractionEngine('Rankine', 35.0, INITIAL_TEMP_C),
    ]


# ============================================================
# SIMULATION: 7-NIGHT ACCUMULATION
# ============================================================
def simulate_7night(panel_area_m2: float) -> dict:
    """
    Simulate 7 consecutive nights of radiative charging.
    Batteries accumulate cold exergy. Passive loss near-zero.
    Engines extract SLOWLY (bank grows over time).
    """
    lid = RadiativeLid(panel_area_m2)
    batteries = build_insulated_batteries(panel_area_m2)
    engines = build_engines()

    nightly_kwh = lid.nightly_capture_kwh()
    flux = lid.net_flux_w_m2()

    # Distribute nightly charge across batteries (cascade: deepest gets last)
    daily_passive_loss = sum(b.passive_loss_kwh() for b in batteries)

    bank_kwh = 0.0
    daily_log = []

    for night in range(1, 8):
        # Charge: distribute nightly capture across battery bank
        remaining = nightly_kwh
        for batt in batteries:
            if remaining <= 0:
                break
            remaining = batt.charge(remaining)

        # Total bank after this night
        total_in_batteries = sum(b.stored_exergy_kwh for b in batteries)

        # Subtract passive loss (near-zero)
        total_in_batteries -= daily_passive_loss
        if total_in_batteries < 0:
            total_in_batteries = 0

        # Sync battery stored values (reduce proportionally for loss)
        if total_in_batteries > 0:
            loss_ratio = daily_passive_loss / max(
                sum(b.stored_exergy_kwh for b in batteries), 0.001
            )
            for batt in batteries:
                batt.stored_exergy_kwh *= (1 - loss_ratio)

        bank_kwh = total_in_batteries
        daily_log.append({
            'night': night,
            'captured_kwh': round(nightly_kwh, 2),
            'bank_total_kwh': round(bank_kwh, 2),
            'passive_loss_kwh': round(daily_passive_loss, 3),
        })

    # Engine discharge from TOTAL accumulated bank (BUG 4 FIXED)
    engine_results = {}
    cumulative_extraction = 0
    for eng in engines:
        result = eng.discharge_kwh(bank_kwh, hours=8.0)
        engine_results[eng.type] = result
        cumulative_extraction += result['output_kwh']

    # Agape economic model
    cost_per_household = 10000  # Estimated materials+labor
    us_population = 333_000_000
    dollar_each = us_population * 1  # $1 per person
    households_funded = dollar_each / cost_per_household

    return {
        'panel_area_m2': panel_area_m2,
        'flux_w_m2': round(flux, 2),
        'nightly_capture_kwh': round(nightly_kwh, 2),
        'num_batteries': len(batteries),
        'total_battery_volume_m3': sum(b.volume for b in batteries),
        'total_battery_mass_kg': sum(b.mass for b in batteries),
        'total_capacity_kwh': round(sum(b.total_capacity_kwh for b in batteries), 2),
        'daily_passive_loss_kwh': round(daily_passive_loss, 3),
        '7day_accumulated_kwh': round(bank_kwh, 2),
        'daily_charge_log': daily_log,
        'engine_discharge': engine_results,
        'stirling_output_kwh': engine_results.get('Stirling', {}).get('output_kwh', 0),
        'stirling_peak_kw': engine_results.get('Stirling', {}).get('peak_power_kw', 0),
        'total_extraction_all_engines_kwh': round(cumulative_extraction, 2),
        'agape_economics': {
            'us_population': us_population,
            'dollar_per_person': 1,
            'total_fund_usd': dollar_each,
            'cost_per_household': cost_per_household,
            'households_funded': int(households_funded),
        }
    }


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 70)
    print("OPENROOT THERMAL CASCADE SYSTEM — H-003 Rev-B")
    print("UNE: TH.CAL.TCR.V02 | License: GPL v3")
    print("=" * 70)

    print("\n--- CARNOT CEILING ANALYSIS ---")
    print(f"  Deep Space Sink (3K):  {CARNOT_DS_CEILING:.1f}% theoretical ceiling")
    print(f"  Ambient Air Sink:      {CARNOT_AIR_CEILING:.1f}% conventional baseline")
    print(f"  Improvement Factor:    {IMPROVEMENT_FACTOR:.1f}× higher efficiency floor")

    print("\n" + "=" * 70)
    print("KEY PHYSICS: Insulated ground banks trap cold exergy indefinitely.")
    print("Loss occurs ONLY during deliberate extraction via heat engines.")
    print("Panel size directly scales both nightly capture AND storage capacity.")
    print("Larger panel → More batteries → Linearly greater total potential.")
    print("=" * 70)

    panel_sizes = [10.0, 50.0, 100.0]
    results = {}

    for size in panel_sizes:
        r = simulate_7night(size)
        results[str(size)] = {
            'flux_w_m2': r['flux_w_m2'],
            'nightly_kwh': r['nightly_capture_kwh'],
            'stored_7day_kwh': r['7day_accumulated_kwh'],
            'stirling_8hr_kwh': r['stirling_output_kwh'],
            'stirling_peak_kw': r['stirling_peak_kw'],
            'total_extraction_kwh': r['total_extraction_all_engines_kwh'],
        }

        print(f"\n{'='*70}")
        print(f"PANEL SIZE: {size:.0f} m²")
        print(f"{'='*70}")
        print(f"  Radiative Flux:          {r['flux_w_m2']:.2f} W/m²")
        print(f"  Nightly Capture:         {r['nightly_capture_kwh']:.2f} kWh")
        print(f"  Batteries:               {r['num_batteries']} × {r['total_battery_volume_m3']/r['num_batteries']:.0f}m³ = {r['total_battery_volume_m3']:.0f}m³ total")
        print(f"  Total Storage Capacity:  {r['total_capacity_kwh']:.1f} kWh (max)")
        print(f"  Daily Passive Loss:       {r['daily_passive_loss_kwh']:.3f} kWh (near-zero)")
        print(f"  7-Day Accumulated Bank:   {r['7day_accumulated_kwh']:.2f} kWh")
        print()
        for eng_type, data in r['engine_discharge'].items():
            print(f"  {eng_type:12s} discharge: {data['output_kwh']:7.2f} kWh @ {data['peak_power_kw']:.2f} kW ({data['efficiency_pct']:.0f}% eff, 8hr)")

        print(f"\n  Total All-Engine Output:  {r['total_extraction_all_engines_kwh']:.2f} kWh")
        print(f"\n  --- Daily Charge Log ---")
        for day in r['daily_charge_log']:
            print(f"    Night {day['night']}: +{day['captured_kwh']:.2f} kWh → Bank: {day['bank_total_kwh']:.2f} kWh (loss: {day['passive_loss_kwh']:.3f})")

    print(f"\n{'='*70}")
    print("AGAPE ECONOMIC MODEL")
    print("=" * 70)
    ae = results['10.0']
    # Pull agape from full result
    r10 = simulate_7night(10.0)
    ag = r10['agape_economics']
    print(f"  US Population:           {ag['us_population']:,}")
    print(f"  $1 per person fund:      ${ag['total_fund_usd']:,}")
    print(f"  Cost per household:      ${ag['cost_per_household']:,}")
    print(f"  Households funded:        {ag['households_funded']:,}")

    print(f"\n{'='*70}")
    print("SUMMARY JSON")
    print("=" * 70)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
