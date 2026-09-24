"""Portable coverage for deployed query indexes; no Firebase or credentials."""
import json
from pathlib import Path
import unittest

BACKEND = Path(__file__).resolve().parents[1]


def signature(index):
    return (
        index['collectionGroup'],
        index.get('queryScope', 'COLLECTION'),
        tuple((field['fieldPath'], field.get('order', field.get('arrayConfig')))
              for field in index['fields']),
    )


def collection_index(name, *fields):
    return name, 'COLLECTION', tuple(fields)


class FirestoreIndexManifestTests(unittest.TestCase):
    def setUp(self):
        config = json.loads((BACKEND / 'firebase.json').read_text())
        self.manifest_path = BACKEND / config['firestore']['indexes']
        self.manifest = json.loads(self.manifest_path.read_text())
        self.indexes = {signature(index) for index in self.manifest['indexes']}

    def test_backend_config_resolves_canonical_manifest(self):
        self.assertEqual(self.manifest_path.resolve(),
                         (BACKEND / 'firestore.indexes.json').resolve())
        self.assertIn('fieldOverrides', self.manifest)

    def test_gamification_and_history_query_indexes(self):
        # Oldest-first AI-fit recency and newest-first history need distinct
        # indexes: a descending date index cannot serve the ascending query.
        required = {
            collection_index('outfit_history', ('user_id', 'ASCENDING'),
                             ('date_worn', 'ASCENDING')),
            collection_index('outfit_history', ('user_id', 'ASCENDING'),
                             ('date_worn', 'DESCENDING')),
            collection_index('outfit_history', ('user_id', 'ASCENDING'),
                             ('item_ids', 'CONTAINS'), ('date_worn', 'DESCENDING')),
            collection_index('outfit_history', ('user_id', 'ASCENDING'),
                             ('outfit_id', 'ASCENDING'), ('date_worn', 'DESCENDING')),
            collection_index('wear_projection_jobs', ('status', 'ASCENDING'),
                             ('available_at', 'ASCENDING')),
            collection_index('gamification_user_jobs', ('status', 'ASCENDING'),
                             ('available_at', 'ASCENDING')),
        }
        self.assertTrue(required <= self.indexes,
                        f'Missing query indexes: {required - self.indexes}')

    def test_preserves_preexisting_production_query_variants(self):
        # These were already deployed but missing from the old manifest. Keep
        # them so an index reconciliation cannot propose removing live queries.
        preserved = {
            collection_index('outfit_history', ('userId', 'ASCENDING'),
                             ('createdAt', 'DESCENDING')),
            collection_index('feedback', ('outfit_id', 'ASCENDING'),
                             ('created_at', 'DESCENDING')),
            collection_index('feedback', ('user_id', 'ASCENDING'),
                             ('created_at', 'DESCENDING')),
            collection_index('wardrobe', ('userId', 'ASCENDING'),
                             ('favorite', 'DESCENDING')),
            collection_index('outfits', ('user_id', 'ASCENDING'),
                             ('createdAt', 'DESCENDING')),
        }
        self.assertTrue(preserved <= self.indexes,
                        f'Previously deployed indexes missing: {preserved - self.indexes}')

    def test_no_duplicate_or_invalid_index_descriptors(self):
        self.assertEqual(len(self.indexes), len(self.manifest['indexes']))
        for index in self.manifest['indexes']:
            with self.subTest(collection=index['collectionGroup']):
                self.assertIn(index['queryScope'], {'COLLECTION', 'COLLECTION_GROUP'})
                fields = index['fields']
                self.assertEqual(len({f['fieldPath'] for f in fields}), len(fields))
                for field in fields:
                    self.assertEqual(('order' in field) + ('arrayConfig' in field), 1)
                    self.assertIn(field.get('order', field.get('arrayConfig')),
                                  {'ASCENDING', 'DESCENDING', 'CONTAINS'})


if __name__ == '__main__':
    unittest.main()
