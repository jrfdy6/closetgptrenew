"""Wardrobe edit regressions. Fake documents only; never initialize Firebase."""

import ast
from copy import deepcopy
from datetime import datetime
import logging
from pathlib import Path
import time
from types import SimpleNamespace
from unittest.mock import patch
from typing import Any, Dict
import unittest

from fastapi import HTTPException
from src.routes.wardrobe_update_contract import build_wardrobe_update


RICH_ITEM = {
    'id': 'shirt-1', 'userId': 'owner', 'name': 'Striped shirt', 'type': 'Shirt',
    'color': 'Light Gray', 'favorite': False, 'wearCount': 6, 'createdAt': 123,
    'style': ['Classic'], 'season': ['Fall', 'Spring'], 'purchasePrice': 48,
    'material': ['Cotton', 'Linen'],
    'metadata': {
        'naturalDescription': 'A striped cotton and linen shirt',
        'visualAttributes': {
            'material': ['Cotton', 'Linen'], 'fit': 'Slim', 'pattern': 'Striped',
            'temperatureCompatibility': {'minTemp': 50, 'maxTemp': 80},
        },
        'colorHarmony': {'compatibleColors': ['Navy']},
        'imageProcessing': {'backgroundRemovedUrl': '/cutout.png'},
    },
    'analysis': {'confidence': 0.94, 'model': 'original-analyzer'},
}


class FakeDocument:
    id = 'shirt-1'
    exists = True

    def __init__(self, data):
        self.data = deepcopy(data)
        self.writes = []

    def get(self):
        return self

    def to_dict(self):
        return deepcopy(self.data)

    def update(self, updates):
        self.writes.append(deepcopy(updates))
        for path, value in updates.items():
            target = self.data
            *parents, leaf = path.split('.')
            for part in parents:
                target = target.setdefault(part, {})
            target[leaf] = deepcopy(value)


def load_update_route(document, route_name='update_wardrobe_item', overrides=None):
    # Compile the actual route body without importing its unrelated AI/Firebase
    # initialization. This tests auth, persistence, and error mapping entirely offline.
    source = Path(__file__).parents[1] / 'src/routes/wardrobe.py'
    route = next(node for node in ast.parse(source.read_text()).body
                 if isinstance(node, ast.AsyncFunctionDef) and node.name == route_name)
    route.decorator_list = []
    route.args.defaults = []
    namespace = {
        'db': SimpleNamespace(collection=lambda _name: SimpleNamespace(document=lambda _id: document)),
        'build_wardrobe_update': build_wardrobe_update, 'time': time,
        'ANALYTICS_AVAILABLE': False, 'HTTPException': HTTPException,
        'logger': logging.getLogger(__name__), 'Dict': Dict, 'Any': Any,
        'UserProfile': SimpleNamespace, 'datetime': datetime,
    }
    namespace.update(overrides or {})
    exec(compile(ast.Module(body=[route], type_ignores=[]), str(source), 'exec'), namespace)
    return namespace[route_name]


class WardrobeUpdateTests(unittest.IsolatedAsyncioTestCase):
    async def update(self, changes, owner='owner'):
        doc = FakeDocument(RICH_ITEM)
        result = await load_update_route(doc)('shirt-1', changes, SimpleNamespace(id=owner))
        return doc, result

    async def test_name_only_preserves_every_unedited_value_and_nested_metadata(self):
        doc, result = await self.update({'name': 'Oxford shirt'})
        expected = deepcopy(RICH_ITEM)
        expected['name'] = 'Oxford shirt'
        expected['updatedAt'] = doc.data['updatedAt']
        self.assertEqual(doc.data, expected)
        self.assertTrue(result['success'])
        self.assertEqual(set(doc.writes[0]), {'name', 'updatedAt'})

    async def test_nested_edit_preserves_all_metadata_siblings(self):
        doc, _ = await self.update({'metadata': {'visualAttributes': {'fit': 'relaxed'}}})
        expected = deepcopy(RICH_ITEM)
        expected['metadata']['visualAttributes']['fit'] = 'relaxed'
        expected['updatedAt'] = doc.data['updatedAt']
        self.assertEqual(doc.data, expected)
        self.assertEqual(set(doc.writes[0]), {'metadata.visualAttributes.fit', 'updatedAt'})

    async def test_description_clear_preserves_visual_attributes_and_analysis(self):
        doc, _ = await self.update({'metadata': {'naturalDescription': ''}})
        self.assertEqual(doc.data['metadata']['naturalDescription'], '')
        self.assertEqual(doc.data['metadata']['visualAttributes'], RICH_ITEM['metadata']['visualAttributes'])
        self.assertEqual(doc.data['analysis'], RICH_ITEM['analysis'])

    async def test_favorite_does_not_overwrite_metadata_or_wear_history(self):
        doc, _ = await self.update({'favorite': True})
        expected = deepcopy(RICH_ITEM)
        expected.update(favorite=True, updatedAt=doc.data['updatedAt'])
        self.assertEqual(doc.data, expected)

    async def test_zero_price_and_complete_material_selection_persist(self):
        doc, _ = await self.update({'purchasePrice': 0, 'metadata': {'visualAttributes': {'material': 'cotton, linen'}}})
        self.assertEqual(doc.data['purchasePrice'], 0)
        self.assertEqual(doc.data['metadata']['visualAttributes']['material'], 'cotton, linen')
        self.assertEqual(doc.data['metadata']['visualAttributes']['pattern'], 'Striped')

    async def test_worker_metadata_written_after_read_is_not_clobbered(self):
        doc = FakeDocument(RICH_ITEM)
        snapshot = doc.to_dict

        def get_snapshot_then_worker_write():
            result = snapshot()
            doc.data['metadata']['workerResult'] = {'status': 'complete'}
            return result

        doc.to_dict = get_snapshot_then_worker_write
        await load_update_route(doc)('shirt-1', {'metadata': {'visualAttributes': {'fit': 'relaxed'}}}, SimpleNamespace(id='owner'))
        self.assertEqual(doc.data['metadata']['workerResult'], {'status': 'complete'})

    async def test_reload_returns_purchase_price_size_and_legacy_materials(self):
        doc = FakeDocument({**RICH_ITEM, 'purchasePrice': 0, 'size': 'M'})
        query = SimpleNamespace(stream=lambda: [doc])
        fake_db = SimpleNamespace(collection=lambda _name: SimpleNamespace(where=lambda *_args: query))
        firebase = SimpleNamespace(firebase_initialized=True, db=fake_db)
        with patch.dict('sys.modules', {'src.config.firebase': firebase}):
            result = await load_update_route(doc, 'get_wardrobe_items_with_slash')(SimpleNamespace(id='owner'))
        item = result['items'][0]
        self.assertEqual(item['purchasePrice'], 0)
        self.assertEqual(item['size'], 'M')
        self.assertEqual(item['material'], ['Cotton', 'Linen'])
        self.assertEqual(item['metadata'], RICH_ITEM['metadata'])

    async def test_analytics_failure_does_not_turn_successful_save_into_error(self):
        doc = FakeDocument(RICH_ITEM)

        def analytics_failure(_event):
            raise RuntimeError('Analytics offline')

        route = load_update_route(doc, overrides={
            'ANALYTICS_AVAILABLE': True, 'AnalyticsEvent': SimpleNamespace,
            'log_analytics_event': analytics_failure,
        })
        result = await route('shirt-1', {'name': 'Oxford shirt'}, SimpleNamespace(id='owner'))
        self.assertTrue(result['success'])
        self.assertEqual(doc.data['name'], 'Oxford shirt')

    async def test_wrong_owner_cannot_write(self):
        doc = FakeDocument(RICH_ITEM)
        with self.assertRaises(HTTPException) as error:
            await load_update_route(doc)('shirt-1', {'name': 'Changed'}, SimpleNamespace(id='other'))
        self.assertEqual(error.exception.status_code, 403)
        self.assertEqual(doc.writes, [])

    async def test_missing_item_cannot_write(self):
        doc = FakeDocument(RICH_ITEM)
        doc.exists = False
        with self.assertRaises(HTTPException) as error:
            await load_update_route(doc)('shirt-1', {'name': 'Changed'}, SimpleNamespace(id='owner'))
        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(doc.writes, [])

    async def test_rejects_identity_timestamp_and_nested_injection(self):
        for changes in ({'userId': 'other'}, {'id': 'other'}, {'createdAt': 5},
                        {'updatedAt': 5}, {'metadata.visualAttributes.fit': 'regular'},
                        {'metadata': {'userId': 'other'}}, {'favorite': 'false'}):
            with self.subTest(changes=changes):
                doc = FakeDocument(RICH_ITEM)
                with self.assertRaises(HTTPException) as error:
                    await load_update_route(doc)('shirt-1', changes, SimpleNamespace(id='owner'))
                self.assertEqual(error.exception.status_code, 400)
                self.assertEqual(doc.writes, [])

    async def test_empty_nested_patch_is_noop_not_metadata_clear(self):
        doc, result = await self.update({'metadata': {'visualAttributes': {}}})
        self.assertEqual(doc.data, RICH_ITEM)
        self.assertEqual(doc.writes, [])
        self.assertTrue(result['success'])

    def test_invalid_metadata_cannot_delete_the_map(self):
        for value in (None, [], 'invalid'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_wardrobe_update({'metadata': value})


if __name__ == '__main__':
    unittest.main()
