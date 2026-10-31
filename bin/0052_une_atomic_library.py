import math

k = 1.380649e-23
c = 2.99792458e8
phi = (1 + math.sqrt(5)) / 2

def une_name(name: str) -> str:
    cleaned = ''.join(c for c in name.lower() if c.isalnum() or c == '_')
    if not cleaned: raise ValueError("UNE violation")
    return cleaned

def cooperation_efficiency(N: int, epochs: int = 1, base: float = 1.0) -> float:
    if N < 1: return base
    return base * (phi ** min(epochs, 50)) * (1 + math.log(N) / phi)

def golden_angle() -> float:
    return 360 / (phi ** 2)

def physical_efficiency_gain(crew_size: int, mech_factor: float = 50.0, epochs: int = 1) -> float:
    return cooperation_efficiency(crew_size, epochs) * mech_factor

class UNE_SelfFeedback:
    def __init__(self, name: str):
        self.name = une_name(name)
        self.cooperators = 1
        self.epochs = 0
        self.efficiency = 1.0
    def add_cooperator(self):
        self.cooperators += 1
        self.efficiency = cooperation_efficiency(self.cooperators, self.epochs)
        return self.efficiency
    def run_epoch(self):
        self.epochs += 1
        self.efficiency = cooperation_efficiency(self.cooperators, self.epochs)
        return self.efficiency
    def fractal_step(self):
        return fractal_replace(self.name, lambda: self.run_epoch())

def poww_verify(work_type: str, volume: float, crew_size: int) -> float:
    return volume * 0.1 * cooperation_efficiency(crew_size)

def optimal_thermal_layout(area_m2: float, crew_size: int) -> dict:
    return {"angle_deg": round(golden_angle(), 3), "efficiency_multiplier": round(physical_efficiency_gain(crew_size), 2)}

# === Unified Conversion Layer ===
def joules_per_second(raw_energy_joules: float, time_seconds: float) -> float:
    return raw_energy_joules / time_seconds

def human_metabolic_power(watts: float = 200) -> float:
    return watts

def brain_computation_power(watts: float = 20) -> float:
    return watts

def computational_power(electrical_joules: float, time_seconds: float) -> float:
    return electrical_joules / time_seconds

def landauer_bit_rate(bits: float, time_seconds: float, T: float = 300.0) -> float:
    energy = bits * k * T * math.log(2)
    return energy / time_seconds

def frequency_to_power(frequency_hz: float, energy_per_cycle: float) -> float:
    return frequency_hz * energy_per_cycle

def resonance_efficiency(matching_factor: float) -> float:
    return max(0.0, min(1.0, matching_factor))

def unified_effective_power(
    raw_energy_joules: float,
    time_seconds: float,
    N_cooperators: int = 1,
    resonance_factor: float = 1.0,
    fractal_gain: float = 1.0
) -> float:
    base_power = raw_energy_joules / time_seconds
    coop_mult = 1 + math.log(max(N_cooperators, 1)) / phi
    return base_power * coop_mult * resonance_factor * fractal_gain

def unified_power_acceleration(
    raw_energy_joules: float,
    time_seconds: float,
    N_cooperators: int = 1,
    resonance_factor: float = 1.0,
    fractal_gain: float = 1.0,
    epochs: int = 1,
    growth_rate: float = 0.0
) -> float:
    base_power = raw_energy_joules / time_seconds
    coop_mult = 1 + math.log(max(N_cooperators, 1)) / phi
    fractal_compound = fractal_gain ** min(epochs, 50)
    effective_power = base_power * coop_mult * resonance_factor * fractal_compound * (1 + growth_rate * epochs)
    if epochs > 1:
        previous_power = base_power * coop_mult * resonance_factor * (fractal_gain ** (epochs - 1))
        acceleration = (effective_power - previous_power) / time_seconds
    else:
        acceleration = effective_power / time_seconds
    return acceleration

def global_grid_mass(twh_per_year: float = 29000) -> float:
    joules = twh_per_year * 3.6e15
    return joules / (c ** 2)

def transmission_loss_mass(twh_generation: float = 29000, loss_percent: float = 0.07) -> float:
    lost_twh = twh_generation * loss_percent
    joules_lost = lost_twh * 3.6e15
    return joules_lost / (c ** 2)

def information_mass(bits: float, T: float = 300.0) -> float:
    return mass_equivalent(bits * landauer_energy_per_bit(T))

def mass_equivalent(energy_joules: float) -> float:
    return energy_joules / (c ** 2)

def landauer_energy_per_bit(T: float = 300.0) -> float:
    return k * T * math.log(2)

print("=== UNE UNIFIED LIBRARY LOADED (All Three Features) ===")
