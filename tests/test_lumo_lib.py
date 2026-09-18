import contextlib
import importlib.util
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class LumoLibTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module("lumo_lib_under_test", "bin/lumo_lib.py")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.module.CACHE_DB = str(Path(self.temp_dir.name) / "proofs.db")

    def test_post_serializes_json_and_honors_timeout(self):
        with mock.patch.object(
            self.module.urllib.request,
            "urlopen",
            return_value=Response({"response": "done"}),
        ) as urlopen:
            result = self.module._post("/api/generate", {"value": "snowman ☃"}, timeout=17)

        self.assertEqual({"response": "done"}, result)
        request = urlopen.call_args.args[0]
        self.assertEqual("http://localhost:11434/api/generate", request.full_url)
        self.assertEqual({"value": "snowman ☃"}, json.loads(request.data))
        self.assertEqual("application/json", request.headers["Content-type"])
        self.assertEqual(17, urlopen.call_args.kwargs["timeout"])

    def test_generate_and_embed_shape_their_requests_and_results(self):
        with mock.patch.object(self.module, "_post", return_value={"response": "proof"}) as post:
            self.assertEqual("proof", self.module.ollama_generate("claim", model="builder", timeout=9))
        post.assert_called_once_with(
            "/api/generate",
            {"model": "builder", "prompt": "claim", "stream": False},
            9,
        )

        with mock.patch.object(self.module, "_post", return_value={"embeddings": [[1.0, 2.0]]}) as post:
            self.assertEqual([1.0, 2.0], self.module.embed("one", model="embedder", timeout=8))
        post.assert_called_once_with(
            "/api/embed", {"model": "embedder", "input": ["one"]}, 8
        )

        vectors = [[1.0], [2.0]]
        with mock.patch.object(self.module, "_post", return_value={"embeddings": vectors}) as post:
            self.assertEqual(vectors, self.module.embed(["one", "two"]))
        self.assertEqual(["one", "two"], post.call_args.args[1]["input"])

    def test_prove_banks_passed_proof_with_integrity_metadata(self):
        with mock.patch.object(
            self.module, "ollama_generate", side_effect=["rigorous proof", "VERDICT: PASS\nFIX: none"]
        ) as generate:
            result = self.module.prove("A implies A")

        self.assertEqual("PROVED", result["status"])
        self.assertEqual("rigorous proof", result["proof"])
        self.assertEqual(self.module.MODEL_GRADER, generate.call_args_list[1].kwargs["model"])
        with sqlite3.connect(self.module.CACHE_DB) as con:
            row = con.execute(
                "SELECT statement, status, proof, grader_verdict, model, sha256, created_at FROM proofs"
            ).fetchone()
        self.assertEqual(("A implies A", "PROVED", "rigorous proof"), row[:3])
        self.assertEqual("VERDICT: PASS\nFIX: none", row[3])
        self.assertEqual(self.module.MODEL_BUILDER, row[4])
        self.assertEqual(64, len(row[5]))
        self.assertTrue(row[6])

    def test_proved_cache_entry_never_recomputes(self):
        first = mock.Mock(side_effect=["saved proof", "PASS"])
        with mock.patch.object(self.module, "ollama_generate", first):
            self.module.prove("cached theorem")

        with mock.patch.object(self.module, "ollama_generate") as generate:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = self.module.prove("cached theorem")

        generate.assert_not_called()
        self.assertEqual({"statement": "cached theorem", "status": "PROVED", "proof": "saved proof"}, result)
        self.assertIn("[cache-hit]", output.getvalue())

    def test_failed_cache_entry_is_held_without_recompute(self):
        with mock.patch.object(self.module, "ollama_generate", side_effect=["bad proof", "VERDICT: FAIL"]):
            first = self.module.prove("false theorem")
        self.assertEqual("FAILED", first["status"])

        with mock.patch.object(self.module, "ollama_generate") as generate:
            second = self.module.prove("false theorem")
        generate.assert_not_called()
        self.assertEqual({"statement": "false theorem", "status": "FAILED"}, second)

    def test_model_failure_returns_unbanked_and_does_not_poison_cache(self):
        with mock.patch.object(self.module, "ollama_generate", side_effect=OSError("offline")):
            result = self.module.prove("retry later")
        self.assertEqual("UNBANKED", result["status"])

        with sqlite3.connect(self.module.CACHE_DB) as con:
            count = con.execute("SELECT COUNT(*) FROM proofs").fetchone()[0]
        self.assertEqual(0, count)


if __name__ == "__main__":
    unittest.main()
