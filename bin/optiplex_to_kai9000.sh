# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env bash
# OptiPlex → Kai9000 connection (for pushing files, checking A15 state)
set -eu
KAI_IP="${KAI_IP:-100.74.230.127}"  # replace with your A15 Tailscale IP
KAI_USER="${KAI_USER:-root}"
echo "[gate] OPTIPLEX → KAI9000 CONNECT $(date -u +%FT%TZ)"
if ping -c 1 -W 2 "$KAI_IP" >/dev/null 2>&1; then
    echo "  [banked] Kai9000 reachable at $KAI_IP"
    ssh -o ConnectTimeout=5 "$KAI_USER@$KAI_IP" 'echo "Kai9000 online: $(hostname) $(uname -a)"'
else
    echo "  [held] Kai9000 unreachable — verify Tailscale IP"
    echo "  Your A15 Tailscale IP is likely different. Check on A15: tailscale ip -4"
fi
