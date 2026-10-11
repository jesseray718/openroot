#!/data/data/com.termux/files/usr/bin/python3
import os, re, glob

ROOT = "/data/data/com.termux/files/home/AERO_ROOT"
LOGS_DIR = os.path.join(ROOT, "06-ARCHIVE") # Adjust if your logs are elsewhere
REPORT_FILE = "/sdcard/Download/MISTAKE_ANALYSIS_REPORT.txt"

# Common Python/Termux Mistake Patterns & Their Fixes
MISTAKES = {
    "NameError": {
        "pattern": r"NameError: name '(\w+)' is not defined",
        "cause": "Variable or module (like 'inch') not imported or defined.",
        "fix": "Check imports at the top of the file. Did you forget 'from x import y'?"
    },
    "SyntaxError": {
        "pattern": r"SyntaxError: invalid syntax.*\nFile.*line (\d+)",
        "cause": "Typo, missing colon, or mixing shell commands in Python.",
        "fix": "Ensure the file contains ONLY Python code, no 'cd', 'ls', or 'echo' commands."
    },
    "NoModule": {
        "pattern": r"No module named '(\w+)'",
        "cause": "Missing package installation.",
        "fix": "Run: pip install <module_name>"
    },
    "PermissionDenied": {
        "pattern": r"Permission denied|Errno 13",
        "cause": "Android Scoped Storage restrictions.",
        "fix": "Use ~/storage/shared/ paths or run 'termux-setup-storage'."
    },
    "TabError": {
        "pattern": r"TabError.*indentation",
        "cause": "Mixed tabs and spaces.",
        "fix": "In Nano: Press Ctrl+] to convert spaces/tabs consistently."
    }
}

print("🔍 Scanning for mistakes in logs and scripts...")

errors_found = []
files_scanned = 0

# 1. Scan Log Files (if they exist)
log_files = glob.glob(os.path.join(ROOT, "**/*.txt")) + glob.glob(os.path.join(ROOT, "**/*.log"))
for f in log_files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()
            for err_type, info in MISTAKES.items():
                if re.search(info["pattern"], content):
                    errors_found.append({
                        "file": f,
                        "error": err_type,
                        "details": info["cause"],
                        "solution": info["fix"]
                    })
    except: pass

# 2. Scan Current Python Scripts for obvious syntax errors
py_files = glob.glob(os.path.join(ROOT, "**/*.py"))
for py_file in py_files:
    try:
        # Just check first few lines for non-Python garbage
        with open(py_file, "r", encoding="utf-8") as f:
            header = f.read(200)
            if not header.startswith("#!") and not header.startswith("def"):
                 if "cd " in header or "echo " in header:
                     errors_found.append({
                         "file": py_file,
                         "error": "Shell Code in Python",
                         "details": "File starts with shell commands instead of Python.",
                         "solution": "Delete lines like 'cd ~', 'ls', 'echo' from the top."
                     })
    except: pass

# Generate Report
print(f"Found {len(errors_found)} potential issues.")

with open(REPORT_FILE, "w") as report:
    report.write("="*60 + "\n")
    report.write("AERO-CEMENT SYSTEM: MISTAKE ANALYSIS REPORT\n")
    report.write(f"Generated: {os.popen('date').read().strip()}\n")
    report.write("="*60 + "\n\n")

    if not errors_found:
        report.write("✅ NO MAJOR ERRORS DETECTED IN LOGS.\n")
    else:
        for i, err in enumerate(errors_found, 1):
            report.write(f"Issue #{i}:\n")
            report.write(f"  File: {err['file']}\n")
            report.write(f"  Type: {err['error']}\n")
            report.write(f"  Cause: {err['details']}\n")
            report.write(f"  Action: {err['solution']}\n")
            report.write("-" * 40 + "\n")

    report.write("\n💡 LEARNING SUMMARY:\n")
    report.write("  1. Always check imports (e.g., 'from x import y') before using variables.\n")
    report.write("  2. Never put shell commands ('cd', 'ls') inside .py files.\n")
    report.write("  3. Use absolute paths (/sdcard/...) or ~/storage/shared/ for Android.\n")
    report.write("  4. Run 'termux-setup-storage' if permission errors occur.\n")

print(f"\n✅ Analysis Complete! Report saved to: {REPORT_FILE}")
print("   To view: cat /sdcard/Download/MISTAKE_ANALYSIS_REPORT.txt")
