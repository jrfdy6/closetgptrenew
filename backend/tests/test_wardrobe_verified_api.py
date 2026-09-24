"""Real HTTP auth and save/list boundaries, with only storage faked."""
import ast
from datetime import datetime
import logging
from pathlib import Path
import time
from types import SimpleNamespace
from typing import Any, Dict, Optional
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from firebase_admin import auth

from src.auth.verified_identity import verified_identity, reject_identity_overrides
from src.routes.wardrobe_update_contract import build_wardrobe_update
from src.services import wardrobe_persistence
from test_wardrobe_update_contract import FakeDocument, RICH_ITEM


def wardrobe_app(database):
    """Compile active route bodies/dependencies without unrelated AI startup."""
    root = Path(__file__).resolve().parents[1]
    app = FastAPI()
    namespace = {
        'app': app, 'router': APIRouter(), 'Depends': Depends, 'Request': Request,
        'HTTPException': HTTPException, 'SimpleNamespace': SimpleNamespace,
        'UserProfile': SimpleNamespace, 'Dict': Dict, 'Any': Any, 'Optional': Optional,
        'verified_identity': verified_identity, 'reject_identity_overrides': reject_identity_overrides,
        'verified_wardrobe_identity': verified_identity,
        'reject_wardrobe_identity_overrides': reject_identity_overrides,
        'time': time, 'datetime': datetime, 'logger': logging.getLogger(__name__),
        'db': database, 'ANALYTICS_AVAILABLE': False, 'build_wardrobe_update': build_wardrobe_update,
    }
    names = {'verified_wardrobe_user', '_owned_wardrobe_item', 'get_wardrobe_items_with_slash',
             'get_wardrobe_item', 'update_wardrobe_item'}
    source = root / 'src/routes/wardrobe.py'
    nodes = [node for node in ast.parse(source.read_text()).body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    assert {node.name for node in nodes} == names
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
    app_tree = ast.parse((root / 'app.py').read_text())
    registrations = next(ast.literal_eval(node.value) for node in app_tree.body
                         if isinstance(node, ast.Assign) and any(
                             isinstance(target, ast.Name) and target.id == 'ROUTERS' for target in node.targets))
    assert ('src.routes.wardrobe', '/api/wardrobe') in registrations
    app.include_router(namespace['router'], prefix='/api/wardrobe')
    save = next(node for node in app_tree.body
                if isinstance(node, ast.AsyncFunctionDef) and node.name == 'add_wardrobe_item_direct')
    exec(compile(ast.Module(body=[save], type_ignores=[]), str(root / 'app.py'), 'exec'), namespace)
    return app


class WardrobeVerifiedHttpTests(unittest.TestCase):
    def setUp(self):
        self.document = FakeDocument({**RICH_ITEM, 'imageUrl': 'https://assets.example/original.jpg'})
        self.rows = [self.document]
        self.query = Mock(return_value=SimpleNamespace(stream=lambda: self.rows))
        self.database = SimpleNamespace(collection=lambda _: SimpleNamespace(
            where=self.query, document=lambda _: self.document))
        firebase = SimpleNamespace(firebase_initialized=True, db=self.database)
        modules = patch.dict('sys.modules', {'src.config.firebase': firebase})
        modules.start()
        self.addCleanup(modules.stop)
        auth_patch = patch('src.auth.verified_user.auth.verify_id_token', return_value={'uid': 'owner'})
        self.verify = auth_patch.start()
        self.addCleanup(auth_patch.stop)
        save_patch = patch.object(wardrobe_persistence, 'create_owned_wardrobe_item', return_value=self.document.data)
        self.save = save_patch.start()
        self.addCleanup(save_patch.stop)
        reward_patch = patch('src.services.challenge_actions.refresh_action_rewards', new_callable=AsyncMock)
        self.refresh_rewards = reward_patch.start()
        self.addCleanup(reward_patch.stop)
        self.client = TestClient(wardrobe_app(self.database))

    def get(self, authorization='Bearer signed-token', suffix='', headers=None):
        return self.client.get('/api/wardrobe/' + suffix,
                               headers={**({'Authorization': authorization} if authorization is not None else {}), **(headers or {})})

    def post(self, authorization='Bearer signed-token', body=None, suffix='', headers=None):
        return self.client.post('/api/wardrobe/add-direct' + suffix,
                                headers={**({'Authorization': authorization} if authorization is not None else {}), **(headers or {})},
                                json=body if body is not None else {'id': 'shirt-1', 'name': 'Shirt'})

    def test_list_is_scoped_to_verified_uid_and_preserves_real_original(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user_id'], 'owner')
        self.assertEqual(response.json()['items'][0]['imageUrl'], 'https://assets.example/original.jpg')
        predicates = [call.kwargs['filter'] for call in self.query.call_args_list]
        self.assertEqual({predicate.field_path for predicate in predicates}, {'userId', 'user_id', 'firebase_uid', 'uid', 'ownerId'})
        self.assertTrue(all(predicate.op_string == '==' and predicate.value == 'owner' for predicate in predicates))
        self.verify.assert_called_once_with('signed-token', check_revoked=True)

    def test_save_uses_verified_owner_and_returns_existing_persisted_acknowledgement(self):
        payload = {'id': 'shirt-1', 'userId': 'owner', 'name': 'Staged name', 'contentHash': 'same-photo'}
        first = self.post(body=payload)
        retry = self.post(body=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(retry.json(), first.json())
        self.assertEqual(first.json()['item'], self.document.data)
        self.assertEqual(first.json()['item_id'], 'shirt-1')
        self.assertEqual(self.save.call_count, 2)
        self.save.assert_called_with(self.database, 'owner', payload)
        self.assertNotEqual(first.json()['item']['name'], payload['name'])

    def test_saved_upload_refreshes_rewards_with_the_committed_epoch(self):
        self.document.data['app_data_epoch'] = 7
        self.assertEqual(self.post().status_code, 200)
        self.refresh_rewards.assert_awaited_once_with('owner', expected_epoch=7, include_upload_milestones=True)

    def test_reward_outage_never_turns_a_committed_upload_into_a_failed_save(self):
        self.refresh_rewards.side_effect = RuntimeError('temporary reward outage')
        result = self.post()
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json()['success'])
        self.assertEqual(result.json()['item']['id'], self.document.data['id'])

    def test_missing_guest_and_test_authorization_never_reach_storage(self):
        for authorization in (None, '', 'Basic token', 'Bearer test', 'Bearer TEST', 'Bearer a b'):
            for request in (self.get, self.post):
                self.assertEqual(request(authorization=authorization).status_code, 401)
        self.verify.assert_not_called()
        self.query.assert_not_called()
        self.save.assert_not_called()

    def test_revoked_disabled_and_unavailable_verification_fail_closed(self):
        for error, status in ((auth.RevokedIdTokenError('revoked'), 401),
                              (auth.UserDisabledError('disabled'), 401),
                              (auth.InvalidIdTokenError('invalid'), 401),
                              (RuntimeError('private verifier'), 503)):
            self.verify.side_effect = error
            for request in (self.get, self.post):
                response = request()
                self.assertEqual(response.status_code, status)
                self.assertNotIn(str(error), response.text)
        self.query.assert_not_called()
        self.save.assert_not_called()

    def test_spoofed_body_aliases_fail_before_persistence(self):
        for key in ('userId', 'user_id', 'firebase_uid', 'uid'):
            self.assertEqual(self.post(body={'id': 'shirt-1', key: 'foreign'}).status_code, 403)
        self.save.assert_not_called()

    def test_query_and_header_owner_spoofing_fail_before_storage(self):
        for request in (self.get, self.post):
            for key in ('userId', 'user_id', 'firebase_uid', 'uid'):
                self.assertEqual(request(suffix=f'?{key}=foreign').status_code, 403)
            self.assertEqual(request(headers={'X-User-ID': 'foreign'}).status_code, 403)
        self.query.assert_not_called()
        self.save.assert_not_called()

    def test_conflicting_stored_owner_aliases_are_not_projected_as_owned(self):
        for key in ('user_id', 'firebase_uid', 'uid', 'ownerId'):
            self.document.data[key] = 'foreign'
            response = self.get()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['items'], [])
            del self.document.data[key]

    def test_foreign_item_and_body_override_cannot_be_updated(self):
        self.document.data['firebase_uid'] = 'foreign'
        response = self.client.put('/api/wardrobe/shirt-1', headers={'Authorization': 'Bearer signed-token'}, json={'name': 'Changed'})
        self.assertEqual(response.status_code, 403)
        del self.document.data['firebase_uid']
        response = self.client.put('/api/wardrobe/shirt-1', headers={'Authorization': 'Bearer signed-token'}, json={'userId': 'foreign'})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.document.writes, [])


if __name__ == '__main__':
    unittest.main()
