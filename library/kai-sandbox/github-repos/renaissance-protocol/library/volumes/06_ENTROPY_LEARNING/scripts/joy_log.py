#!/usr/bin/env python3
"""
The Joy Log: A tool to reduce cognitive entropy and maximize alignment.
Author: Jesse McMillen
Purpose: Track micro-wins and adjust expectations to generate Joy.
"""

import json
import os
from datetime import datetime

LOG_FILE = os.path.expanduser("~/rns/logs/joy_log.json")

def ensure_log_exists():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            json.dump([], f)

def get_today_entries():
    ensure_log_exists()
    with open(LOG_FILE, 'r') as f:
        data = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    return [entry for entry in data if entry['date'] == today]

def add_entry():
    print("\n--- THE JOY LOG ---")
    print("What is ONE thing you accomplished today? (Keep it small)")
    print("Examples: 'Installed python', 'Mixed 1 cup of cement', 'Wrote 1 line of code'")
    
    achievement = input("> ").strip()
    
    if not achievement:
        print("No entry recorded. Remember: Even breathing is a win.")
        return

    print("\nHow did this make you feel? (Scale 1-10, 10 = Pure Joy)")
    try:
        score = int(input("> "))
    except ValueError:
        score = 5 # Default if invalid

    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "achievement": achievement,
        "joy_score": score,
        "note": "Progress is real. The Beast is shrinking."
    }

    # Append to file
    with open(LOG_FILE, 'r') as f:
        data = json.load(f)
    data.append(entry)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"\n✅ Logged: '{achievement}'")
    print(f"🔥 Joy Score: {score}/10")
    print("Remember: You are building the Kingdom. One brick at a time.")

def show_summary():
    entries = get_today_entries()
    if not entries:
        print("\nNo entries for today. Start small!")
        return

    print("\n--- TODAY'S WINS ---")
    total_joy = 0
    for i, entry in enumerate(entries, 1):
        print(f"{i}. {entry['achievement']} (Joy: {entry['joy_score']})")
        total_joy += entry['joy_score']
    
    avg_joy = total_joy / len(entries)
    print(f"\n🌟 Total Wins: {len(entries)}")
    print(f"🌟 Average Joy: {avg_joy:.1f}/10")
    
    if avg_joy > 7:
        print("🚀 You are in FLOW. Keep going!")
    elif avg_joy > 4:
        print("⚡ Good progress. Stay steady.")
    else:
        print("🛠️ Low energy? Rest is part of the build. Tomorrow is a new day.")

def main():
    print("🌍 RENAISSANCE PROTOCOL: JOY MODULE")
    print("1. Log a Win")
    print("2. View Today's Summary")
    print("3. Exit")
    
    choice = input("Choose (1-3): ")
    
    if choice == '1':
        add_entry()
    elif choice == '2':
        show_summary()
    elif choice == '3':
        print("Peace be with you, Jesse.")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()