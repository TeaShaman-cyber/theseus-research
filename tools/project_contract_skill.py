#!/usr/bin/env python3
"""Build a private skills-only projection without changing canonical policy."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import project_contract as pc

NAME = "theseus-project-contract"


def build_package(source_path: Path, version: str) -> bytes:
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version):
        raise ValueError("expected numeric semantic version")
    source = source_path.read_bytes()
    contract = pc.load_source(source_path)
    pc.build_validated_projection(contract)
    if not source.endswith(b"\n") or b"\n```" in source:
        raise pc.ContractError("unsupported source fence boundary")
    digest = hashlib.sha256(source).hexdigest()
    revision = contract["Revision"]
    header = f"""---
name: {NAME}
description: Use when explicitly selecting the Theseus Project Contract or working on Theseus code, research, projects, repositories, or governed operations.
---

# Theseus Project Contract

Generated, lossless candidate projection of the canonical Git YAML.
Revision: {revision}
Source SHA-256: {digest}
Package version: {version}

When invoked, read and apply the complete contract below within the user's
project authority. It governs project workflows, not higher-priority host
rules. No new permission or runtime capability is granted by this skill.
Use the bundled source for routine work; fetch canonical Git only when
currentness matters, a conflict or drift is observed, or an update is requested.
Do not silently replace the installed Project Settings or claim auto-invocation.

For PROJECT_CONTRACT_SKILL_PROBE, independently read the installed skill in
the current host and report the revision, source SHA-256 and package version
from that read. If the installed skill cannot be read, report
REPROBE_REQUIRED. The existing PROJECT_CONTRACT_PROBE remains unchanged;
its reply alone does not distinguish this skill from Project Settings.

## Operational interpretation (explanatory, not additional policy)

The following examples explain the canonical rules below. They do not replace,
weaken or extend them. No new authority is granted. Project Settings and this
skill, when both carry the same revision, express one policy, not cumulative restrictions.
Apply the policy once; do not perform the same bootstrap or verification twice
merely because it appears in two projections. Preserve currentness and the
selected runtime's required checks. A changed or conflicting revision still
requires resolution under the canonical contract.

### Optimize completion cost, not activity count

Attention ergonomics protects the user's attention, not the agent's tool-call
count. The thinnest sufficient route is the least unnecessary work that preserves
intent, evidence, authority and verification. It is not a tool-call budget.
Use additional relevant tools when the evidence, research depth, correctness or
verification requires them. Avoid redundant retrieval, not necessary retrieval.
Do not turn a preference for concise reporting into a preference for shallow work.

### Execution unit and stopping condition

A small reversible change is an engineering unit, not a conversation turn limit.
An authorized task may contain several such units. Continue through the relevant
read, plan, action, test, correction, review, readback and receipt steps until a
meaningful checkpoint: the requested result is verified, a real blocker prevents
further justified progress, an explicit user boundary is reached, or a material
new decision or permission is needed. If a result cannot be finished in the current
turn, distinguish completed work from pending work and preserve recoverable state.
Do not stop simply because one tool succeeded or one intermediate milestone was
reached. Do not open unrelated work to keep the turn busy. Respect explicit
current user requests to stop, narrow scope, or limit the work.

Prefer one concrete next step *in the report*, not one operation per turn.
When the next step is already authorized and can be completed now, execute it
rather than requiring the user to say continue again. Routine promotion is still
conditional on the exact ChangeControl gates; no new permission is inferred.

### Completion rather than checkpoint handoffs

A successful tool call, opened PR or launching CI is not completing the task
unless that was the user's actual goal. For an already authorized next step,
continue through bounded status checks, result inspection, necessary repair,
review, permitted merge and readback while the current turn can still make
useful progress. CI running is an intermediate state, not by itself a blocker.
Use progress messages without turning them into requests for another user turn.
If a real wait prevents further useful work, or an actual runtime or turn limit
is reached, preserve the exact pending state and explain the remaining blocker;
do not invent background execution or promise later delivery.

A provisional resource budget or pilot size is an engineering choice, not a
user-imposed limit. Justify it with measured risk/cost, revise it when evidence
supports expansion, and continue toward the goal-level result rather than
requiring approval for every small experiment. Respect actual permission,
resource and scope boundaries. Small reversible changes can be successive
steps in one substantial iteration. This note adds no authority or policy.

### Evidence and verification

Smallest sufficient evidence means enough evidence to support the actual claim.
It does not mean the shortest source excerpt or the first plausible answer.
Inspect the relevant full source, competing explanation or independent readback
when omitting it could change the result. Scale verification to consequence and
uncertainty; use existing deterministic QA before adding machinery. A failed or
partial check is not success. Retry or take a permitted fallback only under the
canonical failure and routing rules. Reuse observed, still-current evidence within
its authority domain instead of mechanically repeating preflight checks.

### Examples of applying the rules

- Example: authorized code change. Read the current repository rules and state,
  make the narrow change, run focused and required QA, correct evidenced defects,
  and complete permitted PR coordination/promotion and readback in the same turn
  when feasible. Do not stop at a diff just to ask whether to run tests. If gates
  are pending, state that explicitly; do not treat a draft PR as accepted work.
- Example: research. Read enough primary evidence to answer the research question,
  compare meaningful alternatives, identify counterexamples and separate fact from
  hypothesis. Do not stop at the first search result to save tool calls, and do
  not conduct an unrelated literature survey after the question is answered.
- Example: failure. Check the smallest authoritative postcondition before retrying
  an ambiguous mutation; trace the evidenced cause, try the permitted repair or
  finite fallback, and verify recovery. If blocked, report the unresolved layer
  rather than cycling providers or asking the user to repeat known authorization.
- Example: reporting. Explain the useful result, essential evidence, remaining
  uncertainty and next action. Keep necessary verification even when the summary
  is short. A new permission, protected decision or genuine blocker warrants a
  handoff; ordinary authorized mechanics do not.

## Canonical policy (apply in full)

```yaml
"""
    manifest = {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": NAME,
        "version": version,
        "description": "Lossless skill projection of the Theseus Project Contract.",
        "author": {"name": "Theseus"},
        "extensions": {"com.openai": {"interface": {
            "displayName": "Theseus Project Contract",
            "shortDescription": "Theseus governance contract",
            "longDescription": "Apply the pinned canonical Theseus governance contract through a native skill. No MCP server.",
            "developerName": "Theseus",
            "category": "Productivity",
            "capabilities": ["Interactive"],
            "defaultPrompt": "Apply the Theseus Project Contract.",
        }}},
    }
    files = {
        "plugin.json": (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode(),
        f"skills/{NAME}/SKILL.md": header.encode() + source + b"```\n",
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED)
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = build_package(pc.SOURCE, args.version)
    args.output.write_bytes(package)
    print(hashlib.sha256(package).hexdigest())


if __name__ == "__main__":
    main()
