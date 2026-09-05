import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "check_registry.py"


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

    def test_unknown_subcommand_fails_with_argparse_error(self):
        result = run_cli("unknown-command")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("invalid choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
