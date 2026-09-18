import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def current_contract_versions(en: str, ru: str, changelog: str) -> dict[str, str]:
    patterns = {
        "en_header": (en, r"^\*\*Version:\*\* `([^`]+)`$"),
        "ru_header": (ru, r"^\*\*Версия:\*\* `([^`]+)`$"),
        "en_revision": (en, r"^### Revision record: `([^`]+)`"),
        "ru_revision": (ru, r"^### Запись о ревизии: `([^`]+)`"),
        "changelog": (changelog, r"^## ([0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?)\b"),
    }
    out: dict[str, str] = {}
    for name, (text, pattern) in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        if match is None:
            raise ValueError(f"missing current contract version surface: {name}")
        out[name] = match.group(1)
    return out


def assert_atomic_contract_versions(en: str, ru: str, changelog: str) -> None:
    versions = current_contract_versions(en, ru, changelog)
    unique = set(versions.values())
    if len(unique) != 1:
        detail = ", ".join(f"{name}={version}" for name, version in versions.items())
        raise ValueError(f"contract version surfaces disagree: {detail}")


class ContractAtomicityTests(unittest.TestCase):
    def setUp(self):
        self.en = (ROOT / "README.md").read_text(encoding="utf-8")
        self.ru = (ROOT / "README.ru.md").read_text(encoding="utf-8")
        self.changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    def test_committed_contract_version_surfaces_move_atomically(self):
        assert_atomic_contract_versions(self.en, self.ru, self.changelog)

    def test_mismatched_bilingual_header_fails_for_intended_reason(self):
        current = current_contract_versions(self.en, self.ru, self.changelog)["ru_header"]
        replacement = "0.0-test" if current != "0.0-test" else "9.9-test"
        broken_ru = self.ru.replace(
            f"**Версия:** `{current}`",
            f"**Версия:** `{replacement}`",
            1,
        )
        self.assertNotEqual(self.ru, broken_ru)
        with self.assertRaisesRegex(ValueError, "contract version surfaces disagree"):
            assert_atomic_contract_versions(self.en, broken_ru, self.changelog)

    def test_mismatched_changelog_head_fails_for_intended_reason(self):
        current = current_contract_versions(self.en, self.ru, self.changelog)["changelog"]
        replacement = "0.0-test" if current != "0.0-test" else "9.9-test"
        broken_changelog = re.sub(
            rf"^## {re.escape(current)}\b",
            f"## {replacement}",
            self.changelog,
            count=1,
            flags=re.MULTILINE,
        )
        self.assertNotEqual(self.changelog, broken_changelog)
        with self.assertRaisesRegex(ValueError, "contract version surfaces disagree"):
            assert_atomic_contract_versions(self.en, self.ru, broken_changelog)


if __name__ == "__main__":
    unittest.main()
