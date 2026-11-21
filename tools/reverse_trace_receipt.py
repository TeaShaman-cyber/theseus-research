from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.reverse_trace_contract import (
    build_proof_matrix,
    load_contract,
    validate_contract,
)

RECEIPT_SCHEMA_VERSION = "theseus.reverse-trace-receipt.v1"
LOCAL_EVIDENCE_KINDS = frozenset({"code", "test", "doc", "workflow"})


def _git(repo: Path, *args: str, text: bool = False):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=text)


def resolve_commit(repo: Path, value: str) -> str:
    return _git(repo, "rev-parse", "--verify", f"{value}^{{commit}}", text=True).strip()


def _changed_paths(repo: Path, base_sha: str, head_sha: str) -> list[str]:
    raw = _git(repo, "diff", "--name-only", "-z", base_sha, head_sha, "--")
    return sorted({part.decode() for part in raw.split(b"\0") if part})


def _patches(repo: Path, base_sha: str, head_sha: str, paths: list[str]) -> dict[str, str]:
    return {
        path: _git(
            repo,
            "diff",
            "--no-ext-diff",
            "--unified=8",
            base_sha,
            head_sha,
            "--",
            path,
            text=True,
        )
        for path in paths
    }


def _snapshot_refs(document: Mapping[str, object]) -> set[str]:
    refs: set[str] = set()
    invariants = document.get("invariants", [])
    if not isinstance(invariants, list):
        return refs
    for raw in invariants:
        if not isinstance(raw, Mapping):
            continue
        evidence = raw.get("evidence", [])
        if isinstance(evidence, list):
            for item in evidence:
                if not isinstance(item, Mapping):
                    continue
                if item.get("kind") in LOCAL_EVIDENCE_KINDS:
                    ref = item.get("ref")
                    if isinstance(ref, str):
                        refs.add(ref)
        proof_checks = raw.get("proof_checks", [])
        if isinstance(proof_checks, list):
            for check in proof_checks:
                if not isinstance(check, Mapping):
                    continue
                ref = check.get("ref")
                if isinstance(ref, str):
                    refs.add(ref)
    return refs


def _snapshot_files(
    repo: Path,
    head_sha: str,
    refs: set[str],
) -> dict[str, str]:
    files: dict[str, str] = {}
    for ref in sorted(refs):
        cp = subprocess.run(
            ["git", "-C", str(repo), "show", f"{head_sha}:{ref}"],
            text=True,
            capture_output=True,
        )
        if cp.returncode == 0:
            files[ref] = cp.stdout
    return files


def build_receipt_payload(
    *,
    document: Mapping[str, object],
    patches: Mapping[str, str],
    files: Mapping[str, str],
    repository: str,
    base_sha: str,
    head_sha: str,
    contract_sha256: str,
) -> dict[str, object]:
    errors = validate_contract(document)
    if errors:
        raise ValueError("invalid reverse-trace contract: " + "; ".join(errors))

    matrix = build_proof_matrix(document, patches, files)
    review_states = Counter(str(item["review_state"]) for item in matrix)

    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "repository": repository,
        "base_sha": base_sha,
        "head_sha": head_sha,
        "contract_sha256": contract_sha256,
        "changed_path_count": len(patches),
        "changed_paths": sorted(patches),
        "matrix": matrix,
        "summary": {
            "affected_invariant_count": len(matrix),
            "review_states": {
                key: review_states[key]
                for key in sorted(review_states)
            },
        },
    }


def build_receipt(
    *,
    repo: Path,
    contract_path: Path,
    repository: str,
    base: str,
    head: str,
) -> dict[str, object]:
    document = load_contract(contract_path)
    errors = validate_contract(document)
    if errors:
        raise ValueError("invalid reverse-trace contract: " + "; ".join(errors))

    base_sha = resolve_commit(repo, base)
    head_sha = resolve_commit(repo, head)
    paths = _changed_paths(repo, base_sha, head_sha)
    patches = _patches(repo, base_sha, head_sha, paths)
    files = _snapshot_files(repo, head_sha, _snapshot_refs(document))
    contract_sha256 = hashlib.sha256(contract_path.read_bytes()).hexdigest()

    return build_receipt_payload(
        document=document,
        patches=patches,
        files=files,
        repository=repository,
        base_sha=base_sha,
        head_sha=head_sha,
        contract_sha256=contract_sha256,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    receipt = build_receipt(
        repo=args.repo,
        contract_path=args.contract,
        repository=args.repository,
        base=args.base,
        head=args.head,
    )
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
