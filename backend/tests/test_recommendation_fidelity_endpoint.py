"""Credential-free fidelity regressions through the active generation HTTP route.

The generator itself is controlled here; ownership admission, stored-garment
conversion, request normalization, fallback selection, final notes, persistence,
and the history response projection execute their production implementations.
"""
import ast
import logging
import sys
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

import test_generation_admission as admission_tests
from src.custom_types.wardrobe import ClothingItem
from src.routes.outfits import database
from src.utils import recommendation_fidelity
from src.utils.outfit_analysis import generate_outfit_analysis


class RecommendationFidelityEndpointTests(unittest.TestCase):
    seed = admission_tests.ActiveGenerationAdmissionTests.seed
    generate = admission_tests.ActiveGenerationAdmissionTests.generate
    persist_record = admission_tests.ActiveGenerationAdmissionTests.persist_record

    def setUp(self):
        previous_logging = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, previous_logging)
        admission_tests.ActiveGenerationAdmissionTests.setUp(self)
        self.addCleanup(self.client.close)
        # Keep the harness's external-service doubles, but run real model
        # conversion and factual analysis at the actual route boundary.
        sys.modules['src.custom_types.wardrobe'].ClothingItem = ClothingItem
        sys.modules['src.utils.outfit_analysis'].generate_outfit_analysis = generate_outfit_analysis
        sys.modules['src.config.firebase'].firebase_initialized = True
        self.ns['__spec__'] = None
        self.ns.update({key: value for key, value in vars(recommendation_fidelity).items()
                        if not key.startswith('_')})

    def use_minimalist_fixture(self, *, cold=False):
        graphic = admission_tests.garment(
            'graphic', 'shirt', name='Graphic cotton top', color='black',
            analysis={'metadata': {'visualAttributes': {
                'pattern': 'graphic', 'warmthFactor': 'heavy' if cold else 'light',
            }}},
        )
        plain = admission_tests.garment(
            'plain', 'shirt', name='Plain cotton top', color='white',
            metadata={'fileName': 'shirt-on-bed.jpg'},
            analysis={'metadata': {'visualAttributes': {'pattern': 'solid', 'warmthFactor': 'light'}}},
        )
        self.wardrobe = [graphic, plain, *self.wardrobe[1:]]
        self.seed(self.wardrobe)
        self.robust.generate_outfit.return_value.items = [plain, *self.wardrobe[2:]]
        return graphic, plain

    def test_actual_quiz_values_reach_generation_context_without_invented_facts(self):
        profile = {'measurements': {'bodyType': 'Round/Apple', 'skinTone': 'skin_tone_95',
                                    'height': '5\'8" - 5\'11"', 'weight': 'Prefer not to say'}}
        response = self.generate(user_profile=profile)
        self.assertEqual(response.status_code, 200, response.text)
        actual = self.robust.generate_outfit.call_args.args[0].user_profile
        self.assertEqual(actual['bodyType'], 'Round/Apple')
        self.assertEqual(actual['skinTone'], 'skin_tone_95')
        self.assertEqual(actual['height'], profile['measurements']['height'])
        self.assertEqual(actual['weight'], 'Prefer not to say')
        signals = actual['profileSignals']
        self.assertEqual(signals['body_type'], 'apple')
        self.assertEqual(signals['skin_depth_index'], 95)
        self.assertEqual(signals['skin_depth'], 'deep')
        self.assertIsNone(signals['skin_undertone'])
        self.assertIsNone(signals['age'])
        self.assertNotIn('age', actual)
        self.assertEqual(signals['height_range_inches'], {'lower': 68.0, 'upper': 71.0})
        self.assertEqual(signals['height_category'], 'mixed')

    def test_unknown_optional_profile_values_remain_unknown_at_active_endpoint(self):
        response = self.generate(user_profile={'bodyType': 'Prefer not to say', 'skinTone': 'unspecified',
                                                'height': 'unknown', 'age': None})
        self.assertEqual(response.status_code, 200, response.text)
        actual = self.robust.generate_outfit.call_args.args[0].user_profile
        self.assertEqual(actual['bodyType'], 'Prefer not to say')
        self.assertEqual(actual['skinTone'], 'unspecified')
        for key in ('body_type', 'skin_depth', 'skin_undertone', 'height_category', 'age'):
            self.assertIsNone(actual['profileSignals'][key], key)

    def test_configured_and_random_selected_configuration_reach_same_endpoint_unchanged(self):
        # The frontend's separate randomOutfitConfiguration suite proves pool
        # selection; this proves both resulting payloads retain their settings.
        for mode, config in (
            ('configured', {'occasion': 'Casual', 'style': 'Minimalist', 'mood': 'Serene'}),
            ('random-selected', {'occasion': 'Gym', 'style': 'Workout', 'mood': 'Dynamic'}),
        ):
            with self.subTest(mode=mode):
                response = self.generate(**config)
                self.assertEqual(response.status_code, 200, response.text)
                context = self.robust.generate_outfit.call_args.args[0]
                for key, value in config.items():
                    self.assertEqual(getattr(context, key), value)
                    self.assertEqual(response.json()[key], value)
                    self.assertEqual(self.store.writes[-1][key], value)

    def test_required_graphic_is_retained_and_final_notes_acknowledge_the_compromise(self):
        self.use_minimalist_fixture()
        response = self.generate(style='Minimalist', baseItemId='graphic')
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        ids = [item['id'] for item in result['items']]
        self.assertIn('graphic', ids)
        self.assertNotIn('plain', ids)
        note = result['outfitAnalysis']['styleSynergy']['insight'].lower()
        self.assertIn('graphic', note)
        self.assertIn('partial match', note)
        self.assertIn('required', note)
        self.assertEqual(self.store.writes[-1]['outfitAnalysis'], result['outfitAnalysis'])

    def test_fallback_prefers_plain_to_graphic_when_weather_is_equal(self):
        self.use_minimalist_fixture()
        self.robust.generate_outfit.side_effect = RuntimeError('controlled generator failure')
        # Stable input order deliberately puts the graphic first on equal scores.
        with patch('random.uniform', return_value=0):
            response = self.generate(style='Minimalist', weather={'temperature': 72, 'condition': 'Clear', 'source': 'manual'})
        self.assertEqual(response.status_code, 200, response.text)
        ids = {item['id'] for item in response.json()['items']}
        self.assertEqual(ids, {'plain', 'pants', 'shoes'})

    def test_cold_fallback_does_not_trade_warmth_for_a_plain_light_piece(self):
        self.use_minimalist_fixture(cold=True)
        self.robust.generate_outfit.side_effect = RuntimeError('controlled generator failure')
        with patch('random.uniform', return_value=0):
            response = self.generate(style='Minimalist', weather={'temperature': 35, 'condition': 'Cloudy', 'source': 'manual'})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual({item['id'] for item in response.json()['items']}, {'graphic', 'pants', 'shoes'})
        self.assertIn('partial match', response.json()['outfitAnalysis']['styleSynergy']['insight'].lower())

    def test_fallback_required_graphic_stays_required_despite_a_plain_alternative(self):
        self.use_minimalist_fixture()
        self.robust.generate_outfit.side_effect = RuntimeError('controlled generator failure')
        with patch('random.uniform', return_value=0):
            response = self.generate(style='Minimalist', baseItemId='graphic')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual({item['id'] for item in response.json()['items']}, {'graphic', 'pants', 'shoes'})
        self.assertIn('required', response.json()['outfitAnalysis']['styleSynergy']['insight'].lower())

    def test_one_piece_fallback_retains_complete_owned_combination(self):
        self.wardrobe = [admission_tests.garment('dress', 'dress', pattern='solid'),
                         admission_tests.garment('shoes', 'shoes')]
        self.seed(self.wardrobe)
        self.robust.generate_outfit.side_effect = RuntimeError('controlled generator failure')
        response = self.generate(style='Minimalist', baseItemId='dress')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual({item['id'] for item in response.json()['items']}, {'dress', 'shoes'})

    def test_fallback_still_rejects_incomplete_occasion_filtered_combination(self):
        self.store.rows['wardrobe']['shoes']['occasion'] = ['Formal']
        self.robust.generate_outfit.side_effect = RuntimeError('controlled generator failure')
        response = self.generate(style='Minimalist')
        self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.store.writes, [])

    def history_readback(self):
        # Compile the actual history model and HTTP handler to avoid unrelated
        # route initialization. Only the database query adapter is controlled.
        path = Path(__file__).resolve().parents[1] / 'src/routes/outfits/routes.py'
        nodes = [node for node in ast.parse(path.read_text()).body
                 if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef))
                 and node.name in {'OutfitResponse', 'list_outfits_no_slash'}]
        ns = {'BaseModel': BaseModel, 'ConfigDict': ConfigDict, 'datetime': datetime,
              'Any': Any, 'Dict': Dict, 'List': List, 'Optional': Optional,
              'APIRouter': APIRouter, 'router': APIRouter(), 'HTTPException': HTTPException,
              'Depends': Depends, 'UserProfile': SimpleNamespace,
              'get_current_user': lambda: SimpleNamespace(id='owner'),
              'logger': logging.getLogger('fidelity-readback'), 'get_user_outfits': database.get_user_outfits}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), ns)
        app = FastAPI()
        app.include_router(ns['router'], prefix='/api/outfits')
        documents = [self.store.collection('outfits').document(key) for key in self.store.rows['outfits']]
        with patch.object(database, '_get_owned_outfit_documents', return_value=documents):
            with TestClient(app) as client:
                response = client.get('/api/outfits')
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_weather_source_conditions_and_final_notes_survive_saved_history_readback(self):
        weather = {'temperature': 57, 'condition': 'Light rain', 'source': 'manual',
                   'fallback': False, 'location': 'Test location', 'humidity': 80}
        response = self.generate(style='Minimalist', weather=weather)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(vars(self.robust.generate_outfit.call_args.args[0].weather), weather)
        self.assertEqual(response.json()['weather'], weather)
        self.assertEqual(self.store.writes[-1]['weather'], weather)
        history = self.history_readback()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['id'], response.json()['id'])
        self.assertEqual(history[0]['weather'], weather)
        self.assertEqual(history[0]['outfitAnalysis'], response.json()['outfitAnalysis'])

    def test_missing_weather_is_labeled_and_saved_as_the_actual_generation_fallback(self):
        response = self.generate(weather=None)
        self.assertEqual(response.status_code, 200, response.text)
        weather = response.json()['weather']
        self.assertEqual(weather['source'], 'fallback')
        self.assertTrue(weather['fallback'])
        self.assertEqual(vars(self.robust.generate_outfit.call_args.args[0].weather), weather)
        self.assertEqual(self.store.writes[-1]['weather'], weather)
        self.assertEqual(self.history_readback()[0]['weather'], weather)


if __name__ == '__main__':
    unittest.main()
