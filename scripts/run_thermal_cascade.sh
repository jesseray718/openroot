#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd /sdcard/openroot
python src/openroot_optimizer/thermal_cascade.py
python src/openroot_optimizer/thermal_cascade_reports.py
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -q tests/test_thermal_cascade_balance.py
python3 -m kernel.selftest
