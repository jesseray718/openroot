#!/usr/bin/env python3
import json, os, sys, time

CTX = "/sdcard/openroot/relay/context.json"
MAX_LESSONS = 200
MAX_ARTIFACTS = 100

def _load():
    if os.path.exists(CTX):
        try:
            with open(CTX) as f: return json.load(f)
        except (json.JSONDecodeError, IOError): pass
    return {"sessions": [], "lessons": [], "artifacts": [], "version": 1}

def _save(data):
    os.makedirs(os.path.dirname(CTX), exist_ok=True)
    tmp = CTX + ".tmp"
    with open(tmp, "w") as f: json.dump(data, f, indent=2)
    os.replace(tmp, CTX)

def add_lesson(text, source="manual"):
    d = _load()
    d["lessons"].append({"t": time.time(), "src": source, "text": text})
    d["lessons"] = d["lessons"][-MAX_LESSONS:]
    _save(d)
    return f"lesson_added:{len(d['lessons'])}_total"

def add_artifact(name, path):
    d = _load()
    d["artifacts"].append({"t": time.time(), "name": name, "path": path})
    d["artifacts"] = d["artifacts"][-MAX_ARTIFACTS:]
    _save(d)
    return f"artifact_added:{name}"

def add_session(model="unknown", summary=""):
    d = _load()
    d["sessions"].append({"t": time.time(), "model": model, "summary": summary})
    d["sessions"] = d["sessions"][-50:]
    _save(d)
    return "session_logged"

def status():
    d = _load()
    print(f"immortal_context v{d.get('version',1)}")
    print(f"  sessions:  {len(d['sessions'])}")
    print(f"  lessons:   {len(d['lessons'])}")
    print(f"  artifacts: {len(d['artifacts'])}")

def dump_json():
    print(json.dumps(_load(), indent=2))

def export_markdown(path="/sdcard/openroot/wiki/context_export.md"):
    d = _load()
    with open(path, "w") as f:
        f.write("# Immortal Context Export\n\n")
        f.write(f"_Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}_\n\n")
        f.write("## Lessons\n\n")
        for l in d["lessons"]:
            f.write(f"- [{time.strftime('%Y-%m-%d', time.localtime(l['t']))}] ({l['src']}) {l['text']}\n")
        f.write("\n## Artifacts\n\n")
        for a in d["artifacts"]:
            f.write(f"- {a['name']} -> {a['path']}\n")
    return f"exported:{path}"

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "lesson": print(add_lesson(" ".join(sys.argv[2:]) or "(empty)", "cli"))
    elif cmd == "artifact": print(add_artifact(sys.argv[2], sys.argv[3]))
    elif cmd == "session": print(add_session(sys.argv[2] if len(sys.argv)>2 else "?", sys.argv[3] if len(sys.argv)>3 else ""))
    elif cmd == "status": status()
    elif cmd == "dump": dump_json()
    elif cmd == "export": print(export_markdown(sys.argv[2] if len(sys.argv)>2 else None))
    else: print(f"usage: [status|lesson TEXT|artifact NAME PATH|session MODEL SUMMARY|dump|export]")
