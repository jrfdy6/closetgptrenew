"""Badge facts and the canonical award commit share owner, epoch and snapshot."""
import asyncio
import importlib.util
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock, patch

from test_outfit_wear import WearTestFixture
from src.services import reward_ledger, wardrobe_reads
from src.services.app_data_privacy import AppDataDeletionError


class BadgeEligibilityTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        self.db.rows['wardrobe'] = {}
        config = ModuleType('src.config.firebase')
        config.db = self.db
        path = Path(__file__).parents[1] / 'src/services/gamification_service.py'
        spec = importlib.util.spec_from_file_location('src.services.isolated_badge_eligibility', path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'src.config.firebase': config}):
            spec.loader.exec_module(self.module)
        self.service = self.module.GamificationService()
        self.service.db = self.db

    def garments(self, count):
        for i in range(count):
            alias = wardrobe_reads.OWNER_FIELDS[i % len(wardrobe_reads.OWNER_FIELDS)]
            self.db.seed('wardrobe', f'item-{i:03}', {alias: 'owner'})

    def check(self, **kwargs):
        return asyncio.run(self.service.check_badge_unlock_conditions('owner', **kwargs))

    def test_legacy_owned_items_count_once_and_replay_cannot_reaward(self):
        self.garments(10)
        self.db.rows['wardrobe']['item-000'].update(user_id='owner', ownerId='owner')
        self.assertEqual(self.check(), ['starter_closet'])
        self.assertEqual(self.check(), [])
        self.assertEqual(self.db.rows['users']['owner']['badges'], ['starter_closet'])
        self.assertEqual(len(self.db.rows['reward_ledger']), 1)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 0)

    def test_deleted_conflicting_or_foreign_garments_do_not_meet_threshold(self):
        self.garments(9)
        self.db.seed('wardrobe', 'deleted', {'userId': 'owner', 'deleted_at': 1})
        self.db.seed('wardrobe', 'conflict', {'userId': 'owner', 'uid': 'other'})
        self.db.seed('wardrobe', 'foreign', {'userId': 'other'})
        self.assertEqual(self.check(), [])
        self.assertNotIn('reward_ledger', self.db.rows)

    def test_feedback_badges_require_owned_active_records(self):
        for i in range(24):
            self.db.seed('outfit_feedback', str(i), {'user_id': 'owner'})
        self.db.seed('outfit_feedback', 'deleted', {'user_id': 'owner', 'deleted': True})
        self.db.seed('outfit_feedback', 'conflict', {'user_id': 'owner', 'userId': 'other'})
        self.assertEqual(self.check(), [])
        self.db.seed('outfit_feedback', 'last', {'user_id': 'owner'})
        self.assertEqual(self.check(), ['style_contributor'])

    def test_source_changes_during_transaction_are_rechecked(self):
        self.garments(10)
        def remove_item(database):
            database.seed('wardrobe', 'item-009', {'userId': 'owner', 'deletedAt': 1})
        self.db.before_commit = remove_item
        self.assertEqual(self.check(), [])
        self.assertGreater(self.db.conflicts, 0)
        self.assertNotIn('reward_ledger', self.db.rows)

    def test_completed_clear_during_transaction_cannot_award_new_epoch(self):
        self.garments(10)
        def clear(database):
            database.seed('users', 'owner', {'xp': 0, 'app_data_epoch': 1})
        self.db.before_commit = clear
        with self.assertLogs(self.module.logger, 'ERROR'), self.assertRaises(AppDataDeletionError):
            self.check(expected_epoch=0)
        self.assertEqual(self.db.rows['users']['owner'], {'xp': 0, 'app_data_epoch': 1})
        self.assertNotIn('reward_ledger', self.db.rows)

    def test_default_operation_keeps_epoch_between_badge_checks(self):
        self.garments(50)
        original = self.service.unlock_badge
        calls = []
        async def clear_after_first(uid, badge, **kwargs):
            calls.append(kwargs['expected_epoch'])
            result = await original(uid, badge, **kwargs)
            if len(calls) == 1:
                self.db.seed('users', 'owner', {'xp': 0, 'app_data_epoch': 1})
            return result
        with patch.object(self.service, 'unlock_badge', clear_after_first), self.assertLogs(self.module.logger, 'ERROR'):
            self.assertEqual(self.check(), [])
        self.assertEqual(calls, [0, 0])
        self.assertNotIn('badges', self.db.rows['users']['owner'])
        self.assertEqual(len(self.db.rows['reward_ledger']), 1)

    def test_direct_unlock_uses_caller_epoch_and_prior_receipt_skips_fact_queries(self):
        self.db.seed('users', 'owner', {'xp': 0, 'app_data_epoch': 1})
        with self.assertRaises(AppDataDeletionError):
            asyncio.run(self.service.unlock_badge('owner', 'starter_closet', expected_epoch=0))
        ref = reward_ledger.key_for('owner', 'badge-starter_closet')
        self.db.seed('reward_ledger', ref, {'user_id': 'owner'})
        condition = Mock(side_effect=AssertionError('prior receipt must not query facts'))
        result = asyncio.run(self.service.unlock_badge('owner', 'starter_closet', expected_epoch=1, _eligibility_check=condition))
        self.assertTrue(result['already_unlocked'])
        self.assertFalse(result['success'])
        condition.assert_not_called()
        self.assertNotIn('badges', self.db.rows['users']['owner'])
