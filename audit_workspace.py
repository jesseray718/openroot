from pathlib import Path

root = Path(".")
ignore_dirs = {"venv", "node_modules", ".git", "__pycache__"}

root_files = [f.name for f in root.iterdir() if f.is_file()]
bin_scripts = [f.name for f in (root / "bin").iterdir() if f.is_file()] if (root / "bin").exists() else []

# Filtered python file count avoiding heavy dirs
python_scripts = [
    p for p in root.glob("**/*.py")
    if not any(part in ignore_dirs for part in p.parts)
]

print("=== CLEANED OPENROOT WORKSPACE AUDIT ===")
print(f"Total root files: {len(root_files)}")
print(f"Bin scripts available: {len(bin_scripts)}")
print(f"Filtered Python files found: {len(python_scripts)}")

if (root / ".git").exists():
    import subprocess
    git_status = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    print("\n=== GIT STATUS ===")
    print(git_status.stdout if git_status.stdout else "Working tree clean.")
