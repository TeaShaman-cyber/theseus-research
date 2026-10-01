from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs' / 'research-devops-principles-2026-09-19.md'


class ResearchDevOpsPrinciplesTest(unittest.TestCase):
    def test_scope_is_registry_declared_research_lines(self):
        text = DOC.read_text(encoding='utf-8')
        self.assertIn('registry/research-lines.json', text)
        self.assertNotIn('Scope: Theseus project-owned repositories', text)

    def test_git_ci_and_runtime_roles_are_not_collapsed(self):
        text = DOC.read_text(encoding='utf-8')
        self.assertIn('promoted remote Git', text)
        self.assertIn('CI: evidence', text)
        self.assertIn('runtime readback: evidence', text)
        self.assertNotIn('live Git/CI/runtime readback: authority', text)


if __name__ == '__main__':
    unittest.main()
