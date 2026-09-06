import unittest
from pathlib import Path

from tools.registry_contract import load_registry
from tools.registry_projection import (
    BEGIN_MARKER,
    END_MARKER,
    projection_matches,
    render_table,
    replace_projection,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "research-lines.json"


class RegistryProjectionTests(unittest.TestCase):
    def setUp(self):
        self.document = load_registry(REGISTRY)

    def test_every_declared_id_appears_once_in_both_tables(self):
        for language in ("en", "ru"):
            rendered = render_table(self.document, language)
            rows = rendered.splitlines()[2:]
            for line in self.document["lines"]:
                if line["id"] == "sonar":
                    matches = [row for row in rows if "| Sonar |" in row]
                else:
                    matches = [row for row in rows if f"[`{line['id']}`]" in row]
                self.assertEqual(1, len(matches), (language, line["id"]))

    def test_sonar_has_no_github_link(self):
        for language in ("en", "ru"):
            rendered = render_table(self.document, language)
            sonar_row = next(row for row in rendered.splitlines() if "Sonar" in row)
            self.assertNotIn("github.com", sonar_row)

    def test_replacement_is_idempotent(self):
        source = (
            "before\n"
            f"{BEGIN_MARKER}\n"
            "old\n"
            f"{END_MARKER}\n"
            "after\n"
        )
        once = replace_projection(source, "| table |\n")
        self.assertEqual(once, replace_projection(once, "| table |\n"))

    def test_missing_or_duplicate_markers_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "exactly one projection marker pair"):
            replace_projection("no markers\n", "table\n")
        source = f"{BEGIN_MARKER}\na\n{END_MARKER}\n{BEGIN_MARKER}\nb\n{END_MARKER}\n"
        with self.assertRaisesRegex(ValueError, "exactly one projection marker pair"):
            replace_projection(source, "table\n")

    def test_reversed_markers_fail_closed(self):
        source = f"{END_MARKER}\nold\n{BEGIN_MARKER}\n"
        with self.assertRaisesRegex(ValueError, "projection markers out of order"):
            replace_projection(source, "table\n")

    def test_committed_readmes_match_generated_tables(self):
        self.assertTrue(projection_matches(ROOT / "README.md", render_table(self.document, "en")))
        self.assertTrue(projection_matches(ROOT / "README.ru.md", render_table(self.document, "ru")))


if __name__ == "__main__":
    unittest.main()
