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


class TransportBoundaryExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = load_module("extract_plan.py", "skill_contract_extract_plan_transport")

    def projection(self, fixture):
        return self.extractor.extract_payload((FIXTURES / fixture).read_bytes())

    def boundary_relations(self, payload):
        return [r for r in payload["relations"] if r.get("kind") == "TRANSPORT_BOUNDARY"]

    def check(self, payload):
        checker = load_module("check_transport_boundary.py", "skill_contract_check_transport_boundary")
        return checker.check(payload)

    def test_simple_literal_survives_simple_github_env_line(self):
        payload = self.projection("transport-env-line-safe.md")
        relations = self.boundary_relations(payload)
        self.assertEqual(1, len(relations))
        relation = relations[0]
        self.assertEqual("PAYLOAD", relation["binding"])
        self.assertEqual("github_env_simple_line", relation["encoding"]["kind"])
        self.assertEqual("literal_string", relation["source_semantics"]["kind"])
        self.assertFalse(relation["source_semantics"]["contains_line_break"])
        result = self.check(payload)
        self.assertEqual("SAFE_WITHIN_SCOPE", result["scope_status"])

    def test_newline_literal_is_transport_semantic_loss(self):
        payload = self.projection("transport-env-line-newline.md")
        relations = self.boundary_relations(payload)
        self.assertEqual(1, len(relations))
        relation = relations[0]
        self.assertEqual("literal_string", relation["source_semantics"]["kind"])
        self.assertTrue(relation["source_semantics"]["contains_line_break"])
        result = self.check(payload)
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("TRANSPORT_SEMANTIC_LOSS", result["counterexamples"][0]["kind"])

    def test_dynamic_source_is_unobservable_not_safe(self):
        payload = self.projection("transport-env-line-dynamic.md")
        relations = self.boundary_relations(payload)
        self.assertEqual(1, len(relations))
        relation = relations[0]
        self.assertEqual("unknown", relation["source_semantics"]["kind"])
        result = self.check(payload)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("UNOBSERVABLE_ROUTING", result["coverage_gaps"][0]["kind"])

    def test_runtime_delivery_safe_does_not_mask_transport_semantic_loss(self):
        payload = self.projection("transport-env-line-newline.md")
        runtime_checker = load_module("check_runtime_binding.py", "skill_contract_check_runtime_binding_transport_interaction")
        transport_result = self.check(payload)
        runtime_result = runtime_checker.check(payload)
        self.assertEqual("SAFE_WITHIN_SCOPE", runtime_result["scope_status"])
        self.assertEqual("UNSAFE", transport_result["scope_status"])
        self.assertEqual("TRANSPORT_SEMANTIC_LOSS", transport_result["counterexamples"][0]["kind"])

    def test_transport_projection_is_byte_deterministic(self):
        path = FIXTURES / "transport-env-line-newline.md"
        first = self.extractor.canonical_json(self.extractor.extract_payload(path.read_bytes()))
        second = self.extractor.canonical_json(self.extractor.extract_payload(path.read_bytes()))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
