import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_markdown_links.py"
spec = importlib.util.spec_from_file_location("check_markdown_links", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class MarkdownLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.doc = self.root / "README.md"
        (self.root / "target (1).md").write_text("# Section\n# Section\n")

    def check(self, text):
        self.doc.write_text(text)
        return checker.check_file(self.doc, self.root)

    def test_relative_reference_html_and_fragment_links(self):
        errors = self.check(
            '[inline](target%20(1).md#section-1 "title")\n'
            '[reference][item]\n[item]: <target (1).md>\n'
            '<a href="target%20(1).md#section">target</a>\n'
            '![image](missing.png)\n'
        )
        self.assertEqual(1, len(errors))
        self.assertIn("missing.png", errors[0])

    def test_missing_anchor_and_parent_escape(self):
        errors = self.check("[bad](target%20(1).md#missing)\n[outside](../other.md)")
        self.assertEqual(2, len(errors))
        self.assertIn("missing anchor", errors[0])

    def test_code_and_external_links_are_not_checked(self):
        errors = self.check(
            "`[example](missing.md)`\n"
            "```md\n[example](missing.md)\n```\n"
            "[web](https://example.invalid/path)\n"
        )
        self.assertEqual([], errors)

    def test_nested_image_link_checks_both_destinations(self):
        errors = self.check("[![image](missing.png)](missing.md)")
        self.assertEqual(2, len(errors))


if __name__ == "__main__":
    unittest.main()
