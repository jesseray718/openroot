#!/data/data/com.termux/files/usr/bin/bash
# A15 only. Refuse if we look like the box.
set -eu
case "$(pwd)" in
  /home/jesse*) echo "REFUSE: SSH pane. This script is A15."; exit 2 ;;
esac
if [ "$(uname -n)" = "optiplex3060" ]; then
  echo "REFUSE: optiplex host."
  exit 2
fi
CODE=/data/data/com.termux/files/home/code/openroot
KIT=$CODE/kit
mkdir -p "$KIT/bin" "$KIT/sql" "$KIT/data" "$KIT/docs" "$KIT/manual"
echo "A15 kit root $KIT"
python3 "$KIT/bin/kit_init.py"
python3 "$KIT/bin/rounds_sim.py"
python3 "$KIT/bin/tidbit.py" list
echo "NEXT: python3 $KIT/bin/ssh_probe.py"
echo "NEXT: python3 $KIT/bin/coder_client.py status"
