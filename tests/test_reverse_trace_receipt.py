import json
import subprocess
import sys
import unittest
from pathlib import Path

from tools.reverse_trace_contract import load_contract
from tools.reverse_trace_receipt import build_receipt_payload

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "research" / "session-search-invariants.json"


class ReverseTraceReceiptTests(unittest.TestCase):
    def test_receipt_binds_exact_revisions_contract_and_matrix(self):
        document = load_contract(CONTRACT)
        patches = {
            "functions/router/handler.mjs": (
                "+Promise.all\n+PARTIAL\n+shardTimeoutMs\n+TIMEOUT\n"
            ),
            "functions/tests/handlers.test.mjs": (
                "+router times out a stalled shard\n"
                "+new Promise(() => {})\n+TIMEOUT\n"
            ),
        }
        files = {
            "functions/router/handler.mjs": "shardTimeoutMs Promise.race TIMEOUT",
            "functions/tests/handlers.test.mjs": (
                "router times out a stalled shard new Promise(() => {}) TIMEOUT"
            ),
        }

        receipt = build_receipt_payload(
            document=document,
            patches=patches,
            files=files,
            repository="TeaShaman-cyber/theseus-session-search-lab",
            base_sha="a" * 40,
            head_sha="b" * 40,
            contract_sha256="c" * 64,
        )

        self.assertEqual("theseus.reverse-trace-receipt.v1", receipt["schema_version"])
        self.assertEqual("a" * 40, receipt["base_sha"])
        self.assertEqual("b" * 40, receipt["head_sha"])
        self.assertEqual("c" * 64, receipt["contract_sha256"])
        self.assertEqual(2, receipt["changed_path_count"])
        self.assertEqual(
            ["functions/router/handler.mjs", "functions/tests/handlers.test.mjs"],
            receipt["changed_paths"],
        )
        fail = next(item for item in receipt["matrix"] if item["id"] == "FAIL-01")
        self.assertEqual("DECLARED_WITNESSES_PRESENT", fail["witness_status"])
        self.assertEqual(
            "EVIDENCE_CHANGED_RECHECK_SEMANTICS",
            fail["review_state"],
        )
        self.assertEqual(
            {"EVIDENCE_CHANGED_RECHECK_SEMANTICS": 1},
            receipt["summary"]["review_states"],
        )

    def test_receipt_summary_is_deterministic(self):
        document = load_contract(CONTRACT)
        patches = {
            "functions/router/core.mjs": "+session_id\n+from_time\n+to_time\n",
        }
        files = {
            "functions/router/core.mjs": "session_id from_time to_time",
        }
        first = build_receipt_payload(
            document=document,
            patches=patches,
            files=files,
            repository="repo/name",
            base_sha="1" * 40,
            head_sha="2" * 40,
            contract_sha256="3" * 64,
        )
        second = build_receipt_payload(
            document=document,
            patches=dict(reversed(list(patches.items()))),
            files=files,
            repository="repo/name",
            base_sha="1" * 40,
            head_sha="2" * 40,
            contract_sha256="3" * 64,
        )
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )


    def test_direct_cli_help_works_from_repository_root(self):
        cp = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "reverse_trace_receipt.py"),
                "--help",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, cp.returncode, cp.stderr)
        self.assertIn("--contract", cp.stdout)
        self.assertIn("--base", cp.stdout)
        self.assertIn("--head", cp.stdout)



if __name__ == "__main__":
    unittest.main()
