from __future__ import annotations

from dataclasses import dataclass


ALLOWED_KINDS = ("PREFERENCE", "FACT", "PRIORITY", "ROLE")
MAX_TEXT_LENGTH = 240
MAX_MUST = 2
MAX_MUST_NOT = 2

_ORDER = {
    "TARGET": 0,
    "MUST": 1,
    "MUST_NOT": 2,
    "SCOPE": 3,
}


@dataclass(frozen=True)
class MemoryCorrection:
    kind: str
    target: str
    must: tuple[str, ...]
    must_not: tuple[str, ...] = ()
    scope: str = ""


def _parse_quoted(value: str, field: str) -> str:
    if value != value.strip():
        raise ValueError(f"{field} must use exactly one separator space")
    if len(value) < 2 or not (value.startswith('"') and value.endswith('"')):
        raise ValueError(f"{field} must be a double-quoted string")
    parsed = value[1:-1]
    if not parsed.strip():
        raise ValueError(f"{field} must not be empty")
    if '"' in parsed or "\n" in parsed or "\r" in parsed:
        raise ValueError(f"{field} contains unsupported quoting or newline")
    if len(parsed) > MAX_TEXT_LENGTH:
        raise ValueError(f"{field} exceeds {MAX_TEXT_LENGTH} characters")
    return parsed


def parse_correction(text: str) -> MemoryCorrection:
    if not text.endswith("\n"):
        raise ValueError("correction must end with a newline")

    normalized = text.replace("\r\n", "\n")
    if "\r" in normalized:
        raise ValueError("bare carriage returns are not allowed")

    lines = normalized[:-1].split("\n")
    if not lines or any(not line for line in lines):
        raise ValueError("blank lines are not allowed")
    if any(line != line.strip() for line in lines):
        raise ValueError("leading or trailing whitespace is not allowed")

    first = lines[0].split(" ")
    if len(first) != 2 or first[0] != "CORRECTION":
        raise ValueError("CORRECTION must use exactly one separator space")
    kind = first[1]
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"unsupported correction kind: {kind}")

    target = None
    must: list[str] = []
    must_not: list[str] = []
    scope = None
    last_order = -1

    for line in lines[1:]:
        if " " not in line:
            raise ValueError(f"invalid clause: {line}")
        keyword, raw_value = line.split(" ", 1)
        if not raw_value or raw_value.startswith(" "):
            raise ValueError(f"{keyword} must use exactly one separator space")
        if keyword not in _ORDER:
            raise ValueError(f"unsupported clause: {keyword}")

        order = _ORDER[keyword]
        if order < last_order:
            raise ValueError("clauses must follow canonical order: TARGET, MUST, MUST_NOT, SCOPE")
        last_order = order

        if keyword == "TARGET":
            if target is not None:
                raise ValueError("TARGET may appear only once")
            target = _parse_quoted(raw_value, "TARGET")
        elif keyword == "MUST":
            if len(must) >= MAX_MUST:
                raise ValueError(f"MUST may appear at most {MAX_MUST} times")
            must.append(_parse_quoted(raw_value, "MUST"))
        elif keyword == "MUST_NOT":
            if len(must_not) >= MAX_MUST_NOT:
                raise ValueError(f"MUST_NOT may appear at most {MAX_MUST_NOT} times")
            must_not.append(_parse_quoted(raw_value, "MUST_NOT"))
        elif keyword == "SCOPE":
            if scope is not None:
                raise ValueError("SCOPE may appear only once")
            scope = _parse_quoted(raw_value, "SCOPE")

    if target is None:
        raise ValueError("TARGET is required")
    if not must:
        raise ValueError("at least one MUST correction assertion is required")
    if scope is None:
        raise ValueError("SCOPE is required")

    return MemoryCorrection(
        kind=kind,
        target=target,
        must=tuple(must),
        must_not=tuple(must_not),
        scope=scope,
    )


def render_controlled_prose(correction: MemoryCorrection) -> str:
    sentences = [
        f"Correction type: {correction.kind.lower()}.",
        f"Target: {correction.target}.",
    ]
    sentences.extend(f"Required: {value}." for value in correction.must)
    sentences.extend(
        f"Do not characterize this as {value}." for value in correction.must_not
    )
    sentences.append(f"Scope: {correction.scope}.")
    return " ".join(sentences)
