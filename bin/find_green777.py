#!/usr/bin/env python3
import os, stat, time

ROOTS = [
    "/home/jesse/openroot",
    "/home/jesse/une",
    "/home/jesse/wisdom-scaffold",
    "/home/jesse/black-locust-rmh",
    "/home/jesse/agapenet",
    "/home/jesse/Sync",
    "/home/jesse/bin",
    "/opt",
    "/usr/local",
    "/etc",
]
SKIP_DIR = {".git", "__pycache__", "node_modules", ".stversions", "models", ".cache"}
OUT = "/home/jesse/openroot/outbox/GREEN777_SSH.txt"

rows_file = []
rows_dir = []
named = []
world_exec = []
errs = 0
now = time.strftime("%Y-%m-%dT%H:%M:%S")

for root in ROOTS:
    if not os.path.exists(root):
        continue
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR]
        for name in list(dirnames) + list(filenames):
            p = os.path.join(dirpath, name)
            try:
                st = os.lstat(p)
            except OSError:
                errs += 1
                continue
            mo = stat.S_IMODE(st.st_mode)
            isdir = stat.S_ISDIR(st.st_mode)
            isreg = stat.S_ISREG(st.st_mode)
            islnk = stat.S_ISLNK(st.st_mode)
            if "777" in name.lower() or name.lower().startswith("green"):
                named.append((mo, "dir" if isdir else "file", st.st_size, p))
            if islnk:
                continue
            if mo == 0o777:
                rec = (mo, "dir" if isdir else "file", st.st_size, p)
                (rows_dir if isdir else rows_file).append(rec)
            # green in ls = executable bit on a regular file
            if isreg and (st.st_mode & stat.S_IXUSR) and (mo & 0o002):
                world_exec.append((mo, "file", st.st_size, p))

def fmt(rec):
    mo, k, sz, p = rec
    return "%03o  %-4s  %10d  %s" % (mo, k, sz, p)

with open(OUT, "w") as f:
    f.write("# GREEN777 SSH optiplex3060  " + now + "\n")
    f.write("# 777 file = world-writable + executable. This is the real smell.\n\n")
    f.write("== 777 REGULAR FILES count=%d ==\n" % len(rows_file))
    for r in sorted(rows_file, key=lambda x: x[3]):
        f.write(fmt(r) + "\n")
    f.write("\n== 777 DIRECTORIES count=%d ==\n" % len(rows_dir))
    for r in sorted(rows_dir, key=lambda x: x[3]):
        f.write(fmt(r) + "\n")
    f.write("\n== WORLD-WRITABLE EXECUTABLES (any mode, other-write + x) count=%d ==\n" % len(world_exec))
    for r in sorted(world_exec, key=lambda x: x[3]):
        f.write(fmt(r) + "\n")
    f.write("\n== NAME HIT *777* or green* ==\n")
    for r in named:
        f.write(fmt(r) + "\n")
    f.write("\n# errors=%d\n" % errs)

print("wrote", OUT)
print("files", len(rows_file), "dirs", len(rows_dir), "world_exec", len(world_exec), "names", len(named), "errors", errs)
