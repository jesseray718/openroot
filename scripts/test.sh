#!/data/data/com.termux/files/usr/bin/bash
set -eu
cd /sdcard/openroot
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest
