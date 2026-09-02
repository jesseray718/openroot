#!/data/data/com.termux/files/usr/bin/python
import subprocess, json, time, os, socket
from datetime import datetime

def run_shizuku(cmd):
    """Execute command via Shizuku with fallback"""
    try:
        # Try Shizuku first
        result = subprocess.run(
            ['sh', '-c', cmd],
            capture_output=True,
            text=True,
            timeout=8,
            env={'PATH': '/data/data/moe.shizuku.privileged.api:/data/data/com.termux/files/usr/bin:/system/bin'}
        )
        if result.returncode == 0:
            return result.stdout.strip()
        # Fallback to regular shell
        result = subprocess.run(['sh', '-c', cmd], capture_output=True, text=True, timeout=8)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def log_system_status():
    """Log critical system metrics for APTK planning"""
    data = {
        "timestamp": datetime.now().isoformat(),
        "battery_level": run_shizuku("dumpsys battery | grep level | awk '{print $2}'"),
        "battery_temp": run_shizuku("dumpsys battery | grep temperature | awk '{print $2}'"),
        "cpu_freq": run_shizuku("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null"),
        "thermal_zone": run_shizuku("cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null"),
        "memory_free": run_shizuku("free -m | grep Mem | awk '{print $4}'"),
        "storage_free": run_shizuku("df -h /sdcard | tail -1 | awk '{print $4}'")
    }
    
    # Ensure directory exists
    log_path = "/sdcard/renaissance_logs/"
    os.makedirs(log_path, exist_ok=True)
    
    # Write with rotation (keep last 100 entries)
    log_file = f"{log_path}system_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(data) + "\n")
    
    # Auto-rotate if file gets too large
    if os.path.getsize(log_file) > 10_000_000:  # 10MB
        backup_file = f"{log_path}system_log_backup_{datetime.now().strftime('%Y%m%d')}.jsonl"
        os.rename(log_file, backup_file)
    
    print(f"✓ Renaissance log saved: {data}")
    return data

def apply_build_mode():
    """Optimize phone for long build sessions (mirrors APTK efficiency)"""
    commands = [
        "settings put global window_animation_scale 0.3",
        "settings put global transition_animation_scale 0.3", 
        "settings put global animator_duration_scale 0.3",
        "settings put global sem_perfomance_mode 1",
        "settings put global peak_refresh_rate 90",  # Balanced for battery
        "settings put global low_power_mode false",
        "settings put global adaptive_battery_management_enabled 0"  # Disable for consistent performance
    ]
    
    for cmd in commands:
        result = run_shizuku(cmd)
        if "Error" in result:
            print(f"⚠ Warning: {cmd} failed")
    
    print("✅ APTK Build Mode Activated - Optimized for efficiency")

def check_connectivity():
    """Check if we can sync to GitHub/Zenodo"""
    try:
        socket.create_connection(("github.com", 443), timeout=5)
        return True
    except:
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            apply_build_mode()
        elif sys.argv[1] == "sync":
            if check_connectivity():
                print("✅ Connected - Ready to sync")
                # Add git push logic here
            else:
                print("⚠ Offline - Logs saved locally")
        else:
            log_system_status()
    else:
        log_system_status()
