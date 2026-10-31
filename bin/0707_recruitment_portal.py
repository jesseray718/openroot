#!/data/data/com.termux/files/usr/bin/env python3
"""
RAINBOW WARRIOR RECRUITMENT PORTAL v1.0
Intake form for Engineers, Coders, and Builders.
Saves applications to applicants.json for manual review.
"""
import os
import json
from datetime import datetime

DATA_DIR = os.path.expanduser("~/AERO_ROOT/06-COMMUNITY")
APP_FILE = os.path.join(DATA_DIR, "applicants.json")

def main():
    print("\n" + "="*50)
    print("🌈 JOIN THE RAINBOW WARRIORS")
    print("="*50)
    print("Mission: Decentralize Survival. Trash-to-Treasure.")
    print("We seek: Engineers, Coders, Farmers, Builders.")
    print("-" * 50)
    
    name = input("Name/Alias: ").strip()
    role = input("Role (e.g., Mechanical Engineer, Rust Dev): ").strip()
    skills = input("Key Skills (e.g., Stirling Engines, Solidity): ").strip()
    portfolio = input("Link to Portfolio/GitHub/Resume: ").strip()
    why = input("Why do you want to join? (One sentence): ").strip()
    
    applicant = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "role": role,
        "skills": skills,
        "portfolio": portfolio,
        "why": why,
        "status": "PENDING_REVIEW"
    }
    
    # Load existing or create new list
    if os.path.exists(APP_FILE):
        with open(APP_FILE, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []
    
    data.append(applicant)
    
    with open(APP_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    
    print("\n✅ Application Submitted!")
    print(f"   Stored locally at: {APP_FILE}")
    print("   Note: This is a local intake. For public launch, host this script or use a form.")
    print("="*50)

if __name__ == "__main__":
    main()
