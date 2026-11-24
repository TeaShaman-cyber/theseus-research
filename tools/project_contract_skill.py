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
