import argparse
import sys
import unittest
from scripts.knowledge_ledger import KnowledgeLedger, KnowledgeBlockSchema
from scripts.search_ledger import LedgerIndexer

def main():
    parser = argparse.ArgumentParser(description="UNE: Universal Native Descriptor & Knowledge Ledger CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    subparsers.add_parser("init", help="Initialize the ledger and search database")

    # Add block command
    add_parser = subparsers.add_parser("add", help="Add a knowledge block to the ledger")
    add_parser.add_argument("--type", required=True, choices=["code", "bom", "document", "dataset", "blueprint"])
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--author", required=True)
    add_parser.add_argument("--content", required=True)

    # Search command
    search_parser = subparsers.add_parser("search", help="Search the ledger using FTS5")
    search_parser.add_argument("query", help="Keyword query string")

    # Test command
    subparsers.add_parser("test", help="Run the test suite")

    args = parser.parse_args()
    ledger = KnowledgeLedger()
    indexer = LedgerIndexer()

    if args.command == "init":
        print("Initialized UNE ledger databases successfully.")
    elif args.command == "add":
        block = KnowledgeBlockSchema(
            artifact_type=args.type,
            title=args.title,
            author_id=args.author,
            payload={"content": args.content}
        )
        b_hash = ledger.append_block(block)
        indexer.index_ledger()
        print(f"Successfully added block. Hash: {b_hash}")
    elif args.command == "search":
        indexer.index_ledger()
        results = indexer.search_keyword(args.query)
        print(f"Found {len(results)} results for '{args.query}':")
        for r in results:
            print(f"  [{r[1]}] {r[2]} (Tier {r[3]}) -> Hash: {r[0][:12]}...")
    elif args.command == "test":
        suite = unittest.defaultTestLoader.discover("tests")
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
