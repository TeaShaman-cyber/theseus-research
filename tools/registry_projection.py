from __future__ import annotations

from pathlib import Path
from typing import Literal, Mapping

BEGIN_MARKER = "<!-- BEGIN THESEUS_RESEARCH_LINES -->"
END_MARKER = "<!-- END THESEUS_RESEARCH_LINES -->"

_STATUS = {
    "en": {
        "active-root": "public · active / root",
        "active": "public · active",
        "private-incubation": "private incubation",
    },
    "ru": {
        "active-root": "публичное · активно / корень",
        "active": "публичное · активно",
        "private-incubation": "приватная инкубация",
    },
}
_HEADERS = {
    "en": ("Research line", "Visibility / status", "Role"),
    "ru": ("Направление", "Публичность / статус", "Роль"),
}


def _projection_bounds(markdown: str) -> tuple[int, int]:
    if markdown.count(BEGIN_MARKER) != 1 or markdown.count(END_MARKER) != 1:
        raise ValueError("exactly one projection marker pair required")
    begin = markdown.index(BEGIN_MARKER)
    end = markdown.index(END_MARKER)
    if begin >= end:
        raise ValueError("projection markers out of order")
    return begin, end


def render_table(document: Mapping[str, object], language: Literal["en", "ru"]) -> str:
    if language not in _HEADERS:
        raise ValueError(f"unsupported language: {language}")
    raw_lines = document.get("lines")
    if not isinstance(raw_lines, list):
        raise ValueError("registry lines must be a list")

    h1, h2, h3 = _HEADERS[language]
    rows = [f"| {h1} | {h2} | {h3} |", "| --- | --- | --- |"]
    for raw_line in raw_lines:
        if not isinstance(raw_line, Mapping):
            raise ValueError("registry line must be an object")
        line_id = raw_line.get("id")
        status = raw_line.get("status")
        role = raw_line.get("role")
        if not isinstance(line_id, str) or not isinstance(status, str):
            raise ValueError("registry line id/status missing")
        if not isinstance(role, Mapping) or not isinstance(role.get(language), str):
            raise ValueError(f"registry line {line_id} missing {language} role")
        status_text = _STATUS[language].get(status)
        if status_text is None:
            raise ValueError(f"unsupported status for projection: {status}")

        repository = raw_line.get("repository")
        if isinstance(repository, str):
            display = f"[`{line_id}`](https://github.com/{repository})"
        else:
            display = "Sonar" if line_id == "sonar" else f"`{line_id}`"
        role_text = str(role[language]).replace("|", "\\|")
        rows.append(f"| {display} | {status_text} | {role_text} |")
    return "\n".join(rows) + "\n"


def replace_projection(markdown: str, rendered: str) -> str:
    begin, end = _projection_bounds(markdown)
    before = markdown[: begin + len(BEGIN_MARKER)]
    after = markdown[end:]
    normalized = rendered.rstrip("\n") + "\n"
    return f"{before}\n{normalized}{after}"


def projection_matches(path: Path, rendered: str) -> bool:
    markdown = path.read_text(encoding="utf-8")
    try:
        begin, end = _projection_bounds(markdown)
    except ValueError:
        return False
    body_start = begin + len(BEGIN_MARKER)
    observed = markdown[body_start:end]
    if observed.startswith("\n"):
        observed = observed[1:]
    return observed == rendered.rstrip("\n") + "\n"
