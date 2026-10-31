import subprocess
def run_git(args):
    return subprocess.run(["git"] + args, capture_output=True, text=True, shell=False)
def clean_repo():
    print("[bot] Janitor: Cleaning repository state...")
    run_git(["checkout", "main"])
    run_git(["pull", "origin", "main"])
if __name__ == "__main__":
    clean_repo()
