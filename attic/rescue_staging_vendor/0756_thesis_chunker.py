#!/data/data/com.termux/files/usr/bin/env python3
"""
THESIS CHUNKER v1.0
Displays thesis text one chunk at a time for manual Exodus injection.
You copy → paste into Exodus memo → send → press Enter here for next.
"""

THESIS = """CIVILIZATION 2.0 - THE THESIS
MISSION: Decentralize survival. Trash-to-Treasure. Open Source everything.
PHILOSOPHY: No Patents. No Monopolies. No Hierarchy.

PILLAR 1: SHELTER
Aerocement Geodesic Domes. Cardboard formwork. 21-day wet cure mandatory.
Trash becomes shelter for the people.

PILLAR 2: ENERGY
Passive Solar Thermal Loop. PTTR greater than 9000 to 1.
Zero fans. Pure buoyancy. Heat + Cold + Electricity from sunlight.

PILLAR 3: LIFE
Biointensive Permaculture. Black Locust agroforestry. Quail Towers.
Ferrocement Aquaponics. Food sovereignty without corporations.

PILLAR 4: MOBILITY
Thermal Battery Vehicles. Stirling engines on hot concrete blocks.
Freedom of movement without fuel dependence.

TOKEN ECONOMY:
Proof-of-Help. PoPW tokens backed by verified physical work.
One token equals one joule saved or one square foot of shelter built.

RAINBOW WARRIORS:
A tribe of all colors, classes, and creeds.
Making centralized extraction irrelevant through superior alternatives.

As Above, So Below. As Within, So Without."""

MAX_CHUNK = 180

def split_text(text, max_len):
    chunks = []
    words = text.split()
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if len(test.encode('utf-8')) <= max_len:
            current = test
        else:
            if current:
                chunks.append(current)
            current = word
    if current:
        chunks.append(current)
    return chunks

def main():
    chunks = split_text(THESIS, MAX_CHUNK)
    print(f"📜 THESIS CHUNKER — {len(chunks)} chunks ready")
    print(f"💡 How to use:")
    print(f"   1. Read the chunk below")
    print(f"   2. Open Exodus → Send $0.03 to yourself")
    print(f"   3. Paste this chunk into the MEMO field")
    print(f"   4. Send it")
    print(f"   5. Come back here and press Enter for next chunk")
    print(f"   Type 'q' to quit, 'r' to replay current chunk\n")

    i = 0
    while i < len(chunks):
        print("=" * 50)
        print(f"CHUNK {i+1} of {len(chunks)}")
        print("=" * 50)
        print(f"\n{chunks[i]}\n")
        print("-" * 50)
        cmd = input("Press Enter for next chunk (q=quit, r=replay): ").strip()
        if cmd.lower() == 'q':
            print(f"\n👋 Paused at chunk {i+1}. Run again to resume from here.")
            break
        elif cmd.lower() == 'r':
            continue
        else:
            i += 1
    else:
        print("\n🎉 ENTIRE THESIS INJECTED! You wrote history on the blockchain.")

if __name__ == "__main__":
    main()
