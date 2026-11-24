import hashlib
import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import project_contract as pc
import project_contract_skill as skill


class ProjectContractSkillTests(unittest.TestCase):
    def test_lossless_deterministic_skills_only_package(self):
        source = pc.SOURCE.read_bytes()
        a = skill.build_package(pc.SOURCE, '0.1.0')
        self.assertEqual(a, skill.build_package(pc.SOURCE, '0.1.0'))
        with zipfile.ZipFile(io.BytesIO(a)) as package:
            self.assertEqual(set(package.namelist()), {
                'plugin.json', 'skills/theseus-project-contract/SKILL.md',
            })
            manifest = json.loads(package.read('plugin.json'))
            self.assertEqual(manifest['name'], 'theseus-project-contract')
            self.assertEqual(manifest['version'], '0.1.0')
            content = package.read('skills/theseus-project-contract/SKILL.md')
            self.assertEqual(content.split(b'```yaml\n', 1)[1].rsplit(b'```\n', 1)[0], source)
            self.assertIn(hashlib.sha256(source).hexdigest().encode(), content)
            self.assertIn(b'PROJECT_CONTRACT_SKILL_PROBE', content)
            self.assertIn(b'PC_OK_V12', content)

    def test_execution_guidance_is_additive_and_not_a_turn_cap(self):
        source = pc.SOURCE.read_bytes()
        with zipfile.ZipFile(io.BytesIO(skill.build_package(pc.SOURCE, '0.1.1'))) as package:
            content = package.read('skills/theseus-project-contract/SKILL.md')
        self.assertEqual(content.split(b'```yaml\n', 1)[1].rsplit(b'```\n', 1)[0], source)
        guidance = content.split(b'## Operational interpretation', 1)[1].split(b'## Canonical policy', 1)[0]
        for phrase in (b'one policy, not cumulative restrictions', b'not a tool-call budget',
                       b'meaningful checkpoint', b'explicit user boundary',
                       b'necessary verification', b'No new authority', b'Example:'):
            self.assertIn(phrase, guidance)

    def test_invalid_contract_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / 'contract.yaml'
            bad.write_text('Scope: x\nScope: y\n')
            with self.assertRaises(pc.ContractError):
                skill.build_package(bad, '0.1.0')

    def test_invalid_version_rejected(self):
        with self.assertRaises(ValueError):
            skill.build_package(pc.SOURCE, 'latest')
