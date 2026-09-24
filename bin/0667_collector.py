#!/data/data/com.termux/files/usr/bin/env python3
"""
SENSOR DATA COLLECTOR v1.0
Collects temperature, humidity, flow rate from ESP32 sensors via serial/USB.
Stores data in CSV format for analysis.
"""
import csv
import time
from datetime import datetime

DATA_FILE = os.path.expanduser("~/AERO_ROOT/05-DATA/logs/sensor_data.csv")

def main():
    print("📡 Starting sensor data collection...")
    print(f"Data will be saved to: {DATA_FILE}")
    
    # Initialize CSV if not exists
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'temp_c', 'humidity_pct', 'flow_rate_m3s', 'solar_irradiance_w'])
    
    while True:
        try:
            # Placeholder for serial read logic
            timestamp = datetime.now().isoformat()
            temp_c = float(input("Temp (°C): "))
            humidity_pct = float(input("Humidity (%): "))
            flow_rate = float(input("Flow Rate (m³/s): "))
            solar_irradiance = float(input("Solar Irradiance (W/m²): "))
            
            with open(DATA_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, temp_c, humidity_pct, flow_rate, solar_irradiance])
            
            print(f"✅ Data point recorded at {timestamp}")
            
        except KeyboardInterrupt:
            print("\n🛑 Collection stopped by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

if __name__ == "__main__":
    main()
