import json
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import project_contract as pc
import project_contract_formal as formal


class ProjectContractV11Tests(unittest.TestCase):
    def test_legacy_v10_fixture_remains_pinned(self):
        legacy = pc.load_pinned_legacy()
        self.assertEqual(legacy["Revision"], pc.ACCEPTED_V10_REVISION)
        self.assertEqual(legacy["Probe"]["Reply"], "PC_OK_V10")

    def test_v11_source_names_verified_routes(self):
        source = pc.load_source()
        self.assertEqual(source["Revision"], "2026-11-skill-router-v11")
        self.assertEqual(source["Probe"]["Reply"], "PC_OK_V11")
        self.assertIn("theseus-research/governance/chatgpt-project-contract.yaml", source["CanonicalSource"])
        self.assertIn("session-search-usage", source["Continuity"])
        self.assertIn("sprites-core-router", source["OperationalBootstrap"])
        self.assertNotIn("prefer MarcoPolo", source["OperationalBootstrap"])

    def test_projection_roundtrips_and_fits_project_settings(self):
        source = pc.load_source()
        projection = pc.build_validated_projection(source)
        self.assertEqual(pc.parse_wl(projection), source)
        self.assertLessEqual(len(projection), pc.MAX_PROJECT_SETTINGS_CHARS)
        self.assertEqual(pc.PROJECTION.read_text(encoding="utf-8"), projection)

    def test_duplicate_yaml_keys_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.yaml"
            path.write_text("Scope: x\nScope: y\n", encoding="utf-8")
            with self.assertRaises(pc.ContractError):
                pc.load_source(path)

    def test_revision_and_probe_are_bound(self):
        source = pc.load_source()
        bad = dict(source)
        bad["Probe"] = {"Input": "PROJECT_CONTRACT_PROBE", "Reply": "PC_OK_V999"}
        with self.assertRaises(pc.ContractError):
            pc.validate_contract(bad)

    def test_v10_fixture_is_content_address_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "project-contract-v10.wl"
            fixture.write_bytes(pc.LEGACY.read_bytes() + b"\n")
            with self.assertRaises(pc.ContractError):
                pc.load_pinned_legacy(fixture)

    def test_render_rejects_oversize_before_overwriting_projection(self):
        source = pc.load_source()
        bad = dict(source)
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
            self.assertEqual(projection_path.read_text(encoding="utf-8"), "sentinel")

    def test_formal_model_passes_deterministic_invariants(self):
        data = json.loads(formal.MODEL.read_text(encoding="utf-8"))
        receipt = formal.verify_model(data)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["revision"], "2026-11-skill-router-v11")

    def test_cli_validate(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "project_contract.py"), "validate"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["revision"], "2026-11-skill-router-v11")
        self.assertEqual(receipt["probe"], "PC_OK_V11")
        self.assertLessEqual(receipt["projection_chars"], 8000)


if __name__ == "__main__":
    unittest.main()
