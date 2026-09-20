from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from huggingface_hub import snapshot_download


def _section(data: dict, dotted: str) -> object:
    value: object = data
    for key in dotted.split("."):
        if not isinstance(value, dict) or key not in value:
            raise KeyError(dotted)
        value = value[key]
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--hash-section")
    args = parser.parse_args()

    path = Path(
        snapshot_download(
            repo_id=args.repo,
            revision=args.revision,
            local_dir=args.output,
        )
    )

    if bool(args.profile) != bool(args.hash_section):
        raise SystemExit("--profile and --hash-section must be supplied together")

    if args.profile:
        data = json.loads(args.profile.read_text())
        hashes = _section(data, args.hash_section)
        if not isinstance(hashes, dict):
            raise SystemExit(f"{args.hash_section} is not a hash mapping")
        for rel, expected in hashes.items():
            file_path = path / rel
            if not file_path.is_file():
                raise SystemExit(f"missing snapshot file: {rel}")
            got = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if got != expected:
                raise SystemExit(
                    f"snapshot sha256 mismatch {rel}: {got} != {expected}"
                )

    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
