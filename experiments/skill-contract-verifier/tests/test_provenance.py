import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = json.loads((ROOT / "corpus" / "provenance_cases.json").read_text())
VERDICTS = json.loads((ROOT / "corpus" / "verdicts.json").read_text())


def load_checker():
    path = ROOT / "verify.py"
    spec = importlib.util.spec_from_file_location("skill_contract_verify", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProvenanceInvariantTests(unittest.TestCase):
    def test_frozen_corpus_has_matched_bad_fixed_pairs_across_four_domains(self):
        ids = {case["id"] for case in CORPUS["cases"]}
        self.assertEqual(8, len(ids))
        self.assertEqual(
            {"repository-search", "session-search", "needle", "memory-provider"},
            {case["domain"] for case in CORPUS["cases"]},
        )
        for prefix in (
            "repo-search-db-artifact",
            "session-search-membership",
            "needle-experiment-sha",
            "memory-provider-version",
        ):
            self.assertIn(prefix + "-bad", ids)
            self.assertIn(prefix + "-fixed", ids)

    def test_checker_matches_separate_frozen_verdicts_and_emits_counterexamples(self):
        checker = load_checker()
        for case in CORPUS["cases"]:
            result = checker.verify_case(case)
            expected = VERDICTS[case["id"]]
            self.assertEqual(expected, result["disposition"], case["id"])
            if expected == "REJECT":
                self.assertTrue(result["counterexamples"], case["id"])
            else:
                self.assertEqual([], result["counterexamples"], case["id"])

    def test_checker_marks_unrepresentable_binding_unobservable_not_safe(self):
        checker = load_checker()
        case = {
            "id": "plan-layer-runtime-binding",
            "domain": "scope-probe",
            "claim": {"required_bindings": {"runtime_value": "ready"}},
            "scope": {"observable_bindings": []},
            "evidence": {"bindings": {}},
        }
        result = checker.verify_case(case)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("DEFER", result["disposition"])
        self.assertEqual(
            [{"binding": "runtime_value", "kind": "UNOBSERVABLE_BINDING"}],
            result["coverage_gaps"],
        )

    def test_observable_but_missing_binding_is_unsafe(self):
        checker = load_checker()
        case = {
            "id": "plan-layer-missing-binding",
            "domain": "scope-probe",
            "claim": {"required_bindings": {"runtime_value": "ready"}},
            "scope": {"observable_bindings": ["runtime_value"]},
            "evidence": {"bindings": {}},
        }
        result = checker.verify_case(case)
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("REJECT", result["disposition"])
        self.assertEqual([], result["coverage_gaps"])
        self.assertEqual("MISSING_BINDING", result["counterexamples"][0]["kind"])

    def test_checker_does_not_receive_human_verdicts(self):
        checker = load_checker()
        self.assertNotIn("verdict", checker.verify_case.__code__.co_names)
        self.assertNotIn("VERDICTS", checker.verify_case.__code__.co_names)


if __name__ == "__main__":
    unittest.main()
