"""Confidence/ID regressions for the active generator without provider or Firebase I/O."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel
from src.routes.outfit_generation_contract import generator_confidence

ROUTE_PATH = Path(__file__).resolve().parents[1] / 'src/routes/existing_data_personalized_outfits.py'


class GeneratorConfidenceTests(unittest.TestCase):
    def test_missing_score_is_unknown_not_a_fabricated_percentage(self):
        for value in (None, {}, SimpleNamespace()):
            with self.subTest(value=value):
                self.assertIsNone(generator_confidence(value))

    def test_actual_zero_and_boundary_one_survive_mapping_and_model_aliases(self):
        for score in (0, 0.0, 1, 1.0, 0.74):
            for key in ('confidence_score', 'confidence'):
                for value in ({key: score}, SimpleNamespace(**{key: score})):
                    with self.subTest(score=score, key=key, value=value):
                        self.assertEqual(generator_confidence(value), float(score))

    def test_canonical_zero_takes_precedence_over_robust_alias(self):
        self.assertEqual(generator_confidence({'confidence_score': 0, 'confidence': 0.85}), 0.0)

    def test_invalid_or_missing_canonical_score_can_use_actual_robust_alias(self):
        for invalid in (None, True, '0.9', float('nan'), float('inf'), 2):
            with self.subTest(invalid=invalid):
                self.assertEqual(generator_confidence({'confidence_score': invalid, 'confidence': 0.63}), 0.63)

    def test_booleans_strings_nonfinite_and_out_of_range_values_are_rejected(self):
        for score in (True, False, '0.85', '', float('nan'), float('inf'), float('-inf'), -0.01, 1.01, 85, 10 ** 1000):
            for key in ('confidence_score', 'confidence'):
                with self.subTest(score=repr(score)[:40], key=key):
                    self.assertIsNone(generator_confidence({key: score}))


class ActiveGenerationResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(ROUTE_PATH.read_text())
        cls.model_node = next(node for node in cls.tree.body if isinstance(node, ast.ClassDef) and node.name == 'OutfitResponse')
        ns = {'BaseModel': BaseModel, 'Dict': Dict, 'List': List, 'Optional': Optional, 'Any': Any}
        exec(compile(ast.Module(body=[cls.model_node], type_ignores=[]), str(ROUTE_PATH), 'exec'), ns)
        cls.response_model = ns['OutfitResponse']
        cls.generator_builders = [node.value for node in ast.walk(cls.tree)
                                  if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                                  and any(isinstance(target, ast.Name) and target.id == 'existing_result' for target in node.targets)]
        cls.response_builder = next(node.value for node in ast.walk(cls.tree)
                                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                                    and any(isinstance(target, ast.Name) and target.id == 'outfit_response' for target in node.targets))

    def env(self, **overrides):
        return {
            'uuid4': uuid4, 'generator_confidence': generator_confidence, 'user_id': 'owner',
            'req': SimpleNamespace(style='Classic', occasion='Casual', mood='Calm', weather={}),
            'outfit_items': [{'id': 'shirt'}], 'outfit_analysis': None,
            'robust_outfit': SimpleNamespace(confidence=0.61), 'base_metadata': {}, 'base_item_contract': {},
            'existing_result': {'id': 'look', 'items': [{'id': 'shirt'}]},
            'preference': SimpleNamespace(total_interactions=0, data_source='test'),
            'time': SimpleNamespace(time=lambda: 1234), 'start_time': 1234, 'requested_base_item_id': None,
            **overrides,
        }

    def evaluate(self, node, **overrides):
        return eval(compile(ast.Expression(node), str(ROUTE_PATH), 'eval'), self.env(**overrides))

    def test_response_serialization_preserves_unknown_and_actual_zero(self):
        for score in (None, 0.0, 0.73):
            with self.subTest(score=score):
                result = self.evaluate(self.response_builder, existing_result={'id': 'look', 'confidence_score': score, 'items': []})
                serialized = self.response_model(**result).model_dump()
                self.assertEqual(serialized['confidence_score'], score)
                self.assertIsNone(serialized['personalization_score'])

    def test_robust_builder_uses_actual_alias_and_fallback_does_not_invent_confidence(self):
        results = [self.evaluate(builder) for builder in self.generator_builders]
        self.assertEqual(len(results), 2)
        by_source = {result['metadata']['generated_by']: result for result in results}
        self.assertEqual(by_source['robust_service_6d_scoring']['confidence_score'], 0.61)
        self.assertIsNone(by_source['existing_data_personalization']['confidence_score'])

    def test_generated_ids_do_not_collide_when_requests_share_a_timestamp(self):
        for builder in self.generator_builders:
            results = [self.evaluate(builder) for _ in range(30)]
            self.assertEqual(len({result['id'] for result in results}), 30)
            self.assertTrue(all(result['id'].startswith('outfit_') for result in results))

    def test_response_retains_saved_id_and_generates_unique_ids_only_when_absent(self):
        self.assertEqual(self.evaluate(self.response_builder)['id'], 'look')
        results = [self.evaluate(self.response_builder, existing_result=None) for _ in range(30)]
        self.assertEqual(len({result['id'] for result in results}), 30)


if __name__ == '__main__':
    unittest.main()
