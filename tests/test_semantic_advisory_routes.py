import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CALLER = ROOT / ".github/workflows/semantic-advisory.yml"
SEMDUP = ROOT / ".github/workflows/semantic-semdup-advisory.yml"


def workflow(path: Path) -> dict:
    # YAML BaseLoader retains 'on' rather than coercing it to YAML 1.1 boolean.
    return yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


class AdvisoryRoutesTests(unittest.TestCase):
    def test_pull_request_fanout_excludes_expensive_semdup(self):
        jobs = workflow(CALLER)["jobs"]
        self.assertEqual(set(jobs), {"semble", "needle"})
        self.assertNotIn("semantic-semdup-advisory.yml", CALLER.read_text())

    def test_semdup_is_explicit_and_exact_sha_scoped(self):
        w = workflow(SEMDUP)
        self.assertNotIn("pull_request", w["on"])
        self.assertNotIn("schedule", w["on"])
        self.assertIn("workflow_call", w["on"])
        dispatch = w["on"]["workflow_dispatch"]["inputs"]
        for field in ("base_sha", "head_sha", "task_id"):
            self.assertEqual(dispatch[field]["required"], "true")
            self.assertEqual(dispatch[field]["type"], "string")
        call = w["on"]["workflow_call"]["inputs"]
        self.assertEqual(set(call), set(dispatch))
        self.assertIn("inputs.head_sha", SEMDUP.read_text())
        self.assertIn("inputs.base_sha", SEMDUP.read_text())


if __name__ == "__main__":
    unittest.main()
