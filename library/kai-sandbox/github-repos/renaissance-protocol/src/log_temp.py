cat > ~/rns/scripts/log_temp.py << 'LOGGER'
#!/usr/bin/env python3
"""
TEMP LOGGER FOR AEROCEMENT PROTOTYPE
Reads DS18B20 sensors via Arduino/ESP32 connected to Termux.
"""
import serial
import serial.tools.list_ports
import time
import csv
from datetime import datetime

def find_port():
    ports = serial.tools.list_ports.comports()
    print("Available Ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
    choice = input("Select Port Number: ")
    try:
        return ports[int(choice)].device
    except:
        return None

def log_data():
    port = find_port()
    if not port:
        print("No port selected.")
        return

    try:
        ser = serial.Serial(port, 9600, timeout=1)
        print(f"Connected to {port}")
        
        filename = f"~/rns/logs/temp_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Sensor1_Inlet", "Sensor2_Mid", "Sensor3_Exit"])
            
            print("Logging started. Press Ctrl+C to stop.")
            start_time = time.time()
            
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if ',' in line:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow([timestamp] + line.split(','))
                        print(f"[{timestamp}] {line}")
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nLogging stopped.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    print("=== AEROCEMENT TEMP LOGGER ===")
    log_data()
LOGGER