"""Legacy dependency names must preserve the strict verified identity contract."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from firebase_admin import auth
from src.auth.auth_service import get_current_user, get_current_user_id, get_current_user_optional
from src.auth import auth_service
from test_app_data_privacy import Database


class AuthCompatibilityPrivacyTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        @app.get('/required-id')
        async def required_id(uid=Depends(get_current_user_id)):
            return {'uid': uid}
        @app.get('/required-profile')
        async def required_profile(user=Depends(get_current_user)):
            return {'uid': user.id, 'gender': user.gender, 'preferences': user.preferences, 'email': user.email}
        @app.get('/optional')
        async def optional(user=Depends(get_current_user_optional)):
            return {'uid': user.id if user else None}
        self.client = TestClient(app)
        self.db = Database({'users/verified-owner': {'gender': 'female', 'name': 'Profile name',
            'preferences': {'style': ['minimalist']}, 'email': 'untrusted@example.invalid',
            'id': 'untrusted-id', 'subscription': {'role': 'tier3'}}})
        database_patch = patch.object(auth_service, '_profile_database', return_value=self.db)
        database_patch.start()
        self.addCleanup(database_patch.stop)
        auth_patch = patch('src.auth.verified_user.auth.verify_id_token', return_value={
            'uid': 'verified-owner', 'email': 'verified@example.invalid'})
        self.verify = auth_patch.start()
        self.addCleanup(auth_patch.stop)

    def request(self, path, header='Bearer actual-token'):
        return self.client.get(path, headers={'Authorization': header} if header is not None else {})

    def test_all_compatibility_dependencies_check_token_revocation(self):
        for path in ('/required-id', '/required-profile', '/optional'):
            result = self.request(path)
            self.assertEqual(result.status_code, 200, result.text)
            self.assertEqual(result.json()['uid'], 'verified-owner')
        self.assertEqual(self.verify.call_count, 3)
        for call in self.verify.call_args_list:
            self.assertEqual(call.args, ('actual-token',))
            self.assertEqual(call.kwargs, {'check_revoked': True})

    def test_profile_hydration_preserves_gender_preferences_without_trusting_stored_identity_or_writing(self):
        before = deepcopy(self.db.rows)
        response = self.request('/required-profile')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'uid': 'verified-owner', 'gender': 'female',
            'preferences': {'style': ['minimalist']}, 'email': 'verified@example.invalid'})
        self.assertEqual(self.db.rows, before)

    def test_profile_missing_account_conflicting_owner_and_store_failure_fail_closed(self):
        data = deepcopy(self.db.rows['users/verified-owner'])
        del self.db.rows['users/verified-owner']
        self.assertEqual(self.request('/required-profile').status_code, 404)
        for alias in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId'):
            self.db.rows['users/verified-owner'] = {**data, alias: 'other'}
            self.assertEqual(self.request('/required-profile').status_code, 409)
        with patch.object(self.db, 'collection', side_effect=RuntimeError('private database failure')):
            response = self.request('/required-profile')
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('private database failure', response.text)

    def test_literal_test_token_is_never_a_guest_or_a_user(self):
        for path in ('/required-id', '/required-profile', '/optional'):
            for header in ('Bearer test', 'Bearer TEST', 'Bearer a b'):
                self.assertEqual(self.request(path, header).status_code, 401)
        self.verify.assert_not_called()

    def test_optional_missing_credentials_are_allowed_but_required_credentials_are_not(self):
        self.assertEqual(self.request('/optional', None).json(), {'uid': None})
        for path in ('/required-id', '/required-profile'):
            self.assertEqual(self.request(path, None).status_code, 401)
        self.verify.assert_not_called()

    def test_present_malformed_credentials_are_not_treated_as_absent_optional_sign_in(self):
        for header in ('', 'Basic abc', 'Bearer', 'Bearer '):
            self.assertEqual(self.request('/optional', header).status_code, 401, repr(header))
        self.verify.assert_not_called()

    def test_revoked_disabled_invalid_and_provider_outage_never_become_optional_guest(self):
        for error, status in ((auth.RevokedIdTokenError('revoked'), 401),
                              (auth.UserDisabledError('disabled'), 401),
                              (auth.InvalidIdTokenError('invalid'), 401),
                              (RuntimeError('private verifier error'), 503)):
            self.verify.side_effect = error
            for path in ('/required-id', '/required-profile', '/optional'):
                response = self.request(path)
                self.assertEqual(response.status_code, status)
                self.assertNotIn(str(error), response.text)

    def test_anonymous_account_cannot_enter_any_compatibility_dependency(self):
        self.verify.return_value = {'uid': 'guest', 'firebase': {'sign_in_provider': 'anonymous'}}
        for path in ('/required-id', '/required-profile', '/optional'):
            self.assertEqual(self.request(path).status_code, 403)

    def test_invalid_verified_subject_never_selects_an_arbitrary_profile_document(self):
        before = deepcopy(self.db.rows)
        for uid in (None, '', ' padded ', 'users/other', 'x' * 129):
            self.verify.return_value = {'uid': uid}
            for path in ('/required-id', '/required-profile', '/optional'):
                self.assertEqual(self.request(path).status_code, 401)
        self.assertEqual(self.db.rows, before)


if __name__ == '__main__':
    unittest.main()
