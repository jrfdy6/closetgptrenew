"""No-cloud regressions for legacy string-ID outfit item resolution."""
import ast
import copy
import sys
import unittest
import urllib.parse
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List
from unittest.mock import Mock, patch


DATABASE_SOURCE = Path(__file__).resolve().parents[1] / 'src/routes/outfits/database.py'


def load_item_resolver():
    """Run the real resolver/helpers without importing application/cloud setup."""
    names = {'resolve_item_ids_to_objects', 'outfit_belongs_to_user', 'convert_firebase_url'}
    definitions = [node for node in ast.parse(DATABASE_SOURCE.read_text()).body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    if {node.name for node in definitions} != names:
        raise AssertionError('The active outfit resolver or its ownership helper moved')
    namespace = {
        '__name__': 'src.routes.outfits.database', '__package__': 'src.routes.outfits',
        'Any': Any, 'Dict': Dict, 'List': List, 'urllib': urllib, 'logger': Mock(),
    }
    exec(compile(ast.Module(body=definitions, type_ignores=[]), str(DATABASE_SOURCE), 'exec'), namespace)
    return namespace['resolve_item_ids_to_objects']


class FakeDocument:
    def __init__(self, store, item_id):
        self.store, self.id = store, item_id

    def get(self):
        self.store.reads.append(self.id)
        return self

    @property
    def exists(self):
        return self.id in self.store.items

    def to_dict(self):
        return copy.deepcopy(self.store.items.get(self.id))


class FakeWardrobe:
    def __init__(self):
        self.items = {}
        self.reads = []

    def collection(self, name):
        if name != 'wardrobe':
            raise AssertionError(f'Unexpected datastore collection: {name}')
        return self

    def document(self, item_id):
        return FakeDocument(self, item_id)


class SavedOutfitItemOwnershipTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.resolve = load_item_resolver()
        self.store = FakeWardrobe()
        firebase = ModuleType('src.config.firebase')
        firebase.db, firebase.firebase_initialized = self.store, True
        modules = patch.dict(sys.modules, {'src.config.firebase': firebase})
        modules.start()
        self.addCleanup(modules.stop)

    async def test_owned_fetched_items_resolve_for_both_historical_owner_spellings(self):
        for ownership in ({'user_id': 'owner'}, {'userId': 'owner'}, {'user_id': 'owner', 'userId': 'owner'}):
            with self.subTest(ownership=ownership):
                self.store.items = {'shirt': {**ownership, 'id': 'stale-id', 'name': 'My shirt',
                                              'imageUrl': 'gs://test-bucket/wardrobe/owner/shirt.jpg'}}
                before = copy.deepcopy(self.store.items)
                resolved = await self.resolve(['shirt'], 'owner')
                self.assertEqual(len(resolved), 1)
                self.assertEqual(resolved[0]['id'], 'shirt')
                self.assertEqual(resolved[0]['name'], 'My shirt')
                self.assertEqual(resolved[0]['imageUrl'],
                                 'https://firebasestorage.googleapis.com/v0/b/test-bucket/o/wardrobe%2Fowner%2Fshirt.jpg?alt=media')
                self.assertEqual(self.store.items, before)

    async def test_owned_cached_items_resolve_without_fetching_or_mutating_cache(self):
        for ownership in ({'user_id': 'owner'}, {'userId': 'owner'}, {'user_id': 'owner', 'userId': 'owner'}):
            with self.subTest(ownership=ownership):
                cache = {'shirt': {**ownership, 'id': 'shirt', 'name': 'My shirt',
                                    'image_url': 'https://images.invalid/owner-shirt.jpg'}}
                before = copy.deepcopy(cache)
                resolved = await self.resolve(['shirt'], 'owner', cache)
                self.assertEqual([item['id'] for item in resolved], ['shirt'])
                self.assertEqual(resolved[0]['imageUrl'], 'https://images.invalid/owner-shirt.jpg')
                self.assertEqual(self.store.reads, [])
                self.assertEqual(cache, before)

    async def test_foreign_conflicting_and_unowned_fetched_items_are_excluded(self):
        invalid_owners = (
            {'user_id': 'other'}, {'userId': 'other'},
            {'user_id': 'owner', 'userId': 'other'}, {'user_id': 'other', 'userId': 'owner'},
            {'user_id': 'owner', 'userId': ''}, {},
        )
        for ownership in invalid_owners:
            with self.subTest(ownership=ownership):
                self.store.items = {
                    'foreign': {**ownership, 'name': 'Private garment', 'imageUrl': 'https://images.invalid/private.jpg'},
                    'owned': {'userId': 'owner', 'name': 'My shoes', 'imageUrl': 'https://images.invalid/my-shoes.jpg'},
                }
                resolved = await self.resolve(['foreign', 'owned'], 'owner')
                self.assertEqual([item['id'] for item in resolved], ['owned'])
                self.assertNotIn('Private garment', str(resolved))
                self.assertNotIn('private.jpg', str(resolved))

    async def test_foreign_conflicting_and_unowned_cached_items_are_excluded_without_fallback_fetch(self):
        invalid_owners = (
            {'user_id': 'other'}, {'userId': 'other'},
            {'user_id': 'owner', 'userId': 'other'}, {'user_id': 'other', 'userId': 'owner'},
            {'user_id': 'owner', 'userId': ''}, {},
        )
        for ownership in invalid_owners:
            with self.subTest(ownership=ownership):
                cache = {'foreign': {**ownership, 'id': 'foreign', 'name': 'Private garment',
                                      'imageUrl': 'https://images.invalid/private.jpg'}}
                # A rejected cache entry cannot accidentally fall through to
                # an unguarded fetch and reveal either cached or stored content.
                self.store.items = {'foreign': {'userId': 'other', 'name': 'Stored private garment'}}
                resolved = await self.resolve(['foreign'], 'owner', cache)
                self.assertEqual(resolved, [])
                self.assertEqual(self.store.reads, [])


if __name__ == '__main__':
    unittest.main()
