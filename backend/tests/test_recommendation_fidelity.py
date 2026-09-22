"""Deterministic style preference contracts; no account/provider calls."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from src.utils.recommendation_fidelity import pattern_kind, prefer_plain_candidates
from src.services import robust_outfit_generation_service as robust
from src.utils.outfit_admission import normalize_stored_garment
from src.custom_types.wardrobe import ClothingItem, ClothingType


def candidate(item_id, pattern, weather=.8, compatibility=.8, score=.8, kind='shirt'):
    item = {'id': item_id, 'userId': 'test', 'name': item_id, 'type': kind,
            'imageUrl': 'https://example.test/item.jpg', 'color': 'navy',
            'occasion': ['Casual'], 'style': ['Minimalist'], 'wearCount': 0,
            'metadata': {'visualAttributes': {'pattern': pattern}}}
    return (item_id, {'item': item, 'weather_score': weather,
                     'compatibility_score': compatibility, 'composite_score': score})


class PreferenceTests(unittest.TestCase):
    def test_plain_wins_despite_diversity_order_but_unknown_does_not(self):
        rows = [candidate('graphic', 'graphic'), candidate('unknown', ''), candidate('plain', 'solid')]
        result = prefer_plain_candidates(rows, 'Minimalist')
        self.assertEqual([row[0] for row in result], ['plain', 'graphic', 'unknown'])
        self.assertEqual(rows[0][0], 'graphic')
        self.assertEqual(prefer_plain_candidates(rows, 'Streetwear'), rows)

    def test_does_not_trade_weather_compatibility_category_or_admissibility(self):
        graphic = candidate('graphic', 'graphic')
        for plain in (candidate('plain', 'solid', weather=.2),
                      candidate('plain', 'solid', compatibility=.2),
                      candidate('plain', 'solid', kind='pants'),
                      candidate('plain', 'solid', score=-2)):
            self.assertEqual(prefer_plain_candidates([graphic, plain], 'Minimalist')[0][0], 'graphic')
        self.assertEqual(prefer_plain_candidates([graphic, candidate('plain', 'solid')], 'Minimalist', eligible=lambda _: False)[0][0], 'graphic')

    def test_saved_type_correction_beats_nested_category_prediction(self):
        service = robust.RobustOutfitGenerationService()
        for kind, expected in [('dress', 'dress'), ('pants', 'bottoms'), ('shoes', 'shoes')]:
            raw = candidate('corrected', 'solid', kind=kind)[1]['item']
            raw['analysis'] = {'metadata': {'visualAttributes': {'coreCategory': 'top'}}}
            item = ClothingItem(**normalize_stored_garment(raw, {kind.value for kind in ClothingType}))
            self.assertEqual(service._get_item_category(item), expected)

    def test_correction_wins_over_graphic_name_and_nested_prediction(self):
        self.assertEqual(pattern_kind({'name': 'Graphic tee', 'pattern': 'solid',
                                      'analysis': {'metadata': {'visualAttributes': {'pattern': 'graphic'}}}}), 'plain')
        self.assertEqual(pattern_kind({'name': 'Unknown', 'metadata': {'visualAttributes': {}}}), 'unknown')


class RobustCompositionTests(unittest.IsolatedAsyncioTestCase):
    async def compose(self, required=None, cold=False, one_piece=False):
        entries = [candidate('graphic', 'graphic'), candidate('plain', 'solid', weather=.2 if cold else .8),
                   candidate('pants', 'solid', kind='pants'), candidate('shoes', 'solid', kind='shoes')]
        if one_piece:
            entries = [candidate('dress', 'solid', kind='dress'), candidate('shoes', 'solid', kind='shoes')]
            entries[0][1]['item']['analysis'] = {'metadata': {'visualAttributes': {'coreCategory': 'top'}}}
        scores = dict(entries)
        for data in scores.values():
            data['item'] = ClothingItem(**normalize_stored_garment(data['item'], {kind.value for kind in ClothingType}))
        context = robust.GenerationContext(user_id='fixture', occasion='Casual', style='Minimalist', mood='Calm',
                    weather=SimpleNamespace(temperature=72, condition='Clear'),
                    wardrobe=[s['item'] for s in scores.values()], user_profile={}, base_item_id=required)
        diversity = MagicMock()
        diversity.check_outfit_diversity.return_value = {'is_diverse': False, 'diversity_score': .5}
        diversity.get_diversity_suggestions.return_value = [] if one_piece else [{'item_to_replace': scores['plain']['item'], 'alternative': scores['graphic']['item']}]
        with patch.object(robust, 'diversity_filter', diversity), patch.object(robust, 'session_tracker', MagicMock()), \
             patch.object(robust, 'strategy_analytics', MagicMock()), patch.object(robust, 'adaptive_tuning', MagicMock()), \
             patch('random.uniform', return_value=0), patch.object(robust.StrategyImplementation, 'apply_strategy', return_value={'selection_adjustments': {'graphic': 8}, 'strategy_metadata': {'name': 'Fixture', 'description': 'Fixture'}}):
            service = robust.RobustOutfitGenerationService()
            service._get_recently_used_items = lambda *args, **kwargs: {'plain'}
            return await service._cohesive_composition_with_scores(context, scores, 'fixture-session')

    async def test_real_composer_keeps_plain_despite_strategy_diversity_and_final_swap(self):
        outfit = await self.compose()
        ids = {item.id for item in outfit.items}
        self.assertIn('plain', ids)
        self.assertNotIn('graphic', ids)
        self.assertTrue({'pants', 'shoes'} <= ids)

    async def test_corrected_one_piece_remains_a_complete_two_item_outfit(self):
        outfit = await self.compose(required='dress', one_piece=True)
        self.assertEqual({item.id for item in outfit.items}, {'dress', 'shoes'})

    async def test_real_composer_keeps_required_graphic(self):
        outfit = await self.compose(required='graphic')
        self.assertIn('graphic', {item.id for item in outfit.items})

    async def test_real_composer_does_not_promote_weather_worse_plain(self):
        outfit = await self.compose(cold=True)
        self.assertIn('graphic', {item.id for item in outfit.items})


if __name__ == '__main__':
    unittest.main()
