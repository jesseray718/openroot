#!/usr/bin/env python3
"""
Physics Engine
Test and validate physical principles
"""

import math
import time

class PhysicsEngine:
    G = 6.67430e-11  # Gravitational constant
    
    def __init__(self):
        self.models = {
            'gravity': self.test_gravity,
            'energy': self.test_energy,
            'materials': self.test_materials,
            'thermodynamics': self.test_thermodynamics
        }
        
    def test_gravity(self):
        """Test gravitational models"""
        print("\nGravitational Physics Test")
        print("==========================")
        
        # Earth-Moon system
        m_earth = 5.972e24  # kg
        m_moon = 7.342e22   # kg
        r = 384400000       # m
        
        force = self.G * m_earth * m_moon / (r ** 2)
        print(f"Earth-Moon gravitational force: {force:.2e} N")
        
        # Escape velocity
        v_escape = math.sqrt(2 * self.G * m_earth / r)
        print(f"Escape velocity from Earth: {v_escape:.0f} m/s")
        
    def test_energy(self):
        """Test energy systems"""
        print("\nEnergy Systems Test")
        print("====================")
        
        # Solar energy
        solar_constant = 1361  # W/m²
        panel_area = 1.6      # m² (typical panel)
        panel_efficiency = 0.2  # 20%
        
        energy = solar_constant * panel_area * panel_efficiency
        print(f"Solar panel output: {energy:.0f} W")
        
        # Rocket mass heater efficiency
        rmh_efficiency = 0.8  # 80%
        wood_energy = 15e6    # J/kg
        wood_mass = 10        # kg
        
        useful_energy = wood_energy * wood_mass * rmh_efficiency
        print(f"RMH useful energy: {useful_energy/1e6:.0f} MJ")
        
    def test_materials(self):
        """Test material properties"""
        print("\nMaterial Properties Test")
        print("=========================")
        
        # GFRC properties
        gfrc_density = 1800    # kg/m³
        gfrc_strength = 15     # MPa
        
        print(f"GFRC density: {gfrc_density} kg/m³")
        print(f"GFRC strength: {gfrc_strength} MPa")
        
        # Thermal properties
        thermal_conductivity = 0.5  # W/m·K
        thickness = 0.1            # m
        area = 1.0                 # m²
        temp_diff = 20             # °C
        
        heat_flow = thermal_conductivity * area * temp_diff / thickness
        print(f"Heat flow through GFRC: {heat_flow:.0f} W")
        
    def test_thermodynamics(self):
        """Test thermodynamic principles"""
        print("\nThermodynamics Test")
        print("====================")
        
        # Rocket stove efficiency
        stove_efficiency = 0.4  # 40%
        fuel_energy = 45e6      # J/kg (wood)
        fuel_mass = 5           # kg
        
        useful_energy = fuel_energy * fuel_mass * stove_efficiency
        print(f"Useful energy from stove: {useful_energy/1e6:.0f} MJ")
        
        # Heat transfer
        water_mass = 10         # kg
        specific_heat = 4186   # J/kg·K
        temp_change = 80       # °C
        
        energy_needed = water_mass * specific_heat * temp_change
        print(f"Energy to heat water: {energy_needed/1e6:.0f} MJ")
        
    def interactive(self):
        """Interactive mode"""
        print("\nPhysics Engine - Interactive Mode")
        print("Commands: gravity, energy, materials, thermodynamics, exit")
        
        while True:
            try:
                cmd = input("> ").strip().lower()
                
                if not cmd:
                    continue
                    
                if cmd == 'exit':
                    break
                    
                elif cmd in self.models:
                    self.models[cmd]()
                    
                else:
                    print("Unknown command. Try: gravity, energy, materials, thermodynamics, exit")
                    
            except KeyboardInterrupt:
                break
                
        print("\nExiting Physics Engine")

# Main
if __name__ == '__main__':
    engine = PhysicsEngine()
    engine.interactive()
