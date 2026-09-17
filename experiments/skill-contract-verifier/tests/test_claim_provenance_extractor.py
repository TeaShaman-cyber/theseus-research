import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def load_module(filename, module_name):
    path = ROOT / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClaimProvenanceExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = load_module("extract_plan.py", "claim_provenance_extract_plan")
        self.router = load_module("route_checks.py", "claim_provenance_route_checks")

    def projection(self, fixture):
        return self.extractor.extract_payload((FIXTURES / fixture).read_bytes())

    def relations(self, payload):
        return [r for r in payload["relations"] if r.get("kind") == "CLAIM_PROVENANCE"]

    def test_exact_bindings_are_safe_within_extracted_relations(self):
        payload = self.projection("provenance-contract-match.md")
        self.assertEqual(1, len(self.relations(payload)))
        result = self.router.route(payload)
        self.assertEqual("SAFE_WITHIN_EXTRACTED_RELATIONS", result["scope_status"])
        self.assertEqual("SAFE_WITHIN_SCOPE", result["family_results"]["CLAIM_PROVENANCE"]["scope_status"])

    def test_binding_mismatch_is_unsafe(self):
        payload = self.projection("provenance-contract-mismatch.md")
        result = self.router.route(payload)
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("BINDING_MISMATCH", result["family_results"]["CLAIM_PROVENANCE"]["counterexamples"][0]["kind"])

    def test_missing_binding_is_unsafe(self):
        payload = self.projection("provenance-contract-missing.md")
        result = self.router.route(payload)
        self.assertEqual("UNSAFE", result["scope_status"])
        kinds = {item["kind"] for item in result["family_results"]["CLAIM_PROVENANCE"]["counterexamples"]}
        self.assertIn("MISSING_BINDING", kinds)

    def test_absent_contract_is_unobservable_not_safe(self):
        payload = self.projection("provenance-contract-absent.md")
        self.assertEqual([], self.relations(payload))
        result = self.router.route(payload)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])

    def test_malformed_contract_is_visible_and_unobservable(self):
        payload = self.projection("provenance-contract-malformed.md")
        kinds = {r.get("kind") for r in payload["relations"]}
        self.assertIn("CLAIM_PROVENANCE_UNPARSEABLE", kinds)
        result = self.router.route(payload)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertIn("CLAIM_PROVENANCE_UNPARSEABLE", result["unrouted_relation_kinds"])

    def test_mixed_valid_and_invalid_bindings_remain_unsafe(self):
        payload = self.projection("provenance-contract-mixed.md")
        self.assertEqual(2, len(self.relations(payload)))
        result = self.router.route(payload)
        self.assertEqual("UNSAFE", result["scope_status"])
        kinds = {item["kind"] for item in result["family_results"]["CLAIM_PROVENANCE"]["counterexamples"]}
        self.assertIn("BINDING_MISMATCH", kinds)

    def test_provenance_projection_is_byte_deterministic(self):
        path = FIXTURES / "provenance-contract-match.md"
        first = self.extractor.canonical_json(self.extractor.extract_payload(path.read_bytes()))
        second = self.extractor.canonical_json(self.extractor.extract_payload(path.read_bytes()))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
