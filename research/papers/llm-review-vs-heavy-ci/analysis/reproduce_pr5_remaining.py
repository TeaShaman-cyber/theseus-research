#!/usr/bin/env python3
"""Version-pinned, side-effect-isolated reproductions of five PR #5 review claims.

Runs original project-owned Python modules from Git blobs in temporary trees,
using local synthetic files and FakeTransport only. No external GitHub calls
or persistent registry mutations; 'POST' means a fake recorded call.
Requires full local Git history and stdlib Python.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "research/papers/llm-review-vs-heavy-ci/data/review-comments.json"
HEAD = "40b572554b8711dc6fb06de6cdc7e02e99f6dfdb"
CASES = {
    "projection_atomicity": 3939739203,
    "issue_pagination": 3939739209,
    "issue_readback": 3939807479,
    "json_parent": 3939993047,
    "label_pagination": 3939993050,
}


def git_show(sha: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"{sha}:{path}"]
    )


def snapshot(sha: str, root: Path) -> None:
    for path in (
        "tools/__init__.py",
        "tools/check_registry.py",
        "tools/registry_contract.py",
        "tools/registry_doctor.py",
        "tools/registry_projection.py",
        "registry/research-lines.json",
    ):
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            destination.write_bytes(git_show(sha, path))
        except subprocess.CalledProcessError:
            if path != "tools/__init__.py":
                raise


class FakeTransport:
    def __init__(self, responses: dict) -> None:
        self.responses = responses
        self.calls = []

    def request(self, method: str, path: str, body=None):
        import copy
        self.calls.append((method, path))
        key = (method, path)
        if key not in self.responses:
            raise AssertionError(f"unexpected fake request: {method} {path}")
        value = self.responses[key]
        if isinstance(value, BaseException):
            raise value
        return copy.deepcopy(value)


def single_case(case: str, sha: str) -> dict:
    # Separate child Python process per version: prevents module reuse between
    # original and fixed sources and provides a clean import boundary.
    with tempfile.TemporaryDirectory(prefix="theseus-pr5-") as temp:
        root = Path(temp)
        snapshot(sha, root)
        sys.path.insert(0, str(root))
        from tools import check_registry as cli
        from tools import registry_doctor as doctor
        if case == "projection_atomicity":
            return check_projections(cli, root)
        if case == "issue_pagination":
            return check_issue_pagination(doctor)
        if case == "issue_readback":
            return check_issue_readback(doctor)
        if case == "json_parent":
            return check_json_parent(cli, root)
        if case == "label_pagination":
            return check_label_pagination(doctor)
        raise ValueError(case)


def call_cli(fun, *args):
    with contextlib.redirect_stdout(io.StringIO()) as out:
        try:
            result = fun(*args)
            return {"exit_code": result, "output": out.getvalue(), "exception": None}
        except Exception as exc:
            return {"exit_code": None, "output": out.getvalue(),
                    "exception": type(exc).__name__, "error": str(exc)}


def check_projections(cli, root: Path) -> dict:
    en = root / "sample-README.md"
    ru = root / "sample-README.ru.md"
    en.write_text("before\n<!-- BEGIN THESEUS_RESEARCH_LINES -->\nold\n<!-- END THESEUS_RESEARCH_LINES -->\nafter\n")
    ru.write_text("broken projection without markers\n")
    old_en, old_ru = en.read_bytes(), ru.read_bytes()
    cli.README_EN, cli.README_RU = en, ru
    report = call_cli(cli.cmd_render, argparse.Namespace(check=False, write=True))
    return {"exit_code": report["exit_code"], "result_status":
            (json.loads(report["output"]).get("status") if report["output"] else None),
            "english_changed": en.read_bytes() != old_en,
            "russian_changed": ru.read_bytes() != old_ru,
            "exception": report["exception"]}


def report_drift() -> dict:
    return {"status": "DECLARED_DRIFT", "owner": "TeaShaman-cyber",
            "declared": [], "candidates": [], "unreachable": []}


def paths():
    base = "/repos/TeaShaman-cyber/theseus-research"
    return base, f"{base}/issues?state=open&per_page=100"


def check_issue_pagination(doctor) -> dict:
    base, list_path = paths()
    second = list_path + "&page=2"
    existing = {"number": 212, "title": doctor.DRIFT_ISSUE_TITLE,
                "html_url": "https://example.invalid/issues/212"}
    body = doctor.render_drift_issue_body(report_drift())
    first_page = [
        {"number": i, "title": f"unrelated issue {i}",
         "html_url": f"https://example.invalid/issues/{i}"}
        for i in range(1, 101)
    ]
    fake = FakeTransport({
        ("GET", list_path): first_page,
        ("GET", second): [existing],
        ("POST", base + "/issues"): {
            "number": 999, "html_url": "https://example.invalid/issues/999"},
        ("GET", base + "/issues/999"): {
            "number": 999, "title": doctor.DRIFT_ISSUE_TITLE, "body": body,
            "html_url": "https://example.invalid/issues/999"},
        ("POST", base + "/issues/212/comments"): {
            "id": 88, "html_url": "https://example.invalid/comments/88"},
        ("GET", base + "/issues/comments/88"): {
            "id": 88, "body": body, "html_url": "https://example.invalid/comments/88"},
    })
    result = doctor.ensure_drift_issue(
        "TeaShaman-cyber/theseus-research", report_drift(), fake)
    return {"action": result.get("action"),
            "issue_number": result.get("issue_number"),
            "page_2_fetched": ("GET", second) in fake.calls,
            "duplicate_create_attempted": ("POST", base + "/issues") in fake.calls,
            "issue_comment_attempted":
                ("POST", base + "/issues/212/comments") in fake.calls}


def check_issue_readback(doctor) -> dict:
    base, list_path = paths()
    body = doctor.render_drift_issue_body(report_drift())
    cases = {
        "create": FakeTransport({
            ("GET", list_path): [],
            ("POST", base + "/issues"): {
                "number": 41, "html_url": "https://example.invalid/issues/41"},
            ("GET", base + "/issues/41"): {
                "number": 41, "title": "INCORRECT persisted title",
                "body": body, "html_url": "https://example.invalid/issues/41"},
        }),
        "comment": FakeTransport({
            ("GET", list_path): [{
                "number": 12, "title": doctor.DRIFT_ISSUE_TITLE,
                "html_url": "https://example.invalid/issues/12"}],
            ("POST", base + "/issues/12/comments"): {
                "id": 55, "html_url": "https://example.invalid/comments/55"},
            ("GET", base + "/issues/comments/55"): {
                "id": 55, "body": "INCORRECT persisted comment",
                "html_url": "https://example.invalid/comments/55"},
        }),
    }
    outputs = {}
    for label, fake in cases.items():
        try:
            result = doctor.ensure_drift_issue(
                "TeaShaman-cyber/theseus-research", report_drift(), fake)
            outputs[label] = {"reported_action": result["action"],
                              "rejected_mismatch": False}
        except doctor.GitHubUnavailable as error:
            outputs[label] = {
                "reported_action": None, "rejected_mismatch": True,
                "error_class": type(error).__name__,
                "message_has_readback": "readback" in str(error)}
        outputs[label]["readback_requested"] = any(
            method == "GET" and
            (path.endswith("/41") or path.endswith("/55"))
            for method, path in fake.calls)
    return outputs


def check_json_parent(cli, root: Path) -> dict:
    invalid = root / "invalid.json"
    invalid.write_text("{}")
    output = root / "new-directory" / "nested" / "doctor.json"
    cli.REGISTRY = invalid
    report = call_cli(cli.cmd_doctor,
                      argparse.Namespace(owner="TeaShaman-cyber",
                                         json_output=str(output),
                                         drift_issue="off"))
    return {"exit_code": report["exit_code"],
            "exception": report["exception"],
            "report_exists": output.is_file(),
            "report_status": json.loads(output.read_text()).get("status")
            if output.is_file() else None}


def check_label_pagination(doctor) -> dict:
    base, _ = paths()
    line = {"id": "theseus-research",
            "repository": "TeaShaman-cyber/theseus-research",
            "topics": [], "release_policy": "none"}
    path1 = base + "/labels?per_page=100"
    path2 = path1 + "&page=2"
    fake = FakeTransport({
        ("GET", base): {
            "full_name": line["repository"], "private": False,
            "description": "Fake test repository"},
        ("GET", base + "/topics"): {"names": []},
        ("GET", path1): [
            {"name": f"unrelated-label-{i}"} for i in range(100)],
        ("GET", path2): [
            {"name": name} for name in doctor.MANAGED_LABELS],
        ("GET", base + "/releases?per_page=100"): [],
    })
    result = doctor.observe_declared_line(line, fake)
    return {"status": result["status"],
            "page_2_fetched": ("GET", path2) in fake.calls,
            "missing_managed_labels": [
                item for item in result["drift"]
                if item.startswith("missing managed label:")]}


def run_all() -> list[dict]:
    review = json.loads(DATA.read_text())
    rows = {row["comment_id"]: row for row in review["comments"]}
    output = []
    for case, cid in CASES.items():
        original = rows[cid]["original_commit"]
        result = {}
        for stage, sha in (("before", original), ("after", HEAD)):
            run = subprocess.run(
                [sys.executable, __file__, "--case", case, "--sha", sha],
                capture_output=True, text=True, check=True)
            result[stage] = json.loads(run.stdout)
        old, new = result["before"], result["after"]
        if case == "projection_atomicity":
            assert old["exit_code"] == new["exit_code"] == 4
            assert old["result_status"] == new["result_status"] == "INVALID"
            assert old["english_changed"] and not old["russian_changed"]
            assert not new["english_changed"] and not new["russian_changed"]
        elif case == "issue_pagination":
            assert old["action"] == "created" and old["duplicate_create_attempted"]
            assert not old["page_2_fetched"] and old["issue_number"] == 999
            assert new["action"] == "commented" and new["issue_number"] == 212
            assert new["page_2_fetched"] and not new["duplicate_create_attempted"]
        elif case == "issue_readback":
            for operation in ("create", "comment"):
                assert old[operation]["reported_action"] in {"created", "commented"}
                assert not old[operation]["readback_requested"]
                assert not old[operation]["rejected_mismatch"]
                assert new[operation]["readback_requested"]
                assert new[operation]["rejected_mismatch"]
                assert new[operation]["message_has_readback"]
                assert new[operation]["reported_action"] is None
        elif case == "json_parent":
            assert old["exception"] == "FileNotFoundError"
            assert not old["report_exists"]
            assert new["exception"] is None and new["exit_code"] == 4
            assert new["report_exists"] and new["report_status"] == "INVALID"
        elif case == "label_pagination":
            assert old["status"] == "DECLARED_DRIFT"
            assert len(old["missing_managed_labels"]) == 5
            assert not old["page_2_fetched"]
            assert new["status"] == "PASS"
            assert new["page_2_fetched"] and not new["missing_managed_labels"]
        else:
            raise AssertionError(f"unknown case: {case}")
        result.update({"case": case, "review_comment_id": cid,
                       "review_url": rows[cid]["url"],
                       "before_sha": original, "after_sha": HEAD,
                       "type": "red-before-green-after",
                       "assertion_status": "PASS",
                       "scope": "historical source + temporary local inputs, no real GitHub writes"})
        output.append(result)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=CASES)
    parser.add_argument("--sha")
    args = parser.parse_args()
    if args.case:
        print(json.dumps(single_case(args.case, args.sha), sort_keys=True))
    else:
        print(json.dumps(run_all(), indent=2, sort_keys=True))
