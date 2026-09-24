"""Read routes must stay responsive while synchronous Firebase work is pending.

These tests execute the real handlers/dependencies with a read-only SDK fake.
Streams block on iteration, not construction, to catch lazy iterators escaping
the worker. No provider credentials, cloud services, sleeps or timing targets.
"""
import ast
import asyncio
from copy import deepcopy
from datetime import datetime
import importlib.util
import logging
from pathlib import Path
import threading
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, List, Optional
import unittest
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel, ConfigDict

from src.auth import auth_service, verified_user
from src.custom_types.gamification import CHALLENGE_CATALOG
from src.services import saved_outfit


SOURCE = Path(__file__).resolve().parents[1] / 'src'


class ReadGate:
    def __init__(self):
        self.loop = asyncio.get_running_loop()
        self.loop_thread = threading.get_ident()
        self.entered = asyncio.Event()
        self.release = threading.Event()
        self.calls = []

    def read(self, operation):
        thread = threading.get_ident()
        self.calls.append((operation, thread))
        self.loop.call_soon_threadsafe(self.entered.set)
        # An unfixed handler must fail an assertion, not deadlock the test loop.
        if thread != self.loop_thread and not self.release.wait(timeout=5):
            raise AssertionError('Test did not release its synchronous read')


class Snapshot:
    def __init__(self, path, data):
        self.id = path.rsplit('/', 1)[-1]
        self.data = deepcopy(data)
        self.exists = data is not None

    def to_dict(self):
        return deepcopy(self.data)


class Document:
    def __init__(self, store, path):
        self.store, self.path = store, path

    def get(self, transaction=None):
        self.store.gate.read(('get', self.path))
        return Snapshot(self.path, self.store.rows.get(self.path))

    def collection(self, name):
        return Query(self.store, self.path + '/' + name)


class Query:
    def __init__(self, store, path, filters=(), order=None, maximum=None):
        self.store, self.path = store, path
        self.filters, self.order, self.maximum = filters, order, maximum

    def document(self, key):
        return Document(self.store, self.path + '/' + key)

    def where(self, field, operator, value):
        return Query(self.store, self.path, self.filters + ((field, operator, value),), self.order, self.maximum)

    def order_by(self, field, direction=None):
        return Query(self.store, self.path, self.filters, (field, direction), self.maximum)

    def limit(self, maximum):
        return Query(self.store, self.path, self.filters, self.order, maximum)

    def stream(self):
        # This is deliberately a generator: even an empty query performs I/O
        # only when consumed. Query shape is asserted separately below.
        self.store.gate.read(('stream', self.path))
        self.store.queries.append((self.path, self.filters, self.order, self.maximum))
        if self.path in self.store.empty_streams:
            return
        prefix = self.path + '/'
        rows = [(path, value) for path, value in self.store.rows.items()
                if path.startswith(prefix) and '/' not in path[len(prefix):]]
        for path, value in rows[:self.maximum]:
            yield Snapshot(path, value)


class ReadOnlyStore:
    def __init__(self, gate, rows, empty_streams=()):
        self.gate, self.rows = gate, deepcopy(rows)
        self.empty_streams, self.queries = empty_streams, []

    def collection(self, name):
        return Query(self, name)

    def transaction(self):
        # Saved-outfit reads use one transaction; no write API is available.
        return object()


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, SOURCE / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def route_app(relative_path, names, namespace, prefix):
    """Compile real route bodies without unrelated provider initialization."""
    path = SOURCE / relative_path
    nodes = [node for node in ast.parse(path.read_text()).body
             if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    if {node.name for node in nodes} != set(names):
        raise AssertionError('Expected route/helper was removed or renamed')
    namespace = {
        'router': APIRouter(), 'Depends': Depends, 'HTTPException': HTTPException,
        'Dict': Dict, 'Any': Any, 'List': List,
        'logger': logging.getLogger('read-concurrency-tests'), **namespace,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
    app = FastAPI()
    app.include_router(namespace['router'], prefix=prefix)
    return app


class ReadEndpointConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.firebase = ModuleType('src.config.firebase')
        self.firebase.firebase_initialized = True
        self.firebase.db = None
        patcher = patch.dict('sys.modules', {'src.config.firebase': self.firebase})
        patcher.start()
        self.addCleanup(patcher.stop)

    def store(self, gate, rows, empty_streams=()):
        self.firebase.db = ReadOnlyStore(gate, rows, empty_streams)
        return self.firebase.db

    async def while_read_is_pending(self, app, path, gate, headers=None):
        @app.get('/ping')
        async def ping():
            return {'responsive': True}

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            request = asyncio.create_task(client.get(path, headers=headers))
            try:
                await asyncio.wait_for(gate.entered.wait(), timeout=3)
                self.assertNotIn(gate.loop_thread, [thread for _, thread in gate.calls])
                self.assertFalse(request.done(), 'The datastore read must still be held open')
                ping = await asyncio.wait_for(client.get('/ping'), timeout=3)
                self.assertEqual(ping.json(), {'responsive': True})
                self.assertFalse(request.done(), 'An unrelated request must not release the read')
            finally:
                gate.release.set()
                response = await asyncio.wait_for(request, timeout=3)
        self.assertEqual(response.status_code, 200, response.text)
        # A complete synchronous unit includes iterator consumption and hydration.
        self.assertEqual(len({thread for _, thread in gate.calls}), 1)
        self.assertNotEqual(gate.calls[0][1], gate.loop_thread)
        return response

    async def check_auth_dependency(self, dependency):
        gate = ReadGate()
        store = self.store(gate, {'users/owner': {'name': 'Stored name', 'gender': 'female'}})

        def verify(token, *, check_revoked):
            self.assertEqual((token, check_revoked), ('valid-token', True))
            gate.read(('verify', token))
            return {'uid': 'owner', 'email': 'verified@example.invalid'}

        app = FastAPI()
        @app.get('/authenticated')
        async def authenticated(user=Depends(dependency)):
            return {'uid': user if isinstance(user, str) else user.id}

        before = deepcopy(store.rows)
        with patch.object(auth_service, '_profile_database', return_value=store), \
                patch.object(verified_user.auth, 'verify_id_token', side_effect=verify) as verifier:
            response = await self.while_read_is_pending(app, '/authenticated', gate,
                                                       {'Authorization': 'Bearer valid-token'})
        self.assertEqual(response.json(), {'uid': 'owner'})
        verifier.assert_called_once_with('valid-token', check_revoked=True)
        expected = [('verify', 'valid-token')]
        if dependency is not auth_service.get_current_user_id:
            expected.append(('get', 'users/owner'))
        self.assertEqual([operation for operation, _ in gate.calls], expected)
        self.assertEqual(store.rows, before)

    async def test_profile_verification_and_hydration_share_one_worker(self):
        await self.check_auth_dependency(auth_service.get_current_user)

    async def test_id_verification_does_not_block_the_event_loop(self):
        await self.check_auth_dependency(auth_service.get_current_user_id)

    async def test_optional_signed_in_verification_and_profile_share_one_worker(self):
        await self.check_auth_dependency(auth_service.get_current_user_optional)

    async def test_saved_detail_transaction_and_all_garments_share_one_worker(self):
        gate = ReadGate()
        store = self.store(gate, {
            'outfits/look': {'user_id': 'owner', 'name': 'Saved look', 'items': ['shirt', 'shoes']},
            'wardrobe/shirt': {'userId': 'owner', 'name': 'Shirt', 'imageUrl': 'https://example.invalid/shirt.jpg'},
            'wardrobe/shoes': {'userId': 'owner', 'name': 'Shoes', 'imageUrl': 'https://example.invalid/shoes.jpg'},
        })
        app = route_app('routes/outfits/routes.py', {'get_saved_outfit'}, {
            '__package__': 'src.routes.outfits', 'JSONResponse': JSONResponse,
            'verified_user_id': verified_user.verified_user_id,
        }, '/api/outfits')
        app.dependency_overrides[verified_user.verified_user_id] = lambda: 'owner'
        before = deepcopy(store.rows)
        with patch.object(saved_outfit.firestore, 'transactional', lambda callback: callback):
            response = await self.while_read_is_pending(app, '/api/outfits/look', gate)
        self.assertEqual(response.headers['cache-control'], 'private, no-store')
        self.assertEqual(response.json()['name'], 'Saved look')
        self.assertEqual([item['id'] for item in response.json()['items']], ['shirt', 'shoes'])
        self.assertEqual([operation for operation, _ in gate.calls], [
            ('get', 'outfits/look'), ('get', 'flat_lay_requests/look'),
            ('get', 'wardrobe/shirt'), ('get', 'wardrobe/shoes'),
        ])
        self.assertEqual(store.rows, before)

    async def test_list_materializes_all_cohorts_cache_and_fallback_items_in_one_worker(self):
        gate = ReadGate()
        store = self.store(gate, {
            'outfits/look': {'user_id': 'owner', 'name': 'Saved look', 'items': ['shirt', 'shoes'],
                             'createdAt': '2026-09-24T12:00:00Z'},
            'wardrobe/shirt': {'userId': 'owner', 'name': 'Shirt'},
            'wardrobe/shoes': {'userId': 'owner', 'name': 'Shoes'},
        }, empty_streams={'wardrobe'})
        database = load_module('src.routes.outfits.database_concurrency', 'routes/outfits/database.py')
        app = route_app('routes/outfits/routes.py', {'OutfitResponse', 'list_outfits_no_slash'}, {
            'BaseModel': BaseModel, 'ConfigDict': ConfigDict, 'datetime': datetime, 'Optional': Optional,
            'UserProfile': SimpleNamespace, 'get_current_user': lambda: SimpleNamespace(id='owner'),
            'get_user_outfits': database.get_user_outfits,
        }, '/api/outfits')
        before = deepcopy(store.rows)
        with patch.object(database, '_get_owned_outfit_documents', wraps=database._get_owned_outfit_documents) as query:
            response = await self.while_read_is_pending(app, '/api/outfits?limit=5', gate)
        query.assert_called_once_with(store, 'owner', 5)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual([item['id'] for item in response.json()[0]['items']], ['shirt', 'shoes'])
        cohorts = store.queries[:8]
        self.assertEqual(len(store.queries), 9)
        self.assertEqual([entry[1][0] for entry in cohorts],
                         [('user_id', '==', 'owner')] * 4 + [('userId', '==', 'owner')] * 4)
        self.assertEqual([entry[1][1][1] for entry in cohorts], ['>=', '>=', '<=', '>'] * 2)
        self.assertTrue(all(entry[0] == 'outfits' and entry[2] == ('createdAt', 'DESCENDING')
                            and entry[3] == 301 for entry in cohorts))
        self.assertEqual(store.queries[-1], ('wardrobe', (('userId', '==', 'owner'),), None, None))
        self.assertEqual([operation for operation, _ in gate.calls][-2:],
                         [('get', 'wardrobe/shirt'), ('get', 'wardrobe/shoes')])
        self.assertEqual(store.rows, before)

    def privacy_app(self):
        route = load_module('src.routes.privacy_concurrency', 'routes/data_privacy.py')
        app = FastAPI()
        app.include_router(route.router, prefix='/api')
        app.dependency_overrides[verified_user.verified_user_id] = lambda: 'owner'
        return app

    async def test_privacy_settings_read_does_not_block_the_event_loop(self):
        gate = ReadGate()
        self.store(gate, {'users/owner': {'privacy': {'allow_personalization': False}}})
        response = await self.while_read_is_pending(self.privacy_app(), '/api/privacy-settings', gate)
        self.assertFalse(response.json()['allow_personalization'])
        self.assertFalse(response.json()['automatic_retention_supported'])
        self.assertEqual([operation for operation, _ in gate.calls], [('get', 'users/owner')])

    async def test_privacy_status_user_and_job_reads_share_one_worker(self):
        gate = ReadGate()
        self.store(gate, {
            'users/owner': {'app_data_deletion': {'job_id': 'job'}},
            'app_data_deletion_jobs/job': {'user_id': 'owner', 'status': 'complete', 'scope': 'analytics', 'epoch': 1},
        })
        response = await self.while_read_is_pending(self.privacy_app(), '/api/privacy-data/status', gate)
        self.assertTrue(response.json()['completed'])
        self.assertEqual(response.json()['status'], 'complete')
        self.assertEqual([operation for operation, _ in gate.calls],
                         [('get', 'users/owner'), ('get', 'app_data_deletion_jobs/job')])

    async def test_challenge_history_consumes_lazy_stream_and_preserves_completed_order(self):
        gate = ReadGate()
        challenge_id, definition = next(iter(CHALLENGE_CATALOG.items()))
        store = self.store(gate, {
            'user_challenges/owner/completed/older': {'challenge_id': challenge_id, 'status': 'completed', 'completed_at': 1000},
            'user_challenges/owner/completed/newer': {'challenge_id': challenge_id, 'status': 'completed', 'completed_at': 2000},
            'user_challenges/owner/completed/pending': {'challenge_id': challenge_id, 'status': 'in_progress'},
        })
        app = route_app('routes/challenges.py', {'get_challenge_history', '_read_challenge_history'}, {
            '__package__': 'src.routes', 'UserProfile': SimpleNamespace,
            'get_current_user': lambda: SimpleNamespace(id='owner'), 'challenge_service': SimpleNamespace(db=store),
        }, '/api/challenges')
        before = deepcopy(store.rows)
        response = await self.while_read_is_pending(app, '/api/challenges/history', gate)
        history = response.json()['data']
        self.assertEqual(history['count'], 2)
        self.assertEqual([row['instance_id'] for row in history['challenges']], ['newer', 'older'])
        self.assertTrue(all(row['title'] == definition.title for row in history['challenges']))
        self.assertEqual([operation for operation, _ in gate.calls],
                         [('stream', 'user_challenges/owner/completed')])
        self.assertEqual(store.rows, before)


if __name__ == '__main__':
    unittest.main()
