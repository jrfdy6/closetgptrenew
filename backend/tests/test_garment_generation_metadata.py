"""Saved capture shapes through the same typed context used by generation."""
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from src.custom_types.wardrobe import ClothingItem, ClothingType
from src.utils.garment_metadata import normalize_garment_metadata
from src.utils.outfit_admission import normalize_stored_garment
import test_generation_admission as route_tests


FIXTURES = json.loads((Path(__file__).parent / 'fixtures/garment-generation-metadata.json').read_text())


class GarmentMetadataTests(unittest.TestCase):
    def test_real_saved_shapes_reach_typed_context_without_mutating_analysis(self):
        for fixture in FIXTURES:
            with self.subTest(name=fixture['name']):
                original = copy.deepcopy(fixture['item'])
                prepared = normalize_stored_garment(original, {kind.value for kind in ClothingType})
                model = ClothingItem(**prepared)
                self.assertEqual(model.metadata['visualAttributes'], fixture['expectedVisual'])
                for key, value in fixture['expectedMetadata'].items():
                    self.assertEqual(model.metadata[key], value)
                self.assertEqual(model.analysis, original['analysis'])
                self.assertEqual(original, fixture['item'])
                self.assertEqual(normalize_garment_metadata(prepared), prepared)

    def test_direct_model_conversion_also_preserves_nested_analysis(self):
        # Covers generation_service.py, which constructs ClothingItem directly.
        model = ClothingItem(**FIXTURES[0]['item'])
        self.assertEqual(model.metadata['visualAttributes']['pattern'], 'solid')
        self.assertEqual(model.analysis, FIXTURES[0]['item']['analysis'])

    def test_missing_or_malformed_analysis_does_not_fabricate_attributes(self):
        for value in (None, '', [], 'unavailable'):
            normalized = normalize_garment_metadata({'metadata': {'fileName': 'pending.jpg'}, 'analysis': value})
            self.assertNotIn('visualAttributes', normalized['metadata'])
            self.assertEqual(normalized['analysis'], value)
            model = ClothingItem(id='shirt', name='Pending shirt', type='shirt', color='unknown', season=['all'], **normalized)
            self.assertEqual(model.analysis, value)

    def test_actual_endpoint_uses_saved_analysis_and_corrections_not_request_facts(self):
        harness = route_tests.ActiveGenerationAdmissionTests()
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        stored = {**FIXTURES[1]['item'], 'userId': 'owner', 'imageUrl': 'https://example.test/shirt.jpg'}
        harness.store.rows['wardrobe']['shirt'] = copy.deepcopy(stored)
        # Use the real typed model inside the actual route's robust branch.
        with patch.object(sys.modules['src.custom_types.wardrobe'], 'ClothingItem', ClothingItem):
            harness.wardrobe[0].update({'pattern': 'graphic', 'analysis': {'metadata': {'visualAttributes': {'pattern': 'graphic'}}}})
            response = harness.generate()
        self.assertEqual(response.status_code, 200, response.text)
        context = harness.robust.generate_outfit.await_args.args[0]
        shirt = next(item for item in context.wardrobe if item.id == 'shirt')
        self.assertIsInstance(shirt, ClothingItem)
        self.assertEqual(shirt.metadata['visualAttributes']['pattern'], 'solid')
        self.assertEqual(shirt.metadata['visualAttributes']['fit'], 'unknown')
        self.assertEqual(shirt.metadata['imageHash'], 'photo-hash')
        self.assertEqual(shirt.analysis, stored['analysis'])
        self.assertEqual(harness.store.rows['wardrobe']['shirt'], stored)


if __name__ == '__main__':
    unittest.main()
