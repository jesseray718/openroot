# DELL OPTIPLEX 3040 SETUP GUIDE

## Step 1: Physical Inspection

1. **Check all connections:**
   - Power cable firmly seated
   - Monitor cable secure
   - USB devices connected properly
   - Network cable (if using Ethernet)

2. **Inspect for damage:**
   - No bent pins
   - No bulging capacitors
   - No burn marks
   - Fans spin freely

## Step 2: Power Cycle Test

1. Unplug power cable
2. Hold power button for 30 seconds (discharge capacitors)
3. Reconnect power
4. Press power button
5. Observe LED behavior:
   - Solid white: Normal boot
   - Blinking amber: Hardware issue
   - No lights: Power supply problem

## Step 3: BIOS Access

1. Power on
2. Immediately press F2 repeatedly
3. If no response, try F12 for boot menu
4. If still no response, reset CMOS (see below)

## Step 4: CMOS Reset (if needed)

1. Unplug power
2. Open case
3. Locate CMOS battery (CR2032)
4. Remove battery for 5 minutes
5. Reinsert battery
6. Reconnect power
7. Try booting again

## Step 5: Ubuntu Installation

1. Insert flash drive with Ubuntu ISO
2. Boot and press F12 for boot menu
3. Select USB drive
4. Choose "Try or Install Ubuntu"
5. Follow installation prompts
6. When asked about installation type, choose:
   - "Erase disk and install Ubuntu" (for clean install)
   - Or manual partitioning for dual boot

## Step 6: Bluetooth Setup

After Ubuntu installation:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Bluetooth tools
sudo apt install bluetooth bluez blueman

# Start Bluetooth service
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# Add user to bluetooth group
sudo usermod -aG bluetooth $USER

# Reboot
sudo reboot

# After reboot, pair devices via GUI or:
bluetoothctl
power on
agent on
scan on
# Find your device MAC address
pair <MAC>
connect <MAC>
trust <MAC>
```

## Step 7: Verify All Hardware

```bash
# Check system info
lshw -short

# Check Bluetooth
hciconfig -a
rfkill list

# Check network
ip a
ping google.com
```

## Troubleshooting

### If it turns on then immediately off:
1. Check power supply connections
2. Try different power outlet
3. Test with minimal hardware (1 RAM stick, no drives)
4. Inspect for overheating
5. Check CMOS battery voltage

### If no display:
1. Try different monitor/cable
2. Reset BIOS (remove CMOS battery)
3. Test with different GPU if available
4. Check RAM seating

### If Bluetooth not working:
1. Check if hardware switch is on
2. Verify Bluetooth adapter detected (lsusb)
3. Check kernel modules (lsmod | grep bluetooth)
4. Try different USB port if using dongle
