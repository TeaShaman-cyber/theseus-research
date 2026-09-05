import copy
import unittest
from pathlib import Path

from tools.registry_contract import (
    MANAGED_LABELS,
    load_registry,
    public_lines,
    validate_registry,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "research-lines.json"


class RegistryContractTests(unittest.TestCase):
    def test_committed_registry_is_valid(self):
        doc = load_registry(REGISTRY)
        self.assertEqual([], validate_registry(doc))
        self.assertEqual(
            [
                "theseus-research",
                "theseus-public-observatory",
                "theseus-needle-lab",
                "theseus-memory-provider-lab",
                "theseus-model-usage-lab",
                "theseus-session-search-lab",
                "theseus-tech-review-graph",
            ],
            [line["id"] for line in public_lines(doc)],
        )

    def test_ids_must_be_unique(self):
        doc = load_registry(REGISTRY)
        doc["lines"].append(copy.deepcopy(doc["lines"][0]))
        self.assertIn("duplicate line id: theseus-research", validate_registry(doc))

    def test_public_line_requires_repository(self):
        doc = load_registry(REGISTRY)
        line = next(x for x in doc["lines"] if x["id"] == "theseus-needle-lab")
        line.pop("repository")
        self.assertIn(
            "public line theseus-needle-lab requires repository",
            validate_registry(doc),
        )

    def test_private_line_may_omit_repository(self):
        doc = load_registry(REGISTRY)
        sonar = next(x for x in doc["lines"] if x["id"] == "sonar")
        self.assertNotIn("repository", sonar)
        self.assertEqual([], validate_registry(doc))

    def test_invalid_status_is_rejected(self):
        doc = load_registry(REGISTRY)
        line = next(x for x in doc["lines"] if x["id"] == "theseus-needle-lab")
        line["status"] = "activ"
        self.assertIn("invalid status for theseus-needle-lab: activ", validate_registry(doc))

    def test_invalid_release_policy_is_rejected(self):
        doc = load_registry(REGISTRY)
        doc["lines"][0]["release_policy"] = "continuous"
        self.assertIn(
            "invalid release policy for theseus-research: continuous",
            validate_registry(doc),
        )

    def test_managed_labels_are_closed_vocabulary(self):
        doc = load_registry(REGISTRY)
        doc["managed_labels"].append("status:accepted")
        self.assertIn("managed_labels must exactly match contract", validate_registry(doc))
        self.assertEqual(
            (
                "kind:research",
                "kind:engineering",
                "kind:operations",
                "scope:cross-project",
                "evidence:required",
            ),
            MANAGED_LABELS,
        )


if __name__ == "__main__":
    unittest.main()
