"""HTTP controls exercise real transactions without account or cloud access."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from firebase_admin import auth
from test_app_data_privacy import Database, transactional
from src.services import app_data_privacy


class PrivacyRouteTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('src.routes.privacy_isolated', Path(__file__).parents[1] / 'src/routes/data_privacy.py')
        self.route = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.route)
        self.db = Database({'users/owner': {'quotas': {'flatlaysRemaining': 1}, 'subscription': {'role': 'tier1'}},
                            'users/foreign': {'private': 'other'}})
        self.route.db = self.db
        for patcher in (patch.object(app_data_privacy.firestore, 'transactional', transactional),
                        patch('src.auth.verified_user.auth.verify_id_token', return_value={'uid': 'owner'})):
            started = patcher.start()
            self.addCleanup(patcher.stop)
        self.verify = started
        app = FastAPI()
        app.include_router(self.route.router, prefix='/api')
        self.client = TestClient(app)
        self.headers = {'Authorization': 'Bearer valid-token'}

    def test_delete_is_queued_status_owned_and_retry_never_resets_credits(self):
        response = self.client.delete('/api/privacy-data?data_type=all', headers=self.headers)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json()['status'], 'pending')
        self.assertFalse(response.json()['completed'])
        repeated = self.client.delete('/api/privacy-data?data_type=all', headers=self.headers)
        self.assertEqual(repeated.json()['job_id'], response.json()['job_id'])
        status = self.client.get('/api/privacy-data/status', headers=self.headers).json()
        self.assertEqual(status['job_id'], response.json()['job_id'])
        self.assertEqual(self.db.rows['users/owner']['quotas'], {'flatlaysRemaining': 1})
        self.assertEqual(self.db.rows['users/foreign'], {'private': 'other'})

    def test_unsupported_retention_and_unknown_fields_rejected_with_no_write(self):
        for body in ({'data_retention_days': 30}, {'allow_personalization': 'false'}, {'quotas': {'flatlaysRemaining': 99}}):
            self.assertEqual(self.client.post('/api/privacy-settings', json=body, headers=self.headers).status_code, 422)
        self.assertNotIn('privacy', self.db.rows['users/owner'])
        self.assertFalse(self.client.get('/api/privacy-settings', headers=self.headers).json()['automatic_retention_supported'])

    def test_privacy_can_be_revoked_during_clear_and_authority_is_unchanged(self):
        self.client.delete('/api/privacy-data', headers=self.headers)
        response = self.client.post('/api/privacy-settings', json={'allow_personalization': False, 'allow_data_collection': False}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.db.rows['users/owner']['privacy']['allow_personalization'])
        self.assertEqual(self.db.rows['users/owner']['subscription'], {'role': 'tier1'})

    def test_no_test_anonymous_or_revoked_credential_can_start_deletion(self):
        for header in ('Bearer test', 'Basic abc', ''):
            self.assertEqual(self.client.delete('/api/privacy-data', headers={'Authorization': header}).status_code, 401)
        self.verify.side_effect = auth.RevokedIdTokenError('revoked')
        self.assertEqual(self.client.delete('/api/privacy-data', headers=self.headers).status_code, 401)
        self.verify.side_effect = None
        self.verify.return_value = {'uid': 'owner', 'firebase': {'sign_in_provider': 'anonymous'}}
        self.assertEqual(self.client.delete('/api/privacy-data', headers=self.headers).status_code, 403)
        self.assertNotIn('app_data_epoch', self.db.rows['users/owner'])


if __name__ == '__main__':
    unittest.main()
