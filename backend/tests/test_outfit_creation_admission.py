"""Server readiness, transactional outfit mutation, and deletion regressions."""
import copy
import logging
from types import ModuleType, SimpleNamespace
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch, Mock, AsyncMock

from fastapi import HTTPException, FastAPI
from fastapi.testclient import TestClient
from firebase_admin import firestore
from src.services.outfit_creation_admission import require_outfit_creation_ready, persist_created_outfit
from src.services.outfit_mutations import edit_owned_outfit, delete_owned_outfit, record_outfit_rating
from src.services.saved_outfit import read_saved_outfit, SavedOutfitNotFound
from test_onboarding_state import Fixture, Document
from test_outfit_wear import transactional


class AdmissionTests(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.db.seed('users', 'owner', {})
        self.db.creation_times = {}
        original_get = Document.get
        def get_with_creation_time(document, transaction=None):
            snapshot = original_get(document, transaction)
            snapshot.create_time = document.db.creation_times.get((document.collection_name, document.id))
            return snapshot
        creation_patch = patch.object(Document, 'get', get_with_creation_time)
        creation_patch.start(); self.addCleanup(creation_patch.stop)

    def ready(self):
        self.capsule()
        self.db.seed('users', 'owner', {'styleQuizCompletedAt': '2026-09-23T01:00:00Z', 'app_data_epoch': 0})
        return require_outfit_creation_ready(self.db, 'owner')

    def save(self, key='new', items=None, **kwargs):
        admission = require_outfit_creation_ready(self.db, 'owner')
        return persist_created_outfit(self.db, 'owner', key, {'name': 'My look', 'items': items or ['0', '1', '2']}, admission, **kwargs)

    def test_new_user_needs_both_style_and_ten_unique_usable_category_covered_items(self):
        self.capsule()
        self.db.rows['users']['owner'].update(onboardingCompleted=True, onboarding_completed=True)
        with self.assertRaises(HTTPException) as denied:
            require_outfit_creation_ready(self.db, 'owner')
        self.assertEqual(denied.exception.status_code, 409)
        self.assertEqual(denied.exception.detail['code'], 'onboarding_required')
        self.assertEqual(denied.exception.detail['resume'], '/onboarding')
        self.assertEqual(denied.exception.detail['stage'], 'style')
        self.ready()
        del self.db.rows['wardrobe']['9']
        with self.assertRaises(HTTPException) as denied:
            require_outfit_creation_ready(self.db, 'owner')
        self.assertEqual(denied.exception.detail['stage'], 'capsule')
        self.assertEqual(denied.exception.detail['capsule']['usableCount'], 9)

    def test_duplicate_images_unknown_categories_and_deleted_items_do_not_count(self):
        for mutation in ('duplicate', 'unknown', 'deleted', 'deleted-snake', 'no-photo', 'no-shoes'):
            self.ready()
            for garment in self.db.rows['wardrobe'].values():
                if mutation == 'duplicate': garment['contentHash'] = 'same-image'
                if mutation == 'unknown': garment['type'] = 'mystery'
                if mutation == 'deleted': garment['deletedAt'] = '2026-09-23'
                if mutation == 'deleted-snake': garment['deleted_at'] = '2026-09-23'
                if mutation == 'no-photo': garment.pop('imageUrl')
                if mutation == 'no-shoes': garment['type'] = 'shirt'
            with self.subTest(mutation=mutation), self.assertRaises(HTTPException):
                require_outfit_creation_ready(self.db, 'owner')
            self.db.rows['wardrobe'] = {}

    def test_protected_completed_milestone_preserves_historical_access(self):
        self.db.seed('onboarding_states', 'owner', {'milestones': {'capsuleCompletedAt': '2026-09-22T10:00:00Z'}})
        admission = require_outfit_creation_ready(self.db, 'owner')
        self.assertTrue(admission['grandfathered'])
        self.assertEqual(admission['capsule']['usableCount'], 0)

    def test_only_valid_owned_historical_outfit_before_fixed_cutoff_grandfathers(self):
        for i, kind in enumerate(('shirt', 'pants', 'shoes')):
            self.db.seed('wardrobe', str(i), self.garment(str(i), kind))
        self.db.seed('outfits', 'prior', {'user_id': 'owner', 'items': ['0', '1', '2'], 'createdAt': '2026-09-22T10:00:00Z'})
        self.db.creation_times[('outfits', 'prior')] = '2026-09-22T10:00:00Z'
        self.assertTrue(require_outfit_creation_ready(self.db, 'owner')['grandfathered'])
        self.db.creation_times[('outfits', 'prior')] = '2026-09-23T01:00:00Z'
        with self.assertRaises(HTTPException): require_outfit_creation_ready(self.db, 'owner')
        self.db.creation_times[('outfits', 'prior')] = None
        with self.assertRaises(HTTPException): require_outfit_creation_ready(self.db, 'owner')
        self.db.creation_times[('outfits', 'prior')] = '2026-09-22T10:00:00Z'
        for changes in ({'createdAt': '2026-09-22T10:00:00Z', 'userId': 'foreign'},
                        {'userId': 'owner', 'items': ['0']}):
            self.db.rows['outfits']['prior'].update(changes)
            with self.subTest(changes=changes), self.assertRaises(HTTPException):
                require_outfit_creation_ready(self.db, 'owner')

    def test_invalid_cutoff_never_broadens_historical_access(self):
        self.ready()
        self.db.rows['users']['owner'].pop('styleQuizCompletedAt')
        self.db.seed('outfits', 'prior', {'user_id': 'owner', 'items': ['0', '1', '2'], 'createdAt': '2026-09-22T10:00:00Z'})
        with patch.dict('os.environ', {'EASYOUTFIT_ONBOARDING_GRANDFATHER_CUTOFF': 'invalid'}):
            with self.assertRaises(HTTPException): require_outfit_creation_ready(self.db, 'owner')

    def test_manual_one_and_two_piece_saves_use_only_current_owned_garments(self):
        self.ready()
        for count in (1, 2):
            result = self.save(str(count), [{'id': str(i), 'imageUrl': 'https://forged.invalid', 'name': 'forged'} for i in range(count)], require_complete=False)
            self.assertEqual(len(result['items']), count)
            self.assertEqual(result['items'][0]['imageUrl'], 'https://example.test/0')
            self.assertNotIn('forged', str(result))
            self.assertEqual(result['flat_lay_status'], 'awaiting_consent')

    def test_all_supported_legacy_owner_aliases_are_ready_and_usable_at_final_save(self):
        self.ready()
        aliases = ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId')
        for index, garment in enumerate(self.db.rows['wardrobe'].values()):
            garment.pop('userId')
            garment[aliases[index % len(aliases)]] = 'owner'
        self.assertEqual(require_outfit_creation_ready(self.db, 'owner')['capsule']['usableCount'], 10)
        saved = self.save(items=['2', '3', '4'])
        self.assertEqual({item['id'] for item in saved['items']}, {'2', '3', '4'})
        self.assertTrue(read_saved_outfit(self.db, saved['id'], 'owner')['items_available'])

    def test_foreign_missing_duplicate_or_imageless_selected_garments_reject_atomically(self):
        self.ready()
        for items in (['foreign'], ['missing'], ['0', '0']):
            self.db.seed('wardrobe', 'foreign', self.garment('foreign', userId='other'))
            with self.subTest(items=items), self.assertRaises(HTTPException):
                self.save(items=items, require_complete=False)
            self.assertNotIn('new', self.db.rows.get('outfits', {}))
        self.db.rows['wardrobe']['0'].pop('imageUrl')
        self.db.seed('onboarding_states', 'owner', {'milestones': {'firstOutfitId': 'old'}})
        with self.assertRaises(HTTPException): self.save(items=['0'], require_complete=False)

    def test_deletion_epoch_and_readiness_rechecked_before_final_save(self):
        admission = self.ready()
        self.db.seed('users', 'owner', {**self.db.rows['users']['owner'], 'app_data_epoch': 1})
        with self.assertRaises(HTTPException):
            persist_created_outfit(self.db, 'owner', 'new', {'items': ['0', '1', '2']}, admission)
        admission = require_outfit_creation_ready(self.db, 'owner')
        del self.db.rows['wardrobe']['9']
        with self.assertRaises(HTTPException):
            persist_created_outfit(self.db, 'owner', 'new', {'items': ['0', '1', '2']}, admission)
        self.assertNotIn('new', self.db.rows.get('outfits', {}))

    def test_generated_completeness_checked_against_current_categories_at_commit(self):
        admission = self.ready()
        # Keep capsule coverage through other records, but invalidate this choice.
        self.db.rows['wardrobe']['2']['type'] = 'shirt'
        with self.assertRaises(HTTPException) as error:
            persist_created_outfit(self.db, 'owner', 'new', {'items': ['0', '1', '2']}, admission)
        self.assertEqual(error.exception.status_code, 422)
        self.assertNotIn('new', self.db.rows.get('outfits', {}))

    def test_edit_invalidates_old_preview_but_keeps_active_ledger_held(self):
        self.ready(); self.save()
        ledger = {'user_id': 'owner', 'outfit_id': 'new', 'request_id': 'r1', 'status': 'processing', 'credit_status': 'reserved'}
        self.db.seed('flat_lay_requests', 'new', ledger)
        edit_owned_outfit(self.db, 'new', 'owner', {'items': ['0', '1', '5'], 'notes': 'Updated'})
        outfit = self.db.rows['outfits']['new']
        self.assertEqual(outfit['flat_lay_status'], 'processing')
        self.assertFalse(outfit['flat_lay_request_allowed'])
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertEqual(self.db.rows['flat_lay_requests']['new'], ledger)

    def test_edit_rejects_authority_fields_and_foreign_or_deleted_outfits(self):
        self.ready(); self.save()
        for update in ({'user_id': 'other'}, {'flat_lay_status': 'done'}, {'wearCount': 9}, {'items': ['0', 'missing']}):
            with self.assertRaises(HTTPException): edit_owned_outfit(self.db, 'new', 'owner', update)
        with self.assertRaises(HTTPException): edit_owned_outfit(self.db, 'new', 'other', {'notes': 'x'})
        delete_owned_outfit(self.db, 'new', 'owner')
        with self.assertRaises(HTTPException): edit_owned_outfit(self.db, 'new', 'owner', {'notes': 'x'})

    def test_soft_delete_keeps_history_and_retries_normal_pending_settlement(self):
        self.ready(); self.save()
        history = {'user_id': 'owner', 'outfit_id': 'new', 'items': ['0', '1', '2'], 'date': '2026-09-22'}
        self.db.seed('outfit_history', 'wear', history)
        self.db.seed('flat_lay_requests', 'new', {'user_id': 'owner', 'outfit_id': 'new', 'request_id': 'r1', 'status': 'pending'})
        with patch('src.services.outfit_mutations.finish_request', side_effect=[RuntimeError('temporary'), True]) as finish:
            with self.assertRaises(RuntimeError): delete_owned_outfit(self.db, 'new', 'owner')
            self.assertTrue(self.db.rows['outfits']['new']['deleted'])
            self.assertTrue(delete_owned_outfit(self.db, 'new', 'owner')['deleted'])
            self.assertEqual(finish.call_count, 2)
            self.assertEqual(finish.call_args.args, (self.db, 'new', 'r1'))
            self.assertFalse(finish.call_args.kwargs['retryable'])
        self.assertEqual(self.db.rows['outfit_history']['wear'], history)
        with self.assertRaises(SavedOutfitNotFound): read_saved_outfit(self.db, 'new', 'owner')

    def test_soft_delete_refunds_the_private_pending_reservation_only_once(self):
        from test_flatlay_lifecycle import Database, transactional as flatlay_transaction
        from src.services import flatlay_lifecycle as lifecycle
        db = Database()
        now = int(datetime.now(timezone.utc).timestamp())
        db.records['users']['owner']['quotas']['lastRefillAt'] = now
        db.records['outfit_history'] = {'wear': {'user_id': 'owner', 'outfit_id': 'look', 'items': ['shirt', 'pants']}}
        with patch.object(firestore, 'transactional', flatlay_transaction):
            request = lifecycle.reserve_request(db, 'look', 'owner', now=now)
            self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)
            self.assertTrue(delete_owned_outfit(db, 'look', 'owner')['deleted'])
            self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)
            self.assertEqual(db.records['flat_lay_requests']['look']['credit_status'], 'refunded')
            self.assertTrue(delete_owned_outfit(db, 'look', 'owner')['deleted'])
            self.assertFalse(lifecycle.finish_request(db, 'look', request['request_id'], url='https://late.invalid'))
        self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)
        self.assertEqual(db.records['outfit_history']['wear']['items'], ['shirt', 'pants'])
        self.assertIsNone(db.records['outfits']['look'].get('flat_lay_url'))

    def test_rating_retries_and_edits_preserve_first_submission_and_reward_identity(self):
        self.ready(); self.save()
        now = datetime(2026, 9, 23, 12, tzinfo=timezone.utc)
        first = record_outfit_rating(self.db, 'owner', 'new', {'rating': 5}, now=now)
        retry = record_outfit_rating(self.db, 'owner', 'new', {'rating': 5}, now=now + timedelta(days=1))
        self.assertFalse(retry['changed'])
        changed = record_outfit_rating(self.db, 'owner', 'new', {'rating': 2, 'feedback': 'Too warm'}, now=now + timedelta(days=2))
        self.assertTrue(changed['changed'])
        self.assertEqual(changed['reward_operation_id'], first['reward_operation_id'])
        feedback = self.db.rows['outfit_feedback'][first['feedback_id']]
        self.assertEqual(feedback['created_at'], now.isoformat())
        self.assertEqual(feedback['updated_at'], (now + timedelta(days=2)).isoformat())
        self.assertEqual(feedback['rating'], 2)
        self.assertEqual(len(self.db.rows['outfit_feedback']), 1)
        self.assertEqual(self.db.rows['outfits']['new']['userFeedback'], 'Too warm')

    def test_concurrent_rating_retries_create_one_immutable_feedback_event(self):
        self.ready(); self.save()
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(lambda _: record_outfit_rating(self.db, 'owner', 'new', {'isLiked': True}), range(8)))
        self.assertEqual(sum(result['created'] for result in results), 1)
        self.assertEqual(sum(result['changed'] for result in results), 1)
        self.assertEqual(len({result['reward_operation_id'] for result in results}), 1)

    def test_rating_rejects_invalid_foreign_conflicting_deleted_and_deletion_in_progress(self):
        self.ready(); self.save()
        for invalid in ({}, {'rating': 0}, {'rating': True}, {'rating': 6}, {'isLiked': True, 'isDisliked': True}, {'created_at': 'past'}):
            with self.subTest(invalid=invalid), self.assertRaises(HTTPException):
                record_outfit_rating(self.db, 'owner', 'new', invalid)
        self.db.seed('users', 'other', {})
        with self.assertRaises(HTTPException): record_outfit_rating(self.db, 'other', 'new', {'rating': 5})
        self.db.rows['outfits']['new']['userId'] = 'other'
        with self.assertRaises(HTTPException): record_outfit_rating(self.db, 'owner', 'new', {'rating': 5})
        self.db.rows['outfits']['new']['userId'] = 'owner'
        self.db.rows['users']['owner']['app_data_deletion'] = {'status': 'running', 'epoch': 0}
        with self.assertRaises(HTTPException) as blocked: record_outfit_rating(self.db, 'owner', 'new', {'rating': 5})
        self.assertEqual(blocked.exception.status_code, 409)
        del self.db.rows['users']['owner']['app_data_deletion']
        delete_owned_outfit(self.db, 'new', 'owner')
        with self.assertRaises(HTTPException): record_outfit_rating(self.db, 'owner', 'new', {'rating': 5})
        self.assertEqual(self.db.rows.get('outfit_feedback', {}), {})

    def test_old_edit_rating_and_delete_retries_cannot_modify_recreated_outfit_after_clear(self):
        for operation in ('edit', 'rating', 'delete'):
            self.ready()
            outfit_id = 'new-' + operation
            self.save(key=outfit_id)
            replacement = {**self.db.rows['outfits'][outfit_id], 'name': 'New account-data epoch look', 'app_data_epoch': 1}
            def clear_and_recreate(db):
                db.seed('users', 'owner', {**db.rows['users']['owner'], 'app_data_epoch': 1,
                    'app_data_deletion': {'status': 'complete', 'epoch': 1}})
                db.seed('outfits', outfit_id, replacement)
            self.db.before_commit = clear_and_recreate
            with self.subTest(operation=operation), self.assertRaises(HTTPException) as blocked:
                if operation == 'edit':
                    edit_owned_outfit(self.db, outfit_id, 'owner', {'name': 'Stale old form'})
                elif operation == 'rating':
                    record_outfit_rating(self.db, 'owner', outfit_id, {'rating': 5})
                else:
                    delete_owned_outfit(self.db, outfit_id, 'owner')
            self.assertEqual(blocked.exception.status_code, 409)
            self.assertEqual(self.db.rows['outfits'][outfit_id], replacement)
            self.assertEqual(self.db.rows.get('outfit_feedback', {}), {})

    def test_general_generation_http_denies_unready_user_before_provider(self):
        from src.routes.outfits.routes import router, get_current_user_id
        app = FastAPI(); app.include_router(router, prefix='/api/outfits')
        app.dependency_overrides[get_current_user_id] = lambda: 'owner'
        firebase = ModuleType('src.config.firebase'); firebase.db = self.db; firebase.firebase_initialized = True
        with patch.dict('sys.modules', {'src.config.firebase': firebase}), patch('src.routes.outfits.routes.get_generate_outfit_logic') as provider, TestClient(app) as client:
            response = client.post('/api/outfits/generate', json={'occasion': 'Casual', 'style': 'Classic', 'mood': 'Relaxed', 'wardrobe': []})
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(response.json()['detail']['code'], 'onboarding_required')
        provider.assert_not_called()

    def test_rating_http_rewards_once_and_keeps_saved_rating_when_learning_unavailable(self):
        from src.routes.outfits.routes import router, get_current_user_id
        from src.services.reward_ledger import award
        self.ready(); self.save()
        app = FastAPI(); app.include_router(router, prefix='/api/outfits')
        app.dependency_overrides[get_current_user_id] = lambda: 'owner'
        firebase = ModuleType('src.config.firebase'); firebase.db = self.db; firebase.firebase_initialized = True
        preference = ModuleType('src.services.user_preference_service')
        preference.user_preference_service = SimpleNamespace(update_from_rating=AsyncMock(side_effect=RuntimeError('optional learning unavailable')))
        gamification = ModuleType('src.services.gamification_service')
        async def award_xp(user_id, amount, reason, metadata):
            return award(self.db, user_id, metadata['reward_operation_id'], xp=amount, metadata=metadata,
                         expected_epoch=metadata['app_data_epoch'])
        gamification.gamification_service = SimpleNamespace(award_xp=award_xp)
        with patch.dict('sys.modules', {'src.config.firebase': firebase,
            'src.services.user_preference_service': preference, 'src.services.gamification_service': gamification}), TestClient(app) as client:
            first = client.post('/api/outfits/rate', json={'outfitId': 'new', 'rating': 5})
            second = client.post('/api/outfits/rate', json={'outfitId': 'new', 'rating': 5})
            self.assertEqual(first.status_code, 200, first.text)
            self.assertEqual(second.status_code, 200, second.text)
            self.assertEqual(first.json()['xp_earned'], 5)
            self.assertEqual(second.json()['xp_earned'], 0)
            for payload in ({'rating': 0}, {'rating': True}, {'isLiked': 'true'}, {'created_at': 'backdate'}):
                self.assertEqual(client.post('/api/outfits/rate', json={'outfitId': 'new', **payload}).status_code, 422)
        self.assertEqual(self.db.rows['outfits']['new']['rating'], 5)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 5)
        self.assertEqual(len(self.db.rows['reward_ledger']), 1)
        preference.user_preference_service.update_from_rating.assert_awaited_once()
        self.assertEqual(preference.user_preference_service.update_from_rating.call_args.kwargs['expected_epoch'], 0)
