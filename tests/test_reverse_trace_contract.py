import copy
import json
import unittest
from pathlib import Path

from tools.reverse_trace_contract import (
    affected_invariants,
    affected_invariants_from_patches,
    load_contract,
    validate_contract,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "session-search-invariants.json"


class ReverseTraceContractTests(unittest.TestCase):
    def test_committed_session_search_contract_is_valid(self):
        document = load_contract(CONTRACT)
        self.assertEqual([], validate_contract(document))
        self.assertEqual(
            [
                "EVIDENCE-01",
                "CORPUS-01",
                "VERIFY-01",
                "PORT-01",
                "BIND-01",
                "FAIL-01",
                "ROUTE-01",
                "GEN-01",
                "PIN-01",
                "PROV-01",
                "COVERAGE-01",
                "TOOL-ID-01",
                "SEC-01",
                "OBS-01",
                "PRIV-01",
            ],
            [item["id"] for item in document["invariants"]],
        )

    def test_contract_rejects_unknown_fields_and_missing_human_meaning(self):
        document = load_contract(CONTRACT)
        document["invariants"][0]["surprise"] = "silent schema drift"
        document["invariants"][1]["human_promise"] = "   "
        errors = validate_contract(document)
        self.assertIn(
            "EVIDENCE-01 contains unsupported fields: surprise",
            errors,
        )
        self.assertIn(
            "CORPUS-01 human_promise must be non-empty string",
            errors,
        )

    def test_contract_requires_evidence_and_watch_paths(self):
        document = load_contract(CONTRACT)
        document["invariants"][0]["evidence"] = []
        document["invariants"][1]["watch_paths"] = []
        errors = validate_contract(document)
        self.assertIn("EVIDENCE-01 evidence must be non-empty list", errors)
        self.assertIn("CORPUS-01 watch_paths must be non-empty list", errors)

    def test_pr66_changed_paths_surface_relevant_candidate_invariants(self):
        document = load_contract(CONTRACT)
        changed_paths = [
            "docs/federated-serving-plane.md",
            "functions/router/core.mjs",
            "functions/router/handler.mjs",
            "functions/tests/handlers.test.mjs",
            "functions/tests/serving.test.mjs",
            "sql/neon/001_federated_shard_v1.sql",
            "sql/neon/002_federated_shard_privileges.sql",
            "tests/test_neon_federated_contract.py",
        ]
        affected = affected_invariants(document, changed_paths)
        affected_ids = [item["id"] for item in affected]

        for expected in (
            "FAIL-01",
            "ROUTE-01",
            "GEN-01",
            "PIN-01",
            "PROV-01",
            "SEC-01",
        ):
            self.assertIn(expected, affected_ids)

        self.assertNotIn("OBS-01", affected_ids)

    def test_affected_invariants_are_deterministic_and_explain_matches(self):
        document = load_contract(CONTRACT)
        first = affected_invariants(
            document,
            ["functions/router/handler.mjs", "functions/router/core.mjs"],
        )
        second = affected_invariants(
            document,
            ["functions/router/core.mjs", "functions/router/handler.mjs"],
        )
        self.assertEqual(first, second)
        fail = next(item for item in first if item["id"] == "FAIL-01")
        self.assertEqual(
            ["functions/router/core.mjs", "functions/router/handler.mjs"],
            fail["matched_paths"],
        )


    def test_patch_terms_reduce_path_only_noise(self):
        document = load_contract(CONTRACT)

        harmless_router_patch = {
            "functions/router/handler.mjs": "@@\n-const label = 'old';\n+const label = 'new';\n"
        }
        affected = affected_invariants_from_patches(document, harmless_router_patch)
        self.assertNotIn("FAIL-01", [item["id"] for item in affected])
        self.assertNotIn("ROUTE-01", [item["id"] for item in affected])

        failure_semantics_patch = {
            "functions/router/handler.mjs": (
                "@@\n"
                "+const outcomes = await Promise.all(selected.map(fetchShard));\n"
                "+return mergeShardOutcomes(outcomes, 'PARTIAL');\n"
            )
        }
        affected = affected_invariants_from_patches(document, failure_semantics_patch)
        self.assertIn("FAIL-01", [item["id"] for item in affected])

        routing_patch = {
            "functions/router/core.mjs": (
                "@@\n"
                "+if (input.from_time != null) selectShards(catalog, input);\n"
                "+const session_id = input.session_id;\n"
            )
        }
        affected = affected_invariants_from_patches(document, routing_patch)
        self.assertIn("ROUTE-01", [item["id"] for item in affected])

    def test_patch_term_matches_are_reported_deterministically(self):
        document = load_contract(CONTRACT)
        patches = {
            "functions/router/handler.mjs": "+Promise.all\n+PARTIAL\n",
            "functions/router/core.mjs": "+PARTIAL\n",
        }
        affected = affected_invariants_from_patches(document, patches)
        fail = next(item for item in affected if item["id"] == "FAIL-01")
        self.assertEqual(
            ["functions/router/core.mjs", "functions/router/handler.mjs"],
            fail["matched_paths"],
        )
        self.assertEqual(["PARTIAL", "Promise.all"], fail["matched_terms"])



if __name__ == "__main__":
    unittest.main()
