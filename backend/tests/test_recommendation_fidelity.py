"""Deterministic style preference contracts; no account/provider calls."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from src.utils.recommendation_fidelity import pattern_kind, prefer_plain_candidates, minimalist_subtle_cues
from src.utils import recommendation_fidelity as fidelity
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
    def test_ordering_normalizes_each_garment_once_despite_pairwise_comparisons(self):
        rows = [candidate(f'item-{index}', 'solid' if index % 2 else 'graphic') for index in range(20)]
        with patch.object(fidelity, 'normalize_garment_metadata', wraps=fidelity.normalize_garment_metadata) as normalize:
            prefer_plain_candidates(rows, 'Minimalist', mood='Subtle')
        self.assertEqual(normalize.call_count, len(rows))

    def test_subtle_prefers_known_plain_neutral_after_an_intermediate_plain_accent(self):
        graphic, accent, neutral = candidate('graphic', 'graphic'), candidate('accent', 'solid'), candidate('neutral', 'solid')
        accent[1]['item']['color'] = 'red'
        result = prefer_plain_candidates([graphic, accent, neutral], 'Minimalist', mood='Subtle')
        self.assertEqual(result[0][0], 'neutral')
        self.assertEqual({r[0] for r in result}, {'graphic', 'accent', 'neutral'})
        self.assertEqual(prefer_plain_candidates([accent, neutral], 'Minimalist', mood='Calm')[0][0], 'accent')
        self.assertEqual(prefer_plain_candidates([accent, neutral], 'Streetwear', mood='Subtle')[0][0], 'accent')

    def test_subtle_promotion_preserves_practicality_and_never_promotes_unknown_as_plain(self):
        accent = candidate('accent', 'solid')
        accent[1]['item']['color'] = 'red'
        for key in ('weather_score', 'compatibility_score', 'occasion_score'):
            neutral = candidate('neutral', 'solid')
            accent[1][key], neutral[1][key] = .8, .2
            with self.subTest(key=key):
                self.assertEqual(prefer_plain_candidates([accent, neutral], 'Minimalist', mood='Subtle')[0][0], 'accent')
            accent[1].pop(key) if key == 'occasion_score' else accent[1].update({key: .8})
        unknown = candidate('unknown', '')
        self.assertEqual(prefer_plain_candidates([accent, unknown], 'Minimalist', mood='Subtle')[0][0], 'accent')
        neutral = candidate('neutral', 'solid')
        self.assertEqual(prefer_plain_candidates([accent, neutral], 'Minimalist', mood='Subtle', eligible=lambda _: False)[0][0], 'accent')

    def test_saved_cue_corrections_are_consistent_in_raw_and_typed_records(self):
        raw = candidate('corrected', 'graphic')[1]['item']
        raw.update(color='navy', pattern='solid', mood=['Subtle'])
        raw['analysis'] = {'metadata': {'moodTags': ['bold'], 'colorAnalysis': {'dominant': ['red']},
                                       'visual_attributes': {'pattern': 'graphic'}}}
        typed = ClothingItem(**normalize_stored_garment(raw, {kind.value for kind in ClothingType}))
        expected = {'pattern': 'plain', 'palette': 'neutral', 'mood': 'subtle', 'supported': True}
        self.assertEqual(minimalist_subtle_cues(raw), expected)
        self.assertEqual(minimalist_subtle_cues(typed), expected)
        raw.update(name='Graphic logo tee', color='unknown', pattern='unknown', mood=['unknown'])
        typed = ClothingItem(**normalize_stored_garment(raw, {kind.value for kind in ClothingType}))
        expected = {'pattern': 'unknown', 'palette': 'unknown', 'mood': 'unknown', 'supported': False}
        self.assertEqual(minimalist_subtle_cues(raw), expected)
        self.assertEqual(minimalist_subtle_cues(typed), expected)
        for value in (0, False):
            raw['pattern'] = value
            typed = ClothingItem(**normalize_stored_garment(raw, {kind.value for kind in ClothingType}))
            self.assertEqual(minimalist_subtle_cues(raw), expected)
            self.assertEqual(minimalist_subtle_cues(typed), expected)

    def test_statement_levels_are_finite_and_default_zero_does_not_prove_mood(self):
        raw = candidate('neutral', 'solid')[1]['item']
        raw['mood'] = ['relaxed']  # Broad labels are not affirmative Subtle evidence.
        for value in (None, 0, False, True, -1, 11, float('nan'), float('inf'), 'unknown'):
            raw['statementLevel'] = value
            with self.subTest(value=value):
                self.assertEqual(minimalist_subtle_cues(raw)['mood'], 'unknown')
        for value in (1, 2, 6, 8, 10):
            raw['statementLevel'] = value
            cue = minimalist_subtle_cues(raw)
            self.assertEqual(cue['mood'], 'subtle' if value <= 2 else 'statement')
            self.assertEqual(cue['supported'], value <= 2)
        raw['metadata']['visualAttributes']['statementLevel'] = 8
        for value in (0, False, 'unknown'):
            raw['statementLevel'] = value
            typed = ClothingItem(**normalize_stored_garment(raw, {kind.value for kind in ClothingType}))
            self.assertEqual(minimalist_subtle_cues(typed)['mood'], 'unknown')

    def test_recorded_non_neutral_color_never_infers_a_statement_mood(self):
        raw = candidate('red', 'solid')[1]['item']
        raw.update(color='red', mood=['Subtle'])
        self.assertEqual(minimalist_subtle_cues(raw),
                         {'pattern': 'plain', 'palette': 'accent', 'mood': 'subtle', 'supported': False})
        raw.update(color='unknown', mood=['unknown'])
        raw['metadata']['colorAnalysis'] = {'dominant': ['navy']}
        self.assertEqual(minimalist_subtle_cues(raw)['palette'], 'unknown')

    def test_missing_root_color_is_unknown_before_and_after_admission_despite_other_color_fields(self):
        color_shapes = (
            {'colorName': 'navy'},
            {'dominantColors': [{'name': 'navy'}]},
            {'metadata': {'visualAttributes': {'pattern': 'solid'},
                          'colorAnalysis': {'dominant': ['navy']}}},
        )
        for shape in color_shapes:
            for root_color in (None, '', 'unknown'):
                raw = candidate('missing-color', 'solid')[1]['item']
                raw.update(shape)
                if root_color is None:
                    raw.pop('color')
                else:
                    raw['color'] = root_color
                with self.subTest(shape=shape, root_color=root_color):
                    prepared = normalize_stored_garment(raw, {kind.value for kind in ClothingType})
                    typed = ClothingItem(**prepared)
                    expected = {'pattern': 'plain', 'palette': 'unknown', 'mood': 'unknown', 'supported': False}
                    self.assertEqual(minimalist_subtle_cues(raw), expected)
                    self.assertEqual(minimalist_subtle_cues(prepared), expected)
                    self.assertEqual(minimalist_subtle_cues(typed), expected)

    def test_root_color_shapes_have_same_evidence_after_admission_and_typed_conversion(self):
        cases = ((['navy'], 'unknown'), ({'name': 'navy'}, 'unknown'),
                 ('navy', 'neutral'), ('white / navy', 'neutral'), ('white and red', 'accent'))
        for color, palette in cases:
            raw = candidate('color-shape', 'solid')[1]['item']
            raw['color'] = color
            with self.subTest(color=color):
                prepared = normalize_stored_garment(raw, {kind.value for kind in ClothingType})
                typed = ClothingItem(**prepared)
                expected = {'pattern': 'plain', 'palette': palette, 'mood': 'unknown',
                            'supported': palette == 'neutral'}
                for record in (raw, prepared, typed):
                    self.assertEqual(minimalist_subtle_cues(record), expected)

    def test_conflicting_saved_mood_cannot_hide_explicit_statement_evidence(self):
        raw = candidate('neutral', 'solid')[1]['item']
        raw['mood'] = ['Subtle', 'Bold']
        typed = ClothingItem(**normalize_stored_garment(raw, {kind.value for kind in ClothingType}))
        for value in (raw, typed):
            self.assertEqual(minimalist_subtle_cues(value)['mood'], 'statement')
            self.assertFalse(minimalist_subtle_cues(value)['supported'])

    def test_root_mood_tags_alias_survives_admission_with_root_mood_precedence(self):
        cases = (
            ({'moodTags': ['Bold']}, 'statement'),
            ({'moodTags': ['unknown']}, 'unknown'),
            ({'mood': ['Subtle'], 'moodTags': ['Bold']}, 'subtle'),
            ({'mood': ['Bold'], 'moodTags': ['Subtle']}, 'statement'),
        )
        for corrections, expected_mood in cases:
            raw = candidate('mood-alias', 'solid')[1]['item']
            raw['metadata']['moodTags'] = ['Bold']
            raw.update(corrections)
            with self.subTest(corrections=corrections):
                prepared = normalize_stored_garment(raw, {kind.value for kind in ClothingType})
                typed = ClothingItem(**prepared)
                expected = {'pattern': 'plain', 'palette': 'neutral', 'mood': expected_mood,
                            'supported': expected_mood != 'statement'}
                for record in (raw, prepared, typed):
                    self.assertEqual(minimalist_subtle_cues(record), expected)

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
