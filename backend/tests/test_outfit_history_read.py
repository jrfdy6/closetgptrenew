"""Actual route and Firestore query encoding against synthetic rows; no cloud I/O."""
import ast
import copy
from datetime import datetime, timedelta, timezone
import logging
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Optional
import sys
import time
import unittest
from unittest.mock import patch, PropertyMock

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.testclient import TestClient
from google.auth.credentials import AnonymousCredentials
from google.cloud import firestore
from google.cloud.firestore_v1 import _helpers

UTC = timezone.utc
NOW = datetime(2026, 9, 27, 12, tzinfo=UTC)


class HistoryReadTests(unittest.TestCase):
    def setUp(self):
        # Execute the actual route without importing app/auth/provider startup.
        # The installed SDK encodes the real snapshot cursor and query below.
        source = Path(__file__).resolve().parents[1] / 'src/routes/outfit_history.py'
        handler = next(node for node in ast.parse(source.read_text()).body
                       if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'get_outfit_history')
        self.db = firestore.Client(project='synthetic-history', credentials=AnonymousCredentials())
        self.rows, self.queries = {}, []
        self.after_page = self.fail_page = None
        namespace = {
            '__name__': 'src.routes.history_read_test', '__package__': 'src.routes',
            'router': APIRouter(), 'Optional': Optional, 'Query': Query, 'Depends': Depends,
            'UserProfile': object, 'get_current_user': lambda: SimpleNamespace(id='owner'),
            'get_db': lambda: self.db, 'datetime': datetime, 'timedelta': timedelta,
            'timezone': timezone, 'HTTPException': HTTPException,
            'logger': logging.getLogger('history-read-test'),
        }
        exec(compile(ast.Module(body=[handler], type_ignores=[]), str(source), 'exec'), namespace)
        fake_firebase = ModuleType('src.config.firebase')
        fake_firebase.db = self.db
        for guard in (
            patch.dict(sys.modules, {'src.config.firebase': fake_firebase}),
            patch('google.auth.default', side_effect=AssertionError('No credential discovery')),
            patch('socket.socket.connect', side_effect=AssertionError('No network')),
            patch.object(firestore.Client, '_firestore_api', new_callable=PropertyMock,
                         side_effect=AssertionError('No Firestore RPC')),
            patch.object(firestore.Query, 'stream', autospec=True, side_effect=self.stream),
        ):
            guard.start()
            self.addCleanup(guard.stop)
        app = FastAPI()
        app.include_router(namespace['router'], prefix='/history')
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def seed(self, identifier, instant=NOW, **data):
        self.rows[identifier] = {'user_id': 'owner', 'outfit_id': 'look',
                                'date_worn': instant.timestamp() * 1000, **data}

    def stream(self, query):
        proto = query._to_protobuf()
        self.queries.append(proto)
        if self.fail_page == len(self.queries):
            raise RuntimeError('private datastore failure')
        self.assertEqual(proto.offset, 0, 'Paging must not use offsets')
        self.assertEqual([(o.field.field_path, o.direction.name) for o in proto.order_by],
                         [('date_worn', 'DESCENDING'), ('__name__', 'DESCENDING')])
        filters = proto.where.composite_filter.filters or [proto.where]
        def accepted(data):
            for item in filters:
                predicate = item.field_filter
                actual = data.get(predicate.field.field_path)
                expected = _helpers.decode_value(predicate.value, self.db)
                op = predicate.op.name
                if op == 'EQUAL' and actual != expected:
                    return False
                if op == 'GREATER_THAN_OR_EQUAL' and not (actual is not None and actual >= expected):
                    return False
                if op == 'LESS_THAN' and not (actual is not None and actual < expected):
                    return False
            return 'date_worn' in data
        found = [(key, data) for key, data in self.rows.items() if accepted(data)]
        found.sort(key=lambda row: (row[1]['date_worn'], row[0]), reverse=True)
        if proto.start_at.values:
            self.assertFalse(proto.start_at.before)
            self.assertEqual(len(proto.start_at.values), 2, 'Cursor must include timestamp AND identity')
            timestamp = _helpers.decode_value(proto.start_at.values[0], self.db)
            reference = _helpers.decode_value(proto.start_at.values[1], self.db)
            found = [(key, data) for key, data in found if (data['date_worn'], key) < (timestamp, reference.id)]
        found = found[:proto.limit]
        snapshots = [firestore.DocumentSnapshot(self.db.collection('outfit_history').document(key),
                                                copy.deepcopy(data), True, None, None, None)
                     for key, data in found]
        if self.after_page:
            self.after_page(len(self.queries), snapshots)
        return iter(snapshots)

    def read(self, **params):
        return self.client.get('/history/', params=params)

    def ids(self, response):
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data['count'], len(data['outfitHistory']))
        return [entry['id'] for entry in data['outfitHistory']]

    def test_same_day_includes_midnight_noon_last_millisecond_not_next_day(self):
        start = NOW.replace(hour=0)
        for key, instant in [('before', start - timedelta(milliseconds=1)), ('start', start),
                             ('noon', NOW), ('last', start + timedelta(days=1, milliseconds=-1)),
                             ('next', start + timedelta(days=1))]:
            self.seed(key, instant)
        self.assertEqual(self.ids(self.read(start_date='2026-09-27', end_date='2026-09-27')),
                         ['last', 'noon', 'start'])

    @unittest.skipUnless(hasattr(time, 'tzset'), 'Host timezone manipulation requires tzset')
    def test_utc_bounds_do_not_follow_host_timezone_or_dst(self):
        original = os.environ.get('TZ')
        try:
            for zone in ('UTC', 'America/New_York', 'Asia/Kathmandu'):
                os.environ['TZ'] = zone
                time.tzset()
                for day in ('2026-03-08', '2026-11-01', '2026-12-31'):
                    with self.subTest(zone=zone, day=day):
                        self.rows.clear()
                        start = datetime.fromisoformat(day).replace(tzinfo=UTC)
                        self.seed('noon', start + timedelta(hours=12))
                        self.seed('end', start + timedelta(days=1))
                        self.assertEqual(self.ids(self.read(start_date=day, end_date=day)), ['noon'])
        finally:
            if original is None:
                os.environ.pop('TZ', None)
            else:
                os.environ['TZ'] = original
            time.tzset()

    def test_individual_bounds_and_leap_day(self):
        self.seed('feb28', datetime(2024, 2, 28, 12, tzinfo=UTC))
        self.seed('feb29', datetime(2024, 2, 29, 12, tzinfo=UTC))
        self.seed('mar01', datetime(2024, 3, 1, tzinfo=UTC))
        self.assertEqual(self.ids(self.read(end_date='2024-02-29')), ['feb29', 'feb28'])
        self.assertEqual(self.ids(self.read(start_date='2024-02-29')), ['mar01', 'feb29'])

    def test_invalid_dates_and_reversed_bounds_are_422_without_query(self):
        for params in ({'start_date': '2026-02-30'}, {'end_date': 'tomorrow'},
                       {'end_date': '9999-12-31'}, {'start_date': '2026-09-28', 'end_date': '2026-09-27'},
                       {'start_date': '2026-09-27T12:00:00Z'}, {'end_date': '2026-09-27T12:00:00-04:00'}):
            with self.subTest(params=params):
                self.assertEqual(self.read(**params).status_code, 422)
        self.assertEqual(self.queries, [])

    def test_invalid_limit_is_422_without_query(self):
        for limit in (0, -1, 1001, 'bad'):
            with self.subTest(limit=limit):
                self.assertEqual(self.read(limit=limit).status_code, 422)
        self.assertEqual(self.queries, [])

    def test_undone_does_not_consume_active_limit_and_legacy_is_retained(self):
        self.seed('undone', NOW + timedelta(hours=1), undone=True)
        self.seed('legacy')
        self.seed('active', NOW - timedelta(hours=1), undone=False)
        self.assertEqual(self.ids(self.read(limit=1)), ['legacy'])
        self.assertEqual(self.ids(self.read(limit=2)), ['legacy', 'active'])

    def test_pages_fill_limit_preserve_filters_and_equal_timestamp_rows(self):
        for number in range(235):
            self.seed(f'row-{number:03}', undone=number >= 10)
        self.seed('foreign', user_id='other')
        self.seed('other-look', outfit_id='other')
        self.assertEqual(self.ids(self.read(limit=7, outfit_id='look', start_date='2026-09-27', end_date='2026-09-27')),
                         [f'row-{number:03}' for number in range(9, 2, -1)])
        self.assertEqual(len(self.queries), 3)
        self.assertEqual([query.limit for query in self.queries], [100, 100, 100])

    def test_snapshot_cursor_survives_cursor_document_deleted_between_pages(self):
        for number in range(110):
            self.seed(f'row-{number:03}', NOW + timedelta(minutes=number), undone=number >= 3)
        def delete_cursor(page, docs):
            if page == 1:
                self.rows.pop(docs[-1].id)
        self.after_page = delete_cursor
        self.assertEqual(self.ids(self.read(limit=3)), ['row-002', 'row-001', 'row-000'])
        self.assertEqual(len(self.queries), 2)

    def test_empty_or_exhausted_history_returns_success_with_actual_count(self):
        self.assertEqual(self.ids(self.read()), [])
        for number in range(100):
            self.seed(f'row-{number:03}', undone=number > 0)
        self.queries.clear()
        self.assertEqual(self.ids(self.read(limit=2)), ['row-000'])
        self.assertEqual(len(self.queries), 2)

    def test_scan_cap_does_not_return_empty_or_partial_success(self):
        for active in (False, True):
            with self.subTest(active=active):
                self.rows.clear()
                self.queries.clear()
                for number in range(1001):
                    self.seed(f'row-{number:04}', undone=not (active and number == 1000))
                response = self.read(limit=2)
                self.assertEqual(response.status_code, 503)
                self.assertIn('Narrow the date range', response.json()['detail'])
                self.assertEqual(len(self.queries), 10)
                self.assertEqual(sum(query.limit for query in self.queries), 1000)

    def test_exact_scan_boundary_can_satisfy_limit(self):
        for number in range(1000):
            self.seed(f'row-{number:04}', undone=number != 0)
        self.assertEqual(self.ids(self.read(limit=1)), ['row-0000'])
        self.assertEqual(len(self.queries), 10)

    def test_maximum_requested_active_count_is_supported(self):
        for number in range(1000):
            self.seed(f'row-{number:04}')
        self.assertEqual(len(self.ids(self.read(limit=1000))), 1000)

    def test_later_query_failure_does_not_claim_partial_success(self):
        for number in range(110):
            self.seed(f'row-{number:03}', undone=number < 109)
        self.fail_page = 2
        response = self.read(limit=2)
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private', response.text)
        self.assertNotIn('outfitHistory', response.json())

    def test_ordering_failure_does_not_fall_back_to_arbitrary_order(self):
        with patch.object(firestore.Query, 'order_by', side_effect=ValueError('invalid order')):
            self.assertEqual(self.read().status_code, 503)
        self.assertEqual(self.queries, [])

    def test_numeric_milliseconds_and_legacy_seconds_are_returned_unchanged(self):
        for stored in (int(NOW.timestamp() * 1000), int(NOW.timestamp())):
            with self.subTest(stored=stored):
                self.rows.clear()
                self.seed('numeric', date_worn=stored)
                response = self.read()
                self.assertEqual(self.ids(response), ['numeric'])
                self.assertEqual(response.json()['outfitHistory'][0]['dateWorn'], stored)

    def test_success_response_and_serialized_legacy_values_remain_compatible(self):
        self.seed('legacy', outfit_name='Saved look', date_worn='2026-09-27T12:00:00Z', notes='Keep me')
        response = self.read()
        self.assertEqual(self.ids(response), ['legacy'])
        data = response.json()
        self.assertEqual(set(data), {'success', 'outfitHistory', 'count', 'user_id'})
        self.assertEqual(data['outfitHistory'][0], {
            'id': 'legacy', 'outfitId': 'look', 'outfitName': 'Saved look', 'outfitImage': '',
            'dateWorn': '2026-09-27T12:00:00Z', 'weather': {'temperature': 0, 'condition': 'Unknown', 'humidity': 0},
            'occasion': 'Casual', 'mood': 'Comfortable', 'notes': 'Keep me', 'tags': [],
            'createdAt': None, 'updatedAt': None,
        })


if __name__ == '__main__':
    unittest.main()
