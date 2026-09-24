"""Post-commit rating failures must recover once without new user interaction."""
import copy
import threading
from concurrent.futures import ThreadPoolExecutor
from test_outfit_wear import WearTestFixture
from src.services.outfit_mutations import record_outfit_rating
from src.services.feedback_rewards import settle_feedback_reward
from src.services.reward_ledger import award
from src.services.app_data_privacy import AppDataDeletionError


class FeedbackRewardRecoveryTests(WearTestFixture):
    def save(self):
        return record_outfit_rating(self.db, 'owner', 'look', {'rating': 5}, now=self.now)

    def settle(self, saved):
        return settle_feedback_reward(self.db, 'owner', saved['feedback_id'], expected_epoch=saved['app_data_epoch'])

    def test_committed_feedback_survives_reward_failure_and_recovers_once(self):
        saved = self.save()
        self.assertTrue(self.db.rows['outfit_feedback'][saved['feedback_id']]['reward_pending'])
        before = copy.deepcopy(self.db.rows)
        for write in range(3):
            self.db.fail_at_write = write
            with self.assertRaises(RuntimeError): self.settle(saved)
            self.assertEqual(self.db.rows, before)
        self.db.fail_at_write = None
        self.assertEqual(self.settle(saved)['xp_awarded'], 5)
        self.assertEqual(self.settle(saved)['xp_awarded'], 0)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 5)
        self.assertFalse(self.db.rows['outfit_feedback'][saved['feedback_id']]['reward_pending'])
        self.assertEqual(len(self.db.rows['reward_ledger']), 1)

    def test_concurrent_api_and_worker_grant_only_once(self):
        saved = self.save()
        self.db.barrier = threading.Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.settle(saved), range(2)))
        self.assertEqual(sorted(result['xp_awarded'] for result in results), [0, 5])
        self.assertEqual(self.db.rows['users']['owner']['xp'], 5)

    def test_old_successful_ledger_clears_marker_without_reaward(self):
        saved = self.save()
        award(self.db, 'owner', saved['reward_operation_id'], xp=5, expected_epoch=0)
        self.assertEqual(self.settle(saved)['xp_awarded'], 0)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 5)
        self.assertFalse(self.db.rows['outfit_feedback'][saved['feedback_id']]['reward_pending'])

    def test_later_feedback_edits_do_not_create_another_reward(self):
        saved = self.save(); self.settle(saved)
        edited = record_outfit_rating(self.db, 'owner', 'look', {'rating': 4})
        self.assertEqual(self.settle(edited)['xp_awarded'], 0)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 5)
        self.assertEqual(self.db.rows['outfit_feedback'][saved['feedback_id']]['created_at'], self.now.isoformat())

    def test_epoch_reset_foreign_record_and_unmarked_history_never_receive_rewards(self):
        saved = self.save()
        row = self.db.rows['outfit_feedback'][saved['feedback_id']]
        for key, value in [('user_id', 'other'), ('reward_operation_id', None), ('app_data_epoch', 7)]:
            prior = row.get(key); row[key] = value
            self.assertFalse(self.settle(saved)['success'])
            row[key] = prior
        self.db.rows['users']['owner']['app_data_epoch'] = 1
        with self.assertRaises(AppDataDeletionError): self.settle(saved)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 0)

    def test_feedback_and_pending_marker_commit_together(self):
        before = copy.deepcopy(self.db.rows)
        self.db.fail_at_write = 1
        with self.assertRaises(RuntimeError): self.save()
        self.assertEqual(self.db.rows, before)

    def test_fresh_worker_preserves_pending_xp_across_completed_analytics_clear_only(self):
        from src.services.app_data_privacy import JOBS
        saved = self.save()
        self.db.rows['users']['owner'].update(app_data_epoch=1, app_data_deletion={'job_id': 'analytics-1', 'status': 'complete'})
        self.db.seed(JOBS, 'analytics-1', {'user_id': 'owner', 'epoch': 1, 'scope': 'analytics', 'status': 'complete'})
        with self.assertRaises(AppDataDeletionError): self.settle(saved)
        result = settle_feedback_reward(self.db, 'owner', saved['feedback_id'], expected_epoch=1)
        self.assertEqual(result['xp_awarded'], 5)
        self.assertEqual(self.db.rows['outfit_feedback'][saved['feedback_id']]['app_data_epoch'], 1)

    def test_multiple_analytics_clears_require_complete_contiguous_owned_proof(self):
        from src.services.app_data_privacy import JOBS
        saved = self.save()
        self.db.rows['users']['owner'].update(app_data_epoch=2, app_data_deletion={'job_id': 'analytics-2', 'status': 'complete'})
        self.db.seed(JOBS, 'analytics-2', {'user_id': 'owner', 'epoch': 2, 'scope': 'analytics', 'status': 'complete'})
        def settle_current(): return settle_feedback_reward(self.db, 'owner', saved['feedback_id'], expected_epoch=2)
        self.assertFalse(settle_current()['success'])
        for invalid in ({'scope': 'outfits'}, {'status': 'running'}, {'user_id': 'foreign'}):
            self.db.seed(JOBS, 'analytics-1', {'user_id': 'owner', 'epoch': 1, 'scope': 'analytics', 'status': 'complete', **invalid})
            self.assertFalse(settle_current()['success'])
        self.db.seed(JOBS, 'analytics-1', {'user_id': 'owner', 'epoch': 1, 'scope': 'analytics', 'status': 'complete'})
        self.assertEqual(settle_current()['xp_awarded'], 5)
