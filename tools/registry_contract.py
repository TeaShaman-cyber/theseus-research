from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

VALID_VISIBILITIES = frozenset({"public", "private-incubation"})
VALID_RELEASE_POLICIES = frozenset({"none", "checkpoint", "product"})
VALID_STATUSES = frozenset({"active-root", "active", "private-incubation"})
MANAGED_LABELS = (
    "kind:research",
    "kind:engineering",
    "kind:operations",
    "scope:cross-project",
    "evidence:required",
)
SCHEMA_VERSION = "theseus-research-lines-v1"


def load_registry(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("registry root must be object")
    return document


def validate_registry(document: Mapping[str, object]) -> list[str]:
    errors: list[str] = []

    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    managed_labels = document.get("managed_labels")
    if managed_labels != list(MANAGED_LABELS):
        errors.append("managed_labels must exactly match contract")

    lines = document.get("lines")
    if not isinstance(lines, list):
        return errors + ["lines must be a list"]

    seen_ids: set[str] = set()
    for raw_line in lines:
        if not isinstance(raw_line, Mapping):
            errors.append("line must be an object")
            continue

        line_id = raw_line.get("id")
        if not isinstance(line_id, str) or not line_id:
            errors.append("line id must be non-empty string")
            continue
        if line_id in seen_ids:
            errors.append(f"duplicate line id: {line_id}")
        seen_ids.add(line_id)

        visibility = raw_line.get("visibility")
        if visibility not in VALID_VISIBILITIES:
            errors.append(f"invalid visibility for {line_id}: {visibility}")

        repository = raw_line.get("repository")
        if visibility == "public":
            if not isinstance(repository, str):
                errors.append(f"public line {line_id} requires repository")
            else:
                parts = repository.split("/")
                if len(parts) != 2 or any(not part.strip() for part in parts):
                    errors.append(f"public line {line_id} requires repository")
        elif visibility == "private-incubation" and repository is not None:
            errors.append(f"private-incubation line {line_id} must omit repository")

        role = raw_line.get("role")
        if not isinstance(role, Mapping):
            errors.append(f"role for {line_id} must be localized object")
        else:
            for language in ("en", "ru"):
                value = role.get(language)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"role for {line_id} missing {language}")

        status = raw_line.get("status")
        if not isinstance(status, str) or not status:
            errors.append(f"status for {line_id} must be non-empty string")
        elif status not in VALID_STATUSES:
            errors.append(f"invalid status for {line_id}: {status}")
        elif visibility in VALID_VISIBILITIES:
            allowed_statuses = (
                {"active-root", "active"}
                if visibility == "public"
                else {"private-incubation"}
            )
            if status not in allowed_statuses:
                errors.append(
                    f"visibility/status mismatch for {line_id}: {visibility}/{status}"
                )

        topics = raw_line.get("topics")
        if not isinstance(topics, list) or any(
            not isinstance(topic, str) or not topic for topic in topics
        ):
            errors.append(f"topics for {line_id} must be string list")

        release_policy = raw_line.get("release_policy")
        if release_policy not in VALID_RELEASE_POLICIES:
            errors.append(f"invalid release policy for {line_id}: {release_policy}")

    return errors


def public_lines(document: Mapping[str, object]) -> list[Mapping[str, object]]:
    lines = document.get("lines", [])
    if not isinstance(lines, list):
        return []
    return [
        line
        for line in lines
        if isinstance(line, Mapping) and line.get("visibility") == "public"
    ]
