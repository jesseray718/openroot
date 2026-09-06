#!/bin/bash
################################################################################
# sensor_log.sh — OpenRoot Canonical Sensor Logger
#
# Purpose: Log DS18B20 temperature data to CSV, upload to IPFS every 1000 readings
# Usage: 
#   ./sensor_log.sh start                 # Begin continuous logging (background)
#   ./sensor_log.sh stop                  # Stop logging
#   ./sensor_log.sh read                  # One-time read (debugging)
#   ./sensor_log.sh publish               # Publish current CSV to IPFS
#   ./sensor_log.sh install               # Install dependencies (Termux/RPi)
#
# Environment:
#   SENSOR_LOG_DIR        Log directory (default: /root/openroot-logs)
#   NODE_NAME             Node identifier (default: node-zero)
#   IPFS_GATEWAY          IPFS node or Pinata API (optional)
#   IPFS_API_KEY          Pinata API key (optional)
#
# CSV Schema (canonical, immutable):
#   timestamp,inlet_C,outlet_C,ambient_C,panel_C,solar_W_m2,notes
#   2026-06-28T14:23:45Z,42.3,67.8,28.5,71.2,850,clear skies
#
# Sensors (OneWire, DS18B20):
#   28-0119A27BDA2F → inlet (copper coil entry)
#   28-0119A27C1A4C → outlet (copper coil exit)  
#   28-0119A27D0E5F → ambient (outdoor, shaded)
#   28-0119A27E3F2C → panel (embedded absorber surface)
#
# Assumptions:
#   - Raspberry Pi or compatible Linux with /sys/bus/w1/devices/
#   - DS18B20 sensors pre-wired on GPIO4 (OneWire overlay enabled)
#   - Curl and jq for IPFS uploads
#   - User runs script from /root or with appropriate paths
#
################################################################################

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

SENSOR_LOG_DIR="${SENSOR_LOG_DIR:-/root/openroot-logs}"
NODE_NAME="${NODE_NAME:-node-zero}"
IPFS_GATEWAY="${IPFS_GATEWAY:-http://localhost:5001}"
IPFS_PINATA_API="${IPFS_PINATA_API:-https://api.pinata.cloud}"
LOG_FILE="${SENSOR_LOG_DIR}/${NODE_NAME}_sensor_log.csv"
PID_FILE="${SENSOR_LOG_DIR}/.sensor_log.pid"
READINGS_PER_UPLOAD=1000

# Sensor addresses (OneWire device IDs)
# CUSTOMIZE THESE for your specific sensors
SENSOR_INLET="28-0119a27bda2f"      # Copper coil inlet
SENSOR_OUTLET="28-0119a27c1a4c"     # Copper coil outlet
SENSOR_AMBIENT="28-0119a27d0e5f"    # Outdoor ambient (shaded)
SENSOR_PANEL="28-0119a27e3f2c"      # Panel absorber surface

# Logging interval (seconds)
INTERVAL="${INTERVAL:-300}"           # 5 minutes default

# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >&2
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Read DS18B20 sensor value (OneWire)
read_sensor() {
    local sensor_id=$1
    local dev_path="/sys/bus/w1/devices/${sensor_id}/w1_slave"
    
    if [[ ! -f "$dev_path" ]]; then
        echo "ERROR"
        return 1
    fi
    
    # OneWire format: two lines, temp on second line after "t="
    local raw_temp=$(grep "^[0-9a-f].*YES$" "$dev_path" 2>/dev/null || echo "")
    if [[ -z "$raw_temp" ]]; then
        echo "ERROR"
        return 1
    fi
    
    # Extract temp: "t=42312" means 42.312°C
    local temp_raw=$(echo "$raw_temp" | grep -oP "(?<=t=)\d+" || echo "")
    if [[ -z "$temp_raw" ]]; then
        echo "ERROR"
        return 1
    fi
    
    # Convert to Celsius (divide by 1000)
    local temp_c=$(echo "scale=2; $temp_raw / 1000" | bc 2>/dev/null || echo "ERROR")
    echo "$temp_c"
}

# One-time sensor read (for debugging)
read_all_sensors() {
    local inlet=$(read_sensor "$SENSOR_INLET")
    local outlet=$(read_sensor "$SENSOR_OUTLET")
    local ambient=$(read_sensor "$SENSOR_AMBIENT")
    local panel=$(read_sensor "$SENSOR_PANEL")
    
    log_info "Inlet: ${inlet}°C | Outlet: ${outlet}°C | Ambient: ${ambient}°C | Panel: ${panel}°C"
    
    if [[ "$inlet" == "ERROR" ]] || [[ "$outlet" == "ERROR" ]]; then
        log_error "Sensor read failed — check OneWire wiring and /sys/bus/w1/devices/"
        return 1
    fi
}

# Create CSV header (first run only)
init_csv() {
    if [[ ! -f "$LOG_FILE" ]]; then
        mkdir -p "$SENSOR_LOG_DIR"
        echo "timestamp,inlet_C,outlet_C,ambient_C,panel_C,solar_W_m2,notes" > "$LOG_FILE"
        log_info "Created CSV: $LOG_FILE"
    fi
}

# Log one row
log_reading() {
    local inlet=$(read_sensor "$SENSOR_INLET")
    local outlet=$(read_sensor "$SENSOR_OUTLET")
    local ambient=$(read_sensor "$SENSOR_AMBIENT")
    local panel=$(read_sensor "$SENSOR_PANEL")
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local notes="${1:-}"
    
    # Fail gracefully if any sensor errors
    if [[ "$inlet" == "ERROR" ]] || [[ "$outlet" == "ERROR" ]]; then
        log_error "Sensor read failed at $timestamp"
        return 1
    fi
    
    # Solar irradiance placeholder (0 = no data yet; integrate solar sensor separately)
    local solar_w_m2="0"
    
    # Append row to CSV
    echo "${timestamp},${inlet},${outlet},${ambient},${panel},${solar_w_m2},${notes}" >> "$LOG_FILE"
    
    # Calculate delta-T for display
    local delta_t=$(echo "scale=1; $outlet - $inlet" | bc)
    log_info "Logged: inlet=${inlet}°C outlet=${outlet}°C Δ=${delta_t}°C"
}

# Check if it's time to upload (every N readings)
should_upload() {
    local line_count=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
    # Header is line 1, so subtract 1 for actual readings
    local readings=$((line_count - 1))
    
    if (( readings > 0 && readings % READINGS_PER_UPLOAD == 0 )); then
        return 0
    fi
    return 1
}

# Upload CSV to IPFS via Pinata (preferred) or local gateway
upload_to_ipfs() {
    if [[ ! -f "$LOG_FILE" ]]; then
        log_error "CSV file not found: $LOG_FILE"
        return 1
    fi
    
    log_info "Uploading $LOG_FILE to IPFS..."
    
    # Try Pinata first (preferred: immutable, CDN)
    if [[ -n "${IPFS_API_KEY:-}" ]]; then
        local response=$(curl -s -X POST \
            -H "pinata_api_key: ${IPFS_API_KEY}" \
            -H "pinata_secret_api_key: ${IPFS_SECRET_API_KEY:-}" \
            -F "file=@${LOG_FILE}" \
            "${IPFS_PINATA_API}/pinning/pinFileToIPFS" 2>&1)
        
        local ipfs_hash=$(echo "$response" | jq -r '.IpfsHash // empty' 2>/dev/null || echo "")
        if [[ -n "$ipfs_hash" ]]; then
            log_info "IPFS published: ipfs://${ipfs_hash}"
            echo "ipfs://${ipfs_hash}" > "${SENSOR_LOG_DIR}/.last_upload_hash"
            return 0
        fi
    fi
    
    # Fallback: local gateway
    log_info "Pinata unavailable, trying local gateway..."
    local response=$(curl -s -X POST \
        -F "file=@${LOG_FILE}" \
        "${IPFS_GATEWAY}/api/v0/add?wrap-with-directory=true" 2>&1)
    
    local ipfs_hash=$(echo "$response" | jq -r '.Hash // empty' 2>/dev/null || echo "")
    if [[ -n "$ipfs_hash" ]]; then
        log_info "IPFS published (local): ipfs://${ipfs_hash}"
        echo "ipfs://${ipfs_hash}" > "${SENSOR_LOG_DIR}/.last_upload_hash"
        return 0
    fi
    
    log_error "IPFS upload failed"
    return 1
}

# Continuous logging loop
logging_loop() {
    init_csv
    log_info "Starting sensor logging (interval: ${INTERVAL}s)"
    
    while true; do
        log_reading
        
        # Check if it's time to upload
        if should_upload; then
            upload_to_ipfs || log_error "Upload failed (will retry next batch)"
        fi
        
        sleep "$INTERVAL"
    done
}

# Start logging in background
start_logging() {
    if [[ -f "$PID_FILE" ]]; then
        local old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_error "Logging already running (PID: $old_pid)"
            return 1
        fi
    fi
    
    nohup "$0" _loop > "${SENSOR_LOG_DIR}/sensor_log.out" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"
    log_info "Started logging in background (PID: $pid)"
}

# Stop logging
stop_logging() {
    if [[ ! -f "$PID_FILE" ]]; then
        log_error "No PID file found"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        rm "$PID_FILE"
        log_info "Stopped logging (PID: $pid)"
    else
        log_error "Process not running (stale PID: $pid)"
        rm "$PID_FILE"
    fi
}

# Install dependencies (Termux/Raspberry Pi)
install_deps() {
    log_info "Installing dependencies..."
    
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y curl jq bc
        log_info "Installed curl, jq, bc"
    elif command -v pkg &> /dev/null; then
        # Termux
        pkg install -y curl jq bc
        log_info "Installed curl, jq, bc (Termux)"
    else
        log_error "Package manager not found. Install curl, jq, bc manually."
        return 1
    fi
    
    # Verify OneWire is loaded
    if [[ ! -d /sys/bus/w1/devices ]]; then
        log_error "/sys/bus/w1/ not found. Enable OneWire in /boot/config.txt:"
        echo "  dtoverlay=w1-gpio,gpiopin=4"
        echo "Then reboot."
        return 1
    fi
    
    log_info "OneWire detected. Ready to log."
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

main() {
    case "${1:-read}" in
        start)
            start_logging
            ;;
        stop)
            stop_logging
            ;;
        read)
            read_all_sensors
            ;;
        log)
            init_csv
            log_reading "${2:-}"
            ;;
        publish)
            upload_to_ipfs
            ;;
        install)
            install_deps
            ;;
        _loop)
            # Internal: don't call directly
            logging_loop
            ;;
        *)
            cat <<EOF
Usage: $(basename "$0") COMMAND [ARGS]

Commands:
  start               Begin continuous logging (background)
  stop                Stop logging
  read                One-time sensor read (debugging)
  log [NOTES]         Log one reading with optional notes
  publish             Manually upload CSV to IPFS
  install             Install dependencies (curl, jq, bc)

Environment Variables:
  SENSOR_LOG_DIR      Log directory (default: /root/openroot-logs)
  NODE_NAME           Node name (default: node-zero)
  IPFS_API_KEY        Pinata API key (optional, for upload)
  INTERVAL            Logging interval in seconds (default: 300)

Example:
  export NODE_NAME="node-florida"
  export INTERVAL=600
  ./sensor_log.sh start
  
  # Check status
  tail -f /root/openroot-logs/node-florida_sensor_log.csv
  
  # Stop and upload
  ./sensor_log.sh publish
  ./sensor_log.sh stop

CSV Format (immutable schema):
  timestamp,inlet_C,outlet_C,ambient_C,panel_C,solar_W_m2,notes

Sensors (OneWire addresses, customize in script):
  - inlet: $SENSOR_INLET
  - outlet: $SENSOR_OUTLET
  - ambient: $SENSOR_AMBIENT
  - panel: $SENSOR_PANEL

References:
  - projects/aerocement/START-HERE.md (sensor wiring)
  - research/README.md (data validation)
  - bounties/README.md (submission format)

EOF
            exit 1
            ;;
    esac
}

main "$@"
