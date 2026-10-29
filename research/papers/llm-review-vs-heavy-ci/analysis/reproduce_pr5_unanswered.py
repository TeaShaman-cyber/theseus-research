#!/usr/bin/env python3
"""Read-only, exact-Git-source PR #5 -> main continuity probes.

Every source version runs in a clean subprocess with temporary files and fake
GitHub transport. There are NO real GitHub requests or repository writes.
A pass demonstrates the stated source-level behavior, not a deployed incident.
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
from unittest import mock
from urllib.parse import quote_plus

from reproduce_pr5_remaining import ROOT, FakeTransport, snapshot

OLD = "40b572554b8711dc6fb06de6cdc7e02e99f6dfdb"
NEW = "362ef9caebc775f09e75bccc408823849a493984"
COMMENTS = {
    "private_discovery": 3941398477,
    "incomplete_search": 3941398481,
    "publication_failure": 3941398485,
    "projection_rollback": 3941398487,
}

# First verified commits where each synthetic behavior is corrected.
FIRST_FIX = {
    "private_discovery": "1fc4416da7754208f7e913f2ef584ddd269eef29",
    "incomplete_search": "1fc4416da7754208f7e913f2ef584ddd269eef29",
    "publication_failure": "12d158d46fa4e2e22b1047563a4662a11ed4cf90",
    "projection_rollback": "64a01a45cccfe157c0a3ea3cdb49d0b3c1cf53d9",
}


def query_paths():
    old = "user:TeaShaman-cyber theseus in:name,description"
    return {
        ("GET", "/search/repositories?q=" + quote_plus(x) + "&per_page=100"):
        {"items": [], "incomplete_results": False}
        for x in [old, old + " is:public"]
    }


def private_discovery(doctor):
    paths = query_paths()
    sample = {
        "full_name": "TeaShaman-cyber/theseus-private-synthetic",
        "name": "theseus-private-synthetic",
        "description": "synthetic-private-record",
        "private": True,
    }
    for p in paths:
        paths[p] = {"items": [sample], "incomplete_results": False}
    fake = FakeTransport(paths)
    found = doctor.discover_candidates("TeaShaman-cyber", set(), fake)
    return {
        "private_candidate_included": any(
            x["full_name"] == sample["full_name"] for x in found),
        "count": len(found),
        "calls": [p for method, p in fake.calls],
    }


def incomplete_search(doctor):
    paths = query_paths()
    for p in paths:
        paths[p] = {"items": [], "incomplete_results": True}
    fake = FakeTransport(paths)
    try:
        candidates = doctor.discover_candidates("TeaShaman-cyber", set(), fake)
        return {"exception": None, "candidate_count": len(candidates),
                "fail_closed": False}
    except doctor.GitHubUnavailable as e:
        return {"exception": type(e).__name__, "error": str(e),
                "fail_closed": True}


def publication_failure(cli, doctor, root):
    report_path = root / "doctor.json"
    cli._load_valid_registry = lambda: ({"lines": []}, [])
    cli._projection_mismatches = lambda document: []
    cli.UrllibGitHubTransport = lambda: object()
    cli.run_doctor = lambda document, owner, transport: {
        "status": "DECLARED_DRIFT", "declared": [],
        "candidates": [], "unreachable": []}
    def fail(*args):
        raise doctor.GitHubUnavailable("synthetic publication timeout")
    cli.ensure_drift_issue = fail
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            code = cli.cmd_doctor(argparse.Namespace(
                owner="TeaShaman-cyber", json_output=str(report_path),
                drift_issue="write"))
            error = None
        except Exception as e:
            code = None
            error = type(e).__name__
    payload = json.loads(report_path.read_text()) if report_path.is_file() else None
    return {
        "exception": error, "exit_code": code,
        "output_exists": report_path.is_file(),
        "main_status": payload.get("status") if payload else None,
        "publication_status": (payload.get("drift_issue", {})
                               .get("status") if payload else None),
    }


def projection_rollback(cli, root):
    marker = "<!-- BEGIN THESEUS_RESEARCH_LINES -->\nold\n<!-- END THESEUS_RESEARCH_LINES -->\n"
    en, ru = root / "README.md", root / "README.ru.md"
    for path, language in ((en, "EN"), (ru, "RU")):
        path.write_text(language + " before\n" + marker + language + " after\n")
    originals = {en: en.read_bytes(), ru: ru.read_bytes()}
    cli.README_EN, cli.README_RU = en, ru
    original_write = Path.write_text
    injected = {"failed": False}
    def reject_second(path, data, *args, **kwargs):
        if path == ru and not injected["failed"]:
            injected["failed"] = True
            raise OSError("synthetic second README write failure")
        return original_write(path, data, *args, **kwargs)
    with mock.patch.object(Path, "write_text", new=reject_second):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = cli.cmd_render(argparse.Namespace(check=False, write=True))
    response = json.loads(out.getvalue())
    return {
        "exit_code": code, "status": response.get("status"),
        "injected_failure": injected["failed"],
        "english_changed": en.read_bytes() != originals[en],
        "russian_changed": ru.read_bytes() != originals[ru],
    }


def one_case(case: str, sha: str):
    with tempfile.TemporaryDirectory(prefix="theseus-unanswered-") as temp:
        root = Path(temp)
        snapshot(sha, root)
        sys.path.insert(0, str(root))
        from tools import check_registry as cli
        from tools import registry_doctor as doctor
        return {
            "private_discovery": lambda: private_discovery(doctor),
            "incomplete_search": lambda: incomplete_search(doctor),
            "publication_failure": lambda: publication_failure(cli, doctor, root),
            "projection_rollback": lambda: projection_rollback(cli, root),
        }[case]()


def run_all():
    rows = []
    for key, cid in COMMENTS.items():
        results = {}
        for label, sha in (("before", OLD), ("first_fix", FIRST_FIX[key]), ("after", NEW)):
            proc = subprocess.run(
                [sys.executable, __file__, "--case", key, "--sha", sha],
                text=True, capture_output=True, check=True)
            results[label] = json.loads(proc.stdout)
        before, after = results["before"], results["after"]
        # The observable fix works at its pinned repair commit;
        # current main preserves this exact tested behavior.
        assert results["first_fix"] == after, (key, results)
        if key == "private_discovery":
            assert before["private_candidate_included"]
            assert not after["private_candidate_included"]
            assert before["count"] == 1 and after["count"] == 0
        elif key == "incomplete_search":
            assert before["exception"] is None
            assert before["candidate_count"] == 0
            assert after["fail_closed"]
            assert after["exception"] == "GitHubUnavailable"
        elif key == "publication_failure":
            assert before["exception"] == "GitHubUnavailable"
            assert before["exit_code"] is None
            assert not before["output_exists"]
            assert after["exception"] is None
            assert after["exit_code"] == 2
            assert after["output_exists"]
            assert after["main_status"] == "DECLARED_DRIFT"
            assert after["publication_status"] == "UNREACHABLE"
        elif key == "projection_rollback":
            assert before["injected_failure"] and after["injected_failure"]
            assert before["status"] == after["status"] == "INVALID"
            assert before["exit_code"] == after["exit_code"] == 4
            assert before["english_changed"]
            assert not before["russian_changed"]
            assert not after["english_changed"]
            assert not after["russian_changed"]
        rows.append({
            "case": key, "comment_id": cid,
            "comment_url": f"https://github.com/TeaShaman-cyber/theseus-research/pull/5#discussion_r{cid}",
            "historical_sha": OLD, "first_fix_sha": FIRST_FIX[key],
            "canonical_merge_pr": 46,
            "canonical_merge_sha": "94b012d04024131efd572ea4a5b7a96d56d2c255",
            "current_main_sha": NEW,
            "before": before, "first_fix": results["first_fix"], "after": after,
            "assertion_status": "PASS",
            "source_scope": "isolated historical Git source, synthetic inputs; no real GitHub writes"
        })
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=COMMENTS)
    parser.add_argument("--sha", default=OLD)
    args = parser.parse_args()
    if args.case:
        print(json.dumps(one_case(args.case, args.sha), sort_keys=True))
    else:
        print(json.dumps(run_all(), indent=2, sort_keys=True))
