import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


VERSION_TOKEN = r"[0-9]+(?:\.[0-9]+)+(?:-[A-Za-z0-9.-]+)?"


def _first_revision_version(
    text: str,
    name: str,
    marker: str,
    valid_pattern: str,
) -> str:
    candidate = next(
        (line for line in text.splitlines() if marker.casefold() in line.casefold()),
        None,
    )
    if candidate is None:
        raise ValueError(f"missing current contract version surface: {name}")
    match = re.fullmatch(valid_pattern, candidate)
    if match is None:
        raise ValueError(f"malformed current contract version surface: {name}")
    return match.group(1)


def current_contract_versions(en: str, ru: str, changelog: str) -> dict[str, str]:
    patterns = {
        "en_header": (en, r"^\*\*Version:\*\* `([^`]+)`$"),
        "ru_header": (ru, r"^\*\*Версия:\*\* `([^`]+)`$"),
    }
    out: dict[str, str] = {}
    for name, (text, pattern) in patterns.items():
        match = re.search(pattern, text, re.MULTILINE)
        if match is None:
            raise ValueError(f"missing current contract version surface: {name}")
        out[name] = match.group(1)

    out["en_revision"] = _first_revision_version(
        en,
        "en_revision",
        "revision record",
        rf"### Revision record: `({VERSION_TOKEN})` \u2014 .+",
    )
    out["ru_revision"] = _first_revision_version(
        ru,
        "ru_revision",
        "запись о ревизии",
        rf"### Запись о ревизии: `({VERSION_TOKEN})` \u2014 .+",
    )

    lines = changelog.splitlines()
    title_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("# ") and not line.startswith("## ")
        ),
        None,
    )
    if title_index is None:
        raise ValueError("missing current contract version surface: changelog")

    candidate_pattern = re.compile(r"(?:^\s*##|\b[0-9]+\.[A-Za-z0-9.-]+\b)")
    heading = next(
        (
            line
            for line in lines[title_index + 1 :]
            if candidate_pattern.search(line)
        ),
        None,
    )
    if heading is None:
        raise ValueError("missing current contract version surface: changelog")
    match = re.fullmatch(
        rf"## ({VERSION_TOKEN})\s+—\s+.+",
        heading,
    )
    if match is None:
        raise ValueError("malformed current contract version surface: changelog")
    out["changelog"] = match.group(1)
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

    def test_changelog_parser_preserves_patch_version(self):
        versions = current_contract_versions(
            "**Version:** `1.1.1`\n### Revision record: `1.1.1` — 2026-09-18\n",
            "**Версия:** `1.1.1`\n### Запись о ревизии: `1.1.1` — 2026-09-18\n",
            "# Theseus Contract Changelog\n\n## 1.1.1 — 2026-09-18\n",
        )
        self.assertEqual("1.1.1", versions["changelog"])
        self.assertEqual({"1.1.1"}, set(versions.values()))

    def test_malformed_new_changelog_head_does_not_fall_through_to_history(self):
        for malformed_heading in (
            "## 1.2 - 2026-10-01",
            "##1.2 — 2026-10-01",
            " ## 1.2 — 2026-10-01",
            "### 1.2 — 2026-10-01",
            "1.2 — 2026-10-01",
            "draft 1.2 — 2026-10-01",
            "## 1.x — 2026-10-01",
            "## 1.2: 2026-10-01",
        ):
            with self.subTest(heading=malformed_heading):
                broken = (
                    "# Theseus Contract Changelog\n\n"
                    "intro\n\n"
                    f"{malformed_heading}\n"
                    "broken new entry\n\n"
                    "## 1.1 — 2026-09-18\n"
                    "historical valid entry\n"
                )
                with self.assertRaisesRegex(
                    ValueError,
                    "malformed current contract version surface: changelog",
                ):
                    current_contract_versions(self.en, self.ru, broken)

    def test_malformed_new_revision_record_does_not_fall_through_to_history(self):
        valid_en = (
            "**Version:** `1.1`\n"
            "### Revision record: `1.1` — 2026-09-18\n"
        )
        valid_ru = (
            "**Версия:** `1.1`\n"
            "### Запись о ревизии: `1.1` — 2026-09-18\n"
        )
        changelog = "# Theseus Contract Changelog\n\n## 1.1 — 2026-09-18\n"

        malformed_en = (
            "**Version:** `1.1`\n"
            "### Revision Record: `1.2`\n"
            "### Revision record: `1.1` — 2026-09-18\n"
        )
        with self.assertRaisesRegex(
            ValueError,
            "malformed current contract version surface: en_revision",
        ):
            current_contract_versions(malformed_en, valid_ru, changelog)

        malformed_ru = (
            "**Версия:** `1.1`\n"
            "### Запись о ревизии `1.2`\n"
            "### Запись о ревизии: `1.1` — 2026-09-18\n"
        )
        with self.assertRaisesRegex(
            ValueError,
            "malformed current contract version surface: ru_revision",
        ):
            current_contract_versions(valid_en, malformed_ru, changelog)

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
