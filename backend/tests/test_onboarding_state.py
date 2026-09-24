"""Railway onboarding transactions and actual HTTP authentication boundary."""
import copy
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.auth import verified_user
from src.routes import onboarding as api
from src.services import onboarding_state as state
from test_outfit_wear import Database as BaseDatabase, Document as BaseDocument, Snapshot, transactional


class Document(BaseDocument):
    def get(self, transaction=None):
        if transaction is not None:
            result = super().get(transaction)
        else:
            if self.db.fail_read:
                raise RuntimeError('private storage failure')
            result = Snapshot(self.db.rows.get(self.collection_name, {}).get(self.id))
        result.id = self.id
        return result


class Query:
    def __init__(self, db, name, filter):
        self.db, self.name, self.filter = db, name, filter

    def stream(self, transaction=None):
        self.db.queries.append((self.name, self.filter.field_path))
        for key, value in list(self.db.rows.get(self.name, {}).items()):
            if value.get(self.filter.field_path) == self.filter.value:
                yield Document(self.db, self.name, key).get(transaction)


class Collection:
    def __init__(self, db, name):
        self.db, self.name = db, name

    def document(self, key):
        return Document(self.db, self.name, key)

    def where(self, *, filter):
        return Query(self.db, self.name, filter)


class Database(BaseDatabase):
    def __init__(self):
        super().__init__()
        self.queries = []

    def collection(self, name):
        return Collection(self, name)


DRAFT = {'answers': [{'question_id': 'gender', 'selected_option': 'Male'}],
         'currentQuestionId': 'body_type_male'}


class Fixture:
    def setUp(self):
        self.db = Database()
        decorator = patch.object(state.firestore, 'transactional', transactional)
        decorator.start()
        self.addCleanup(decorator.stop)

    @staticmethod
    def garment(key, kind='shirt', **changes):
        return {'id': key, 'userId': 'owner', 'type': kind,
                'imageUrl': 'https://example.test/' + key, **changes}

    def capsule(self):
        for number in range(10):
            item = self.garment(str(number), ['shirt', 'pants', 'shoes'][number % 3])
            self.db.seed('wardrobe', item['id'], item)


class OnboardingStateTests(Fixture, unittest.TestCase):
    def test_draft_is_private_single_document_write_without_collection_scans(self):
        result = state.save_onboarding_draft(self.db, 'owner', 0, DRAFT)
        self.assertEqual(result['revision'], 1)
        self.assertEqual(result['draft'], DRAFT)
        self.assertEqual(set(self.db.rows), {'onboarding_states'})
        self.assertEqual(set(self.db.rows['onboarding_states']), {'owner'})
        self.assertEqual(self.db.queries, [])

    def test_stale_different_draft_returns_latest_without_overwrite(self):
        state.save_onboarding_draft(self.db, 'owner', 0, DRAFT)
        before = copy.deepcopy(self.db.rows)
        with self.assertRaises(state.DraftRevisionConflict) as error:
            state.save_onboarding_draft(self.db, 'owner', 0, {'answers': [], 'currentQuestionId': 'gender'})
        self.assertEqual(error.exception.state['revision'], 1)
        self.assertEqual(self.db.rows, before)

    def test_lost_ack_retry_returns_same_revision_without_second_write(self):
        self.db.lose_ack = True
        with self.assertRaises(RuntimeError):
            state.save_onboarding_draft(self.db, 'owner', 0, DRAFT)
        versions = copy.deepcopy(self.db.versions)
        self.assertEqual(state.save_onboarding_draft(self.db, 'owner', 0, DRAFT)['revision'], 1)
        self.assertEqual(self.db.versions, versions)

    def test_concurrent_milestone_survives_draft_transaction_retry(self):
        self.db.before_commit = lambda db: db.seed('onboarding_states', 'owner', {
            'revision': 0, 'milestones': {'firstOutfitId': 'look'}})
        result = state.save_onboarding_draft(self.db, 'owner', 0, DRAFT)
        self.assertEqual(result['milestones']['firstOutfitId'], 'look')
        self.assertEqual(self.db.conflicts, 1)

    def test_read_merges_legacy_alias_and_rejects_conflicting_ownership_without_writes(self):
        self.db.seed('wardrobe', 'one', self.garment('one'))
        self.db.seed('wardrobe', 'two', {'user_id': 'owner', 'type': 'pants', 'imageUrl': 'https://example.test/two'})
        self.db.seed('wardrobe', 'foreign', self.garment('foreign', userId='other'))
        self.db.seed('wardrobe', 'conflict', self.garment('conflict', user_id='other'))
        before = copy.deepcopy(self.db.rows)
        self.assertEqual(state.read_onboarding_state(self.db, 'owner')['capsule']['usableCount'], 2)
        self.assertEqual(self.db.rows, before)
        self.assertEqual(set(self.db.queries), {('wardrobe', field) for field in
            ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId')} | {('outfits', 'userId'), ('outfits', 'user_id')})

    def test_ten_items_require_style_and_coverage_and_milestone_is_durable(self):
        self.capsule()
        self.assertEqual(state.reconcile_onboarding_state(self.db, 'owner')['stage'], 'style')
        self.assertNotIn('onboarding_states', self.db.rows)
        self.db.seed('users', 'owner', {'styleQuizCompletedAt': 1790092541000})
        result = state.reconcile_onboarding_state(self.db, 'owner')
        self.assertEqual(result['stage'], 'first-look')
        self.assertTrue(result['milestones']['capsuleCompletedAt'])
        versions = copy.deepcopy(self.db.versions)
        state.reconcile_onboarding_state(self.db, 'owner')
        self.assertEqual(self.db.versions, versions)
        self.db.rows['wardrobe'] = {}
        self.assertEqual(state.read_onboarding_state(self.db, 'owner')['stage'], 'first-look')

    def test_reconcile_preserves_newer_draft_after_concurrent_save(self):
        self.db.seed('users', 'owner', {'stylePreferences': ['Minimalist']})
        self.db.before_commit = lambda db: db.seed('onboarding_states', 'owner', {'revision': 7, 'draft': DRAFT})
        result = state.reconcile_onboarding_state(self.db, 'owner')
        self.assertEqual((result['revision'], result['draft']), (7, DRAFT))
        self.assertEqual(self.db.conflicts, 1)

    def test_empty_historic_outfit_and_client_flag_do_not_finish_onboarding(self):
        self.db.seed('users', 'owner', {'onboardingCompleted': True})
        self.db.seed('outfits', 'empty', {'userId': 'owner', 'items': []})
        result = state.reconcile_onboarding_state(self.db, 'owner')
        self.assertEqual(result['stage'], 'style')
        self.assertIsNone(result['milestones']['firstOutfitId'])

    def test_saved_item_ids_resolve_to_complete_look_and_milestone_survives_deletion(self):
        for key, kind in [('dress', 'dress'), ('shoes', 'shoes')]:
            self.db.seed('wardrobe', key, self.garment(key, kind))
        self.db.seed('outfits', 'look', {'user_id': 'owner', 'items': ['dress', 'shoes']})
        self.assertEqual(state.reconcile_onboarding_state(self.db, 'owner')['milestones']['firstOutfitId'], 'look')
        self.db.rows['outfits'] = {}
        self.db.rows['wardrobe'] = {}
        self.assertEqual(state.read_onboarding_state(self.db, 'owner')['stage'], 'complete')

    def test_duplicates_deleted_unknown_and_missing_images_do_not_pad_capsule(self):
        items = [self.garment('one', contentHash='same'), self.garment('two', contentHash='same'),
                 self.garment('one'), self.garment('deleted', deleted=True), self.garment('unknown', 'unknown'),
                 self.garment('no-image', imageUrl=''), self.garment('shoes', 'shoes')]
        result = state.evaluate_capsule(items)
        self.assertEqual((result['savedCount'], result['usableCount'], result['missingCategories']), (5, 2, ['bottom or one-piece']))
        self.assertFalse(result['ready'])

    def test_draft_bounds_use_utf16_and_reject_duplicate_questions(self):
        for value in [{'answers': DRAFT['answers'] * 2, 'currentQuestionId': None},
                      {'answers': [], 'currentQuestionId': '../bad'},
                      {'answers': [{'question_id': 'gender', 'selected_option': '😀' * 1001}], 'currentQuestionId': None}]:
            self.assertIsNone(state.parse_draft(value))
        self.assertEqual(state.parse_draft(DRAFT), DRAFT)


class OnboardingHTTPTests(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        app = FastAPI()
        app.include_router(api.router, prefix='/api/onboarding')
        self.client = TestClient(app)
        database = patch.object(api, 'database', return_value=self.db)
        database.start()
        self.addCleanup(database.stop)
        auth = patch.object(verified_user.auth, 'verify_id_token', return_value={'uid': 'owner'})
        self.verify = auth.start()
        self.addCleanup(auth.stop)
        self.headers = {'Authorization': 'Bearer signed-token'}

    def test_verifies_revocation_and_rejects_body_header_query_identity_override(self):
        self.assertEqual(self.client.get('/api/onboarding', headers=self.headers).status_code, 200)
        self.verify.assert_called_once_with('signed-token', check_revoked=True)
        for key in ('userId', 'user_id', 'firebase_uid', 'uid'):
            self.assertEqual(self.client.post('/api/onboarding', headers=self.headers, json={key: 'other'}).status_code, 403)
            self.assertEqual(self.client.get('/api/onboarding?' + key + '=other', headers=self.headers).status_code, 403)
        self.assertEqual(self.client.get('/api/onboarding', headers={**self.headers, 'x-user-id': 'other'}).status_code, 403)
        self.assertEqual(self.db.rows, {})

    def test_invalid_revoked_disabled_deleted_anonymous_and_test_tokens_fail_closed(self):
        for error in (verified_user.auth.InvalidIdTokenError, verified_user.auth.RevokedIdTokenError,
                      verified_user.auth.UserDisabledError, verified_user.auth.UserNotFoundError):
            self.verify.side_effect = error('invalid')
            self.assertEqual(self.client.post('/api/onboarding', headers=self.headers).status_code, 401)
        self.verify.side_effect = None
        self.verify.return_value = {'uid': 'owner', 'firebase': {'sign_in_provider': 'anonymous'}}
        self.assertEqual(self.client.post('/api/onboarding', headers=self.headers).status_code, 403)
        for headers in ({}, {'Authorization': 'Bearer test'}):
            self.assertEqual(self.client.get('/api/onboarding', headers=headers).status_code, 401)
        self.assertEqual(self.db.rows, {})

    def test_storage_failure_and_sdk_transaction_exhaustion_are_retryable(self):
        self.db.fail_read = True
        for method in ('get', 'post'):
            self.assertEqual(getattr(self.client, method)('/api/onboarding', headers=self.headers).status_code, 503)
        with patch.object(api, 'save_onboarding_draft', side_effect=ValueError('Failed to commit after 5 attempts')):
            response = self.client.patch('/api/onboarding', headers=self.headers, json={'expectedRevision': 0, 'draft': DRAFT})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('5 attempts', response.text)

    def test_conflict_envelope_and_validation_remain_compatible(self):
        state.save_onboarding_draft(self.db, 'owner', 0, DRAFT)
        response = self.client.patch('/api/onboarding', headers=self.headers, json={
            'expectedRevision': 0, 'draft': {'answers': [], 'currentQuestionId': 'gender'}})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['state']['revision'], 1)
        self.assertEqual(response.json()['code'], 'revision_conflict')
        self.assertEqual(response.headers['cache-control'], 'private, no-store')
        for revision in (True, -1, 1.1, 2**53):
            self.assertEqual(self.client.patch('/api/onboarding', headers=self.headers,
                json={'expectedRevision': revision, 'draft': DRAFT}).status_code, 422)
        self.assertEqual(self.client.patch('/api/onboarding', headers=self.headers, content='{').status_code, 422)

    def test_client_completion_claims_are_ignored(self):
        response = self.client.post('/api/onboarding', headers=self.headers, json={
            'milestones': {'firstOutfitId': 'forged'}, 'capsule': {'usableCount': 100}, 'onboardingCompleted': True})
        self.assertEqual(response.json()['state']['stage'], 'style')
        self.assertEqual(self.db.rows, {})

    def test_integral_json_revision_matches_the_previous_javascript_contract(self):
        response = self.client.patch('/api/onboarding', headers=self.headers,
            json={'expectedRevision': 0.0, 'draft': DRAFT})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['state']['revision'], 1)
        self.assertIs(type(self.db.rows['onboarding_states']['owner']['revision']), int)
