# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python3
# pod_pipeline_v1.py - any-file to pod: txt/md/code/pdf/zip -> sha256+blake3+fts5+nomic+merkle
# Wraps bin/pod_loader_v1.py (reuse, no schema fork). Run on OptiPlex (ollama for embed).
# Subcommands: ingest | embed | seal | query | status | lesson
# Canary: CANARY:OPENROOT-POD-PIPELINE-V1
import os, sys, time, hashlib, zipfile, subprocess
from pathlib import Path

BIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BIN))
try:
    import pod_loader_v1 as pl
except Exception as e:
    print("[held] import pod_loader_v1 failed:", e); sys.exit(1)

REPO = Path(os.environ.get("OPENROOT_REPO", "/home/jesse/openroot"))
GARDEN = REPO / "pods_garden"
SKIP_DIRS = (".git", "__pycache__", "node_modules", "extracted")
TEXT_EXT = {".txt",".md",".markdown",".csv",".tsv",".json",".jsonl",".py",".sh",".log",
            ".yaml",".yml",".toml",".xml",".html",".css",".js",".ts",".c",".h",".cpp",
            ".rs",".go",".sql",".rst",".conf",".ini"}

def pod_dir(name):
    d = GARDEN / name
    d.mkdir(parents=True, exist_ok=True)
    return d

def pdf_text(p):
    try:
        r = subprocess.run(["pdftotext","-layout",str(p),"-"],capture_output=True,text=True,timeout=120)
        if r.returncode == 0 and r.stdout.strip(): return r.stdout
    except FileNotFoundError: pass
    try:
        from pypdf import PdfReader
        return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
    except Exception:
        return None

def collect(paths, sink, acc):
    for p in map(Path, paths):
        if p.is_dir():
            for q in sorted(p.rglob("*")):
                if q.is_file() and not any(x in q.parts for x in SKIP_DIRS):
                    collect([q], sink, acc)
        elif p.suffix.lower() == ".zip":
            td = sink / (p.stem + "-" + hashlib.sha256(str(p).encode()).hexdigest()[:10])
            td.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(p) as z: z.extractall(td)
            print("[gate] zip expanded ->", td.name)
            collect([td], sink, acc)
        elif p.suffix.lower() == ".pdf":
            t = pdf_text(p)
            if not t: print("[held] pdf: no text layer or no extractor:", p); continue
            out = sink / (p.stem + "." + hashlib.sha256(str(p).encode()).hexdigest()[:10] + ".txt")
            out.write_text(t, encoding="utf-8")
            acc.append((out, str(p)))
        elif p.suffix.lower() in TEXT_EXT or p.suffix == "":
            acc.append((p, str(p)))
        else:
            try: p.read_bytes().decode("utf-8"); acc.append((p, str(p)))
            except Exception: print("[held] binary skipped:", p)

def cmd_ingest(pod, paths):
    d = pod_dir(pod); sink = d / "extracted"; sink.mkdir(exist_ok=True)
    acc = []; collect(paths, sink, acc)
    c = pl.init_db(d); n = 0
    for f, origin in acc:
        if pl.ingest_file(c, str(f), origin, {"origin_path": origin, "pipeline": "pod_pipeline_v1"}): n += 1
    c.commit(); c.close()
    print("[banked] ingested", n, "docs into pod", pod)

def cmd_embed(pod, model):
    c = pl.init_db(pod_dir(pod))
    ok = pl.embed_chunks(c, model); c.commit(); c.close()
    print("[banked] embedded", ok, "chunks in pod", pod)

def cmd_seal(pod):
    c = pl.init_db(pod_dir(pod))
    res = pl.seal_pod(c, pod)
    root = res[0] if isinstance(res, tuple) else res
    n = res[1] if isinstance(res, tuple) and len(res) > 1 else "?"
    c.commit(); c.close()
    if not root: print("[held] pod empty - nothing to seal"); sys.exit(1)
    print("[banked] merkle_root:", root, "| chunks:", n)

def cmd_query(pod, q):
    c = pl.init_db(pod_dir(pod))
    r = pl.query_pod(c, q); c.close()
    print("chunks:", r.get("chunks_returned"), "chars:", r.get("total_chars"))
    for ch in r.get("dossier", [])[:5]:
        print("-", ch.get("doc_path"), "|", ch.get("text","")[:160].replace("\n"," "))

def cmd_status(pod):
    c = pl.init_db(pod_dir(pod))
    for t in ("documents","chunks","vectors"):
        print(t + ":", c.execute("SELECT COUNT(*) FROM " + t).fetchone()[0])
    row = c.execute("SELECT value FROM pod_meta WHERE key='merkle_root'").fetchone()
    print("merkle_root:", row[0] if row else "unsealed"); c.close()

def cmd_lesson(slug):
    d = pod_dir("lesson-" + slug); src = d / "sources"; src.mkdir(exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H%M%SZ", time.gmtime())
    print("Paste lesson text below, finish with Ctrl-D:")
    text = sys.stdin.read()
    f = src / ("lesson-" + slug + "-" + ts + ".md")
    f.write_text("id: lesson-" + slug + "\ntimestamp: " + ts + "\ntype: lesson\n\n" + text, encoding="utf-8")
    print("[gate] saved", f)
    cmd_ingest("lesson-" + slug, [str(f)])

USAGE = ("usage: pod_pipeline_v1.py ingest POD PATHS... | embed POD [MODEL] | "
         "seal POD | query POD QUERY | status POD | lesson SLUG")

def main():
    a = sys.argv[1:]
    if len(a) < 2: print(USAGE); sys.exit(2)
    cmd, pod = a[0], a[1]
    if cmd == "ingest" and len(a) > 2: cmd_ingest(pod, a[2:])
    elif cmd == "embed": cmd_embed(pod, a[2] if len(a) > 2 else "nomic-embed-text")
    elif cmd == "seal": cmd_seal(pod)
    elif cmd == "query" and len(a) > 2: cmd_query(pod, a[2])
    elif cmd == "status": cmd_status(pod)
    elif cmd == "lesson": cmd_lesson(pod)
    else: print(USAGE); sys.exit(2)
    print("[exit=0]")

if __name__ == "__main__": main()
