import copy
import unittest

from tools.registry_doctor import (
    DRIFT_ISSUE_TITLE,
    ensure_drift_issue,
    render_drift_issue_body,
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = dict(responses)
        self.calls = []

    def request(self, method, path, body=None):
        self.calls.append((method, path, copy.deepcopy(body)))
        key = (method, path)
        if key not in self.responses:
            raise AssertionError(f"unexpected request: {method} {path}")
        value = self.responses[key]
        return copy.deepcopy(value)


def drift_report():
    return {
        "status": "DECLARED_DRIFT",
        "owner": "TeaShaman-cyber",
        "declared": [
            {
                "id": "theseus-needle-lab",
                "repository": "TeaShaman-cyber/theseus-needle-lab",
                "status": "DECLARED_DRIFT",
                "drift": ["missing topic: needle"],
                "observed": {},
            },
            {
                "id": "theseus-tech-review-graph",
                "repository": "TeaShaman-cyber/theseus-tech-review-graph",
                "status": "DECLARED_DRIFT",
                "drift": ["missing managed label: kind:research"],
                "observed": {},
            },
        ],
        "candidates": [],
        "unreachable": [],
    }


class RegistryIssueTests(unittest.TestCase):
    repository = "TeaShaman-cyber/theseus-research"
    list_path = "/repos/TeaShaman-cyber/theseus-research/issues?state=open&per_page=100"
    create_path = "/repos/TeaShaman-cyber/theseus-research/issues"

    def test_create_once_when_exact_open_issue_missing(self):
        transport = FakeTransport(
            {
                ("GET", self.list_path): [],
                ("POST", self.create_path): {
                    "number": 41,
                    "html_url": "https://github.com/TeaShaman-cyber/theseus-research/issues/41",
                },
            }
        )
        result = ensure_drift_issue(self.repository, drift_report(), transport)
        self.assertEqual("created", result["action"])
        posts = [call for call in transport.calls if call[0] == "POST"]
        self.assertEqual(1, len(posts))
        self.assertEqual(DRIFT_ISSUE_TITLE, posts[0][2]["title"])
        self.assertIn(
            "This issue is a drift report. It does not declare any repository part of Theseus.",
            posts[0][2]["body"],
        )

    def test_existing_exact_issue_gets_one_comment(self):
        comment_path = "/repos/TeaShaman-cyber/theseus-research/issues/12/comments"
        transport = FakeTransport(
            {
                ("GET", self.list_path): [
                    {"number": 12, "title": DRIFT_ISSUE_TITLE, "html_url": "https://example/12"}
                ],
                ("POST", comment_path): {"id": 55, "html_url": "https://example/comment/55"},
            }
        )
        result = ensure_drift_issue(self.repository, drift_report(), transport)
        self.assertEqual("commented", result["action"])
        self.assertEqual(12, result["issue_number"])
        self.assertEqual(1, len([call for call in transport.calls if call[0] == "POST"]))

    def test_existing_issue_on_second_page_is_reused_not_duplicated(self):
        second_page = self.list_path + "&page=2"
        comment_path = "/repos/TeaShaman-cyber/theseus-research/issues/212/comments"
        first_page = [
            {"number": n, "title": f"Other issue {n}", "html_url": f"https://example/{n}"}
            for n in range(1, 101)
        ]
        transport = FakeTransport(
            {
                ("GET", self.list_path): first_page,
                ("GET", second_page): [
                    {"number": 212, "title": DRIFT_ISSUE_TITLE, "html_url": "https://example/212"}
                ],
                ("POST", comment_path): {"id": 88, "html_url": "https://example/comment/88"},
            }
        )
        result = ensure_drift_issue(self.repository, drift_report(), transport)
        self.assertEqual("commented", result["action"])
        self.assertEqual(212, result["issue_number"])
        self.assertNotIn(("POST", self.create_path), [(m, p) for m, p, _ in transport.calls])

    def test_multiple_drift_entries_still_produce_one_write_action(self):
        transport = FakeTransport(
            {
                ("GET", self.list_path): [],
                ("POST", self.create_path): {"number": 9, "html_url": "https://example/9"},
            }
        )
        ensure_drift_issue(self.repository, drift_report(), transport)
        self.assertEqual(1, len([call for call in transport.calls if call[0] == "POST"]))

    def test_pull_request_with_same_title_is_ignored(self):
        transport = FakeTransport(
            {
                ("GET", self.list_path): [
                    {
                        "number": 77,
                        "title": DRIFT_ISSUE_TITLE,
                        "pull_request": {"url": "https://api.github.com/pulls/77"},
                    }
                ],
                ("POST", self.create_path): {"number": 78, "html_url": "https://example/78"},
            }
        )
        result = ensure_drift_issue(self.repository, drift_report(), transport)
        self.assertEqual("created", result["action"])
        self.assertEqual(78, result["issue_number"])

    def test_pass_refuses_write_before_transport_call(self):
        transport = FakeTransport({})
        with self.assertRaisesRegex(ValueError, "drift issue write not allowed for PASS"):
            ensure_drift_issue(self.repository, {"status": "PASS"}, transport)
        self.assertEqual([], transport.calls)

    def test_unreachable_refuses_write_before_transport_call(self):
        transport = FakeTransport({})
        with self.assertRaisesRegex(ValueError, "drift issue write not allowed for UNREACHABLE"):
            ensure_drift_issue(self.repository, {"status": "UNREACHABLE"}, transport)
        self.assertEqual([], transport.calls)

    def test_body_is_deterministic_and_contains_candidate_warning(self):
        report = drift_report()
        report["status"] = "CANDIDATE_UNDECLARED"
        report["candidates"] = [{"full_name": "TeaShaman-cyber/theseus-new-lab"}]
        first = render_drift_issue_body(report)
        self.assertEqual(first, render_drift_issue_body(report))
        self.assertIn("theseus-new-lab", first)
        self.assertIn("does not declare any repository part of Theseus", first)


if __name__ == "__main__":
    unittest.main()
