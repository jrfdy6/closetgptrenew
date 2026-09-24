"""Real composer regressions using anonymized, allowlisted saved garment facts.

The ten rows retain saved type/color/pattern/mood/occasion/season/formality only.
IDs, names and image addresses below are synthetic. Practicality scores and wear
history are explicitly injected adversarial test inputs, not inferred facts.
"""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.custom_types.wardrobe import ClothingItem, ClothingType
from src.services import robust_outfit_generation_service as robust
from src.utils.outfit_admission import normalize_stored_garment, has_complete_combination
from src.utils.recommendation_fidelity import minimalist_subtle_cues


SAVED_FACTS = [
    ('shirt', 'White', 'solid', 1, 'Casual', ['relaxed', 'neutral'], ['casual', 'everyday'], ['spring', 'summer']),
    ('pants', 'Dark Blue', 'solid', 2, 'Casual', ['relaxed'], ['everyday', 'casual'], ['fall', 'winter', 'spring']),
    ('shoes', 'Navy Blue', 'solid', 5, 'Casual', ['active', 'relaxed'], ['casual', 'sports'], ['spring', 'summer', 'fall']),
    ('sweater', 'Black', 'graphic', 6, 'Casual', ['relaxed', 'edgy'], ['casual', 'everyday'], ['fall', 'winter']),
    ('sweater', 'Red', 'solid', 5, 'Smart Casual', ['confident', 'bold'], ['casual', 'office', 'brunch'], ['fall', 'winter']),
    ('jacket', 'Light Blue', 'solid', 5, 'Casual', ['relaxed', 'cool'], ['casual', 'everyday'], ['spring', 'fall']),
    ('shoes', 'Brown', 'solid', 5, 'Formal', ['sophisticated', 'professional'], ['business', 'formal', 'wedding'], ['fall', 'winter']),
    ('jacket', 'White', 'solid', 3, 'Casual', ['relaxed', 'comfortable'], ['casual', 'everyday'], ['spring', 'fall']),
    ('pants', 'Beige', 'solid', 2, 'Smart Casual', ['relaxed', 'neutral'], ['everyday', 'work', 'casual'], ['spring', 'summer', 'fall']),
    ('shorts', 'Khaki', 'solid', 3, 'Casual', ['relaxed'], ['casual', 'outdoor'], ['summer', 'spring']),
]


def saved_fixture():
    return [{
        'id': f'fixture-{index:02}', 'name': f'Saved {kind}', 'type': kind, 'color': color,
        'userId': 'fixture-user', 'imageUrl': 'https://example.test/fixture.png',
        'mood': mood, 'occasion': occasion, 'season': season,
        'metadata': {'visualAttributes': {'pattern': pattern, 'statementLevel': statement, 'formalLevel': formal}},
    } for index, (kind, color, pattern, statement, formal, mood, occasion, season) in enumerate(SAVED_FACTS, 1)]


class SubtleRankingTests(unittest.IsolatedAsyncioTestCase):
    async def compose(self, *, items=None, mood='Subtle', required=None, worse=None, unscored_swap=False):
        rows = copy.deepcopy(items if items is not None else saved_fixture())
        scores = {}
        for row in rows:
            # Make the supported alternatives older/recent, and the rivals new.
            row['wearCount'] = 12 if minimalist_subtle_cues(row)['supported'] else 0
            item = ClothingItem(**normalize_stored_garment(row, {kind.value for kind in ClothingType}))
            scores[item.id] = {'item': item, 'composite_score': .8, 'weather_score': .8,
                               'compatibility_score': .8, 'occasion_score': .8}
        if worse:
            scores['fixture-01'][worse] = .2
        context = robust.GenerationContext(user_id='fixture-user', occasion='Casual', style='Minimalist', mood=mood,
                    weather=SimpleNamespace(temperature=72, condition='Clear'),
                    wardrobe=[s['item'] for s in scores.values()], user_profile={}, base_item_id=required)
        supported = [s['item'].id for s in scores.values() if minimalist_subtle_cues(s['item'])['supported']]
        diversity = MagicMock()
        diversity.get_recent_outfits.return_value = [{'items': [{'id': item_id} for item_id in supported]}]
        diversity.check_outfit_diversity.return_value = {'is_diverse': False, 'diversity_score': .5}
        suggestions = []
        if 'fixture-01' in scores and 'fixture-05' in scores:
            replacement = scores['fixture-05']['item']
            if unscored_swap:
                replacement = replacement.model_copy(update={'id': 'unscored-alternative'})
            suggestions = [{'item_to_replace': scores['fixture-01']['item'], 'alternative': replacement}]
        diversity.get_diversity_suggestions.return_value = suggestions
        noises = iter([-.5 if row_id in supported else .5 for row_id in scores])
        boosts = {row_id: 20 if row_id == 'fixture-04' else 19 if row_id == 'fixture-05' else 0 for row_id in scores}
        with patch.object(robust, 'diversity_filter', diversity), patch.object(robust, 'session_tracker', MagicMock()), \
             patch.object(robust, 'strategy_analytics', MagicMock()), patch.object(robust, 'adaptive_tuning', MagicMock()), \
             patch('random.uniform', side_effect=lambda *_: next(noises, 0)), \
             patch.object(robust.StrategyImplementation, 'apply_strategy', return_value={
                 'selection_adjustments': boosts, 'strategy_metadata': {'name': 'Adversarial fixture', 'description': 'Fixture'}}):
            service = robust.RobustOutfitGenerationService()
            service._get_recently_used_items = lambda *args, **kwargs: set(supported)
            result = await service._cohesive_composition_with_scores(context, scores, 'fixture-session')
        self.assertTrue(has_complete_combination([item.model_dump() for item in result.items]))
        return result

    async def test_saved_ten_item_fixture_prefers_supported_top_despite_all_novelty_biases_and_swap(self):
        result = await self.compose()
        ids = {item.id for item in result.items}
        self.assertIn('fixture-01', ids)
        self.assertFalse({'fixture-04', 'fixture-05'} & ids)

    async def test_other_mood_keeps_existing_plain_over_graphic_and_allows_red(self):
        result = await self.compose(mood='Bold')
        ids = {item.id for item in result.items}
        self.assertIn('fixture-05', ids)
        self.assertNotIn('fixture-04', ids)

    async def test_required_statement_piece_is_preserved(self):
        for required in ('fixture-04', 'fixture-05'):
            with self.subTest(required=required):
                result = await self.compose(required=required)
                self.assertIn(required, {item.id for item in result.items})

    async def test_worse_weather_compatibility_or_occasion_cannot_buy_visual_preference(self):
        for key in ('weather_score', 'compatibility_score', 'occasion_score'):
            with self.subTest(key=key):
                result = await self.compose(worse=key)
                self.assertIn('fixture-05', {item.id for item in result.items})

    async def test_unscored_diversity_suggestion_cannot_undo_evidenced_selection(self):
        result = await self.compose(unscored_swap=True)
        self.assertIn('fixture-01', {item.id for item in result.items})
        self.assertNotIn('unscored-alternative', {item.id for item in result.items})

    async def test_limited_closet_keeps_only_available_accent_top_complete(self):
        limited = [row for row in saved_fixture() if row['id'] in {'fixture-02', 'fixture-03', 'fixture-05'}]
        result = await self.compose(items=limited)
        self.assertEqual({item.id for item in result.items}, {row['id'] for row in limited})

    async def test_missing_visual_evidence_keeps_complete_fallback_without_invented_cues(self):
        limited = [row for row in saved_fixture() if row['id'] in {'fixture-01', 'fixture-02', 'fixture-03'}]
        for row in limited:
            row.update(color='unknown', mood=['unknown'])
            row['metadata']['visualAttributes'].update(pattern='unknown', statementLevel=0)
        result = await self.compose(items=limited)
        for item in result.items:
            self.assertEqual(minimalist_subtle_cues(item),
                             {'pattern': 'unknown', 'palette': 'unknown', 'mood': 'unknown', 'supported': False})


class SubtleFallbackRouteTests(unittest.TestCase):
    def test_actual_fallback_route_passes_requested_mood_to_ordering(self):
        from tests.test_generation_admission import ActiveGenerationAdmissionTests, garment
        harness = ActiveGenerationAdmissionTests(methodName='runTest')
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        harness.wardrobe = [
            garment('accent', 'shirt', color='red', pattern='solid'),
            garment('neutral', 'shirt', color='navy', pattern='solid'),
            garment('pants', 'pants'), garment('shoes', 'shoes'),
        ]
        harness.seed(harness.wardrobe)
        harness.robust.generate_outfit.side_effect = RuntimeError('fixture unavailable')
        for mood, expected in (('Subtle', 'neutral'), ('Calm', 'accent')):
            with self.subTest(mood=mood), patch('random.uniform', return_value=0):
                response = harness.generate(style='Minimalist', mood=mood)
            self.assertEqual(response.status_code, 200, response.text)
            ids = {item['id'] for item in response.json()['items']}
            self.assertIn(expected, ids)
            self.assertEqual(len(ids), 3)


if __name__ == '__main__':
    unittest.main()
