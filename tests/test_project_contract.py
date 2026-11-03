import json
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import project_contract as pc


class ProjectContractTests(unittest.TestCase):
    def test_v10_structured_source_matches_accepted_wl_fixture(self):
        self.assertEqual(
            pc.load_pinned_legacy(),
            pc.load_source(),
        )

    def test_v10_fixture_is_content_address_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "project-contract-v10.wl"
            fixture.write_bytes(pc.LEGACY.read_bytes() + b"\n")
            with self.assertRaises(pc.ContractError):
                pc.load_pinned_legacy(fixture)

    def test_render_rejects_oversize_before_overwriting_projection(self):
        source = pc.load_source()
        bad = dict(source)
        bad["Revision"] = "2026-11-skill-router-v11"
        bad["Probe"] = {
            "Input": "PROJECT_CONTRACT_PROBE",
            "Reply": "PC_OK_V11",
        }
        bad["Permission"] = "x" * 9000

        with tempfile.TemporaryDirectory() as tmp:
            source_path = Path(tmp) / "contract.yaml"
            projection_path = Path(tmp) / "project-settings.txt"
            source_path.write_text(
                pc.yaml.dump(
                    bad,
                    Dumper=pc._IndentedSafeDumper,
                    sort_keys=False,
                    allow_unicode=True,
                    width=120,
                ),
                encoding="utf-8",
            )
            projection_path.write_text("sentinel", encoding="utf-8")

            with self.assertRaises(pc.ContractError):
                pc.render_file(source_path, projection_path)

            self.assertEqual(
                projection_path.read_text(encoding="utf-8"),
                "sentinel",
            )

    def test_projection_roundtrips_and_fits_project_settings(self):
        source = pc.load_source()
        projection = pc.render_projection(source)
        self.assertEqual(pc.parse_wl(projection), source)
        self.assertLessEqual(len(projection), pc.MAX_PROJECT_SETTINGS_CHARS)
        self.assertEqual(
            pc.PROJECTION.read_text(encoding="utf-8"),
            projection,
        )

    def test_duplicate_yaml_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.yaml"
            path.write_text("Scope: x\nScope: y\n", encoding="utf-8")
            with self.assertRaises(pc.ContractError):
                pc.load_source(path)

    def test_revision_and_probe_are_bound(self):
        source = pc.load_source()
        bad = dict(source)
        bad["Probe"] = {
            "Input": "PROJECT_CONTRACT_PROBE",
            "Reply": "PC_OK_V999",
        }
        with self.assertRaises(pc.ContractError):
            pc.validate_contract(bad)

    def test_cli_validate(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "project_contract.py"),
                "validate",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(
            receipt["revision"],
            "2026-11-skill-router-v10",
        )
        self.assertEqual(receipt["probe"], "PC_OK_V10")
        self.assertLessEqual(receipt["projection_chars"], 8000)


if __name__ == "__main__":
    unittest.main()
