from src.openroot_optimizer.rmh_labyrinth_model import compare_current_vs_rmh_lab

def test_compare_runs():
    current, proposed = compare_current_vs_rmh_lab()
    assert current["baseline_all_electric_J"] > 0
    assert proposed["baseline_all_electric_J"] > 0

def test_heat_for_heat_cold_for_cold_allocation():
    current, proposed = compare_current_vs_rmh_lab()
    assert proposed["heat_served_by_rmh_J"] >= 0
    assert proposed["cool_served_by_labyrinth_J"] >= 0
    assert proposed["electric_fallback_J"] >= 0

def test_energy_saving_signal():
    current, proposed = compare_current_vs_rmh_lab()
    # Proposed should usually save some electrical fallback vs current all-electric
    assert proposed["electricity_saved_J"] >= 0
