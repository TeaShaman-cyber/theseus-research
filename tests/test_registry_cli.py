import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "check_registry.py"

import tools.check_registry as check_registry


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class RegistryCliTests(unittest.TestCase):
    def test_validate_prints_machine_readable_pass(self):
        result = run_cli("validate")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual({"errors": [], "status": "PASS"}, json.loads(result.stdout))

    def test_render_check_passes_for_committed_readmes(self):
        result = run_cli("render", "--check")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("PASS", payload["status"])
        self.assertEqual([], payload["mismatched_files"])

    def test_render_write_validates_both_projections_before_writing_either(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            readme_en = root / "README.md"
            readme_ru = root / "README.ru.md"
            readme_en.write_text(
                "before\n<!-- BEGIN THESEUS_RESEARCH_LINES -->\nold\n<!-- END THESEUS_RESEARCH_LINES -->\nafter\n",
                encoding="utf-8",
            )
            readme_ru.write_text("broken projection without markers\n", encoding="utf-8")
            original_en = readme_en.read_bytes()
            original_ru = readme_ru.read_bytes()
            saved_en, saved_ru = check_registry.README_EN, check_registry.README_RU
            check_registry.README_EN, check_registry.README_RU = readme_en, readme_ru
            try:
                code = check_registry.cmd_render(argparse.Namespace(check=False, write=True))
            finally:
                check_registry.README_EN, check_registry.README_RU = saved_en, saved_ru
            self.assertEqual(4, code)
            self.assertEqual(original_en, readme_en.read_bytes())
            self.assertEqual(original_ru, readme_ru.read_bytes())

    def test_unknown_subcommand_fails_with_argparse_error(self):
        result = run_cli("unknown-command")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
