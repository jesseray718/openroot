import re

with open("constitutive_voice_engine.py", "r") as f:
    code = f.read()

new_func = '''def capture_voice_input():
    """Real voice capture via Android termux-speech-to-text."""
    import subprocess
    try:
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True, text=True, timeout=15
        )
        text = result.stdout.strip()
        if text:
            return text
        print("[WARN] No speech detected. SIMULATED MODE.")
        return "Amendment H-004: Thermal Labyrinth efficiency increased to 98%"
    except Exception as e:
        print(f"[WARN] termux-speech-to-text failed ({e}). SIMULATED MODE.")
        return "Amendment H-004: Thermal Labyrinth efficiency increased to 98%"
'''

# Replace old function with new one
pattern = r'def capture_voice_input\(\):.*?(?=\ndef )'
code = re.sub(pattern, new_func + "\n\n", code, flags=re.DOTALL)

with open("constitutive_voice_engine.py", "w") as f:
    f.write(code)
print("[PATCHED] Voice capture updated to termux-speech-to-text")
