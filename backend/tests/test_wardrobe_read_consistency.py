"""Real read handlers share owned legacy records; storage is the only fake."""
import ast
import copy
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path
import time
from types import SimpleNamespace
from typing import Any, Dict, Optional
import unittest
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from src.auth.verified_identity import verified_identity, reject_identity_overrides
from src.services.wardrobe_reads import OWNER_FIELDS
from test_wear_statistics import Store, Query
from test_wardrobe_update_contract import RICH_ITEM


class ReadQuery(Query):
    def document(self, identifier):
        row = self.db.rows.get(self.collection, {}).get(identifier)
        return SimpleNamespace(get=lambda: SimpleNamespace(exists=row is not None,
            id=identifier, to_dict=lambda: copy.deepcopy(row)))
    def where(self, *, filter):
        return ReadQuery(self.db, self.collection, (filter.field_path, filter.value))


class ReadStore(Store):
    def collection(self, name):
        return ReadQuery(self, name)
    def get_all(self, references):
        return [reference.get() for reference in references]


def wardrobe_reads_app(db):
    source = Path(__file__).parents[1] / 'src/routes/wardrobe.py'
    names = {'verified_wardrobe_user', '_owned_wardrobe_item', 'get_wardrobe_items_with_slash',
             'get_wardrobe_item', 'get_top_worn_items', 'get_most_worn_by_category',
             'get_trending_styles', 'count_wardrobe_items'}
    nodes = [node for node in ast.parse(source.read_text()).body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    namespace = {'router': APIRouter(), 'Depends': Depends, 'Request': Request,
                 'HTTPException': HTTPException, 'SimpleNamespace': SimpleNamespace,
                 'UserProfile': SimpleNamespace, 'Dict': Dict, 'Any': Any, 'Optional': Optional,
                 'verified_identity': verified_identity, 'reject_identity_overrides': reject_identity_overrides,
                 'logger': logging.getLogger(__name__), 'time': time, 'datetime': datetime,
                 'db': db, 'FIREBASE_AVAILABLE': True, 'ANALYTICS_AVAILABLE': False,
                 'safe_get': lambda value, key, default=None: value.get(key, default)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
    app = FastAPI(); app.include_router(namespace['router'], prefix='/api/wardrobe')
    return app


class WardrobeReadConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.db = ReadStore()
        self.db.rows['wardrobe'] = {}
        for index, alias in enumerate(OWNER_FIELDS):
            row = {**RICH_ITEM, 'id': 'forged-snapshot-id', 'name': alias, 'wearCount': index + 1,
                   'type': 'shirt', 'lastWorn': None, 'imageUrl': f'https://original.test/{alias}'}
            row.pop('userId', None); row[alias] = 'owner'
            self.db.rows['wardrobe'][f'item-{index}'] = row
        self.db.rows['wardrobe'].update({
            'dual': {**RICH_ITEM, 'userId': 'owner', 'user_id': 'owner', 'imageUrl': 'https://original.test/dual'},
            'foreign': {**RICH_ITEM, 'userId': 'other', 'wearCount': 100},
            'conflict': {**RICH_ITEM, 'userId': 'owner', 'user_id': 'other', 'wearCount': 100},
            'deleted': {**RICH_ITEM, 'deleted_at': '2026-09-20', 'wearCount': 100},
        })
        self.expected = {f'item-{index}' for index in range(5)} | {'dual'}
        modules = patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=self.db, firebase_initialized=True)})
        modules.start(); self.addCleanup(modules.stop)
        verifier = patch('src.auth.verified_user.auth.verify_id_token', return_value={'uid': 'owner'})
        self.verify = verifier.start(); self.addCleanup(verifier.stop)
        self.client = TestClient(wardrobe_reads_app(self.db)); self.addCleanup(self.client.close)
        self.headers = {'Authorization': 'Bearer valid-token'}

    def read(self, path):
        response = self.client.get('/api/wardrobe' + path, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_library_count_and_insights_union_deduplicate_and_filter_the_same_items(self):
        before = copy.deepcopy(self.db.rows)
        library = self.read('/')
        self.assertEqual({row['id'] for row in library['items']}, self.expected)
        self.assertEqual(library['count'], 6)
        self.assertEqual(self.read('/count')['total_items'], 6)
        top = self.read('/top-worn-items')['data']
        self.assertEqual(top['total_items'], 6)
        self.assertEqual({row['id'] for row in top['top_worn_items']}, self.expected)
        self.assertEqual(top['total_wear_count'], 21)
        self.assertEqual(self.read('/most-worn-by-category')['data']['total_items'], 6)
        trends = self.read('/trending-styles')['data']
        self.assertEqual(trends['total_items_analyzed'], 6)
        self.assertEqual({row['id'] for row in trends['trending_items']}, self.expected)
        self.assertEqual(self.db.rows, before)

    def test_count_and_all_readers_require_real_auth_before_any_queries(self):
        for path in ('/', '/count', '/top-worn-items', '/most-worn-by-category', '/trending-styles'):
            self.assertEqual(self.client.get('/api/wardrobe' + path).status_code, 401)
        self.assertEqual(self.db.queries, [])
        self.verify.assert_not_called()

    def test_one_alias_query_failure_is_not_reported_as_partial_or_empty_success(self):
        original = ReadQuery.stream
        def fail_one(query):
            if query.predicate and query.predicate[0] == 'uid':
                raise RuntimeError('alias query unavailable')
            return original(query)
        with patch.object(ReadQuery, 'stream', fail_one):
            for path in ('/', '/count', '/top-worn-items', '/most-worn-by-category', '/trending-styles'):
                response = self.client.get('/api/wardrobe' + path, headers=self.headers)
                self.assertIn(response.status_code, (500, 503), response.text)
                self.assertIsNot(response.json().get('success'), True)

    def test_owned_detail_rejects_soft_deleted_or_conflicting_owners(self):
        self.assertEqual(self.client.get('/api/wardrobe/deleted', headers=self.headers).status_code, 404)
        self.assertEqual(self.client.get('/api/wardrobe/conflict', headers=self.headers).status_code, 403)

    def test_recent_wear_and_trends_handle_milliseconds_without_treating_old_or_future_wears_as_recent(self):
        now = datetime.now(timezone.utc)
        rows = self.db.rows['wardrobe']
        rows['item-0']['lastWorn'] = int(now.timestamp() * 1000)
        rows['item-1']['lastWorn'] = int((now - timedelta(days=60)).timestamp() * 1000)
        rows['item-2']['lastWorn'] = now - timedelta(days=1)
        rows['item-3']['lastWorn'] = int((now + timedelta(days=60)).timestamp() * 1000)
        self.assertEqual(self.read('/top-worn-items')['data']['recently_worn_count'], 2)
        trends = {item['id']: item for item in self.read('/trending-styles')['data']['trending_items']}
        self.assertEqual(trends['item-0']['trending_score'], rows['item-0']['wearCount'] + 2)
        self.assertEqual(trends['item-1']['trending_score'], rows['item-1']['wearCount'])
        self.assertEqual(trends['item-2']['trending_score'], rows['item-2']['wearCount'] + 2)
        self.assertEqual(trends['item-3']['trending_score'], rows['item-3']['wearCount'])

    def test_generation_uses_owned_legacy_sources_without_rewriting_or_trusting_client_aliases(self):
        from src.utils.outfit_admission import load_owned_wardrobe, InvalidGeneratedOutfit
        rows = self.db.rows['wardrobe']
        rows['item-2']['type'] = 'shirt'
        rows['item-3']['type'] = 'pants'
        rows['item-4']['type'] = 'shoes'
        before = copy.deepcopy(rows)
        items = load_owned_wardrobe(self.db, [
            {'id': f'item-{index}', 'userId': 'forged', 'imageUrl': 'https://forged.test'} for index in (2, 3, 4)], 'owner')
        self.assertTrue(all(item['userId'] == 'owner' for item in items))
        self.assertTrue(all(item['imageUrl'].startswith('https://original.test/') for item in items))
        self.assertEqual(rows, before)
        rows['item-2']['userId'] = 'other'
        with self.assertRaises(InvalidGeneratedOutfit):
            load_owned_wardrobe(self.db, [{'id': f'item-{index}'} for index in (2, 3, 4)], 'owner')
