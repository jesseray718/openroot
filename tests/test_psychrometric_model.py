from src.openroot_optimizer.psychrometric_model import (
    humidity_ratio_kg_per_kg_da, moist_air_enthalpy_kj_per_kg_da, cooling_power_w
)

def test_humidity_ratio_nonnegative():
    w = humidity_ratio_kg_per_kg_da(30.0, 50.0)
    assert w >= 0

def test_enthalpy_increases_with_temp():
    w = humidity_ratio_kg_per_kg_da(25.0, 50.0)
    h1 = moist_air_enthalpy_kj_per_kg_da(20.0, w)
    h2 = moist_air_enthalpy_kj_per_kg_da(30.0, w)
    assert h2 > h1

def test_cooling_power_nonnegative():
    p = cooling_power_w(38.0, 20.0, 24.0, 70.0, 0.4)
    assert p >= 0
