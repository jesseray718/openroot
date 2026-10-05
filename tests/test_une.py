import os
import unittest
from scripts.knowledge_ledger import KnowledgeLedger, KnowledgeBlockSchema, ValidationTier
from scripts.search_ledger import LedgerIndexer

class TestUneSystem(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/test_ledger.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.ledger = KnowledgeLedger(db_path=self.db_path)
        self.indexer = LedgerIndexer(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_block_chaining_and_hashing(self):
        block1 = KnowledgeBlockSchema(
            artifact_type="blueprint",
            title="Aerocement 2.0 Formulation",
            author_id="jesseray718",
            payload={"content": "Xanthan gum and alcohol slurry mixed with Portland cement and micro glass fibers.", "specs": {"ratio": "standard"}}
        )
        hash1 = self.ledger.append_block(block1)
        self.assertEqual(len(hash1), 64)

        block2 = KnowledgeBlockSchema(
            artifact_type="dataset",
            title="Aero-Disc Thermodynamic Test Data",
            author_id="jesseray718",
            payload={"content": "Darcy-Forchheimer volumetric heat exchanger pressure drop recordings.", "specs": {"flow": "optimal"}}
        )
        hash2 = self.ledger.append_block(block2)
        self.assertNotEqual(hash1, hash2)

    def test_fts5_search(self):
        block = KnowledgeBlockSchema(
            artifact_type="blueprint",
            title="Aero-Disc Heat Exchanger",
            author_id="jesseray718",
            payload={"content": "High efficiency volumetric thermal absorber blackbody core.", "specs": {"temp": "high"}}
        )
        self.ledger.append_block(block)
        self.indexer.index_ledger()

        results = self.indexer.search_keyword("volumetric")
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0][2], "Aero-Disc Heat Exchanger")

if __name__ == "__main__":
    unittest.main()
