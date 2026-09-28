"""Actual route dispatch with held transaction doubles; no server, cloud or sleeps."""
import asyncio
from datetime import datetime, timedelta, timezone
from types import ModuleType, SimpleNamespace
from typing import Optional
import unittest
from unittest.mock import patch

from fastapi import Body, Query, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, ConfigDict, Field

from .test_outfit_wear import Document, FakeQuery, Transaction, WearTestFixture
from .test_read_endpoint_concurrency import ReadGate, route_app


class WearRouteConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.fixture = WearTestFixture()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.db = self.fixture.db
        firebase = ModuleType('src.config.firebase')
        firebase.db = self.db
        fake = patch.dict('sys.modules', {'src.config.firebase': firebase})
        fake.start()
        self.addCleanup(fake.stop)
        self.db.seed('daily_outfit_suggestions', 'suggestion', {'user_id': 'owner', 'outfit_id': 'look'})

    def history_app(self, handler):
        return route_app('routes/outfit_history.py', {handler}, {
            '__package__': 'src.routes', 'get_db': lambda: self.db,
            'get_current_user': lambda: SimpleNamespace(id='owner'), 'UserProfile': object,
            'Optional': Optional, 'Query': Query, 'datetime': datetime,
            'timedelta': timedelta, 'timezone': timezone,
        }, '/history')

    def wear_app(self):
        return route_app('routes/outfits/routes.py', {'OutfitWearRequest', 'mark_outfit_as_worn'}, {
            '__package__': 'src.routes.outfits', 'BaseModel': BaseModel, 'ConfigDict': ConfigDict,
            'Field': Field, 'Body': Body, 'Request': Request, 'Optional': Optional,
            'JSONResponse': JSONResponse, 'verified_user_id': lambda: 'owner',
        }, '/outfits')

    async def held_request(self, app, method, path, **kwargs):
        gate = ReadGate()
        get, stream, commit = Document.get, FakeQuery.stream, Transaction.commit

        def held_get(doc, *args, **kw):
            gate.read(('get', doc.path))
            return get(doc, *args, **kw)

        def held_stream(query, *args, **kw):
            # Gate iteration, not generator creation, to catch a lazy stream
            # that accidentally escapes the worker onto the request loop.
            gate.read(('stream', query.name))
            yield from stream(query, *args, **kw)

        def held_commit(transaction):
            gate.read(('commit',))
            return commit(transaction)

        @app.get('/ping')
        async def ping():
            return {'responsive': True}

        with patch.object(Document, 'get', held_get), patch.object(FakeQuery, 'stream', held_stream), \
                patch.object(Transaction, 'commit', held_commit):
            async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
                pending = asyncio.create_task(client.request(method, path, **kwargs))
                try:
                    await asyncio.wait_for(gate.entered.wait(), timeout=3)
                    self.assertNotIn(gate.loop_thread, [thread for _, thread in gate.calls])
                    self.assertFalse(pending.done(), 'SDK operation must still be held')
                    response = await asyncio.wait_for(client.get('/ping'), timeout=3)
                    self.assertEqual(response.json(), {'responsive': True})
                    self.assertFalse(pending.done(), 'Unrelated request must not release the SDK gate')
                finally:
                    gate.release.set()
                    result = await asyncio.wait_for(pending, timeout=3)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertEqual(len({thread for _, thread in gate.calls}), 1)
        self.assertTrue(all(thread != gate.loop_thread for _, thread in gate.calls))
        return result, [operation[0] for operation, _ in gate.calls]

    async def test_history_lazy_stream_keeps_loop_responsive(self):
        self.fixture.record()
        response, calls = await self.held_request(self.history_app('get_outfit_history'), 'GET', '/history/?limit=1')
        self.assertEqual(response.json()['count'], 1)
        self.assertIn('stream', calls)

    async def test_empty_history_still_consumes_stream_in_worker(self):
        response, calls = await self.held_request(self.history_app('get_outfit_history'), 'GET', '/history/')
        self.assertEqual(response.json()['outfitHistory'], [])
        self.assertEqual(calls, ['stream'])

    async def test_managed_undo_scan_and_commit_keep_loop_responsive(self):
        event = self.fixture.record()
        response, calls = await self.held_request(self.history_app('delete_outfit_history_entry'), 'DELETE', '/history/' + event['event_id'])
        self.assertTrue(response.json()['undone'])
        self.assertTrue(response.json()['rewards_retained'])
        self.assertIn('stream', calls)
        self.assertIn('commit', calls)
        self.assertEqual(self.db.rows['outfits']['look']['wearCount'], 4)

    async def test_calendar_wear_transaction_keeps_loop_responsive(self):
        response, calls = await self.held_request(self.history_app('mark_outfit_as_worn'), 'POST', '/history/mark-worn',
            json={'outfitId': 'look', 'dateWorn': '2026-09-27', 'idempotency_key': 'calendar-request'})
        self.assertEqual(response.json()['wear_count'], 5)
        self.assertEqual(response.json()['message'], 'Outfit recorded')
        self.assertIn('commit', calls)

    async def test_suggestion_read_and_transaction_keep_loop_responsive(self):
        response, calls = await self.held_request(self.history_app('mark_today_suggestion_as_worn'), 'POST', '/history/today-suggestion/wear',
            json={'suggestionId': 'suggestion', 'idempotency_key': 'suggestion-request'})
        self.assertFalse(response.json()['alreadyWorn'])
        self.assertEqual(response.json()['wear_count'], 5)
        self.assertIn('commit', calls)
        self.assertTrue(self.db.rows['daily_outfit_suggestions']['suggestion']['is_worn'])

    async def test_primary_wear_transaction_keeps_loop_responsive(self):
        response, calls = await self.held_request(self.wear_app(), 'POST', '/outfits/look/worn',
            json={'idempotency_key': 'wear-request', 'timezone': 'UTC'})
        self.assertEqual(response.json()['wear_count'], 5)
        self.assertEqual(response.headers['cache-control'], 'private, no-store')
        self.assertIn('commit', calls)

    async def test_primary_omitted_body_legacy_transaction_keeps_loop_responsive(self):
        response, calls = await self.held_request(self.wear_app(), 'POST', '/outfits/look/worn')
        self.assertEqual(response.json()['wear_count'], 5)
        self.assertIn('commit', calls)

    async def test_primary_explicit_null_still_rejected_before_transaction(self):
        with patch.object(Transaction, 'commit', side_effect=AssertionError('No transaction expected')):
            async with AsyncClient(transport=ASGITransport(app=self.wear_app()), base_url='http://test') as client:
                response = await client.post('/outfits/look/worn', content='null', headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 422)
        self.assertNotIn('outfit_history', self.db.rows)
