import json

def book_slot(date, time):
    with open("data/ewaste/slots.json", "r+") as f:
        slots = json.load(f)
        if date in slots and time in slots[date]:
            slots[date].remove(time)
            f.seek(0)
            json.dump(slots, f, indent=4)
            print(f"[logistics] Slot {date} {time} booked successfully.")
        else:
            print("[alert] Slot unavailable.")

if __name__ == "__main__":
    # Example: Book a pickup
    book_slot("2026-11-01", "09:00")
