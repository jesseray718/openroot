import ast, contextlib, hashlib, io, json, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SHA = "1c148b1c6f9a4474c3b1840ba0819de6fa343457d2681bec1812ae9107cffc5c"
BASE = Path(__file__).resolve().parent

def load_native(path=None):
    data = Path(path or BASE / "source_snapshot.py").read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA: raise ValueError("Snapshot hash differs")
    names = {"sha256_bytes", "ledger_path", "load_chain", "entry_hash", "cmd_verify"}
    nodes = [n for n in ast.parse(data.decode()).body if isinstance(n, ast.FunctionDef) and n.name in names]
    if len(nodes) != 5: raise ValueError("Expected functions missing")
    ns = {"Path": Path, "hashlib": hashlib, "json": json, "DEFAULT_LEDGER": "data/pathway_cache.jsonl"}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), "snapshot", "exec"), ns)
    return ns

def run_cases():
    ns = load_native(); results = []
    with tempfile.TemporaryDirectory(prefix="openroot-example-") as td:
        root = Path(td); evidence = root / "evidence.txt"; ledger = root / "ledger.jsonl"
        evidence.write_text("original fixture\n")
        entry = {"seq": 1, "previous_hash": None, "name": "fixture", "evidence": [{"path": str(evidence), "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest()}]}
        entry["hash"] = ns["entry_hash"](entry)
        ledger.write_text(json.dumps(entry) + "\n")
        real_open = Path.open
        def check(name, expected):
            reads = []
            def tracked(path, mode="r", *args, **kwargs):
                if "r" in mode or "+" in mode: reads.append(Path(path).name)
                return real_open(path, mode, *args, **kwargs)
            with patch.object(Path, "open", tracked), contextlib.redirect_stdout(io.StringIO()):
                code = ns["cmd_verify"](SimpleNamespace(ledger=str(ledger)), root)
            results.append({"case": name, "expected_exit": expected, "actual_exit": code, "files_read": reads, "external_evidence_reads": reads.count("evidence.txt")})
        check("original", 0)
        evidence.write_text("CHANGED fixture\n"); check("external_file_changed", 0)
        with ledger.open("a") as f: f.write("NOT JSON\n")
        check("changed_file_and_invalid_json", 0)
        altered = dict(entry); altered["name"] = "changed without resealing"
        ledger.write_text(json.dumps(altered) + "\n"); check("entry_tampered", 1)
    return results

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.cases = run_cases()
    def test_original(self): self.assertEqual(self.cases[0]["actual_exit"], 0)
    def test_external_change(self): self.assertEqual(self.cases[1]["actual_exit"], 0)
    def test_invalid_json(self): self.assertEqual(self.cases[2]["actual_exit"], 0)
    def test_entry_change(self): self.assertEqual(self.cases[3]["actual_exit"], 1)
    def test_no_evidence_reads(self): self.assertTrue(all(c["external_evidence_reads"] == 0 for c in self.cases))
    def test_only_ledger_read(self): self.assertTrue(all(c["files_read"] == ["ledger.jsonl"] for c in self.cases))
    def test_snapshot_change_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "changed.py"; p.write_bytes((BASE / "source_snapshot.py").read_bytes() + b"\n# changed\n")
            with self.assertRaises(ValueError): load_native(p)

if __name__ == "__main__":
    if "--self-test" in sys.argv: unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        cases = run_cases()
        ok = all(c["actual_exit"] == c["expected_exit"] and c["external_evidence_reads"] == 0 for c in cases)
        print(json.dumps({"status": "BEHAVIOR_REPRODUCED" if ok else "BEHAVIOR_DIFFERS", "source_sha256": SHA, "cases": cases, "model_calls": 0, "production_database_writes": 0}, indent=2))
        raise SystemExit(0 if ok else 1)
