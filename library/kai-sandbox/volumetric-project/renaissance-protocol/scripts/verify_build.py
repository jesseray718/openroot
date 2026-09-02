#!/usr/bin/env python3
"""
verify_build.py — Renaissance Protocol: Proof-of-Build Verification Tool
Version: 0.1.0 (Genesis)
Author: Jesse McMillen
License: CC-BY-SA-4.0

Runs on Termux (Android). Local-first, blockchain-ready.
"""

import json
import os
import hashlib
import time
import uuid
import base64
from datetime import datetime, timezone

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.expanduser("~"), "rns_data")
BUILDS_DIR = os.path.join(DATA_DIR, "builds")
INSPECTORS_DIR = os.path.join(DATA_DIR, "inspectors")
WALLET_FILE = os.path.join(DATA_DIR, "wallet.json")

MIN_INSPECTOR_STAKE = 100  # RNS tokens minimum to be an inspector
MIN_INSPECTORS_FOR_CONSENSUS = 3
INSPECTOR_MAX_VERIFICATION_PCT = 0.10  # No inspector verifies >10% of builds

BUILD_CATEGORIES = {
    "A": "Community Infrastructure",
    "B": "Cannabis & Agriculture",
    "C": "Suppressed Science Research",
    "D": "Open-Source Knowledge",
    "E": "Mechanical Renaissance",
}

PROHIBITED_CHEMICALS = ["glyphosate", "roundup", "paraquat", "dicamba",
                         "atrazine", "chlorpyrifos", "neonicotinoid"]

# ──────────────────────────────────────────────
# INITIALIZATION
# ──────────────────────────────────────────────

def init_directories():
    """Create the directory structure if it doesn't exist."""
    for d in [DATA_DIR, BUILDS_DIR, INSPECTORS_DIR]:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "w") as f:
            json.dump({"balance": 0, "staked": 0, "transactions": []}, f, indent=2)


def hash_data(data):
    """SHA-256 hash of a JSON string."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def timestamp_now():
    """ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────────────
# WALLET (SIMULATED — REPLACES WITH REAL CHAIN)
# ──────────────────────────────────────────────

class Wallet:
    """Simulated local wallet. Will be replaced by real blockchain integration."""

    def __init__(self):
        with open(WALLET_FILE, "r") as f:
            self.data = json.load(f)

    def save(self):
        with open(WALLET_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    @property
    def balance(self):
        return self.data["balance"]

    @property
    def staked(self):
        return self.data["staked"]

    def credit(self, amount, reason):
        self.data["balance"] += amount
        self.data["transactions"].append({
            "type": "credit",
            "amount": amount,
            "reason": reason,
            "timestamp": timestamp_now()
        })
        self.save()

    def debit(self, amount, reason):
        if self.data["balance"] < amount:
            return False
        self.data["balance"] -= amount
        self.data["transactions"].append({
            "type": "debit",
            "amount": amount,
            "reason": reason,
            "timestamp": timestamp_now()
        })
        self.save()
        return True

    def stake(self, amount):
        if self.data["balance"] < amount:
            return False
        self.data["balance"] -= amount
        self.data["staked"] += amount
        self.data["transactions"].append({
            "type": "stake",
            "amount": amount,
            "reason": "inspector_stake",
            "timestamp": timestamp_now()
        })
        self.save()
        return True

    def slash(self, amount, reason):
        """Destroy staked tokens (penalty for fraudulent verification)."""
        slash_amount = min(amount, self.data["staked"])
        self.data["staked"] -= slash_amount
        self.data["transactions"].append({
            "type": "slash",
            "amount": slash_amount,
            "reason": reason,
            "timestamp": timestamp_now()
        })
        self.save()
        return slash_amount


# ──────────────────────────────────────────────
# BUILDER: SUBMIT A BUILD
# ──────────────────────────────────────────────

def submit_build():
    """Walk a builder through submitting a Proof-of-Build claim."""

    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: SUBMIT A BUILD                ║")
    print("╚══════════════════════════════════════╝\n")

    # Category selection
    print("Build Categories:")
    for code, name in BUILD_CATEGORIES.items():
        print(f"  [{code}] {name}")

    cat = input("\nSelect category (A-E): ").strip().upper()
    if cat not in BUILD_CATEGORIES:
        print("❌ Invalid category.")
        return

    builder_name = input("Your name/handle: ").strip()
    build_title = input("Build title: ").strip()
    build_desc = input("Description: ").strip()
    location = input("Location (city/state or lat,lon): ").strip()

    # Materials check
    print("\n⚠️  Prohibited Chemical Check")
    materials = input("List all materials/chemicals used (comma-separated): ").strip().lower()
    mat_list = [m.strip() for m in materials.split(",")]
    violations = [m for m in mat_list if any(p in m for p in PROHIBITED_CHEMICALS)]

    if violations:
        print(f"\n❌ BUILD REJECTED — Prohibited chemicals detected: {violations}")
        print("   Builds using glyphosate, synthetic pesticides on food crops,")
        print("   or other prohibited substances are INVALID per Protocol rules.")
        return

    # Sensor data (manual entry for now)
    print("\n📊 Sensor/Data Readings (press Enter to skip any)")
    temp = input("  Temperature (°F or °C): ").strip() or "N/A"
    humidity = input("  Humidity (%): ").strip() or "N/A"
    airflow = input("  Airflow (CFM or m/s): ").strip() or "N/A"
    custom = input("  Custom reading (label:value): ").strip() or "N/A"

    # Photo hashes (user takes photos separately, we hash them)
    print("\n📸 Photo Evidence")
    print("   Take photos with your phone camera, then run:")
    print("   sha256sum /path/to/photo.jpg")
    photo_count = int(input("How many photos? ") or "0")
    photo_hashes = []
    for i in range(photo_count):
        h = input(f"  Hash of photo {i+1}: ").strip()
        photo_hashes.append(h)

    # Construct build object
    build_id = str(uuid.uuid4())
    build_data = {
        "build_id": build_id,
        "version": "0.1.0",
        "category": cat,
        "category_name": BUILD_CATEGORIES[cat],
        "builder": builder_name,
        "title": build_title,
        "description": build_desc,
        "location": location,
        "materials": mat_list,
        "prohibited_check": "PASS" if not violations else "FAIL",
        "sensor_data": {
            "temperature": temp,
            "humidity": humidity,
            "airflow": airflow,
            "custom": custom,
        },
        "photo_hashes": photo_hashes,
        "timestamp": timestamp_now(),
        "status": "PENDING_INSPECTION",
        "inspections": [],
        "hash": None,  # Computed after construction
    }

    # Compute integrity hash
    build_data["hash"] = hash_data(build_data)

    # Save
    filepath = os.path.join(BUILDS_DIR, f"{build_id}.json")
    with open(filepath, "w") as f:
        json.dump(build_data, f, indent=2)

    print(f"\n✅ BUILD SUBMITTED SUCCESSFULLY")
    print(f"   Build ID: {build_id}")
    print(f"   Status:   PENDING_INSPECTION")
    print(f"   File:     {filepath}")
    print(f"\n   Next: Assign inspectors to verify this build.")
# ──────────────────────────────────────────────
# INSPECTOR: REGISTER & VERIFY
# ──────────────────────────────────────────────

def register_inspector():
    """Register as an inspector by staking RNS tokens."""

    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: REGISTER AS INSPECTOR         ║")
    print("╚══════════════════════════════════════╝\n")

    inspector_id = str(uuid.uuid4())
    name = input("Your name/handle: ").strip()
    specialties = input("Specialties (comma-separated, e.g. cannabis,construction,hvac): ").strip()

    wallet = Wallet()

    print(f"\n💰 Current balance: {wallet.balance} RNS")
    print(f"   Minimum stake required: {MIN_INSPECTOR_STAKE} RNS")

    stake_amount = int(input("Stake amount (RNS): ").strip())

    if stake_amount < MIN_INSPECTOR_STAKE:
        print(f"❌ Minimum stake is {MIN_INSPECTOR_STAKE} RNS. You offered {stake_amount}.")
        return

    if not wallet.stake(stake_amount):
        print(f"❌ Insufficient balance. You have {wallet.balance} RNS.")
        return

    inspector_data = {
        "inspector_id": inspector_id,
        "name": name,
        "specialties": [s.strip() for s in specialties.split(",")],
        "stake": stake_amount,
        "registered": timestamp_now(),
        "verifications_completed": 0,
        "reputation": 100,
        "status": "ACTIVE",
    }

    filepath = os.path.join(INSPECTORS_DIR, f"{inspector_id}.json")
    with open(filepath, "w") as f:
        json.dump(inspector_data, f, indent=2)

    print(f"\n✅ INSPECTOR REGISTERED")
    print(f"   ID:     {inspector_id}")
    print(f"   Staked: {stake_amount} RNS")
    print(f"   ⚠️  WARNING: Fraudulent verifications will result in SLASHING")
    print(f"   (your staked tokens will be destroyed)")


def list_pending_builds():
    """Show all builds pending inspection."""
    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: PENDING BUILDS                ║")
    print("╚══════════════════════════════════════╝\n")

    found = False
    for filename in os.listdir(BUILDS_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(BUILDS_DIR, filename)
        with open(filepath, "r") as f:
            build = json.load(f)
        if build["status"] == "PENDING_INSPECTION":
            print(f"  ID:       {build['build_id'][:8]}...")
            print(f"  Title:    {build['title']}")
            print(f"  Category: {build['category_name']}")
            print(f"  Builder:  {build['builder']}")
            insp_count = len(build.get("inspections", []))
            print(f"  Inspected: {insp_count}/{MIN_INSPECTORS_FOR_CONSENSUS}")
            print()
            found = True

    if not found:
        print("  No pending builds. Submit one first.")


def inspect_build():
    """Inspector reviews and verifies/rejects a build."""

    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: INSPECT A BUILD               ║")
    print("╚══════════════════════════════════════╝\n")

    build_id = input("Enter Build ID (first 8 chars OK): ").strip()

    # Find the build
    build = None
    build_path = None
    for filename in os.listdir(BUILDS_DIR):
        if filename.startswith(build_id) and filename.endswith(".json"):
            build_path = os.path.join(BUILDS_DIR, filename)
            with open(build_path, "r") as f:
                build = json.load(f)
            break

    if not build:
        print("❌ Build not found.")
        return

    if build["status"] != "PENDING_INSPECTION":
        print(f"❌ Build status is '{build['status']}', not pending inspection.")
        return

    # Show build details
    print(f"\n📋 BUILD DETAILS")
    print(f"   Title:       {build['title']}")
    print(f"   Category:    {build['category_name']}")
    print(f"   Builder:     {build['builder']}")
    print(f"   Description: {build['description']}")
    print(f"   Location:    {build['location']}")
    print(f"   Materials:   {', '.join(build['materials'])}")
    print(f"   Prohibited:  {build['prohibited_check']}")
    print(f"   Sensor Data: {json.dumps(build['sensor_data'], indent=2)}")
    print(f"   Photos:      {len(build['photo_hashes'])} registered")

    inspector_name = input("\nYour inspector name: ").strip()

    # Verification checklist
    print("\n🔍 VERIFICATION CHECKLIST")
    print("   Answer each item honestly. Fraud = SLASHING.\n")

    checks = [
        "Did you physically visit this site or thoroughly review remote evidence?",
        "Does the build match the description and photos?",
        "Are sensor readings consistent with the claimed build?",
        "Are materials as declared (no prohibited substances)?",
        "Is this build beneficial to the community?",
    ]

    responses = []
    for i, check in enumerate(checks):
        ans = input(f"  [{i+1}] {check} (y/n): ").strip().lower()
        responses.append(ans == "y")

    notes = input("\n  Additional notes: ").strip()

    all_passed = all(responses)
    verdict = "VERIFIED" if all_passed else "REJECTED"

    # Record the inspection
    inspection_record = {
        "inspector": inspector_name,
        "timestamp": timestamp_now(),
        "checklist": dict(zip(
            [f"check_{i+1}" for i in range(len(checks))],
            responses
        )),
        "notes": notes,
        "verdict": verdict,
        "hash": None,
    }
    inspection_record["hash"] = hash_data(inspection_record)

    build["inspections"].append(inspection_record)

    # Check for consensus
    verified_count = sum(1 for i in build["inspections"] if i["verdict"] == "VERIFIED")
    rejected_count = sum(1 for i in build["inspections"] if i["verdict"] == "REJECTED")

    if verified_count >= MIN_INSPECTORS_FOR_CONSENSUS:
        build["status"] = "VERIFIED"
        print(f"\n✅ BUILD VERIFIED — Consensus reached ({verified_count}/{MIN_INSPECTORS_FOR_CONSENSUS})")
        print(f"   🪙 Mining reward: Builder earns RNS tokens!")
    elif rejected_count >= MIN_INSPECTORS_FOR_CONSENSUS:
        build["status"] = "REJECTED"
        print(f"\n❌ BUILD REJECTED — {rejected_count} inspectors rejected.")
    else:
        print(f"\n⏳ Inspection recorded. Waiting for more inspectors.")
        print(f"   Current: {verified_count} verified / {rejected_count} rejected")
        print(f"   Need: {MIN_INSPECTORS_FOR_CONSENSUS} for consensus")

    # Save updated build
    with open(build_path, "w") as f:
        json.dump(build, f, indent=2)

    print(f"\n   Inspection hash: {inspection_record['hash'][:16]}...")
# ──────────────────────────────────────────────
# DISPUTE RESOLUTION (APPEAL)
# ──────────────────────────────────────────────

def appeal_build():
    """Builder disputes an inspection result."""

    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: FILE AN APPEAL                ║")
    print("╚══════════════════════════════════════╝\n")

    build_id = input("Enter Build ID: ").strip()

    build = None
    build_path = None
    for filename in os.listdir(BUILDS_DIR):
        if filename.startswith(build_id) and filename.endswith(".json"):
            build_path = os.path.join(BUILDS_DIR, filename)
            with open(build_path, "r") as f:
                build = json.load(f)
            break

    if not build:
        print("❌ Build not found.")
        return

    if build["status"] not in ["REJECTED"]:
        print(f"❌ Can only appeal REJECTED builds. Current status: {build['status']}")
        return

    reason = input("Reason for appeal: ").strip()
    evidence = input("Additional evidence (description): ").strip()

    print("\n⚠️  Frivolous appeals cost RNS tokens.")
    confirm = input("Submit appeal? (y/n): ").strip().lower()

    if confirm != "y":
        print("Appeal cancelled.")
        return

    appeal_record = {
        "type": "appeal",
        "build_id": build["build_id"],
        "reason": reason,
        "evidence": evidence,
        "timestamp": timestamp_now(),
        "status": "PENDING_JURY",
    }

    # Save appeal alongside the build
    build["appeal"] = appeal_record
    build["status"] = "APPEAL_PENDING"

    with open(build_path, "w") as f:
        json.dump(build, f, indent=2)

    print("\n✅ Appeal submitted. Will go to a 21-member community jury.")
    print("   You will be notified when the jury reaches a decision.")


# ──────────────────────────────────────────────
# STATUS & VIEWING
# ──────────────────────────────────────────────

def view_all_builds():
    """Display a summary of all builds in the system."""

    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: ALL BUILDS                    ║")
    print("╚══════════════════════════════════════╝\n")

    if not os.listdir(BUILDS_DIR):
        print("  No builds yet. Submit the first one!")
        return

    status_icons = {
        "PENDING_INSPECTION": "⏳",
        "VERIFIED": "✅",
        "REJECTED": "❌",
        "APPEAL_PENDING": "⚖️",
    }

    for filename in sorted(os.listdir(BUILDS_DIR)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(BUILDS_DIR, filename), "r") as f:
            build = json.load(f)

        icon = status_icons.get(build["status"], "?")
        print(f"  {icon} [{build['category']}] {build['title']}")
        print(f"     Builder: {build['builder']} | Status: {build['status']}")
        print(f"     ID: {build['build_id'][:8]}... | Inspections: {len(build['inspections'])}")
        print()


def show_wallet():
    """Display wallet status."""

    print("\n╔══════════════════════════════════════╗")
    print("║   RNS: WALLET                        ║")
    print("╚══════════════════════════════════════╝\n")

    wallet = Wallet()
    print(f"  Balance: {wallet.balance} RNS")
    print(f"  Staked:  {wallet.staked} RNS")
    print(f"  Total:   {wallet.balance + wallet.staked} RNS")

    if wallet.data["transactions"]:
        print(f"\n  Recent transactions:")
        for tx in wallet.data["transactions"][-5:]:
            print(f"    {tx['type'].upper():8} {tx['amount']:6} RNS — {tx['reason']}")


# ──────────────────────────────────────────────
# MAIN MENU
# ──────────────────────────────────────────────

def main_menu():
    """Interactive menu for the Proof-of-Build system."""

    while True:
        print("\n╔══════════════════════════════════════════╗")
        print("║   RENAISSANCE PROTOCOL — Proof-of-Build  ║")
        print("║   Version 0.1.0 (Genesis)                ║")
        print("╠══════════════════════════════════════════╣")
        print("║                                          ║")
        print("║   [1] Submit a Build                     ║")
        print("║   [2] Register as Inspector              ║")
        print("║   [3] List Pending Builds                ║")
        print("║   [4] Inspect a Build                    ║")
        print("║   [5] Appeal a Rejection                 ║")
        print("║   [6] View All Builds                    ║")
        print("║   [7] Wallet Status                      ║")
        print("║   [0] Exit                               ║")
        print("║                                          ║")
        print("╚══════════════════════════════════════════╝")

        choice = input("\n  Choice: ").strip()

        actions = {
            "1": submit_build,
            "2": register_inspector,
            "3": list_pending_builds,
            "4": inspect_build,
            "5": appeal_build,
            "6": view_all_builds,
            "7": show_wallet,
        }

        if choice == "0":
            print("\n  🏗️  Keep building. The Beast starves when we work.\n")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("  ❌ Invalid choice.")


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    init_directories()
    print("""
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║   ██▀███ ▓█████▓█████ ▄▄▄█████▓      ║
    ║   ▓██ ▒██▒█▀  █▒█▀  █ ▓  ██▒ ▓▒     ║
    ║   ▓██ ░▄█  █  █  █  █ ▒ ▓██░ ▒░     ║
    ║   ▒██▀▀█▄ ▐████ ▐████ ░ ▓███          ║
    ║   ░██ ░ ▒ █  █  █  █   ▒▓▒           ║
    ║   ░  ░   █  █  █  █   ▒ ░▒░▓▒       ║
    ║                                       ║
    ║   RENAISSANCE PROTOCOL                ║
    ║   Proof-of-Build Verification Tool    ║
    ║   "The Beast starves when we build."  ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """)
    main_menu()
