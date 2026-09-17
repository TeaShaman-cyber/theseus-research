import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
ROUTER = ROOT / "route_checks.py"


def load_extractor():
    path = ROOT / "extract_plan.py"
    spec = importlib.util.spec_from_file_location("skill_contract_extract_plan_for_router", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApplicabilityDispatcherTests(unittest.TestCase):
    def setUp(self):
        self.extractor = load_extractor()

    def route_payload(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            projection = pathlib.Path(tmp) / "projection.json"
            projection.write_text(json.dumps(payload, sort_keys=True))
            completed = subprocess.run(
                [sys.executable, str(ROUTER), str(projection)],
                text=True,
                capture_output=True,
            )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def route_fixture(self, name):
        payload = self.extractor.extract_payload((FIXTURES / name).read_bytes())
        return self.route_payload(payload)

    def test_transport_unsafe_is_not_masked_by_runtime_safe(self):
        result = self.route_fixture("transport-env-line-newline.md")
        self.assertEqual(
            ["RUNTIME_BINDING", "TRANSPORT_BOUNDARY"],
            sorted(result["family_results"]),
        )
        self.assertEqual(
            "SAFE_WITHIN_SCOPE",
            result["family_results"]["RUNTIME_BINDING"]["scope_status"],
        )
        self.assertEqual(
            "UNSAFE",
            result["family_results"]["TRANSPORT_BOUNDARY"]["scope_status"],
        )
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("REJECT", result["disposition"])

    def test_all_green_families_are_only_safe_within_extracted_relations(self):
        result = self.route_fixture("transport-env-line-safe.md")
        self.assertEqual(
            ["RUNTIME_BINDING", "TRANSPORT_BOUNDARY"],
            sorted(result["family_results"]),
        )
        self.assertTrue(
            all(
                family["scope_status"] == "SAFE_WITHIN_SCOPE"
                for family in result["family_results"].values()
            )
        )
        self.assertEqual("SAFE_WITHIN_EXTRACTED_RELATIONS", result["scope_status"])
        self.assertEqual("ACCEPT_SCOPED", result["disposition"])

    def test_unobservable_family_prevents_safe_aggregate(self):
        result = self.route_fixture("tdd-unittest-unobservable.md")
        self.assertEqual(["TDD_RUNNER_WITNESS"], sorted(result["family_results"]))
        self.assertEqual(
            "UNOBSERVABLE_AT_THIS_LAYER",
            result["family_results"]["TDD_RUNNER_WITNESS"]["scope_status"],
        )
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("DEFER", result["disposition"])

    def test_unknown_relation_kind_is_not_silently_ignored(self):
        result = self.route_payload(
            {
                "schema_version": 1,
                "source": {"bytes": 0, "sha256": "0" * 64},
                "relations": [{"kind": "FUTURE_RELATION"}],
            }
        )
        self.assertEqual({}, result["family_results"])
        self.assertEqual(["FUTURE_RELATION"], result["unrouted_relation_kinds"])
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("DEFER", result["disposition"])

    def test_empty_projection_is_unobservable_not_safe(self):
        result = self.route_payload(
            {
                "schema_version": 1,
                "source": {"bytes": 0, "sha256": "0" * 64},
                "relations": [],
            }
        )
        self.assertEqual({}, result["family_results"])
        self.assertEqual([], result["unrouted_relation_kinds"])
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("DEFER", result["disposition"])

    def test_known_unsafe_keeps_precedence_while_unknown_kind_stays_visible(self):
        payload = self.extractor.extract_payload(
            (FIXTURES / "transport-env-line-newline.md").read_bytes()
        )
        payload["relations"].append({"kind": "FUTURE_RELATION"})
        result = self.route_payload(payload)
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("REJECT", result["disposition"])
        self.assertEqual(["FUTURE_RELATION"], result["unrouted_relation_kinds"])
        self.assertEqual(
            "UNSAFE",
            result["family_results"]["TRANSPORT_BOUNDARY"]["scope_status"],
        )


if __name__ == "__main__":
    unittest.main()
