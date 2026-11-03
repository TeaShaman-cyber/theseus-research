#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import yaml
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "governance" / "chatgpt-project-contract.yaml"
LEGACY = ROOT / "governance" / "legacy" / "project-contract-v10.wl"
PROJECTION = ROOT / "governance" / "project-settings.txt"
MAX_PROJECT_SETTINGS_CHARS = 8000
ACCEPTED_V10_REVISION = "2026-11-skill-router-v10"
ACCEPTED_V10_LEGACY_GIT_BLOB = "614fee41c7dc16816e0cdbd35441466bd9bb7904"

_REQUIRED_TOP = {
    "Scope",
    "Revision",
    "Probe",
    "CanonicalSource",
    "Epistemics",
    "Truth",
    "WorkingCulture",
    "OperationalBootstrap",
    "Precedence",
    "ChangeControl",
    "Continuity",
    "Currentness",
    "Authority",
    "Capabilities",
    "Routing",
    "QADiscovery",
    "Fallback",
    "Permission",
    "Verification",
    "Persistence",
    "RuntimeBoundary",
    "DegradedMode",
    "Action",
}


class ContractError(ValueError):
    pass


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


class _IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def _construct_unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ContractError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_source(path: Path | None = None) -> dict[str, Any]:
    path = SOURCE if path is None else path
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise ContractError(f"invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError("project contract source must be a YAML mapping")
    return data


_TOKEN = re.compile(
    r'\s*(?:(<\||\|>|->|[{},=;])|("(?:\\.|[^"\\])*")|([A-Za-z_][A-Za-z0-9_]*))',
    re.DOTALL,
)


class _WLParser:
    def __init__(self, text: str):
        self.tokens: list[tuple[str, str]] = []
        pos = 0
        while pos < len(text):
            match = _TOKEN.match(text, pos)
            if not match:
                if text[pos:].strip() == "":
                    pos = len(text)
                    break
                raise ContractError(
                    f"unsupported WL syntax near offset {pos}: {text[pos:pos+40]!r}"
                )
            punct, string, ident = match.groups()
            if punct is not None:
                self.tokens.append(("punct", punct))
            elif string is not None:
                self.tokens.append(("string", string))
            elif ident is not None:
                self.tokens.append(("ident", ident))
            pos = match.end()
        self.i = 0

    def _peek(self) -> tuple[str, str] | None:
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def _take(
        self,
        kind: str | None = None,
        value: str | None = None,
    ) -> tuple[str, str]:
        tok = self._peek()
        if tok is None:
            raise ContractError("unexpected end of WL source")
        if kind is not None and tok[0] != kind:
            raise ContractError(f"expected {kind}, got {tok}")
        if value is not None and tok[1] != value:
            raise ContractError(f"expected {value!r}, got {tok}")
        self.i += 1
        return tok

    def _string(self) -> str:
        raw = self._take("string")[1]
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid WL string literal: {raw}") from exc

    def _value(self) -> Any:
        tok = self._peek()
        if tok is None:
            raise ContractError("missing WL value")
        if tok == ("punct", "<|"):
            return self._assoc()
        if tok == ("punct", "{"):
            return self._list()
        if tok[0] == "string":
            return self._string()
        raise ContractError(f"unsupported WL value token: {tok}")

    def _assoc(self) -> dict[str, Any]:
        self._take("punct", "<|")
        out: dict[str, Any] = {}
        if self._peek() == ("punct", "|>"):
            self._take("punct", "|>")
            return out
        while True:
            key = self._string()
            if key in out:
                raise ContractError(f"duplicate WL association key: {key}")
            self._take("punct", "->")
            out[key] = self._value()
            if self._peek() == ("punct", ","):
                self._take("punct", ",")
                continue
            self._take("punct", "|>")
            return out

    def _list(self) -> list[Any]:
        self._take("punct", "{")
        out: list[Any] = []
        if self._peek() == ("punct", "}"):
            self._take("punct", "}")
            return out
        while True:
            out.append(self._value())
            if self._peek() == ("punct", ","):
                self._take("punct", ",")
                continue
            self._take("punct", "}")
            return out

    def parse(self) -> dict[str, Any]:
        self._take("ident", "PROJECT_CONTRACT")
        self._take("punct", "=")
        data = self._assoc()
        self._take("punct", ";")
        if self._peek() is not None:
            raise ContractError(f"unexpected trailing token: {self._peek()}")
        return data


def parse_wl(text: str) -> dict[str, Any]:
    return _WLParser(text).parse()


def _git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def load_pinned_legacy(path: Path | None = None) -> dict[str, Any]:
    path = LEGACY if path is None else path
    raw = path.read_bytes()
    actual = _git_blob_sha(raw)
    if actual != ACCEPTED_V10_LEGACY_GIT_BLOB:
        raise ContractError(
            "accepted v10 WL migration fixture drift: "
            f"expected Git blob {ACCEPTED_V10_LEGACY_GIT_BLOB}, got {actual}"
        )
    return parse_wl(raw.decode("utf-8"))


def _render(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, list):
        return "{" + ",".join(_render(item) for item in value) + "}"
    if isinstance(value, dict):
        return "<|" + ",".join(
            f"{json.dumps(key, ensure_ascii=False)}->{_render(item)}"
            for key, item in value.items()
        ) + "|>"
    raise ContractError(
        f"unsupported contract value type: {type(value).__name__}"
    )


def render_projection(data: dict[str, Any]) -> str:
    return "PROJECT_CONTRACT=" + _render(data) + ";"


def validate_contract(data: dict[str, Any]) -> None:
    missing = sorted(_REQUIRED_TOP - set(data))
    extra = sorted(set(data) - _REQUIRED_TOP)
    if missing:
        raise ContractError(f"missing required top-level keys: {missing}")
    if extra:
        raise ContractError(f"unexpected top-level keys: {extra}")

    if data["Scope"] != "All project chats":
        raise ContractError("Scope drift")

    revision = data["Revision"]
    if not isinstance(revision, str):
        raise ContractError("Revision must be a string")
    match = re.search(r"v(\d+)$", revision)
    if not match:
        raise ContractError(f"Revision must end in vN: {revision!r}")

    probe = data["Probe"]
    if not isinstance(probe, dict) or set(probe) != {"Input", "Reply"}:
        raise ContractError("Probe must contain exactly Input and Reply")
    if probe["Input"] != "PROJECT_CONTRACT_PROBE":
        raise ContractError("Probe input drift")
    if probe["Reply"] != f"PC_OK_V{match.group(1)}":
        raise ContractError("Probe reply does not match revision")

    if data["Epistemics"] != ["FACT", "INFERENCE", "HYPOTHESIS", "UNKNOWN"]:
        raise ContractError("Epistemics drift")

    capabilities = data["Capabilities"]
    if not isinstance(capabilities, dict):
        raise ContractError("Capabilities must be an object")
    if capabilities.get("States") != [
        "CONFIGURED",
        "EXPOSED",
        "AVAILABLE",
        "INVOKED",
        "COMPLETED",
        "VERIFIED",
    ]:
        raise ContractError("Capabilities.States drift")

    change = data["ChangeControl"]
    required_change = {
        "ProjectOwnedRepositories",
        "IssueFirst",
        "IssueContents",
        "ProjectOwnedPermission",
        "RoutinePromotion",
        "ExternalRepositories",
        "Exceptions",
        "Authority",
    }
    if not isinstance(change, dict) or set(change) != required_change:
        raise ContractError("ChangeControl key drift")

    persistence = data["Persistence"]
    if (
        not isinstance(persistence, dict)
        or set(persistence) != {"Rule", "Readback", "Separation"}
    ):
        raise ContractError("Persistence key drift")


def build_validated_projection(data: dict[str, Any]) -> str:
    validate_contract(data)

    legacy = load_pinned_legacy()
    if data["Revision"] == ACCEPTED_V10_REVISION and legacy != data:
        raise ContractError(
            "structured source is not semantically identical to accepted v10 WL baseline"
        )

    rendered = render_projection(data)
    roundtrip = parse_wl(rendered)
    if roundtrip != data:
        raise ContractError(
            "generated projection does not round-trip to canonical structure"
        )

    if len(rendered) > MAX_PROJECT_SETTINGS_CHARS:
        raise ContractError(
            f"generated Project Settings projection is {len(rendered)} chars; "
            f"limit is {MAX_PROJECT_SETTINGS_CHARS}"
        )

    return rendered


def validate_all() -> dict[str, Any]:
    source = load_source()
    rendered = build_validated_projection(source)

    committed = PROJECTION.read_text(encoding="utf-8")
    if committed != rendered:
        raise ContractError(
            "project-settings.txt is stale; run tools/project_contract.py render"
        )

    return {
        "revision": source["Revision"],
        "probe": source["Probe"]["Reply"],
        "projection_chars": len(rendered),
    }


def migrate_from_legacy() -> None:
    data = load_pinned_legacy()
    SOURCE.write_text(
        yaml.dump(data, Dumper=_IndentedSafeDumper, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def render_file(
    source_path: Path | None = None,
    projection_path: Path | None = None,
) -> None:
    data = load_source(source_path)
    rendered = build_validated_projection(data)
    target = PROJECTION if projection_path is None else projection_path
    target.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and project the ChatGPT Project Contract."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "migrate-v10",
        help="rebuild structured source from the accepted v10 WL fixture",
    )
    sub.add_parser("render", help="render compact Project Settings projection")
    sub.add_parser(
        "validate",
        help="validate source, legacy equivalence, roundtrip and projection budget",
    )
    args = parser.parse_args()

    if args.command == "migrate-v10":
        migrate_from_legacy()
    elif args.command == "render":
        render_file()
    elif args.command == "validate":
        receipt = validate_all()
        print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
