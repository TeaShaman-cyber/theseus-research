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


class RuntimeBindingExtractorTests(unittest.TestCase):
    def setUp(self):
        self.extractor = load_module("extract_plan.py", "skill_contract_extract_plan")

    def projection(self, fixture):
        return self.extractor.extract_payload((FIXTURES / fixture).read_bytes())

    def runtime_relations(self, payload):
        return [r for r in payload["relations"] if r.get("kind") == "RUNTIME_BINDING"]

    def check(self, payload):
        checker = load_module("check_runtime_binding.py", "skill_contract_check_runtime_binding")
        return checker.check(payload)

    def test_process_local_export_does_not_cross_explicit_actions_run_steps(self):
        payload = self.projection("runtime-binding-actions-process-local.md")
        relations = self.runtime_relations(payload)
        self.assertEqual(1, len(relations))
        relation = relations[0]
        self.assertEqual("BUILD_ROOT", relation["binding"])
        self.assertEqual("github_actions_run_step", relation["producer"]["boundary"])
        self.assertEqual("shell_export", relation["producer"]["kind"])
        self.assertEqual("process_local", relation["transport"]["kind"])
        self.assertEqual("github_actions_run_step", relation["consumer"]["boundary"])
        result = self.check(payload)
        self.assertEqual("UNSAFE", result["scope_status"])
        self.assertEqual("RUNTIME_BINDING_NOT_TRANSPORTED", result["counterexamples"][0]["kind"])

    def test_github_env_write_crosses_explicit_actions_run_steps(self):
        payload = self.projection("runtime-binding-actions-github-env.md")
        relations = self.runtime_relations(payload)
        self.assertEqual(1, len(relations))
        relation = relations[0]
        self.assertEqual("BUILD_ROOT", relation["binding"])
        self.assertEqual("github_env_write", relation["producer"]["kind"])
        self.assertEqual("github_env_next_steps", relation["transport"]["kind"])
        result = self.check(payload)
        self.assertEqual("SAFE_WITHIN_SCOPE", result["scope_status"])
        self.assertEqual([], result["counterexamples"])
        self.assertEqual([], result["coverage_gaps"])

    def test_markdown_adjacency_alone_does_not_create_runtime_boundary(self):
        payload = self.projection("runtime-binding-markdown-no-boundary.md")
        self.assertEqual([], self.runtime_relations(payload))
        result = self.check(payload)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])

    def test_runtime_projection_is_byte_deterministic(self):
        path = FIXTURES / "runtime-binding-actions-github-env.md"
        first = self.extractor.canonical_json(self.extractor.extract_payload(path.read_bytes()))
        second = self.extractor.canonical_json(self.extractor.extract_payload(path.read_bytes()))
        self.assertEqual(first, second)

    def test_unknown_producer_is_unobservable_not_safe(self):
        payload = self.projection("runtime-binding-actions-unobservable.md")
        relations = self.runtime_relations(payload)
        self.assertEqual(1, len(relations))
        relation = relations[0]
        self.assertEqual("BUILD_ROOT", relation["binding"])
        self.assertIsNone(relation["producer"])
        self.assertEqual("unknown", relation["transport"]["kind"])
        result = self.check(payload)
        self.assertEqual("UNOBSERVABLE_AT_THIS_LAYER", result["scope_status"])
        self.assertEqual("UNOBSERVABLE_ROUTING", result["coverage_gaps"][0]["kind"])


if __name__ == "__main__":
    unittest.main()
