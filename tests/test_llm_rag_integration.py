#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0
import unittest
import tempfile
import sqlite3
import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, "/home/jesse/openroot/bin")
import llm_rag_integration

class TestLLMRagIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database = os.path.join(self.temp_dir.name, "test_embeddings.db")
        
        # Patch the DB path in the module to point to our temp DB
        self.db_patcher = patch("llm_rag_integration.DB", self.database)
        self.db_patcher.start()
        self.addCleanup(self.db_patcher.stop)

    def test_retrieve_context_empty_db(self):
        with sqlite3.connect(self.database) as con:
            con.execute("CREATE TABLE chunks (path TEXT, chunk TEXT, embedding BLOB)")
        
        with patch("llm_rag_integration.lumo_lib.embed", return_value=[0.1, 0.2]):
            context = llm_rag_integration.retrieve_context("test query")
            self.assertEqual(context, "(No relevant local context found.)")

    def test_retrieve_context_with_matches(self):
        with sqlite3.connect(self.database) as con:
            con.execute("CREATE TABLE chunks (path TEXT, chunk TEXT, embedding BLOB)")
            # Insert a perfect match vector [1.0, 0.0] and an orthogonal vector [0.0, 1.0]
            con.execute("INSERT INTO chunks VALUES (?, ?, ?)", 
                        ("docs/test1.md", "Relevant chunk", json.dumps([1.0, 0.0]).encode()))
            con.execute("INSERT INTO chunks VALUES (?, ?, ?)", 
                        ("docs/test2.md", "Irrelevant chunk", json.dumps([0.0, 1.0]).encode()))
        
        # Mock embed to return [1.0, 0.0] so it perfectly matches test1.md
        with patch("llm_rag_integration.lumo_lib.embed", return_value=[1.0, 0.0]):
            context = llm_rag_integration.retrieve_context("query")
            self.assertIn("docs/test1.md", context)
            self.assertIn("Relevant chunk", context)
            self.assertIn("docs/test2.md", context) # Still returned because K=3, but sorted lower.
            
            # test1 should be first
            self.assertTrue(context.index("test1.md") < context.index("test2.md"))

    def test_generate_answer(self):
        with patch("llm_rag_integration.lumo_lib.ollama_generate", return_value="Mocked Answer") as mock_gen:
            answer = llm_rag_integration.generate_answer("What is X?", "Context about X")
            self.assertEqual(answer, "Mocked Answer")
            mock_gen.assert_called_once()
            args = mock_gen.call_args[0][0]
            self.assertIn("What is X?", args)
            self.assertIn("Context about X", args)

    def test_missing_db_graceful_fail(self):
        # Database file does not exist at self.database
        with patch("llm_rag_integration.lumo_lib.embed", return_value=[0.1, 0.2]):
            context = llm_rag_integration.retrieve_context("query")
            self.assertEqual(context, "(No relevant local context found.)")

if __name__ == "__main__":
    unittest.main()
