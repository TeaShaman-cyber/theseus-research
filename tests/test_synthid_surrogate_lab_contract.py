import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
LAB = ROOT / "labs" / "synthid-surrogate"


class SynthIDSurrogateLabContractTest(unittest.TestCase):
    def test_lab_is_public_surrogate_only(self):
        script = (LAB / "run_smoke.py").read_text(encoding="utf-8")
        readme = (LAB / "README.md").read_text(encoding="utf-8")
        self.assertIn('STATUS = "SURROGATE_ONLY"', script)
        self.assertIn("does **not**", readme)
        self.assertNotIn("/workspace/research/", script)
        self.assertNotIn("watermark-candidate-panel", script)

    def test_runner_is_bounded_and_not_scheduled(self):
        workflow = (ROOT / ".github" / "workflows" / "synthid-surrogate-lab.yml").read_text(encoding="utf-8")
        self.assertIn("timeout-minutes: 12", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("schedule:", workflow)
        self.assertIn("runs-on: ubuntu-latest", workflow)

    def test_smoke_script_compiles_without_heavy_runtime_import(self):
        source = (LAB / "run_smoke.py").read_text(encoding="utf-8")
        compile(source, str(LAB / "run_smoke.py"), "exec")


if __name__ == "__main__":
    unittest.main()
