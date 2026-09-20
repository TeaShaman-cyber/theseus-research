from __future__ import annotations

import hashlib
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from tools.semantic_qa.prepare_toolchain import _extract, _verify_build_receipt


class ToolchainPrepareTests(unittest.TestCase):
    def test_extract_rejects_wrong_tar_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tar_path = root / "package.tar.gz"
            payload = root / "payload.txt"
            payload.write_text("hello\n")
            with tarfile.open(tar_path, "w:gz") as tf:
                tf.add(payload, arcname="payload.txt")

            package = {
                "tar_file": tar_path.name,
                "tar_sha256": "0" * 64,
            }
            with self.assertRaisesRegex(RuntimeError, "package tar sha mismatch"):
                _extract(package, root, root / "runtime")

    def test_extract_accepts_exact_tar_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tar_path = root / "package.tar.gz"
            payload = root / "payload.txt"
            payload.write_text("hello\n")
            with tarfile.open(tar_path, "w:gz") as tf:
                tf.add(payload, arcname="payload.txt")

            digest = hashlib.sha256(tar_path.read_bytes()).hexdigest()
            package = {
                "tar_file": tar_path.name,
                "tar_sha256": digest,
            }
            runtime = _extract(package, root, root / "runtime")
            self.assertEqual((runtime / "payload.txt").read_text(), "hello\n")

    def test_build_receipt_binds_source_and_model(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = {
                "status": "BUILT",
                "source_sha": "a" * 40,
                "model_repo": "example/model",
                "model_revision": "b" * 40,
            }
            (root / "build-receipt.json").write_text(
                json.dumps(receipt) + "\n"
            )
            cfg = {
                "source_sha": "a" * 40,
                "model_repo": "example/model",
                "model_revision": "b" * 40,
            }
            observed = _verify_build_receipt("semble", cfg, root)
            self.assertEqual(observed["status"], "BUILT")

            cfg["model_revision"] = "c" * 40
            with self.assertRaisesRegex(RuntimeError, "model revision mismatch"):
                _verify_build_receipt("semble", cfg, root)


if __name__ == "__main__":
    unittest.main()
