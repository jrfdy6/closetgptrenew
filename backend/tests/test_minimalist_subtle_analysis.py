"""User-facing notes must reflect actual final garment evidence and limits."""
import unittest
from types import SimpleNamespace

from src.utils.outfit_analysis import generate_outfit_analysis


def garment(item_id, color='navy', pattern='solid', **fields):
    return {'id': item_id, 'name': item_id, 'color': color,
            'metadata': {'visualAttributes': {'pattern': pattern}}, **fields}


class MinimalistSubtleAnalysisTests(unittest.IsolatedAsyncioTestCase):
    async def note(self, items, required=None):
        request = SimpleNamespace(style='Minimalist', mood='Subtle', occasion='Casual', baseItemId=required)
        result = await generate_outfit_analysis(items, request, {'score': 95, 'diversity_score': 100})
        return result['styleSynergy']

    async def test_plain_non_neutral_is_an_accent_not_a_saturation_or_boldness_claim(self):
        note = await self.note([garment('Red cardigan', color='red')], required='Red cardigan')
        self.assertEqual(note['compromise'], 'color_accent')
        self.assertIn('color accent', note['insight'])
        self.assertIn('required piece', note['insight'])
        for unsupported in ('saturated', 'bright', 'bold', 'incompatible', 'perfect', '95'):
            self.assertNotIn(unsupported, note['insight'].lower())

    async def test_required_graphic_is_preserved_and_explained_without_false_plainness(self):
        note = await self.note([garment('Required tee', pattern='graphic'), garment('Plain trousers')], 'Required tee')
        self.assertEqual(note['compromise'], 'graphic_detail')
        self.assertIn('partial match', note['insight'])
        self.assertIn('required piece', note['insight'])

    async def test_explicit_statement_detail_blocks_plain_neutral_endorsement(self):
        item = garment('Statement coat')
        item['metadata']['visualAttributes']['statementLevel'] = 8
        note = await self.note([item], required='Statement coat')
        self.assertEqual(note['compromise'], 'statement_detail')
        self.assertIn('required piece', note['insight'])
        self.assertNotIn('plain pieces and neutral palette', note['insight'])

    async def test_unknown_piece_does_not_become_plain_or_neutral_from_another_piece(self):
        note = await self.note([garment('Known tee'), garment('Unknown layer', color='unknown', pattern='unknown')])
        self.assertEqual(note['compromise'], 'insufficient_detail')
        self.assertNotIn('plain pieces and neutral palette', note['insight'])

    async def test_empty_evidence_and_default_zero_do_not_create_an_endorsement(self):
        for items in ([], [{'id': 'pending', 'name': 'Pending', 'color': 'unknown',
                           'metadata': {'visualAttributes': {'statementLevel': 0, 'embellishments': 'none'}}}]):
            with self.subTest(items=items):
                note = await self.note(items)
                self.assertEqual(note['compromise'], 'insufficient_detail')

    async def test_partial_plain_neutral_cues_never_claim_complete_fit_or_use_ranking_score(self):
        note = await self.note([garment('White tee', color='white'), garment('Navy trousers')])
        self.assertIn('support', note['insight'])
        self.assertNotIn('compromise', note)
        for unsupported in ('perfect', 'complete match', '95', 'confidence'):
            self.assertNotIn(unsupported, note['insight'].lower())


if __name__ == '__main__':
    unittest.main()
