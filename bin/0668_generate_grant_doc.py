#!/data/data/com.termux/files/usr/bin/python3
import os

# Paths
input_file = "/data/data/com.termux/files/home/AERO_ROOT/99-INBOX/downloads/MASTER_CONTEXT_ANCHOR_v2.txt"
output_file = "/sdcard/Download/AeroCement_Grant_Document.txt"

print(f"📄 Generating Grant Document from: {input_file}")

try:
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()
except FileNotFoundError:
    print("❌ Error: Source file not found.")
    exit(1)

# Add Professional Header
header = """================================================================================
          OFFICIAL GRANT PROPOSAL DOCUMENT
          PROJECT: AEROCENT ECOSYSTEM & OPEN-CELL AEROCEMENT
================================================================================
PRINCIPAL INVESTIGATOR: Jesse McMillen
DATE: June 8, 2026
STATUS: Physics Validated | Patent Pending Strategy
CONTACT: [Your Email Here]
================================================================================

"""

# Ensure PTTR typo is fixed in the final output
clean_content = content.replace("PTTR): 000:1", "PTTR): >9,000:1").replace("PTTR: 000:1", "PTTR: >9,000:1")

full_document = header + "\n" + clean_content

with open(output_file, "w", encoding="utf-8") as f:
    f.write(full_document)

file_size = os.path.getsize(output_file) / 1024 # KB
print(f"✅ SUCCESS! Grant Document created.")
print(f"   Location: {output_file}")
print(f"   Size: {file_size:.1f} KB (Should be ~50+ KB for full text)")
print(f"\n   To view immediately: cat '{output_file}'")
print(f"   Or find it in your Downloads folder.")
