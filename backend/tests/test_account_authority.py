"""Public input and auth regressions; no live Firebase access."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.auth_service import get_current_user_id, get_current_user, get_current_user_optional
from src.services.profile_updates import profile_patch
from src.services.outfit_edits import save_owned_outfit
from test_flatlay_lifecycle import Database, transactional
from test_outfit_persistence import FakeFirestore, transactional as profile_transactional
from fastapi import FastAPI
from fastapi.testclient import TestClient
from types import ModuleType
import sys
from src.routes.auth_working import router as profile_router


class ProfileAuthorityTests(unittest.TestCase):
    user = SimpleNamespace(id='owner', email='owner@example.com')

    def test_profile_preserves_identity_and_server_timestamp(self):
        result = profile_patch({'name': 'Owner', 'stylePreferences': ['Classic'],
                                'onboardingCompleted': True, 'createdAt': 1,
                                'updated_at': 2, 'userId': 'owner'}, self.user, 100)
        self.assertEqual(result['updated_at'], 100)
        self.assertEqual(result['email'], self.user.email)
        self.assertNotIn('createdAt', result)
        self.assertTrue(result['onboardingCompleted'])

    def test_authority_and_dotted_field_injection_rejected(self):
        for key in ('subscription', 'quotas', 'billing', 'role', 'firebase_uid', 'quotas.flatlaysRemaining'):
            with self.subTest(key=key), self.assertRaises(HTTPException) as caught:
                profile_patch({key: {}}, self.user, 100)
            self.assertEqual(caught.exception.status_code, 422)

    def test_invalid_identity_and_types(self):
        for data in ({'userId': 'other'}, {'email': 'other@example.com'}, {'name': {}},
                     {'preferences': []}, {'stylePreferences': {}}, {'onboardingCompleted': 'true'},
                     {'height': {}}, {'stylePreferences': [{}]}, {'stylePersonality': {'bold': 2}},
                     {'preferences': {'style': 'Classic'}}, {'budget': []}):
            with self.subTest(data=data), self.assertRaises(HTTPException):
                profile_patch(data, self.user, 100)


class AuthenticationTests(unittest.TestCase):
    def test_literal_test_token_is_not_a_bypass(self):
        credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='test')
        for handler in (get_current_user_id, get_current_user, get_current_user_optional):
            with self.subTest(handler=handler.__name__), patch('firebase_admin.auth.verify_id_token', side_effect=ValueError('bad token')):
                with self.assertRaises(HTTPException) as caught:
                    asyncio.run(handler(credentials))
                self.assertEqual(caught.exception.status_code, 401)

    def test_verified_identity_checks_revocation(self):
        credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='verified')
        with patch('firebase_admin.auth.verify_id_token', return_value={'uid': 'owner', 'email': 'owner@example.com'}) as verify:
            self.assertEqual(asyncio.run(get_current_user_id(credentials)), 'owner')
            verify.assert_called_once_with('verified', check_revoked=True)
        self.assertIsNone(asyncio.run(get_current_user_optional(None)))


class ProfileHTTPTests(unittest.TestCase):
    def setUp(self):
        self.db = FakeFirestore()
        self.db.records['users'] = {'owner': {'quotas': {'flatlaysRemaining': 0, 'lastRefillAt': 1000},
                                             'subscription': {'role': 'tier1'}, 'wardrobeItemCount': 10}}
        module = ModuleType('src.config.firebase')
        module.db, module.firebase_initialized = self.db, True
        modules = patch.dict(sys.modules, {'src.config.firebase': module})
        modules.start()
        self.addCleanup(modules.stop)
        tx = patch('firebase_admin.firestore.transactional', profile_transactional)
        tx.start()
        self.addCleanup(tx.stop)
        app = FastAPI()
        app.include_router(profile_router, prefix='/api/auth')
        app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
            id='owner', email='owner@example.com', name='Owner', createdAt=0, updatedAt=0)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_quiz_saves_and_returns_ten_item_count_without_credit_reset(self):
        response = self.client.put('/api/auth/profile', json={
            'userId': 'owner', 'name': 'Owner', 'email': 'owner@example.com',
            'stylePreferences': ['Classic'], 'onboardingCompleted': True})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['wardrobeCount'], 10)
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 0)
        self.assertEqual(self.client.get('/api/auth/profile').status_code, 200)

    def test_http_authority_edit_rejected_and_spent_balance_preserved(self):
        response = self.client.put('/api/auth/profile', json={'quotas': {'flatlaysRemaining': 30}})
        self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 0)


class OutfitAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.tx = patch('firebase_admin.firestore.transactional', transactional)
        self.tx.start()
        self.addCleanup(self.tx.stop)

    def create(self):
        return save_owned_outfit(self.db, 'owner', {'name': 'Look', 'items': [{'id': 'shirt', 'imageUrl': 'forged'}]}, outfit_id='new', create=True)

    def test_create_rehydrates_items_and_supports_one_and_two(self):
        result = self.create()
        self.assertEqual(result['items'][0]['imageUrl'], 'https://assets.invalid/shirt')
        self.assertEqual(result['flat_lay_status'], 'awaiting_consent')
        result = save_owned_outfit(self.db, 'owner', {'items': [{'id': 'shirt'}, {'id': 'pants'}]}, outfit_id='two', create=True)
        self.assertEqual([x['id'] for x in result['items']], ['shirt', 'pants'])

    def test_concurrent_create_is_idempotent(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.create(), range(2)))
        self.assertEqual(results[0], results[1])
        self.db.records['outfits']['new']['flat_lay_url'] = 'server-result'
        self.assertEqual(self.create()['flat_lay_url'], 'server-result')

    def test_foreign_outfits_and_garments_rejected(self):
        self.db.records['outfits']['foreign'] = {'user_id': 'other'}
        self.db.records['wardrobe']['pants']['user_id'] = 'other'
        for key, data, create in [('foreign', {'name': 'Bad'}, False), ('foreign', {'items': [{'id': 'shirt'}]}, True), ('new', {'items': [{'id': 'pants'}]}, True)]:
            with self.assertRaises(HTTPException):
                save_owned_outfit(self.db, 'owner', data, outfit_id=key, create=create)
        self.assertNotIn('new', self.db.records['outfits'])

    def test_item_edit_invalidates_preview_preserving_private_reservation(self):
        self.create()
        self.db.records['outfits']['new']['flat_lay_url'] = 'old'
        self.db.records['flat_lay_requests'] = {'new': {'status': 'processing', 'credit_status': 'reserved'}}
        result = save_owned_outfit(self.db, 'owner', {'items': [{'id': 'pants'}]}, outfit_id='new')
        self.assertIsNone(result['flat_lay_url'])
        self.assertEqual(result['metadata']['flatLayStatus'], 'processing')
        self.assertFalse(result['flat_lay_request_allowed'])
        self.assertEqual(self.db.records['flat_lay_requests']['new']['credit_status'], 'reserved')

    def test_notes_preserve_preview_but_authority_edits_rejected(self):
        self.create()
        self.db.records['outfits']['new']['flat_lay_url'] = 'kept'
        self.assertEqual(save_owned_outfit(self.db, 'owner', {'notes': 'My notes'}, outfit_id='new')['flat_lay_url'], 'kept')
        for key in ('user_id', 'flat_lay_status', 'metadata', 'createdAt'):
            with self.assertRaises(HTTPException):
                save_owned_outfit(self.db, 'owner', {key: 'forged'}, outfit_id='new')

    def test_duplicate_empty_and_excess_items_rejected(self):
        for items in ([], [{'id': 'shirt'}] * 2, [{'id': str(i)} for i in range(11)]):
            with self.assertRaises(HTTPException):
                save_owned_outfit(self.db, 'owner', {'items': items}, create=True)
