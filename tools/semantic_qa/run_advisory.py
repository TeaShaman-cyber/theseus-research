from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    from .prepare_toolchain import prepare
except ImportError:
    from prepare_toolchain import prepare


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')


def _merge_toolchain(receipt_path: Path, toolchain: dict, orchestration_ms: float) -> dict:
    payload = json.loads(receipt_path.read_text())
    payload['toolchain'] = toolchain
    payload['orchestration_ms'] = orchestration_ms
    _write(receipt_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool', choices=['semdup', 'semble', 'needle3'], required=True)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--base-sha', required=True)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--input-manifest', type=Path, required=True)
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--failure-classes', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--download-dir', type=Path, required=True)
    parser.add_argument('--runtime-dir', type=Path, required=True)
    parser.add_argument('--env-dir', type=Path)
    args = parser.parse_args()

    started = time.perf_counter()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = args.output_dir / 'receipt.json'
    toolchain_path = args.output_dir / 'toolchain-receipt.json'
    manifest = json.loads(args.input_manifest.read_text())
    profiles = json.loads(args.profile.read_text())

    toolchain = prepare(
        tool=args.tool,
        profiles=profiles,
        repository=args.repository,
        input_status=manifest['status'],
        download_dir=args.download_dir,
        runtime_dir=args.runtime_dir,
        env_dir=args.env_dir,
    )
    _write(toolchain_path, toolchain)

    if toolchain['status'] == 'UNAVAILABLE':
        payload = {
            'schema_version': 1,
            'tool': args.tool,
            'status': 'UNAVAILABLE',
            'repository': args.repository,
            'task_id': args.task_id,
            'base_sha': args.base_sha,
            'candidate_sha': args.candidate_sha,
            'reason': 'toolchain_unavailable',
            'acceptance_authority': False,
            'toolchain': toolchain,
            'orchestration_ms': (time.perf_counter() - started) * 1000,
        }
        _write(receipt_path, payload)
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    env = os.environ.copy()
    runtime = toolchain.get('runtime') or {}
    interpreter = sys.executable

    if args.tool == 'semdup':
        if toolchain['status'] == 'READY':
            env['PATH'] = str(Path(runtime['binary']).parent) + os.pathsep + env.get('PATH', '')
            env['SEMDUP_CACHE'] = runtime['cache_dir']
        command = [
            interpreter, 'tools/semantic_qa/semdup_trace.py',
            '--repo', str(args.repo),
            '--base-sha', args.base_sha,
            '--candidate-sha', args.candidate_sha,
            '--repository', args.repository,
            '--task-id', args.task_id,
            '--profile', str(args.profile),
            '--input-manifest', str(args.input_manifest),
            '--output-dir', str(args.output_dir),
        ]
    elif args.tool == 'semble':
        if toolchain['status'] == 'READY':
            interpreter = str(Path(runtime['env_dir']) / 'bin' / 'python')
            env['PATH'] = str(Path(runtime['env_dir']) / 'bin') + os.pathsep + env.get('PATH', '')
            env['SEMBLE_MODEL_NAME'] = runtime['model_dir']
            env['SEMBLE_CACHE_LOCATION'] = str(args.output_dir / 'semble-cache')
            env['HF_HUB_OFFLINE'] = '1'
        command = [
            interpreter, 'tools/semantic_qa/semble_trace.py',
            '--input-manifest', str(args.input_manifest),
            '--input-root', str(args.input_root),
            '--failure-classes', str(args.failure_classes),
            '--profile', str(args.profile),
            '--output', str(receipt_path),
            '--top-k', str(profiles['semble']['top_k']),
        ]
    else:
        snapshot = args.runtime_dir / 'model'
        if toolchain['status'] == 'READY':
            interpreter = str(Path(runtime['env_dir']) / 'bin' / 'python')
            env['PATH'] = str(Path(runtime['env_dir']) / 'bin') + os.pathsep + env.get('PATH', '')
            env['HF_HUB_OFFLINE'] = '1'
            env['NEEDLE_TELEMETRY'] = '0'
        command = [
            interpreter, 'tools/semantic_qa/needle_trace.py',
            '--input-manifest', str(args.input_manifest),
            '--input-root', str(args.input_root),
            '--failure-classes', str(args.failure_classes),
            '--profile', str(args.profile),
            '--snapshot', str(snapshot),
            '--output', str(receipt_path),
            '--top-k', str(profiles['needle3']['top_k']),
        ]

    cp = subprocess.run(command, env=env, text=True, capture_output=True)
    (args.output_dir / 'runner.log').write_text(
        cp.stdout + '\n--- stderr ---\n' + cp.stderr
    )
    if cp.returncode != 0 or not receipt_path.is_file():
        payload = {
            'schema_version': 1,
            'tool': args.tool,
            'status': 'UNAVAILABLE',
            'repository': args.repository,
            'task_id': args.task_id,
            'base_sha': args.base_sha,
            'candidate_sha': args.candidate_sha,
            'reason': 'trace_execution_failed',
            'returncode': cp.returncode,
            'error_tail': cp.stderr[-4000:],
            'acceptance_authority': False,
            'toolchain': toolchain,
            'orchestration_ms': (time.perf_counter() - started) * 1000,
        }
        _write(receipt_path, payload)
    else:
        payload = _merge_toolchain(
            receipt_path, toolchain, (time.perf_counter() - started) * 1000
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
