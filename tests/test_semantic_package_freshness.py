from __future__ import annotations

import unittest
from datetime import datetime, timezone

from tools.semantic_qa.package_freshness import evaluate_freshness


class PackageFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 20, tzinfo=timezone.utc)

    def test_upstream_move_is_stale_but_not_unavailable(self):
        result = evaluate_freshness(
            now=self.now,
            built_at="2026-09-19T00:00:00Z",
            expires_at="2026-12-19T00:00:00Z",
            max_age_days=30,
            expiry_warning_days=14,
            pinned_git_sha="a" * 40,
            current_git_sha="b" * 40,
        )
        self.assertEqual(result["status"], "STALE_AVAILABLE")
        self.assertTrue(any(x.startswith("upstream_git_moved:") for x in result["reasons"]))

    def test_currentness_failure_is_unknown_not_stale(self):
        result = evaluate_freshness(
            now=self.now,
            built_at="2026-09-19T00:00:00Z",
            expires_at="2026-12-19T00:00:00Z",
            max_age_days=30,
            expiry_warning_days=14,
            currentness_errors=["network unavailable"],
        )
        self.assertEqual(result["status"], "CURRENTNESS_UNKNOWN")

    def test_age_warning_is_nonblocking_stale_state(self):
        result = evaluate_freshness(
            now=self.now,
            built_at="2026-08-01T00:00:00Z",
            expires_at="2026-12-19T00:00:00Z",
            max_age_days=30,
            expiry_warning_days=14,
        )
        self.assertEqual(result["status"], "STALE_AVAILABLE")


if __name__ == "__main__":
    unittest.main()
