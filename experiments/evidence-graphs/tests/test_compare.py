import importlib.util
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "compare.py"
spec = importlib.util.spec_from_file_location("compare", MODULE)
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)


def sample(edges=None):
    return {
        "schema_version": "1.0",
        "case_id": "sample",
        "label": "sample",
        "outcome_class": "successful",
        "sources": [
            {"id": "s1", "kind": "primary", "locator": "https://example.test/1"},
            {"id": "s2", "kind": "formal_artifact", "locator": "https://example.test/2"}
        ],
        "nodes": [
            {"id": "p", "label": "problem", "role": "problem"},
            {"id": "b", "label": "bridge", "role": "bridge_theorem"},
            {"id": "c", "label": "consequence", "role": "consequence"}
        ],
        "edges": edges or [
            {"source": "p", "target": "b", "role": "bridges", "evidence": "established_theorem", "source_refs": ["s1"]},
            {"source": "b", "target": "c", "role": "verifies", "evidence": "kernel_checked", "source_refs": ["s2"]}
        ]
    }


class CompareTests(unittest.TestCase):
    def test_baseline_passes_sourced_chain(self):
        case = sample()
        compare.validate_case(case)
        self.assertTrue(compare.baseline(case)["pass"])

    def test_analogy_breaks_baseline(self):
        case = sample([
            {"source": "p", "target": "b", "role": "analogy", "evidence": "analogy_only", "source_refs": ["s1"]},
            {"source": "b", "target": "c", "role": "verifies", "evidence": "kernel_checked", "source_refs": ["s2"]}
        ])
        compare.validate_case(case)
        self.assertFalse(compare.baseline(case)["pass"])

    def test_cycle_detected(self):
        case = sample()
        case["edges"].append({"source": "c", "target": "p", "role": "depends_on", "evidence": "primary_exposition", "source_refs": ["s1"]})
        self.assertIsNone(compare.topo(case))

    def test_analogy_cannot_claim_kernel_checked(self):
        case = sample([
            {"source": "p", "target": "c", "role": "analogy", "evidence": "kernel_checked", "source_refs": ["s2"]}
        ])
        with self.assertRaises(ValueError):
            compare.validate_case(case)


if __name__ == "__main__":
    unittest.main()
