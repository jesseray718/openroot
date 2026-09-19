import contextlib
import importlib.util
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "bin"))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "embed_index_under_test", REPO_ROOT / "bin/embed_index_v1.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EmbedIndexTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.module.ROOT = str(self.root)
        self.module.DB = str(self.root / "data" / "embeddings.db")
        (self.root / "data").mkdir()

    def test_chunk_text_enforces_boundary_and_drops_whitespace_tail(self):
        self.module.CHUNK_CHARS = 5
        self.assertEqual(["abcde", "f\n"], self.module.chunk_text("abcdef\n"))
        self.assertEqual([], self.module.chunk_text("   \n"))
        self.assertEqual(["abc\nd", "ef\n"], self.module.chunk_text("abc\ndef\n"))
        self.assertEqual(["abcde", "fghij", "k"], self.module.chunk_text("abcdefghijk"))

    def test_iter_files_filters_extensions_and_prunes_skip_directories(self):
        (self.root / "keep").mkdir()
        (self.root / "keep" / "note.md").write_text("included")
        (self.root / "keep" / "image.png").write_text("excluded")
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules" / "hidden.py").write_text("excluded")
        (self.root / "data" / "database.json").write_text("excluded")

        paths = {Path(path).relative_to(self.root).as_posix() for path in self.module.iter_files()}
        self.assertEqual({"keep/note.md"}, paths)

    def test_build_is_incremental_and_persists_relative_path_and_vector(self):
        (self.root / "a.md").write_text("alpha")
        (self.root / "b.py").write_text("beta")
        vectors = {"alpha": [1.0, 0.0], "beta": [0.0, 1.0]}

        with mock.patch.object(self.module, "embed", side_effect=lambda text: vectors[text]) as embed:
            self.module.build()
            self.module.build()

        self.assertEqual(2, embed.call_count)
        with sqlite3.connect(self.module.DB) as con:
            rows = con.execute("SELECT path, chunk, embedding FROM chunks ORDER BY path").fetchall()
        self.assertEqual(["a.md", "b.py"], [row[0] for row in rows])
        self.assertEqual(["alpha", "beta"], [row[1] for row in rows])
        self.assertEqual([[1.0, 0.0], [0.0, 1.0]], [json.loads(row[2]) for row in rows])

    def test_build_skips_unreadable_file_and_commits_prior_chunks(self):
        paths = [str(self.root / "good.md"), str(self.root / "missing.md")]
        (self.root / "good.md").write_text("content")
        with mock.patch.object(self.module, "iter_files", return_value=paths), mock.patch.object(
            self.module, "embed", return_value=[0.5]
        ):
            self.assertFalse(self.module.build())
        with sqlite3.connect(self.module.DB) as con:
            self.assertEqual(1, con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    def test_build_removes_stale_chunks_only_after_a_complete_scan(self):
        path = self.root / "a.md"
        path.write_text("old")
        with mock.patch.object(self.module, "embed", return_value=[1.0]):
            self.assertTrue(self.module.build())
        path.write_text("new")
        with mock.patch.object(self.module, "embed", return_value=[2.0]):
            self.assertTrue(self.module.build())
        with sqlite3.connect(self.module.DB) as con:
            self.assertEqual(["new"], [row[0] for row in con.execute("SELECT chunk FROM chunks")])

        with mock.patch.object(self.module, "embed", side_effect=OSError("offline")):
            path.write_text("newer")
            self.assertFalse(self.module.build())
        with sqlite3.connect(self.module.DB) as con:
            self.assertEqual(["new"], [row[0] for row in con.execute("SELECT chunk FROM chunks")])

    def test_build_and_query_reject_invalid_embedding_responses(self):
        (self.root / "a.md").write_text("alpha")
        output = io.StringIO()
        with mock.patch.object(self.module, "embed", return_value=[]), contextlib.redirect_stdout(output):
            self.assertFalse(self.module.build())
        self.assertIn("empty or non-numeric", output.getvalue())

        with sqlite3.connect(self.module.DB) as con:
            con.execute("INSERT INTO chunks VALUES (?, ?, ?, ?)", ("x", "a.md", "alpha", b"[1.0]"))
        with mock.patch.object(self.module, "embed", return_value=["bad"]), contextlib.redirect_stdout(output):
            self.assertFalse(self.module.query("alpha"))

    def test_query_ranks_cosine_similarity_and_ignores_zero_vectors(self):
        with sqlite3.connect(self.module.DB) as con:
            con.execute("CREATE TABLE chunks (sha256 TEXT PRIMARY KEY, path TEXT, chunk TEXT, embedding BLOB)")
            con.executemany(
                "INSERT INTO chunks VALUES (?, ?, ?, ?)",
                [
                    ("a", "best.md", "best\nchunk", json.dumps([1.0, 0.0]).encode()),
                    ("b", "second.md", "second", json.dumps([1.0, 1.0]).encode()),
                    ("c", "zero.md", "zero", json.dumps([0.0, 0.0]).encode()),
                ],
            )
        output = io.StringIO()
        with mock.patch.object(self.module, "embed", return_value=[1.0, 0.0]), contextlib.redirect_stdout(output):
            self.module.query("target", k=2)

        rendered = output.getvalue()
        self.assertLess(rendered.index("best.md"), rendered.index("second.md"))
        self.assertNotIn("zero.md", rendered)
        self.assertIn("best chunk", rendered)

    def test_query_empty_index_does_not_request_embedding(self):
        with sqlite3.connect(self.module.DB) as con:
            con.execute("CREATE TABLE chunks (sha256 TEXT PRIMARY KEY, path TEXT, chunk TEXT, embedding BLOB)")
        with mock.patch.object(self.module, "embed") as embed:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.module.query("anything")
        embed.assert_not_called()
        self.assertIn("index empty", output.getvalue())

    def test_main_selects_query_mode_without_rebuilding(self):
        with mock.patch.object(sys, "argv", ["embed_index_v1.py", "two", "words"]), mock.patch.object(
            self.module, "query"
        ) as query, mock.patch.object(self.module, "build") as build:
            self.module.main()
        query.assert_called_once_with("two words")
        build.assert_not_called()


if __name__ == "__main__":
    unittest.main()
