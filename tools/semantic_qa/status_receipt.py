from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tool", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--error-file", type=Path)
    parser.add_argument("--reason", default="")
    parser.add_argument("--started-ms", type=int)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    error = ""
    if args.error_file and args.error_file.exists():
        error = args.error_file.read_text(errors="replace")[-4000:]

    receipt = {
        "schema_version": 1,
        "tool": args.tool,
        "status": args.status,
        "repository": args.repository,
        "task_id": args.task_id,
        "base_sha": args.base_sha,
        "candidate_sha": args.candidate_sha,
        "profile_sha256": hashlib.sha256(args.profile.read_bytes()).hexdigest(),
        "reason": args.reason,
        "error_tail": error,
        "elapsed_ms": (
            int(time.time() * 1000) - args.started_ms if args.started_ms else None
        ),
        "acceptance_authority": False,
    }
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
