import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
CHECKER = ROOT / "experiments" / "riemann-form" / "check.py"


class RiemannFormCheckTests(unittest.TestCase):
    def run_checker(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt = pathlib.Path(tmp) / "receipt.json"
            proc = subprocess.run(
                [sys.executable, str(CHECKER), "--receipt", str(receipt)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(receipt.read_text(encoding="utf-8")) if receipt.exists() else None
            return proc, data

    def test_checker_succeeds_and_records_exact_mobius_identity(self):
        proc, data = self.run_checker()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(data["mobius"]["difference"], "(2*x - 1)/(x**2 - 2*x + y**2 + 1)")
        self.assertTrue(data["mobius"]["critical_line_iff_unit_circle"])

    def test_checker_maps_functional_equation_involution_to_reciprocal(self):
        proc, data = self.run_checker()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(data["functional_involution"]["difference"], "0")
        self.assertTrue(data["functional_involution"]["one_minus_s_maps_to_reciprocal"])

    def test_checker_records_real_rooted_self_adjoint_canaries(self):
        proc, data = self.run_checker()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(data["self_adjoint_canaries"]["swap_2x2"]["charpoly"], [1, 0, -1])
        self.assertEqual(data["self_adjoint_canaries"]["path_3x3"]["charpoly"], [1, -6, 10, -4])
        self.assertTrue(all(item["all_roots_real"] for item in data["self_adjoint_canaries"].values()))

    def test_checker_rejects_complex_root_negative_control(self):
        proc, data = self.run_checker()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        control = data["negative_control"]
        self.assertEqual(control["charpoly"], [1, 0, 1])
        self.assertLess(control["discriminant"], 0)
        self.assertFalse(control["all_roots_real"])

    def test_receipt_is_deterministic(self):
        first_proc, first = self.run_checker()
        second_proc, second = self.run_checker()
        self.assertEqual(first_proc.returncode, 0, first_proc.stderr)
        self.assertEqual(second_proc.returncode, 0, second_proc.stderr)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
