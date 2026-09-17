import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
EXTRACTOR = ROOT / "extract_plan.py"
CHECKER = ROOT / "check_tdd.py"


def extract(name):
    completed = subprocess.run(
        [sys.executable, str(EXTRACTOR), str(FIXTURES / name)],
        text=True,
        capture_output=True,
    )
    return completed


def check(payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(payload, handle, sort_keys=True, separators=(",", ":"))
        path = pathlib.Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(CHECKER), str(path)],
            text=True,
            capture_output=True,
        )
    finally:
        path.unlink(missing_ok=True)


class DeterministicExtractorTests(unittest.TestCase):
    def test_module_level_unittest_witness_is_extracted_then_rejected(self):
        completed = extract("tdd-unittest-undiscoverable.md")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(1, payload["schema_version"])
        self.assertEqual(1, len(payload["relations"]))
        relation = payload["relations"][0]
        self.assertEqual("TDD_RUNNER_WITNESS", relation["kind"])
        self.assertEqual("python_unittest_discover", relation["runner"]["kind"])
        self.assertEqual(1, relation["producer_step"]["number"])
        self.assertEqual(2, relation["consumer_step"]["number"])
        self.assertEqual(
            [
                {
                    "discoverable": False,
                    "form": "module_function",
                    "name": "test_runtime_contract_files_exist",
                    "span": {"end_line": 5, "start_line": 4},
                }
            ],
            relation["witnesses"],
        )
        verdict = check(payload)
        self.assertEqual(verdict.returncode, 0, verdict.stderr)
        result = json.loads(verdict.stdout)
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("RED_WITNESS_UNDISCOVERABLE", result["counterexamples"][0]["kind"])

    def test_testcase_method_is_extracted_then_accepted_within_scope(self):
        completed = extract("tdd-unittest-discoverable.md")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        relation = payload["relations"][0]
        self.assertEqual(
            [
                {
                    "discoverable": True,
                    "form": "unittest_testcase_method",
                    "name": "test_runtime_contract_files_exist",
                    "span": {"end_line": 8, "start_line": 7},
                }
            ],
            relation["witnesses"],
        )
        verdict = check(payload)
        self.assertEqual(verdict.returncode, 0, verdict.stderr)
        result = json.loads(verdict.stdout)
        self.assertEqual("SAFE_WITHIN_SCOPE", result["scope_status"])
        self.assertEqual([], result["counterexamples"])

    def test_missing_machine_readable_witness_is_unobservable_not_safe(self):
        completed = extract("tdd-unittest-unobservable.md")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(1, len(payload["relations"]))
        self.assertEqual([], payload["relations"][0]["witnesses"])
        verdict = check(payload)
        self.assertEqual(verdict.returncode, 0, verdict.stderr)
        result = json.loads(verdict.stdout)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("UNOBSERVABLE_ROUTING", result["coverage_gaps"][0]["kind"])

    def test_mixed_observable_and_unobservable_relations_do_not_collapse_to_safe(self):
        payload = {
            "schema_version": 1,
            "source": {"bytes": 1, "sha256": "0" * 64},
            "relations": [
                {
                    "kind": "TDD_RUNNER_WITNESS",
                    "consumer_step": {"number": 2, "span": {"start_line": 10, "end_line": 12}},
                    "runner": {"kind": "python_unittest_discover", "span": {"start_line": 11, "end_line": 11}},
                    "witnesses": [
                        {
                            "name": "test_visible",
                            "form": "unittest_testcase_method",
                            "discoverable": True,
                            "span": {"start_line": 4, "end_line": 5},
                        }
                    ],
                },
                {
                    "kind": "TDD_RUNNER_WITNESS",
                    "consumer_step": {"number": 6, "span": {"start_line": 30, "end_line": 32}},
                    "runner": {"kind": "python_unittest_discover", "span": {"start_line": 31, "end_line": 31}},
                    "witnesses": [],
                },
            ],
        }
        verdict = check(payload)
        self.assertEqual(verdict.returncode, 0, verdict.stderr)
        result = json.loads(verdict.stdout)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("UNOBSERVABLE_ROUTING", result["coverage_gaps"][0]["kind"])
        self.assertEqual(6, result["coverage_gaps"][0]["consumer_step"])

    def test_projection_is_byte_deterministic_and_bound_to_source_bytes(self):
        first = extract("tdd-unittest-discoverable.md")
        second = extract("tdd-unittest-discoverable.md")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout.encode(), second.stdout.encode())
        self.assertEqual(
            hashlib.sha256(first.stdout.encode()).hexdigest(),
            hashlib.sha256(second.stdout.encode()).hexdigest(),
        )
        payload = json.loads(first.stdout)
        source = (FIXTURES / "tdd-unittest-discoverable.md").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), payload["source"]["sha256"])
        self.assertEqual(len(source), payload["source"]["bytes"])


if __name__ == "__main__":
    unittest.main()
