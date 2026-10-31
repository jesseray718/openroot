# SPDX-License-Identifier: GPL-3.0
#!/bin/bash
# core_view_server.sh — rebuild + serve core view on :8088, survive reboots of terminal
cd /home/${OPENROOT_USER}/openroot/data/core_view
python3 /home/${OPENROOT_USER}/openroot/bin/build_core_view.py || exit 1
if pgrep -f "http.server 8088" > /dev/null; then
  echo "[alive] server already on :8088"
else
  nohup python3 -m http.server 8088 --bind 0.0.0.0 \
    > /home/${OPENROOT_USER}/openroot/logs/core_view_http.log 2>&1 &
  echo "[send] server pid $!"
fi
echo "[verify] $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8088/index.html) <- want 200"
echo "[phone] on A15 open: http://192.168.1.193:8088"
echo "[away]  via Tailscale: http://${OPENROOT_HUB}:8088"
