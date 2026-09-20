from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

from tools.semantic_qa.package_freshness import _git_head, _hf_head, evaluate_freshness


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _freshness(cfg: dict) -> dict:
    package = cfg['package']
    policy = cfg['freshness']
    errors: list[str] = []
    current_git = None
    current_hf = None
    try:
        current_git = _git_head(policy['git_url'], policy['git_ref'])
    except Exception as exc:
        errors.append(f'git_currentness:{type(exc).__name__}:{exc}')
    if policy.get('hf_repo') and cfg.get('model_revision'):
        try:
            current_hf = _hf_head(policy['hf_repo'])
        except Exception as exc:
            errors.append(f'hf_currentness:{type(exc).__name__}:{exc}')
    result = evaluate_freshness(
        now=datetime.now(timezone.utc),
        built_at=package.get('built_at'),
        expires_at=package.get('expires_at'),
        max_age_days=int(policy.get('max_age_days', 30)),
        expiry_warning_days=int(policy.get('expiry_warning_days', 14)),
        pinned_git_sha=cfg.get('source_sha'),
        current_git_sha=current_git,
        pinned_hf_revision=cfg.get('model_revision'),
        current_hf_revision=current_hf,
        currentness_errors=errors,
    )
    return {
        **result,
        'pinned_git_sha': cfg.get('source_sha'),
        'current_git_sha': current_git,
        'pinned_hf_revision': cfg.get('model_revision'),
        'current_hf_revision': current_hf,
        'blocking': False,
    }


def _artifact_metadata(repository: str, package: dict) -> dict:
    cp = subprocess.run(
        ['gh', 'api', f"repos/{repository}/actions/artifacts/{package['artifact_id']}"],
        text=True,
        capture_output=True,
        check=True,
        timeout=30,
    )
    metadata = json.loads(cp.stdout)
    if metadata.get('expired'):
        raise RuntimeError('pinned package artifact is expired')
    if metadata.get('name') != package['artifact_name']:
        raise RuntimeError('artifact name mismatch')
    if metadata.get('digest') != package['artifact_digest']:
        raise RuntimeError('artifact digest mismatch')
    run = metadata.get('workflow_run') or {}
    if int(run.get('id', -1)) != int(package['run_id']):
        raise RuntimeError('artifact workflow run mismatch')
    return metadata


def _download(repository: str, package: dict, download_dir: Path) -> None:
    shutil.rmtree(download_dir, ignore_errors=True)
    download_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            'gh', 'run', 'download', str(package['run_id']),
            '--repo', repository,
            '--name', package['artifact_name'],
            '--dir', str(download_dir),
        ],
        check=True,
        timeout=180,
    )


def _extract(package: dict, download_dir: Path, runtime_dir: Path) -> Path:
    tar_path = download_dir / package['tar_file']
    if not tar_path.is_file():
        raise RuntimeError(f'missing package tarball: {tar_path}')
    got = _sha256(tar_path)
    if got != package['tar_sha256']:
        raise RuntimeError(f"package tar sha mismatch: {got} != {package['tar_sha256']}")
    shutil.rmtree(runtime_dir, ignore_errors=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar_path, 'r:gz') as tf:
        tf.extractall(runtime_dir, filter='data')
    return runtime_dir


def _verify_build_receipt(tool: str, cfg: dict, root: Path) -> dict:
    path = root / 'build-receipt.json'
    if not path.is_file():
        raise RuntimeError('package build-receipt.json missing')
    receipt = json.loads(path.read_text())
    if receipt.get('status') != 'BUILT':
        raise RuntimeError('package build receipt is not BUILT')
    if receipt.get('source_sha') != cfg.get('source_sha'):
        raise RuntimeError('package source SHA mismatch')
    if tool == 'semdup':
        if receipt.get('model_key') != cfg.get('model_key'):
            raise RuntimeError('semdup package model key mismatch')
    else:
        if receipt.get('model_repo') != cfg.get('model_repo'):
            raise RuntimeError('package model repo mismatch')
        if receipt.get('model_revision') != cfg.get('model_revision'):
            raise RuntimeError('package model revision mismatch')
    return receipt


def _install_python(tool: str, cfg: dict, root: Path, env_dir: Path) -> dict:
    shutil.rmtree(env_dir, ignore_errors=True)
    subprocess.run([os.sys.executable, '-m', 'venv', str(env_dir)], check=True)
    pip = env_dir / 'bin' / 'pip'
    wheels = root / 'wheels'
    if tool == 'semble':
        packages = ['semble']
    else:
        packages = ['cactus-needle', f"scikit-learn=={cfg['ranker_version']}"]
    subprocess.run(
        [
            str(pip), 'install', '--disable-pip-version-check',
            '--no-index', '--find-links', str(wheels), *packages,
        ],
        check=True,
        timeout=180,
    )
    return {'env_dir': str(env_dir), 'model_dir': str(root / 'model')}


def prepare(
    *, tool: str, profiles: dict, repository: str, input_status: str,
    download_dir: Path, runtime_dir: Path, env_dir: Path | None,
) -> dict:
    cfg = profiles[tool]
    package = cfg['package']
    freshness = _freshness(cfg)
    receipt = {
        'schema_version': 1,
        'tool': tool,
        'status': 'PENDING',
        'freshness': freshness,
        'package': package,
        'input_status': input_status,
        'blocking': False,
    }
    if input_status == 'NO_SIGNAL':
        receipt['status'] = 'SKIPPED_NO_SIGNAL'
        receipt['setup_ms'] = 0.0
        return receipt
    started = time.perf_counter()
    try:
        metadata = _artifact_metadata(repository, package)
        _download(repository, package, download_dir)
        root = _extract(package, download_dir, runtime_dir)
        build_receipt = _verify_build_receipt(tool, cfg, root)
        runtime: dict[str, str]
        if tool == 'semdup':
            binary = root / 'bin' / 'semdup'
            if not binary.is_file():
                raise RuntimeError('semdup binary missing from package')
            binary.chmod(binary.stat().st_mode | 0o111)
            runtime = {'binary': str(binary), 'cache_dir': str(root / 'cache')}
        else:
            if env_dir is None:
                raise RuntimeError('Python toolchain requires --env-dir')
            runtime = _install_python(tool, cfg, root, env_dir)
        receipt.update({
            'status': 'READY',
            'artifact_metadata': {
                'id': metadata.get('id'),
                'name': metadata.get('name'),
                'digest': metadata.get('digest'),
                'expires_at': metadata.get('expires_at'),
            },
            'build_receipt': build_receipt,
            'runtime': runtime,
        })
    except Exception as exc:
        receipt.update({
            'status': 'UNAVAILABLE',
            'error': f'{type(exc).__name__}: {exc}',
        })
    receipt['setup_ms'] = (time.perf_counter() - started) * 1000
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--tool', choices=['semdup', 'semble', 'needle3'], required=True)
    parser.add_argument('--profile', type=Path, required=True)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--input-status', required=True)
    parser.add_argument('--download-dir', type=Path, required=True)
    parser.add_argument('--runtime-dir', type=Path, required=True)
    parser.add_argument('--env-dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    profiles = json.loads(args.profile.read_text())
    receipt = prepare(
        tool=args.tool, profiles=profiles, repository=args.repository,
        input_status=args.input_status, download_dir=args.download_dir,
        runtime_dir=args.runtime_dir, env_dir=args.env_dir,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
