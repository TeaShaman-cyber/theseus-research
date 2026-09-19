from __future__ import annotations

import re

import json
from pathlib import Path
from typing import Mapping

from tools.registry_projection import BEGIN_MARKER, END_MARKER

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
ROOT_FIELDS = frozenset({"schema_version", "managed_labels", "lines"})
BASELINE_PUBLIC_TOPICS = frozenset({"theseus", "theseus-research-line"})
LINE_FIELDS = frozenset(
    {"id", "repository", "visibility", "role", "topics", "release_policy", "status"}
)
ROLE_FIELDS = frozenset({"en", "ru"})
MAX_REPOSITORY_TOPICS = 20

_GITHUB_OWNER_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")
_GITHUB_REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]{1,100}")
_GITHUB_TOPIC_RE = re.compile(r"[a-z0-9-]{1,50}")


def _is_github_repository_identity(value: object) -> bool:
    if not isinstance(value, str) or value.count("/") != 1:
        return False
    owner, repository = value.split("/", 1)
    if _GITHUB_OWNER_RE.fullmatch(owner) is None or "--" in owner:
        return False
    if _GITHUB_REPOSITORY_RE.fullmatch(repository) is None:
        return False
    if repository in {".", ".."}:
        return False
    return True


def load_registry(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise ValueError("registry root must be object")
    return document


def validate_registry(document: Mapping[str, object]) -> list[str]:
    errors: list[str] = []

    unexpected_root_fields = sorted(set(document) - ROOT_FIELDS)
    if unexpected_root_fields:
        errors.append(
            "registry root contains unsupported fields: "
            + ", ".join(unexpected_root_fields)
        )

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

        unexpected_fields = sorted(set(raw_line) - LINE_FIELDS)
        if unexpected_fields:
            errors.append(
                "line contains unsupported fields: " + ", ".join(unexpected_fields)
            )

        line_id = raw_line.get("id")
        if not isinstance(line_id, str) or not line_id:
            errors.append("line id must be non-empty string")
            continue
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", line_id) is None:
            errors.append(f"line id must be lowercase ASCII slug: {line_id!r}")
            continue
        if line_id in seen_ids:
            errors.append(f"duplicate line id: {line_id}")
        seen_ids.add(line_id)

        visibility = raw_line.get("visibility")
        if not isinstance(visibility, str):
            errors.append(f"visibility for {line_id} must be string")
        elif visibility not in VALID_VISIBILITIES:
            errors.append(f"invalid visibility for {line_id}: {visibility}")

        repository = raw_line.get("repository")
        if visibility == "public":
            if not _is_github_repository_identity(repository):
                errors.append(f"public line {line_id} requires repository")
        elif visibility == "private-incubation" and repository is not None:
            errors.append(f"private-incubation line {line_id} must omit repository")

        role = raw_line.get("role")
        if not isinstance(role, Mapping):
            errors.append(f"role for {line_id} must be localized object")
        else:
            unexpected_role_fields = sorted(set(role) - ROLE_FIELDS)
            if unexpected_role_fields:
                errors.append(
                    f"role for {line_id} contains unsupported fields: "
                    + ", ".join(unexpected_role_fields)
                )
            for language in ("en", "ru"):
                value = role.get(language)
                if not isinstance(value, str) or not value.strip():
                    errors.append(f"role for {line_id} missing {language}")
                elif "\n" in value or "\r" in value:
                    errors.append(f"role for {line_id} {language} must be single-line")
                elif BEGIN_MARKER in value or END_MARKER in value:
                    errors.append(
                        f"role for {line_id} {language} must not contain "
                        "reserved projection markers"
                    )

        status = raw_line.get("status")
        if not isinstance(status, str) or not status:
            errors.append(f"status for {line_id} must be non-empty string")
        elif status not in VALID_STATUSES:
            errors.append(f"invalid status for {line_id}: {status}")
        elif isinstance(visibility, str) and visibility in VALID_VISIBILITIES:
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
        topics_are_valid = isinstance(topics, list) and not any(
            not isinstance(topic, str)
            or _GITHUB_TOPIC_RE.fullmatch(topic) is None
            for topic in topics
        )
        if isinstance(topics, list) and len(topics) > MAX_REPOSITORY_TOPICS:
            errors.append(
                f"topics for {line_id} must contain at most {MAX_REPOSITORY_TOPICS} entries"
            )
        if not topics_are_valid:
            errors.append(
                f"topics for {line_id} must match GitHub topic grammar "
                "(lowercase ASCII letters, digits, hyphens; 1-50 chars)"
            )
        elif visibility == "public":
            missing_baseline = sorted(BASELINE_PUBLIC_TOPICS - set(topics))
            if missing_baseline:
                errors.append(
                    f"public line {line_id} missing baseline topics: "
                    + ", ".join(missing_baseline)
                )

        release_policy = raw_line.get("release_policy")
        if not isinstance(release_policy, str):
            errors.append(f"release policy for {line_id} must be string")
        elif release_policy not in VALID_RELEASE_POLICIES:
            errors.append(f"invalid release policy for {line_id}: {release_policy}")

    active_roots = [
        line.get("id")
        for line in lines
        if isinstance(line, Mapping)
        and line.get("visibility") == "public"
        and line.get("status") == "active-root"
    ]
    if active_roots != ["theseus-research"]:
        errors.append(
            "public active-root must be exactly theseus-research; observed: "
            + (", ".join(str(item) for item in active_roots) if active_roots else "none")
        )

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
