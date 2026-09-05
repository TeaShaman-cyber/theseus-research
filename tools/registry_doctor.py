from __future__ import annotations

import json
import os
from typing import Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from tools.registry_contract import MANAGED_LABELS, public_lines


class GitHubUnavailable(RuntimeError):
    pass


class GitHubNotFound(GitHubUnavailable):
    pass


class GitHubTransport:
    def request(self, method: str, path: str, body: object | None = None) -> object:
        raise NotImplementedError


class UrllibGitHubTransport(GitHubTransport):
    def __init__(self, token: str | None = None, timeout: int = 15):
        self.token = token if token is not None else os.environ.get("GITHUB_TOKEN")
        self.timeout = timeout

    def request(self, method: str, path: str, body: object | None = None) -> object:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "theseus-registry-doctor/1",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            f"https://api.github.com{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            if exc.code == 404:
                raise GitHubNotFound(f"GitHub object not found: {path}") from exc
            raise GitHubUnavailable(f"GitHub HTTP {exc.code}: {method} {path}") from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise GitHubUnavailable(f"GitHub request failed: {method} {path}: {exc}") from exc

        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubUnavailable(f"GitHub returned non-JSON response: {method} {path}") from exc


def _repo_paths(repository: str) -> tuple[str, str]:
    owner, repo = repository.split("/", 1)
    return owner, f"/repos/{owner}/{repo}"


def observe_declared_line(line: Mapping[str, object], transport: GitHubTransport) -> dict[str, object]:
    line_id = str(line["id"])
    repository = line.get("repository")
    if not isinstance(repository, str):
        return {
            "id": line_id,
            "status": "PASS",
            "drift": [],
            "observed": {"visibility": line.get("visibility"), "repository": None},
        }

    _, base = _repo_paths(repository)
    try:
        metadata = transport.request("GET", base)
    except GitHubNotFound:
        return {
            "id": line_id,
            "repository": repository,
            "status": "DECLARED_DRIFT",
            "drift": ["repository missing"],
            "observed": {"repository": None},
        }

    if not isinstance(metadata, Mapping):
        raise GitHubUnavailable(f"unexpected repository metadata shape: {repository}")
    topics_payload = transport.request("GET", f"{base}/topics")
    labels_payload = transport.request("GET", f"{base}/labels?per_page=100")
    releases_payload = transport.request("GET", f"{base}/releases?per_page=100")

    if not isinstance(topics_payload, Mapping) or not isinstance(topics_payload.get("names"), list):
        raise GitHubUnavailable(f"unexpected topics payload: {repository}")
    if not isinstance(labels_payload, list):
        raise GitHubUnavailable(f"unexpected labels payload: {repository}")
    if not isinstance(releases_payload, list):
        raise GitHubUnavailable(f"unexpected releases payload: {repository}")

    expected_topics = set(str(topic) for topic in line.get("topics", []))
    observed_topics = set(str(topic) for topic in topics_payload["names"])
    missing_topics = sorted(expected_topics - observed_topics)
    unexpected_managed_topics = sorted(
        topic
        for topic in observed_topics - expected_topics
        if topic == "theseus" or topic.startswith("theseus-")
    )
    unmanaged_topics = sorted(
        topic
        for topic in observed_topics - expected_topics
        if topic not in unexpected_managed_topics
    )

    observed_labels = {
        str(item.get("name"))
        for item in labels_payload
        if isinstance(item, Mapping) and isinstance(item.get("name"), str)
    }
    missing_labels = [name for name in MANAGED_LABELS if name not in observed_labels]

    drift: list[str] = []
    if metadata.get("full_name") != repository:
        drift.append(f"repository identity mismatch: {metadata.get('full_name')}")
    if bool(metadata.get("private")):
        drift.append("repository unexpectedly private")
    drift.extend(f"missing topic: {topic}" for topic in missing_topics)
    drift.extend(f"unexpected managed topic: {topic}" for topic in unexpected_managed_topics)
    drift.extend(f"missing managed label: {label}" for label in missing_labels)

    release_policy = line.get("release_policy")
    release_count = len(releases_payload)
    if release_policy == "none" and release_count:
        drift.append(f"release policy none but {release_count} release(s) observed")

    return {
        "id": line_id,
        "repository": repository,
        "status": "DECLARED_DRIFT" if drift else "PASS",
        "drift": drift,
        "observed": {
            "full_name": metadata.get("full_name"),
            "private": bool(metadata.get("private")),
            "description": metadata.get("description"),
            "topics": sorted(observed_topics),
            "unmanaged_topics": unmanaged_topics,
            "labels": sorted(observed_labels),
            "release_count": release_count,
        },
    }


def discover_candidates(
    owner: str, declared: set[str], transport: GitHubTransport
) -> list[dict[str, object]]:
    query = quote_plus(f"user:{owner} theseus in:name,description")
    payload = transport.request(
        "GET", f"/search/repositories?q={query}&per_page=100"
    )
    if not isinstance(payload, Mapping) or not isinstance(payload.get("items"), list):
        raise GitHubUnavailable("unexpected repository search payload")

    candidates: list[dict[str, object]] = []
    for item in payload["items"]:
        if not isinstance(item, Mapping):
            continue
        full_name = item.get("full_name")
        if not isinstance(full_name, str) or full_name in declared:
            continue
        candidates.append(
            {
                "full_name": full_name,
                "name": item.get("name"),
                "description": item.get("description"),
                "private": bool(item.get("private")),
            }
        )
    return sorted(candidates, key=lambda item: str(item["full_name"]))


def run_doctor(
    document: Mapping[str, object], owner: str, transport: GitHubTransport
) -> dict[str, object]:
    declared_results: list[dict[str, object]] = []
    unreachable: list[dict[str, str]] = []

    public = public_lines(document)
    for line in public:
        try:
            declared_results.append(observe_declared_line(line, transport))
        except GitHubUnavailable as exc:
            line_id = str(line.get("id"))
            repository = str(line.get("repository"))
            unreachable.append({"id": line_id, "repository": repository, "error": str(exc)})
            declared_results.append(
                {
                    "id": line_id,
                    "repository": repository,
                    "status": "UNREACHABLE",
                    "drift": [],
                    "observed": {},
                }
            )

    declared_repositories = {
        str(line["repository"])
        for line in public
        if isinstance(line.get("repository"), str)
    }
    candidates: list[dict[str, object]] = []
    try:
        candidates = discover_candidates(owner, declared_repositories, transport)
    except GitHubUnavailable as exc:
        unreachable.append({"id": "candidate-search", "repository": owner, "error": str(exc)})

    if unreachable:
        status = "UNREACHABLE"
    elif any(item["status"] == "DECLARED_DRIFT" for item in declared_results):
        status = "DECLARED_DRIFT"
    elif candidates:
        status = "CANDIDATE_UNDECLARED"
    else:
        status = "PASS"

    return {
        "status": status,
        "owner": owner,
        "declared": declared_results,
        "candidates": candidates,
        "unreachable": unreachable,
    }

DRIFT_ISSUE_TITLE = "Registry drift: Theseus research-line metadata"
_DRIFT_DISCLAIMER = (
    "This issue is a drift report. It does not declare any repository part of Theseus."
)


def render_drift_issue_body(report: Mapping[str, object]) -> str:
    lines = [
        _DRIFT_DISCLAIMER,
        "",
        f"Doctor status: `{report.get('status')}`",
        "",
        "## Declared drift",
    ]
    declared = report.get("declared", [])
    drift_rows = []
    if isinstance(declared, list):
        for item in declared:
            if not isinstance(item, Mapping):
                continue
            drift = item.get("drift", [])
            if not isinstance(drift, list) or not drift:
                continue
            line_id = item.get("id", "unknown")
            repository = item.get("repository", "no repository")
            drift_rows.append(f"- `{line_id}` (`{repository}`): " + "; ".join(str(x) for x in drift))
    lines.extend(drift_rows or ["- none"])

    lines.extend(["", "## Advisory undeclared candidates"])
    candidates = report.get("candidates", [])
    candidate_rows = []
    if isinstance(candidates, list):
        for candidate in candidates:
            if isinstance(candidate, Mapping) and candidate.get("full_name"):
                candidate_rows.append(f"- `{candidate['full_name']}`")
    lines.extend(candidate_rows or ["- none"])

    lines.extend(
        [
            "",
            "Candidates are advisory only. Membership changes require an explicit registry edit and review.",
            "",
        ]
    )
    return "\n".join(lines)


def ensure_drift_issue(
    repository: str,
    report: Mapping[str, object],
    transport: GitHubTransport,
) -> dict[str, object]:
    status = report.get("status")
    if status in {"PASS", "UNREACHABLE"}:
        raise ValueError(f"drift issue write not allowed for {status}")
    if status not in {"DECLARED_DRIFT", "CANDIDATE_UNDECLARED"}:
        raise ValueError(f"drift issue write not allowed for {status}")

    owner, repo = repository.split("/", 1)
    base = f"/repos/{owner}/{repo}"
    issues = transport.request("GET", f"{base}/issues?state=open&per_page=100")
    if not isinstance(issues, list):
        raise GitHubUnavailable(f"unexpected issues payload: {repository}")

    body = render_drift_issue_body(report)
    existing = next(
        (
            item
            for item in issues
            if isinstance(item, Mapping)
            and "pull_request" not in item
            and item.get("title") == DRIFT_ISSUE_TITLE
            and isinstance(item.get("number"), int)
        ),
        None,
    )

    if existing is not None:
        number = int(existing["number"])
        response = transport.request(
            "POST", f"{base}/issues/{number}/comments", {"body": body}
        )
        return {
            "action": "commented",
            "issue_number": number,
            "issue_url": existing.get("html_url"),
            "comment_url": response.get("html_url") if isinstance(response, Mapping) else None,
        }

    response = transport.request(
        "POST",
        f"{base}/issues",
        {"title": DRIFT_ISSUE_TITLE, "body": body},
    )
    if not isinstance(response, Mapping) or not isinstance(response.get("number"), int):
        raise GitHubUnavailable(f"unexpected issue-create response: {repository}")
    return {
        "action": "created",
        "issue_number": int(response["number"]),
        "issue_url": response.get("html_url"),
    }
