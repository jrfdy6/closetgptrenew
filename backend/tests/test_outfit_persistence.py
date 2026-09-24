"""Credential-free HTTP/datastore regressions for manual saves and favorites."""

import copy
import functools
import logging
import sys
import unittest
from datetime import datetime, timedelta, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from firebase_admin import firestore
from fastapi.testclient import TestClient

from src.routes.outfits.routes import get_current_user, get_current_user_id, router


def firestore_order(value):
    """Firestore type precedence; integer/double values share numeric ordering."""
    if value is None:
        return (0, 0)
    if isinstance(value, bool):
        return (1, value)
    if isinstance(value, (int, float)):
        return (2, value)
    if isinstance(value, datetime):
        aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return (3, aware.timestamp())
    if isinstance(value, str):
        return (4, value.encode('utf-8'))
    raise AssertionError(f'Unsupported fake Firestore type: {type(value)}')


def firestore_matches(row, field, operator, expected):
    if field not in row:
        return False
    actual = firestore_order(row[field])
    expected = firestore_order(expected)
    # Firestore inequalities are type-bracketed, unlike ordered cursors.
    if actual[0] != expected[0]:
        return False
    return {
        '==': actual == expected,
        '>': actual > expected,
        '>=': actual >= expected,
        '<': actual < expected,
        '<=': actual <= expected,
    }[operator]


class FakeDocument:
    def __init__(self, store, collection, document_id):
        self.store = store
        self.collection = collection
        self.id = document_id

    @property
    def exists(self):
        return self.id in self.store.records.get(self.collection, {})

    def get(self, transaction=None):
        if self.store.fail_reads:
            raise RuntimeError('simulated read failure')
        if transaction is not None and transaction.pending:
            raise AssertionError('Firestore does not allow reads after transactional writes')
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

    def where(self, key=None, operator=None, value=None, *, filter=None):
        if filter is not None:
            key, operator, value = filter.field_path, filter.op_string, filter.value
        return FakeQuery(self.store, self.collection, (*self.filters, (key, operator, value)), self.ordering, self.count)

    def order_by(self, key, direction=None):
        return FakeQuery(self.store, self.collection, self.filters, key, self.count)

    def limit(self, count):
        return FakeQuery(self.store, self.collection, self.filters, self.ordering, count)

    def stream(self, transaction=None):
        if transaction is not None and transaction.pending:
            raise AssertionError('Firestore does not allow reads after transactional writes')
        # This is a generator: errors happen on iteration like Firestore.
        if self.store.fail_reads:
            raise RuntimeError('simulated read failure')
        self.store.queries.append(self)
        if self.ordering and (self.store.fail_ordering or any(
            field in self.store.fail_ordering_fields for field, _, _ in self.filters
        )):
            raise RuntimeError('simulated missing composite index')
        rows = [
            (key, value) for key, value in self.store.records.get(self.collection, {}).items()
            if all(firestore_matches(value, field, operator, expected)
                   for field, operator, expected in self.filters)
        ]
        if self.ordering:
            rows = [(key, value) for key, value in rows if self.ordering in value]
            rows.sort(key=lambda row: (firestore_order(row[1][self.ordering]), row[0]), reverse=True)
        else:
            rows.sort(key=lambda row: row[0])
        for key, _ in rows[:self.count]:
            self.store.reads.append((self.collection, key))
            yield FakeDocument(self.store, self.collection, key)


class FakeTransaction:
    def __init__(self, store):
        self.store = store
        self.pending = []

    def set(self, reference, data):
        self.pending.append(('set', reference, copy.deepcopy(data)))

    def update(self, reference, data):
        self.pending.append(('update', reference, copy.deepcopy(data)))

    def commit(self):
        # Fail before applying buffered mutations, like an uncommitted write.
        if self.pending and self.store.fail_writes:
            raise RuntimeError('simulated transaction commit failure')
        for method, reference, data in self.pending:
            getattr(reference, method)(data)
        self.pending.clear()


def transactional(function):
    @functools.wraps(function)
    def run(transaction):
        result = function(transaction)
        transaction.commit()
        return result
    return run


class FakeFirestore:
    def __init__(self):
        self.records = {
            'outfits': {},
            'users': {'owner-1': {'app_data_epoch': 0}},
            'onboarding_states': {'owner-1': {'milestones': {'capsuleCompletedAt': '2026-09-21T10:00:00Z'}}},
            'wardrobe': {f'item-{index}': {'userId': 'owner-1', 'name': f'Saved garment {index}',
                'type': kind, 'imageUrl': f'https://example.test/original-{index}.jpg'}
                for index, kind in enumerate(('shirt', 'pants'))},
        }
        self.writes = []
        self.reads = []
        self.queries = []
        self.fail_ordering = False
        self.fail_ordering_fields = set()
        self.fail_writes = False
        self.fail_reads = False

    def collection(self, name):
        return FakeQuery(self, name)

    def transaction(self):
        return FakeTransaction(self)


class OutfitPersistenceTests(unittest.TestCase):
    def setUp(self):
        previous_logging = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, previous_logging)
        self.store = FakeFirestore()
        transactions = patch.object(firestore, 'transactional', transactional)
        transactions.start()
        self.addCleanup(transactions.stop)
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

    def create(self, item_count=1, **overrides):
        return self.client.post('/api/outfits/', json={
            'name': f'Manual {item_count}',
            'occasion': 'Casual',
            'style': 'Classic',
            'notes': 'Keep this note',
            'description': 'A manually selected combination',
            'items': [{'id': f'item-{index}', 'name': 'Garment'} for index in range(item_count)],
            **overrides,
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

    def test_manual_save_rejects_owner_assertions_before_writing(self):
        for field in ('user_id', 'userId'):
            with self.subTest(field=field):
                response = self.create(**{field: 'foreign-owner'})
                self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.store.writes, [])
        self.assertEqual(self.store.records['outfits'], {})

    def test_manual_browser_default_payload_saves_with_server_owned_identity(self):
        # The create form defaults untouched occasion/style selectors to these
        # values. Its service sends only editable fields and garment IDs.
        payload = {
            'name': 'QA One Piece Selection',
            'occasion': 'Casual',
            'style': 'Classic',
            'items': [{'id': 'item-0'}],
        }
        # Reproduce the original browser failure even with a matching UID:
        # identity belongs to authentication, not the create request schema.
        rejected = self.client.post('/api/outfits/', json={**payload, 'user_id': 'owner-1'})
        self.assertEqual(rejected.status_code, 422, rejected.text)
        self.assertEqual(rejected.json()['detail'][0]['loc'], ['body', 'user_id'])
        self.assertEqual(self.store.writes, [])

        response = self.client.post('/api/outfits/', json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        saved = response.json()
        self.assertTrue(saved['success'])
        self.assertEqual(saved['name'], payload['name'])
        self.assertEqual((saved['occasion'], saved['style']), ('Casual', 'Classic'))
        self.assertEqual(saved['user_id'], 'owner-1')
        self.assertEqual(saved['userId'], 'owner-1')
        self.assertEqual(len(saved['items']), 1)
        self.assertEqual(saved['items'][0]['id'], 'item-0')
        self.assertEqual(saved['items'][0]['name'], 'Saved garment 0')
        self.assertEqual(saved['items'][0]['imageUrl'], 'https://example.test/original-0.jpg')
        self.assertEqual(self.store.records['outfits'][saved['id']]['user_id'], 'owner-1')

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

    def test_firestore_fake_models_type_order_and_type_bracketed_ranges(self):
        instant = datetime(2026, 9, 21, tzinfo=timezone.utc)
        for key, value in [('number', instant.timestamp()), ('date', instant), ('iso', instant.isoformat())]:
            self.seed(key, user_id='owner-1', createdAt=value)
        query = self.store.collection('outfits').where('user_id', '==', 'owner-1')
        self.assertEqual([doc.id for doc in query.order_by('createdAt').stream()], ['iso', 'date', 'number'])
        self.assertEqual([doc.id for doc in query.where('createdAt', '>=', '').stream()], ['iso'])
        self.assertEqual([doc.id for doc in query.where('createdAt', '>=', datetime.min.replace(tzinfo=timezone.utc)).stream()], ['date'])
        self.assertEqual([doc.id for doc in query.where('createdAt', '<=', 1e12).stream()], ['number'])

    def test_fresh_generated_milliseconds_survive_more_than_100_older_strings_and_dates(self):
        now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
        for index in range(130):
            old = now - timedelta(days=1, minutes=index)
            self.seed(f'iso-{index:03}', user_id='owner-1', createdAt=old.isoformat())
            self.seed(f'date-{index:03}', user_id='owner-1', createdAt=old)
        self.seed('fresh-generated', user_id='owner-1', createdAt=now.timestamp() * 1000)
        # The real Firestore comparator reproduces the former omission.
        old_page = self.store.collection('outfits').where('user_id', '==', 'owner-1').order_by('createdAt').limit(100)
        self.assertNotIn('fresh-generated', [doc.id for doc in old_page.stream()])
        self.store.reads.clear()
        listed = self.listed(limit=50)
        self.assertEqual(len(listed), 50)
        self.assertEqual(listed[0]['id'], 'fresh-generated')
        self.assertLessEqual(sum(collection == 'outfits' for collection, _ in self.store.reads), 2910)
        self.assertEqual(self.store.writes, [])

    def test_seconds_are_not_hidden_by_older_milliseconds(self):
        now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
        for index in range(130):
            self.seed(f'old-{index:03}', user_id='owner-1', createdAt=(now - timedelta(days=1, minutes=index)).timestamp() * 1000)
        self.seed('new-seconds', user_id='owner-1', createdAt=now.timestamp())
        self.assertEqual(self.listed(limit=50)[0]['id'], 'new-seconds')

    def test_mixed_pagination_has_no_skips_or_duplicates_including_tied_times(self):
        now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
        expected = []
        for index in range(120):
            instant = now - timedelta(minutes=index // 4)
            value = [instant.isoformat(), instant, instant.timestamp(), instant.timestamp() * 1000][index % 4]
            document_id = f'outfit-{index:03}'
            owners = [{'user_id': 'owner-1'}, {'userId': 'owner-1'}, {'user_id': 'owner-1', 'userId': 'owner-1'}][index % 3]
            self.seed(document_id, **owners, createdAt=value)
            expected.append((int(instant.timestamp() * 1000), document_id))
        expected = [document_id for _, document_id in sorted(expected, reverse=True)]
        actual = [row['id'] for offset in range(0, 120, 20) for row in self.listed(limit=20, offset=offset)]
        self.assertEqual(actual, expected)
        self.assertEqual(len(set(actual)), 120)

    def test_missing_legacy_index_uses_complete_owner_set_and_global_sort(self):
        self.store.fail_ordering_fields = {'userId'}
        self.seed('canonical', user_id='owner-1', createdAt='2026-09-19T10:00:00Z')
        self.seed('legacy-latest', userId='owner-1', createdAt='2026-09-21T10:00:00Z')
        self.assertEqual([row['id'] for row in self.listed(limit=1)], ['legacy-latest'])
        self.assertEqual(self.store.writes, [])

    def test_missing_index_never_returns_an_incomplete_unordered_sample(self):
        self.store.fail_ordering = True
        for index in range(251):
            self.seed(f'old-{index:03}', user_id='owner-1', createdAt='2026-09-19T10:00:00Z')
        self.seed('zzz-newest', user_id='owner-1', createdAt='2026-09-21T10:00:00Z')
        response = self.client.get('/api/outfits', params={'limit': 50})
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(len(self.store.reads), 251)
        self.assertEqual(self.store.writes, [])

    def test_conflicting_owner_saturation_fails_instead_of_hiding_owned_rows(self):
        for index in range(301):
            self.seed(f'conflict-{index:03}', user_id='owner-1', userId='owner-2', createdAt='2026-09-21T10:00:00Z')
        self.seed('owned', user_id='owner-1', createdAt='2026-09-19T10:00:00Z')
        response = self.client.get('/api/outfits', params={'limit': 1})
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(len(self.store.reads), 301)

    def test_iso_fraction_variants_are_normalized_before_pagination(self):
        # Z sorts after '.', although the fractional timestamp is newer.
        for index in range(130):
            self.seed(f'old-{index:03}', user_id='owner-1', createdAt='2026-09-21T10:00:00Z')
        self.seed('fraction-latest', user_id='owner-1', createdAt='2026-09-21T10:00:00.999Z')
        self.assertEqual(self.listed(limit=1)[0]['id'], 'fraction-latest')

    def test_uncertifiable_iso_boundary_fails_with_bounded_reads(self):
        for index in range(301):
            self.seed(f'old-{index:03}', user_id='owner-1', createdAt='2026-09-21T10:00:00Z')
        self.seed('fraction-latest', user_id='owner-1', createdAt='2026-09-21T10:00:00.999Z')
        response = self.client.get('/api/outfits', params={'limit': 1})
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(len(self.store.reads), 301)

    def test_large_chronologically_ordered_cohorts_remain_bounded(self):
        now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
        for index in range(400):
            self.seed(f'outfit-{index:03}', user_id='owner-1', createdAt=(now - timedelta(hours=index)).isoformat())
        self.assertEqual([row['id'] for row in self.listed(limit=50, offset=200)], [f'outfit-{index:03}' for index in range(200, 250)])
        self.assertEqual(sum(collection == 'outfits' for collection, _ in self.store.reads), 301)

    def test_unseen_negative_offset_cannot_hide_behind_a_full_utc_prefix(self):
        now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
        for index in range(301):
            self.seed(f'utc-{index:03}', user_id='owner-1', createdAt=(now - timedelta(minutes=index)).isoformat())
        # Raw 06:59 sorts below the last UTC row at07:00, but means18:59UTC.
        self.seed('actually-newest', user_id='owner-1', createdAt='2026-09-21T06:59:00-12:00')
        response = self.client.get('/api/outfits', params={'limit': 1})
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(len(self.store.reads), 301)

    def test_dense_saturated_iso_history_fails_without_a_certifiable_utc_boundary(self):
        now = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)
        for index in range(400):
            self.seed(f'outfit-{index:03}', user_id='owner-1', createdAt=(now - timedelta(minutes=index)).isoformat())
        response = self.client.get('/api/outfits', params={'limit': 50})
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(len(self.store.reads), 301)

    def test_invalid_pagination_is_rejected_before_any_reads(self):
        for params in ({'limit': 0}, {'limit': -1}, {'offset': -1}, {'limit': 50, 'offset': 201}):
            response = self.client.get('/api/outfits', params=params)
            self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.store.reads, [])
        self.assertEqual(self.store.queries, [])

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

    def test_library_excludes_every_soft_delete_alias_before_pagination(self):
        self.seed('active', user_id='owner-1')
        for index, field in enumerate(('deleted', 'isDeleted', 'deletedAt', 'deleted_at')):
            self.seed(f'deleted-{index}', user_id='owner-1', **{field: True})
        self.assertEqual([outfit['id'] for outfit in self.listed()], ['active'])
        self.assertEqual(len(self.store.records['outfits']), 5)

    def test_favorite_respects_soft_delete_and_pending_app_data_clear(self):
        self.seed('deleted', user_id='owner-1', deleted=True)
        self.assertEqual(self.client.put('/api/outfits/deleted/favorite', json={'isFavorite': True}).status_code, 404)
        self.seed('active', user_id='owner-1')
        self.store.records['users']['owner-1']['app_data_deletion'] = {'status': 'running', 'epoch': 0}
        response = self.client.put('/api/outfits/active/favorite', json={'isFavorite': True})
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(self.store.writes, [])

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
