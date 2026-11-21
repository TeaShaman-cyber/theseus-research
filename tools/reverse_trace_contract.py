from __future__ import annotations

import fnmatch
import json
import re
from pathlib import Path
from typing import Mapping

SCHEMA_VERSION = "theseus.reverse-trace-invariants.v1"
ROOT_FIELDS = frozenset({"schema_version", "target_repository", "invariants"})
INVARIANT_FIELDS = frozenset(
    {
        "id",
        "title",
        "human_promise",
        "why",
        "status",
        "evidence",
        "watch_paths",
        "watch_terms",
    }
)
EVIDENCE_FIELDS = frozenset({"kind", "ref", "supports"})
VALID_STATUSES = frozenset({"STRONG", "PARTIAL", "DOCUMENTED"})
VALID_EVIDENCE_KINDS = frozenset(
    {"code", "test", "doc", "workflow", "runtime_readback", "historical"}
)
_ID_RE = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]{2}")


def load_contract(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("reverse-trace contract root must be object")
    return document


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _safe_watch_pattern(value: object) -> bool:
    if not _nonempty_string(value):
        return False
    assert isinstance(value, str)
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and "\\" not in value


def validate_contract(document: Mapping[str, object]) -> list[str]:
    errors: list[str] = []

    unexpected_root = sorted(set(document) - ROOT_FIELDS)
    if unexpected_root:
        errors.append(
            "contract root contains unsupported fields: " + ", ".join(unexpected_root)
        )

    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    if not _nonempty_string(document.get("target_repository")):
        errors.append("target_repository must be non-empty string")

    invariants = document.get("invariants")
    if not isinstance(invariants, list):
        return errors + ["invariants must be a list"]

    seen: set[str] = set()
    for raw in invariants:
        if not isinstance(raw, Mapping):
            errors.append("invariant must be an object")
            continue

        invariant_id = raw.get("id")
        if not isinstance(invariant_id, str) or _ID_RE.fullmatch(invariant_id) is None:
            errors.append(f"invariant id has invalid grammar: {invariant_id!r}")
            continue

        if invariant_id in seen:
            errors.append(f"duplicate invariant id: {invariant_id}")
        seen.add(invariant_id)

        unexpected = sorted(set(raw) - INVARIANT_FIELDS)
        if unexpected:
            errors.append(
                f"{invariant_id} contains unsupported fields: "
                + ", ".join(unexpected)
            )

        for field in ("title", "human_promise", "why"):
            if not _nonempty_string(raw.get(field)):
                errors.append(f"{invariant_id} {field} must be non-empty string")

        status = raw.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"{invariant_id} status must be one of {sorted(VALID_STATUSES)}")

        evidence = raw.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{invariant_id} evidence must be non-empty list")
        else:
            for index, item in enumerate(evidence):
                if not isinstance(item, Mapping):
                    errors.append(f"{invariant_id} evidence[{index}] must be object")
                    continue
                unexpected_evidence = sorted(set(item) - EVIDENCE_FIELDS)
                if unexpected_evidence:
                    errors.append(
                        f"{invariant_id} evidence[{index}] contains unsupported fields: "
                        + ", ".join(unexpected_evidence)
                    )
                if item.get("kind") not in VALID_EVIDENCE_KINDS:
                    errors.append(
                        f"{invariant_id} evidence[{index}] has invalid kind: "
                        f"{item.get('kind')!r}"
                    )
                for field in ("ref", "supports"):
                    if not _nonempty_string(item.get(field)):
                        errors.append(
                            f"{invariant_id} evidence[{index}] {field} "
                            "must be non-empty string"
                        )

        watch_paths = raw.get("watch_paths")
        if not isinstance(watch_paths, list) or not watch_paths:
            errors.append(f"{invariant_id} watch_paths must be non-empty list")
        else:
            seen_patterns: set[str] = set()
            for pattern in watch_paths:
                if not _safe_watch_pattern(pattern):
                    errors.append(
                        f"{invariant_id} watch path must be safe relative pattern: "
                        f"{pattern!r}"
                    )
                    continue
                assert isinstance(pattern, str)
                if pattern in seen_patterns:
                    errors.append(f"{invariant_id} duplicate watch path: {pattern}")
                seen_patterns.add(pattern)

        watch_terms = raw.get("watch_terms")
        if not isinstance(watch_terms, list) or not watch_terms:
            errors.append(f"{invariant_id} watch_terms must be non-empty list")
        else:
            seen_terms: set[str] = set()
            for term in watch_terms:
                if not _nonempty_string(term):
                    errors.append(
                        f"{invariant_id} watch term must be non-empty string: {term!r}"
                    )
                    continue
                assert isinstance(term, str)
                if term in seen_terms:
                    errors.append(f"{invariant_id} duplicate watch term: {term}")
                seen_terms.add(term)

    return errors


def affected_invariants(
    document: Mapping[str, object], changed_paths: list[str]
) -> list[dict[str, object]]:
    errors = validate_contract(document)
    if errors:
        raise ValueError("invalid reverse-trace contract: " + "; ".join(errors))

    normalized_paths = sorted(set(changed_paths))
    invariants = document["invariants"]
    assert isinstance(invariants, list)

    affected: list[dict[str, object]] = []
    for raw in invariants:
        assert isinstance(raw, Mapping)
        patterns = raw["watch_paths"]
        assert isinstance(patterns, list)
        matched = [
            path
            for path in normalized_paths
            if any(
                isinstance(pattern, str) and fnmatch.fnmatchcase(path, pattern)
                for pattern in patterns
            )
        ]
        if matched:
            affected.append(
                {
                    "id": raw["id"],
                    "title": raw["title"],
                    "status": raw["status"],
                    "human_promise": raw["human_promise"],
                    "matched_paths": matched,
                }
            )
    return affected

def affected_invariants_from_patches(
    document: Mapping[str, object], patches: Mapping[str, str]
) -> list[dict[str, object]]:
    """Return candidate invariants whose path and semantic-term guards both match.

    This is an impact preflight, not a correctness verdict. A match means
    "review this promise"; absence means only that the declared guards did not
    observe a relevant change.
    """

    errors = validate_contract(document)
    if errors:
        raise ValueError("invalid reverse-trace contract: " + "; ".join(errors))

    normalized = {
        path: patches[path]
        for path in sorted(patches)
    }
    invariants = document["invariants"]
    assert isinstance(invariants, list)

    affected: list[dict[str, object]] = []
    for raw in invariants:
        assert isinstance(raw, Mapping)
        patterns = raw["watch_paths"]
        terms = raw["watch_terms"]
        assert isinstance(patterns, list)
        assert isinstance(terms, list)

        matched_paths: list[str] = []
        matched_terms: set[str] = set()
        for path, patch in normalized.items():
            path_matches = any(
                isinstance(pattern, str) and fnmatch.fnmatchcase(path, pattern)
                for pattern in patterns
            )
            if not path_matches:
                continue

            patch_folded = patch.casefold()
            local_terms = [
                term
                for term in terms
                if isinstance(term, str) and term.casefold() in patch_folded
            ]
            if not local_terms:
                continue

            matched_paths.append(path)
            matched_terms.update(local_terms)

        if matched_paths:
            affected.append(
                {
                    "id": raw["id"],
                    "title": raw["title"],
                    "status": raw["status"],
                    "human_promise": raw["human_promise"],
                    "matched_paths": matched_paths,
                    "matched_terms": sorted(matched_terms),
                }
            )
    return affected
