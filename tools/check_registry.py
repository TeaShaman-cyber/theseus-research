#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.registry_contract import load_registry, validate_registry
from tools.registry_doctor import UrllibGitHubTransport, ensure_drift_issue, run_doctor
from tools.registry_projection import projection_matches, render_table, replace_projection

REGISTRY = ROOT / "registry" / "research-lines.json"
README_EN = ROOT / "README.md"
README_RU = ROOT / "README.ru.md"
DRIFT_REPOSITORY = "TeaShaman-cyber/theseus-research"


def _dump(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _load_valid_registry() -> tuple[dict[str, object] | None, list[str]]:
    try:
        document = load_registry(REGISTRY)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, [str(exc)]
    errors = validate_registry(document)
    return document, errors


def _projection_mismatches(document: dict[str, object]) -> list[str]:
    mismatches = []
    if not projection_matches(README_EN, render_table(document, "en")):
        mismatches.append("README.md")
    if not projection_matches(README_RU, render_table(document, "ru")):
        mismatches.append("README.ru.md")
    return mismatches


def cmd_validate(_: argparse.Namespace) -> int:
    _, errors = _load_valid_registry()
    status = "PASS" if not errors else "INVALID"
    sys.stdout.write(_dump({"status": status, "errors": errors}))
    return 0 if not errors else 4


def cmd_render(args: argparse.Namespace) -> int:
    document, errors = _load_valid_registry()
    if document is None or errors:
        sys.stdout.write(_dump({"status": "INVALID", "errors": errors}))
        return 4

    if args.check:
        mismatches = _projection_mismatches(document)
        status = "PASS" if not mismatches else "PROJECTION_MISMATCH"
        sys.stdout.write(_dump({"status": status, "mismatched_files": mismatches}))
        return 0 if not mismatches else 4

    rendered = ((README_EN, "en"), (README_RU, "ru"))
    written = []
    try:
        for path, language in rendered:
            source = path.read_text(encoding="utf-8")
            output = replace_projection(source, render_table(document, language))
            path.write_text(output, encoding="utf-8")
            written.append(path.name)
    except (OSError, ValueError) as exc:
        sys.stdout.write(_dump({"status": "INVALID", "errors": [str(exc)]}))
        return 4
    sys.stdout.write(_dump({"status": "PASS", "written_files": written}))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    document, errors = _load_valid_registry()
    if document is None or errors:
        payload = {"status": "INVALID", "errors": errors}
        Path(args.json_output).write_text(_dump(payload), encoding="utf-8")
        return 4

    mismatches = _projection_mismatches(document)
    if mismatches:
        payload = {"status": "PROJECTION_MISMATCH", "mismatched_files": mismatches}
        Path(args.json_output).write_text(_dump(payload), encoding="utf-8")
        return 4

    transport = UrllibGitHubTransport()
    report = run_doctor(document, args.owner, transport)
    if args.drift_issue == "write" and report["status"] in {
        "DECLARED_DRIFT",
        "CANDIDATE_UNDECLARED",
    }:
        report["drift_issue"] = ensure_drift_issue(DRIFT_REPOSITORY, report, transport)

    output = Path(args.json_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_dump(report), encoding="utf-8")

    return {
        "PASS": 0,
        "DECLARED_DRIFT": 2,
        "CANDIDATE_UNDECLARED": 2,
        "UNREACHABLE": 3,
    }.get(str(report.get("status")), 4)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and observe the Theseus research-line registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.set_defaults(func=cmd_validate)

    render = subparsers.add_parser("render")
    mode = render.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    render.set_defaults(func=cmd_render)

    doctor = subparsers.add_parser("doctor")
    doctor.add_argument("--owner", required=True)
    doctor.add_argument("--json-output", required=True)
    doctor.add_argument("--drift-issue", choices=("off", "write"), default="off")
    doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
