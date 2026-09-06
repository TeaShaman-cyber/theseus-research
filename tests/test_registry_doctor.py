import copy
import json
import unittest
from pathlib import Path
from urllib.parse import quote_plus

from tools.registry_contract import MANAGED_LABELS, load_registry, public_lines
from tools.registry_doctor import (
    GitHubNotFound,
    GitHubUnavailable,
    discover_candidates,
    run_doctor,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "research-lines.json"


class FakeTransport:
    def __init__(self, responses):
        self.responses = dict(responses)
        self.calls = []

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        key = (method, path)
        if key not in self.responses:
            raise AssertionError(f"unexpected request: {method} {path}")
        value = self.responses[key]
        if isinstance(value, BaseException):
            raise value
        return copy.deepcopy(value)


def search_path(owner="TeaShaman-cyber"):
    query = f"user:{owner} theseus in:name,description"
    return f"/search/repositories?q={quote_plus(query)}&per_page=100"


def healthy_responses(document, candidates=None):
    responses = {}
    for line in public_lines(document):
        repository = line["repository"]
        owner, repo = repository.split("/", 1)
        base = f"/repos/{owner}/{repo}"
        responses[("GET", base)] = {
            "full_name": repository,
            "private": False,
            "description": f"Observed metadata for {repo}",
        }
        responses[("GET", f"{base}/topics")] = {"names": list(line["topics"])}
        responses[("GET", f"{base}/labels?per_page=100")] = [
            {"name": name} for name in MANAGED_LABELS
        ]
        responses[("GET", f"{base}/releases?per_page=100")] = []
    responses[("GET", search_path())] = {"items": candidates or []}
    return responses


class RegistryDoctorTests(unittest.TestCase):
    def setUp(self):
        self.document = load_registry(REGISTRY)

    def _run(self, responses=None):
        transport = FakeTransport(responses or healthy_responses(self.document))
        return run_doctor(self.document, "TeaShaman-cyber", transport), transport

    def test_missing_managed_topic_reports_declared_drift(self):
        responses = healthy_responses(self.document)
        path = "/repos/TeaShaman-cyber/theseus-needle-lab/topics"
        responses[("GET", path)]["names"].remove("needle")
        report, _ = self._run(responses)
        self.assertEqual("DECLARED_DRIFT", report["status"])
        needle = next(x for x in report["declared"] if x["id"] == "theseus-needle-lab")
        self.assertIn("missing topic: needle", needle["drift"])

    def test_unrelated_local_topic_is_informational_not_drift(self):
        responses = healthy_responses(self.document)
        path = "/repos/TeaShaman-cyber/theseus-needle-lab/topics"
        responses[("GET", path)]["names"].append("python")
        report, _ = self._run(responses)
        self.assertEqual("PASS", report["status"])
        needle = next(x for x in report["declared"] if x["id"] == "theseus-needle-lab")
        self.assertIn("python", needle["observed"]["unmanaged_topics"])

    def test_missing_managed_label_reports_declared_drift(self):
        responses = healthy_responses(self.document)
        path = "/repos/TeaShaman-cyber/theseus-research/labels?per_page=100"
        responses[("GET", path)] = [{"name": name} for name in MANAGED_LABELS[:-1]]
        report, _ = self._run(responses)
        self.assertEqual("DECLARED_DRIFT", report["status"])
        root = next(x for x in report["declared"] if x["id"] == "theseus-research")
        self.assertIn("missing managed label: evidence:required", root["drift"])

    def test_managed_labels_are_collected_across_all_pages_before_drift(self):
        responses = healthy_responses(self.document)
        base = "/repos/TeaShaman-cyber/theseus-research"
        first = f"{base}/labels?per_page=100"
        second = f"{base}/labels?per_page=100&page=2"
        responses[("GET", first)] = [{"name": f"unmanaged-{n}"} for n in range(100)]
        responses[("GET", second)] = [{"name": name} for name in MANAGED_LABELS]
        report, transport = self._run(responses)
        self.assertEqual("PASS", report["status"])
        root = next(x for x in report["declared"] if x["id"] == "theseus-research")
        self.assertFalse(any(item.startswith("missing managed label:") for item in root["drift"]))
        self.assertIn(("GET", second, None), transport.calls)

    def test_missing_repository_is_drift_not_deletion(self):
        responses = healthy_responses(self.document)
        path = "/repos/TeaShaman-cyber/theseus-session-search-lab"
        responses[("GET", path)] = GitHubNotFound("not found")
        before = json.dumps(self.document, sort_keys=True)
        report, _ = self._run(responses)
        self.assertEqual("DECLARED_DRIFT", report["status"])
        self.assertEqual(before, json.dumps(self.document, sort_keys=True))
        line = next(x for x in report["declared"] if x["id"] == "theseus-session-search-lab")
        self.assertIn("repository missing", line["drift"])

    def test_api_failure_is_unreachable_not_absence_or_pass(self):
        responses = healthy_responses(self.document)
        path = "/repos/TeaShaman-cyber/theseus-research/topics"
        responses[("GET", path)] = GitHubUnavailable("timeout")
        report, _ = self._run(responses)
        self.assertEqual("UNREACHABLE", report["status"])
        self.assertTrue(report["unreachable"])

    def test_undeclared_candidate_is_advisory_and_does_not_mutate_registry(self):
        candidate = {
            "full_name": "TeaShaman-cyber/theseus-new-lab",
            "name": "theseus-new-lab",
            "description": "Possible Theseus experiment",
            "private": False,
        }
        before = json.dumps(self.document, sort_keys=True)
        report, _ = self._run(healthy_responses(self.document, [candidate]))
        self.assertEqual("CANDIDATE_UNDECLARED", report["status"])
        self.assertEqual(["TeaShaman-cyber/theseus-new-lab"], [x["full_name"] for x in report["candidates"]])
        self.assertEqual(before, json.dumps(self.document, sort_keys=True))

    def test_declared_candidate_is_filtered_out(self):
        declared = {line["repository"] for line in public_lines(self.document)}
        responses = {("GET", search_path()): {"items": [{"full_name": "TeaShaman-cyber/theseus-needle-lab"}]}}
        transport = FakeTransport(responses)
        self.assertEqual([], discover_candidates("TeaShaman-cyber", declared, transport))

    def test_checkpoint_policy_allows_zero_releases(self):
        report, _ = self._run()
        self.assertEqual("PASS", report["status"])

    def test_none_policy_with_release_reports_drift_but_never_creates_release(self):
        document = copy.deepcopy(self.document)
        line = next(x for x in document["lines"] if x["id"] == "theseus-needle-lab")
        line["release_policy"] = "none"
        responses = healthy_responses(document)
        path = "/repos/TeaShaman-cyber/theseus-needle-lab/releases?per_page=100"
        responses[("GET", path)] = [{"id": 1, "tag_name": "v0.1"}]
        transport = FakeTransport(responses)
        report = run_doctor(document, "TeaShaman-cyber", transport)
        self.assertEqual("DECLARED_DRIFT", report["status"])
        self.assertTrue(all(method == "GET" for method, _, _ in transport.calls))
        needle = next(x for x in report["declared"] if x["id"] == "theseus-needle-lab")
        self.assertIn("release policy none but 1 release(s) observed", needle["drift"])

    def test_read_only_doctor_uses_only_get_requests(self):
        report, transport = self._run()
        self.assertEqual("PASS", report["status"])
        self.assertTrue(transport.calls)
        self.assertTrue(all(method == "GET" for method, _, _ in transport.calls))


if __name__ == "__main__":
    unittest.main()

class RegistryDoctorWorkflowTests(unittest.TestCase):
    def test_workflow_is_weekly_manual_and_read_only(self):
        workflow = ROOT / ".github" / "workflows" / "registry-doctor.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("schedule:", text)
        self.assertIn('cron: "17 6 * * 1"', text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("permissions:\n  contents: read", text)
        self.assertNotIn("issues: write", text)
        self.assertNotIn("--drift-issue write", text)
        self.assertRegex(text, r"actions/checkout@[0-9a-f]{40}")
        self.assertIn("python3 tools/check_registry.py doctor", text)
