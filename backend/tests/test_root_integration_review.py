"""Independent regressions for mutation/deletion races and cross-path wear state."""
import copy
from datetime import timedelta
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from firebase_admin import firestore
from src.services import user_profile, onboarding_state, quiz_profile, outfit_wear
from src.services.wardrobe_mutations import mutate_wardrobe
from test_user_profile import ProfileFixture
from test_onboarding_state import DRAFT
from test_quiz_profile import Database as QuizDatabase, Transaction as QuizTransaction, transactional as quiz_transactional, IDENTITY, payload
from test_outfit_wear import WearTestFixture
from test_app_data_privacy import Database as DeleteDatabase, transactional as delete_transactional


class ProfileEpochRaceTests(ProfileFixture):
    def clear_during_first_commit(self):
        self.db.before_commit = lambda db: db.seed('users', 'owner', {
            'app_data_epoch': 1, 'app_data_deletion': {'status': 'complete', 'epoch': 1}})

    def test_delayed_profile_transaction_cannot_restore_cleared_measurements(self):
        self.clear_during_first_commit()
        with self.assertRaises(HTTPException) as rejected:
            self.save({'measurements': {'height': 'old pre-clear answer'}})
        self.assertEqual(rejected.exception.status_code, 409)
        self.assertNotIn('measurements', self.stored)

    def test_delayed_draft_transaction_cannot_recreate_deleted_questionnaire(self):
        self.clear_during_first_commit()
        with self.assertRaises(HTTPException) as rejected:
            onboarding_state.save_onboarding_draft(self.db, 'owner', 0, copy.deepcopy(DRAFT))
        self.assertEqual(rejected.exception.status_code, 409)
        self.assertNotIn('onboarding_states', self.db.rows)

    def test_onboarding_reconcile_rejects_epoch_change_instead_of_acknowledging_old_session(self):
        self.clear_during_first_commit()
        with self.assertRaises(HTTPException) as rejected:
            onboarding_state.reconcile_onboarding_state(self.db, 'owner')
        self.assertEqual(rejected.exception.status_code, 409)
        self.assertNotIn('onboarding_states', self.db.rows)

    def test_onboarding_read_and_transactional_reconcile_count_all_legacy_owner_aliases(self):
        aliases = ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId')
        for index in range(10):
            self.db.seed('wardrobe', str(index), {'id': str(index), aliases[index % 5]: 'owner',
                'type': ('shirt', 'pants', 'shoes')[index % 3], 'imageUrl': f'https://owned.test/{index}'})
        self.db.seed('wardrobe', 'conflict', {'userId': 'owner', 'ownerId': 'other', 'type': 'shoes', 'imageUrl': 'https://owned.test/conflict'})
        for state in (onboarding_state.read_onboarding_state(self.db, 'owner'),
                      onboarding_state.reconcile_onboarding_state(self.db, 'owner')):
            self.assertEqual(state['capsule']['usableCount'], 10)
            self.assertTrue(state['capsule']['ready'])
        self.assertTrue(self.db.rows['onboarding_states']['owner']['milestones']['capsuleCompletedAt'])


class QuizEpochRaceTests(unittest.TestCase):
    def test_completed_clear_between_transaction_attempts_rejects_old_quiz(self):
        db = QuizDatabase({'app_data_epoch': 0})
        original = QuizTransaction.commit
        fired = False
        def clear_before_commit(transaction):
            nonlocal fired
            if not fired:
                fired = True
                transaction.db.rows[('users', IDENTITY['uid'])] = {
                    'app_data_epoch': 1, 'app_data_deletion': {'status': 'complete', 'epoch': 1}}
                transaction.db.version += 1
            return original(transaction)
        with patch.object(firestore, 'transactional', quiz_transactional), patch.object(QuizTransaction, 'commit', clear_before_commit):
            with self.assertRaises(quiz_profile.QuizSubmissionError) as rejected:
                quiz_profile.save_quiz_profile(db, IDENTITY, payload())
        self.assertEqual(rejected.exception.status_code, 409)
        self.assertNotIn('styleQuizCompletedAt', db.profile)


class CrossPathWearTests(WearTestFixture):
    def test_undo_outfit_preserves_later_standalone_garment_wear(self):
        recorded = self.record()
        later = self.now + timedelta(days=1)
        standalone = mutate_wardrobe(self.db, 'owner', 'dress', 'wear',
                                    idempotency_key='individual-wear', now=later)
        result = outfit_wear.undo_wear(self.db, 'owner', recorded['event_id'], now=later + timedelta(minutes=1))
        self.assertTrue(result['undone'])
        garment = self.db.rows['wardrobe']['dress']
        self.assertEqual(garment['wearCount'], standalone['newWearCount'] - 1)
        self.assertIsNotNone(garment['lastWorn'], 'Undo must retain the later standalone wear timestamp')
        self.assertEqual(outfit_wear._timestamp_ms(garment['lastWorn']), int(later.timestamp() * 1000))


class AtomicWardrobeDeletionReviewTests(unittest.TestCase):
    def setUp(self):
        self.db = DeleteDatabase({'users/owner': {'app_data_epoch': 0, 'wardrobeItemCount': 3},
                                 'wardrobe/shirt': {'userId': 'owner', 'name': 'Shirt'},
                                 'wardrobe/foreign': {'userId': 'other'}})
        transaction = patch.object(firestore, 'transactional', delete_transactional)
        transaction.start(); self.addCleanup(transaction.stop)

    def test_repeat_delete_decrements_count_once_and_keeps_owned_receipt(self):
        first = mutate_wardrobe(self.db, 'owner', 'shirt', 'delete')
        second = mutate_wardrobe(self.db, 'owner', 'shirt', 'delete')
        self.assertFalse(first['already_deleted'])
        self.assertTrue(second['already_deleted'])
        self.assertEqual(self.db.rows['users/owner']['wardrobeItemCount'], 2)
        self.assertNotIn('wardrobe/shirt', self.db.rows)
        receipts = [value for key, value in self.db.rows.items() if key.startswith('wardrobe_deletion_receipts/')]
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]['user_id'], 'owner')

    def test_failed_delete_commit_preserves_item_count_and_receipt_then_retry_succeeds(self):
        before = copy.deepcopy(self.db.rows)
        self.db.fail_once = True
        with self.assertRaises(RuntimeError):
            mutate_wardrobe(self.db, 'owner', 'shirt', 'delete')
        self.assertEqual(self.db.rows, before)
        self.assertTrue(mutate_wardrobe(self.db, 'owner', 'shirt', 'delete')['deleted'])
        self.assertEqual(self.db.rows['users/owner']['wardrobeItemCount'], 2)

    def test_foreign_delete_and_negative_count_do_not_corrupt_aggregate(self):
        with self.assertRaises(HTTPException) as foreign:
            mutate_wardrobe(self.db, 'owner', 'foreign', 'delete')
        self.assertEqual(foreign.exception.status_code, 403)
        self.db.rows['users/owner']['wardrobeItemCount'] = 0
        mutate_wardrobe(self.db, 'owner', 'shirt', 'delete')
        self.assertEqual(self.db.rows['users/owner']['wardrobeItemCount'], 0)
        self.assertIn('wardrobe/foreign', self.db.rows)

    def test_soft_deleted_garment_cannot_be_edited_or_worn_but_can_be_removed(self):
        for marker in ('deleted', 'isDeleted', 'deletedAt', 'deleted_at'):
            self.db.rows['wardrobe/shirt'] = {'userId': 'owner', marker: True}
            for operation in ('edit', 'wear'):
                with self.subTest(marker=marker, operation=operation), self.assertRaises(HTTPException) as rejected:
                    mutate_wardrobe(self.db, 'owner', 'shirt', operation, {'name': 'Restore'})
                self.assertEqual(rejected.exception.status_code, 404)
        self.assertTrue(mutate_wardrobe(self.db, 'owner', 'shirt', 'delete')['deleted'])
