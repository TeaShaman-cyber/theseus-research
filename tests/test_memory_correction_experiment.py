import json
from pathlib import Path
import unittest

from tools.memory_correction_experiment import (
    MemoryCorrection,
    parse_correction,
    render_controlled_prose,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / 'docs' / 'research' / '2026-10-07-memory-correction-v1'


class MemoryCorrectionExperimentTest(unittest.TestCase):
    def test_parser_accepts_frozen_structured_canary(self) -> None:
        fixtures = json.loads((FIXTURE_DIR / 'fixtures.json').read_text(encoding='utf-8'))
        parsed = parse_correction(fixtures['B_raw_structured'])

        self.assertEqual(
            parsed,
            MemoryCorrection(
                kind='PREFERENCE',
                target='OpenAI engineering and reliability',
                must=(
                    'strong persistent negative preference',
                    'criticism concerns engineering and product reliability',
                ),
                must_not=('neutral or generally positive attitude',),
                scope='durable user preference',
            ),
        )

    def test_controlled_prose_is_deterministic_and_keeps_negative_boundary(self) -> None:
        fixtures = json.loads((FIXTURE_DIR / 'fixtures.json').read_text(encoding='utf-8'))
        parsed = parse_correction(fixtures['B_raw_structured'])

        self.assertEqual(render_controlled_prose(parsed), fixtures['C_controlled_prose'])
        self.assertIn('Do not characterize this as neutral or generally positive attitude.', fixtures['C_controlled_prose'])

    def test_free_form_and_structured_conditions_share_the_same_frozen_semantics(self) -> None:
        fixtures = json.loads((FIXTURE_DIR / 'fixtures.json').read_text(encoding='utf-8'))

        self.assertEqual(
            fixtures['semantic_contract'],
            {
                'kind': 'PREFERENCE',
                'target': 'OpenAI engineering and reliability',
                'must': [
                    'strong persistent negative preference',
                    'criticism concerns engineering and product reliability',
                ],
                'must_not': ['neutral or generally positive attitude'],
                'scope': 'durable user preference',
            },
        )
        self.assertTrue(fixtures['A_free_form'].startswith('Please treat this as a durable correction:'))

    def test_parser_rejects_clause_order_drift(self) -> None:
        invalid = '''CORRECTION PREFERENCE\nTARGET "OpenAI engineering and reliability"\nMUST_NOT "neutral or generally positive attitude"\nMUST "strong persistent negative preference"\nSCOPE "durable user preference"\n'''
        with self.assertRaisesRegex(ValueError, 'canonical order'):
            parse_correction(invalid)

    def test_parser_rejects_whitespace_only_clause(self) -> None:
        invalid = '''CORRECTION PREFERENCE\nTARGET "   "\nMUST "strong persistent negative preference"\nSCOPE "durable user preference"\n'''
        with self.assertRaisesRegex(ValueError, 'must not be empty'):
            parse_correction(invalid)

    def test_parser_rejects_unknown_clause(self) -> None:
        invalid = '''CORRECTION PREFERENCE\nTARGET "OpenAI engineering and reliability"\nMUST "strong persistent negative preference"\nMAGIC "hidden backend"\n'''
        with self.assertRaisesRegex(ValueError, 'unsupported clause'):
            parse_correction(invalid)


if __name__ == '__main__':
    unittest.main()
