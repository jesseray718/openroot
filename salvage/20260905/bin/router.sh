#!/data/data/com.termux/files/usr/bin/bash
# OpenRoot Compute Router
# Routes tasks based on resource availability

OPTIPLEX_IP="${OPTIPLEX_IP:-192.168.1.50}"
PHONE_RAM=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
THRESHOLD_MB=1024  # If phone has <1GB RAM, use OptiPlex

log() { echo "[$(date '+%Y-%m-%d %H:%M')] ROUTER: $*" >> /sdcard/openroot/output/router.log; }

route_task() {
  local task="$1"
  local target="phone"
  
  if [ "$PHONE_RAM" -lt "$THRESHOLD_MB" ]; then
    if ping -c 1 -W 2 "$OPTIPLEX_IP" >/dev/null 2>&1; then
      target="optiplex"
      log "Low RAM ($PHONE_RAM KB) — routing to OptiPlex"
    else
      log "OptiPlex unreachable — queueing locally"
      echo "QUEUE:$task" >> /sdcard/openroot/queue/tasks.pending
    fi
  else
    log "Phone has adequate RAM ($PHONE_RAM KB) — local execution"
  fi
  
  echo "$target"
}

# Main
case "${1:-help}" in
  check)
    echo "Phone RAM: $PHONE_RAM KB"
    echo "Threshold: $THRESHOLD_MB KB"
    echo "OptiPlex: $(ping -c 1 -W 2 $OPTIPLEX_IP >/dev/null 2>&1 && echo 'reachable' || echo 'unreachable')"
    ;;
  route)
    route_task "$2"
    ;;
  *)
    echo "Usage: router.sh [check|route <task>]"
    ;;
esac
