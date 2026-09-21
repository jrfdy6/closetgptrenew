"""Credential-free HTTP/datastore regressions for manual saves and favorites."""

import copy
import logging
import sys
import unittest
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.routes.outfits.routes import get_current_user, get_current_user_id, router


class FakeDocument:
    def __init__(self, store, collection, document_id):
        self.store = store
        self.collection = collection
        self.id = document_id

    @property
    def exists(self):
        return self.id in self.store.records.get(self.collection, {})

    def get(self):
        return self

    def to_dict(self):
        return copy.deepcopy(self.store.records.get(self.collection, {}).get(self.id))

    def set(self, data):
        if self.store.fail_writes:
            raise RuntimeError('simulated write failure')
        self.store.records.setdefault(self.collection, {})[self.id] = copy.deepcopy(data)
        self.store.writes.append(('set', self.collection, self.id, copy.deepcopy(data)))

    def update(self, data):
        if self.store.fail_writes:
            raise RuntimeError('simulated write failure')
        self.store.records[self.collection][self.id].update(copy.deepcopy(data))
        self.store.writes.append(('update', self.collection, self.id, copy.deepcopy(data)))


class FakeQuery:
    def __init__(self, store, collection, filters=(), ordering=None, count=None):
        self.store = store
        self.collection = collection
        self.filters = filters
        self.ordering = ordering
        self.count = count

    def document(self, document_id):
        return FakeDocument(self.store, self.collection, document_id)

    def where(self, key, operator, value):
        assert operator == '=='
        return FakeQuery(self.store, self.collection, (*self.filters, (key, value)), self.ordering, self.count)

    def order_by(self, key, direction=None):
        return FakeQuery(self.store, self.collection, self.filters, key, self.count)

    def limit(self, count):
        return FakeQuery(self.store, self.collection, self.filters, self.ordering, count)

    def stream(self):
        # This is a generator: errors happen on iteration like Firestore.
        if self.store.fail_reads:
            raise RuntimeError('simulated read failure')
        if self.ordering and self.store.fail_ordering:
            raise RuntimeError('simulated missing composite index')
        rows = [
            (key, value) for key, value in self.store.records.get(self.collection, {}).items()
            if all(value.get(field) == expected for field, expected in self.filters)
        ]
        if self.ordering:
            rows = [(key, value) for key, value in rows if self.ordering in value]
            rows.sort(key=lambda row: row[1][self.ordering], reverse=True)
        for key, _ in rows[:self.count]:
            yield FakeDocument(self.store, self.collection, key)


class FakeFirestore:
    def __init__(self):
        self.records = {'outfits': {}, 'wardrobe': {}}
        self.writes = []
        self.fail_ordering = False
        self.fail_writes = False
        self.fail_reads = False

    def collection(self, name):
        return FakeQuery(self, name)


class OutfitPersistenceTests(unittest.TestCase):
    def setUp(self):
        previous_logging = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, previous_logging)
        self.store = FakeFirestore()
        self.firebase = ModuleType('src.config.firebase')
        self.firebase.db = self.store
        self.firebase.firebase_initialized = True
        self.modules = patch.dict(sys.modules, {'src.config.firebase': self.firebase})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.app = FastAPI()
        self.app.include_router(router, prefix='/api/outfits')
        self.app.dependency_overrides[get_current_user_id] = lambda: 'owner-1'
        self.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id='owner-1')
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def create(self, item_count=1):
        return self.client.post('/api/outfits/', json={
            'name': f'Manual {item_count}',
            'occasion': 'Casual',
            'style': 'Classic',
            'notes': 'Keep this note',
            'description': 'A manually selected combination',
            'items': [{'id': f'item-{index}', 'name': 'Garment'} for index in range(item_count)],
            # Ownership is derived from authentication, never the request.
            'user_id': 'foreign-owner',
            'userId': 'foreign-owner',
        })

    def seed(self, document_id, **data):
        self.store.records['outfits'][document_id] = {
            'name': document_id,
            'items': [{'id': 'item-1', 'name': 'Shirt'}],
            'createdAt': '2026-09-21T10:00:00Z',
            **data,
        }

    def listed(self, **params):
        response = self.client.get('/api/outfits', params=params)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_one_and_two_item_saves_return_unique_ids_and_survive_listing(self):
        saved = []
        for count in (1, 2):
            response = self.create(count)
            self.assertEqual(response.status_code, 200, response.text)
            body = response.json()
            self.assertEqual(body['id'], body['outfit_id'])
            self.assertEqual(body['user_id'], 'owner-1')
            self.assertEqual(body['userId'], 'owner-1')
            self.assertEqual(len(body['items']), count)
            self.assertEqual(body['notes'], 'Keep this note')
            saved.append(body)

        self.assertNotEqual(saved[0]['id'], saved[1]['id'])
        listed = {outfit['id']: outfit for outfit in self.listed()}
        self.assertEqual(set(listed), {outfit['id'] for outfit in saved})
        for body in saved:
            record = listed[body['id']]
            self.assertEqual(len(record['items']), len(body['items']))
            self.assertEqual(record['notes'], 'Keep this note')
            self.assertEqual(record['description'], 'A manually selected combination')
            self.assertFalse(record['isFavorite'])
            self.assertEqual(record['wearCount'], 0)
            self.assertIsNotNone(record['updatedAt'])

    def test_lists_legacy_records_deduplicates_and_hides_conflicting_owners(self):
        self.seed('legacy', userId='owner-1', favorite=True, notes='Legacy note', wearCount=4)
        self.seed('canonical', user_id='owner-1')
        self.seed('dual', user_id='owner-1', userId='owner-1')
        self.seed('foreign', userId='owner-2')
        self.seed('conflict-a', user_id='owner-2', userId='owner-1')
        self.seed('conflict-b', user_id='owner-1', userId='owner-2')
        self.seed('unowned')

        listed = {outfit['id']: outfit for outfit in self.listed()}
        self.assertEqual(set(listed), {'legacy', 'canonical', 'dual'})
        self.assertEqual(listed['legacy']['user_id'], 'owner-1')
        self.assertTrue(listed['legacy']['isFavorite'])
        self.assertEqual(listed['legacy']['wearCount'], 4)
        self.assertEqual(listed['legacy']['notes'], 'Legacy note')
        self.assertEqual(self.store.writes, [])

    def test_legacy_and_canonical_results_share_sorting_and_pagination(self):
        self.seed('old', user_id='owner-1', createdAt='2026-09-19T10:00:00Z')
        self.seed('middle', userId='owner-1', createdAt='2026-09-20T10:00:00Z')
        self.seed('new', user_id='owner-1', userId='owner-1', createdAt='2026-09-21T10:00:00Z')
        self.assertEqual([row['id'] for row in self.listed(limit=1, offset=1)], ['middle'])

    def test_missing_legacy_index_falls_back_on_iteration_without_losing_saves(self):
        self.store.fail_ordering = True
        self.seed('legacy', userId='owner-1')
        self.seed('canonical', user_id='owner-1')
        self.assertEqual({row['id'] for row in self.listed()}, {'legacy', 'canonical'})

    def test_mixed_legacy_timestamps_remain_readable_and_sort_consistently(self):
        timestamps = [
            '2026-09-19T10:00:00',
            datetime(2026, 9, 20, 10),
            datetime(2026, 9, 21, 10, tzinfo=timezone.utc),
            datetime(2026, 9, 22, 10, tzinfo=timezone.utc).timestamp() * 1000,
        ]
        for index, timestamp in enumerate(timestamps):
            self.seed(str(index), userId='owner-1', createdAt=timestamp, isFavorite=False, favorite=True)
        listed = self.listed()
        self.assertEqual([row['id'] for row in listed], ['3', '2', '1', '0'])
        self.assertTrue(all(row['isFavorite'] is False for row in listed))
        self.assertTrue(all(row['createdAt'].endswith('Z') for row in listed))

    def test_favorite_true_false_and_retries_persist_without_changing_other_fields(self):
        self.seed('legacy', userId='owner-1', favorite=True, notes='Preserve', wearCount=7)
        before = copy.deepcopy(self.store.records['outfits']['legacy'])
        for value in (True, True, False, False):
            response = self.client.put('/api/outfits/legacy/favorite', json={'isFavorite': value})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()['isFavorite'], value)
            self.assertEqual(self.listed()[0]['isFavorite'], value)
            after = self.store.records['outfits']['legacy']
            self.assertEqual({key: after[key] for key in before}, before)
            self.assertEqual(set(self.store.writes[-1][3]), {'isFavorite', 'updatedAt'})

    def test_favorite_rejects_foreign_unowned_and_conflicting_records(self):
        for document_id, owners in {
            'foreign': {'userId': 'owner-2'},
            'unowned': {},
            'conflict-a': {'userId': 'owner-1', 'user_id': 'owner-2'},
            'conflict-b': {'userId': 'owner-2', 'user_id': 'owner-1'},
        }.items():
            self.seed(document_id, **owners)
            response = self.client.put(f'/api/outfits/{document_id}/favorite', json={'isFavorite': True})
            self.assertEqual(response.status_code, 403)
        missing = self.client.put('/api/outfits/missing/favorite', json={'isFavorite': True})
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(self.store.writes, [])

    def test_favorite_requires_an_explicit_boolean_and_authentication(self):
        self.seed('owned', user_id='owner-1')
        for body in ({}, {'isFavorite': 'false'}, {'isFavorite': 1}, {'isFavorite': None}, {'isFavorite': True, 'notes': 'overwrite'}):
            response = self.client.put('/api/outfits/owned/favorite', json=body)
            self.assertEqual(response.status_code, 422, response.text)
        self.app.dependency_overrides[get_current_user_id] = lambda: None
        response = self.client.put('/api/outfits/owned/favorite', json={'isFavorite': True})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.create().status_code, 401)
        self.assertEqual(self.store.writes, [])

    def test_datastore_failures_do_not_report_success(self):
        self.seed('owned', user_id='owner-1')
        self.firebase.firebase_initialized = False
        self.assertEqual(self.create().status_code, 503)
        self.assertEqual(self.client.get('/api/outfits').status_code, 503)
        self.assertEqual(self.client.put('/api/outfits/owned/favorite', json={'isFavorite': True}).status_code, 503)
        self.firebase.firebase_initialized = True
        self.store.fail_writes = True
        self.assertEqual(self.create().status_code, 500)
        self.assertEqual(self.client.put('/api/outfits/owned/favorite', json={'isFavorite': True}).status_code, 500)
        self.assertEqual(self.store.writes, [])

    def test_listing_failures_are_errors_rather_than_an_empty_wardrobe(self):
        self.seed('owned', user_id='owner-1')
        self.store.fail_reads = True
        response = self.client.get('/api/outfits')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Failed to fetch outfits'})
        self.app.dependency_overrides[get_current_user] = lambda: None
        self.assertEqual(self.client.get('/api/outfits').status_code, 401)


if __name__ == '__main__':
    unittest.main()
