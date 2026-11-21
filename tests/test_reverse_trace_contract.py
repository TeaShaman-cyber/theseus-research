import copy
import json
import unittest
from pathlib import Path

from tools.reverse_trace_contract import (
    affected_invariants,
    affected_invariants_from_patches,
    evaluate_proof_witnesses,
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



    def test_declared_proof_witnesses_are_presence_checks_not_correctness_verdicts(self):
        document = load_contract(CONTRACT)
        fail = next(item for item in document["invariants"] if item["id"] == "FAIL-01")
        mini = {
            "schema_version": document["schema_version"],
            "target_repository": document["target_repository"],
            "invariants": [copy.deepcopy(fail)],
        }

        missing = evaluate_proof_witnesses(
            mini,
            {
                "functions/router/handler.mjs": "const shardTimeoutMs = 20; Promise.race([]); TIMEOUT",
            },
        )
        self.assertEqual("DECLARED_WITNESS_MISSING", missing[0]["witness_status"])
        self.assertEqual(
            ["functions/tests/handlers.test.mjs"],
            missing[0]["missing_refs"],
        )

        present = evaluate_proof_witnesses(
            mini,
            {
                "functions/router/handler.mjs": (
                    "shardTimeoutMs Promise.race TIMEOUT"
                ),
                "functions/tests/handlers.test.mjs": (
                    "router times out a stalled shard new Promise(() => {}) TIMEOUT"
                ),
            },
        )
        self.assertEqual(
            "DECLARED_WITNESSES_PRESENT",
            present[0]["witness_status"],
        )

    def test_invariant_without_proof_checks_stays_explicitly_unproven_by_machine_map(self):
        document = load_contract(CONTRACT)
        evidence = next(
            item for item in document["invariants"] if item["id"] == "EVIDENCE-01"
        )
        mini = {
            "schema_version": document["schema_version"],
            "target_repository": document["target_repository"],
            "invariants": [copy.deepcopy(evidence)],
        }
        result = evaluate_proof_witnesses(mini, {})
        self.assertEqual(
            "NO_DECLARED_MACHINE_WITNESS",
            result[0]["witness_status"],
        )

    def test_proof_check_schema_rejects_empty_terms(self):
        document = load_contract(CONTRACT)
        fail = next(item for item in document["invariants"] if item["id"] == "FAIL-01")
        fail["proof_checks"][0]["contains_all"] = []
        self.assertIn(
            "FAIL-01 proof_checks[0] contains_all must be non-empty list",
            validate_contract(document),
        )



if __name__ == "__main__":
    unittest.main()
