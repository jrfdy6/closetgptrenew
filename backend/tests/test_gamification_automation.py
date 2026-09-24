"""Clock-driven, no-credential automation failure and calendar regressions."""
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
from unittest.mock import Mock, patch
from zoneinfo import ZoneInfo

from test_outfit_wear import WearTestFixture
from src.worker import gamification_tasks as tasks

actual_weekly_generation = tasks.weekly_challenge_generation_task


class AutomationTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        self.now = datetime(2026, 12, 31, 23, 59, tzinfo=timezone.utc)
        self.weekly = patch.object(tasks, 'weekly_challenge_generation_task', return_value='fixture')
        self.weekly_mock = self.weekly.start()
        self.addCleanup(self.weekly.stop)

    def job(self, key='job', **overrides):
        value = {'user_id': 'owner', 'app_data_epoch': 0, 'activation_ms': 1,
                 'status': 'pending', 'available_at': 0, 'lease_until': 0, 'attempts': 0}
        value.update(overrides)
        self.db.seed('gamification_user_jobs', key, value)
        return self.db.rows['gamification_user_jobs'][key]

    def run_jobs(self, now=None, limit=2, effect=None):
        async def reconcile(*args):
            if effect:
                return effect(*args)
        with patch.object(tasks, 'reconcile_user', reconcile):
            return tasks.process_reconciliation_jobs(self.db, 'worker', now=now or self.now, limit=limit)

    def test_daily_page_survives_midnight_and_then_coalesces_missed_days(self):
        for uid in ('second', 'third'):
            self.db.seed('users', uid, {'app_data_epoch': 0})
        with patch.object(tasks, 'PAGE_SIZE', 2):
            tasks.run_maintenance_page(self.db, 'one', self.now)
            before = self.db.rows['gamification_jobs']['activation-v2']['activated_at']
            self.assertEqual(self.db.rows['gamification_jobs']['daily-2026-12-31']['status'], 'pending')
            future = self.now + timedelta(days=40)
            tasks.run_maintenance_page(self.db, 'two', future)
            self.assertEqual(self.db.rows['gamification_jobs']['daily-2026-12-31']['status'], 'complete')
            self.assertEqual(len(self.db.rows['gamification_user_jobs']), 3)
            tasks.run_maintenance_page(self.db, 'two', future)
            self.assertEqual(self.db.rows['gamification_jobs']['activation-v2']['active_daily_run'], 'daily-2027-02-09')
            self.assertEqual(self.db.rows['gamification_jobs']['activation-v2']['activated_at'], before)
            self.assertEqual(self.weekly_mock.call_count, 2)

    def test_daily_pagination_does_not_starve_weekly_generation(self):
        self.db.seed('users', 'second', {'app_data_epoch': 0})
        with patch.object(tasks, 'PAGE_SIZE', 1):
            tasks.run_maintenance_page(self.db, 'one', self.now)
        self.assertEqual(self.weekly_mock.call_count, 1)
        self.assertEqual(self.db.rows['gamification_jobs']['daily-2026-12-31']['status'], 'pending')
        weekly = [v for v in self.db.rows['gamification_jobs'].values() if v.get('kind') == 'weekly']
        self.assertEqual(weekly[0]['status'], 'complete')

    def test_live_legacy_lease_is_repaired_and_next_account_runs_next_pass(self):
        ms = int(self.now.timestamp() * 1000)
        self.job('held', status='running', lease_until=ms + tasks.LEASE_MS)
        self.job('later', available_at=1)
        calls = []
        self.run_jobs(limit=1, effect=lambda *args: calls.append(args[1]))
        self.assertEqual(calls, [])
        self.assertEqual(self.db.rows['gamification_user_jobs']['held']['available_at'], ms + tasks.LEASE_MS)
        self.run_jobs(limit=1, effect=lambda *args: calls.append(args[1]))
        self.assertEqual(calls, ['owner'])
        self.assertEqual(self.db.rows['gamification_user_jobs']['later']['status'], 'complete')

    def test_crash_after_claim_retries_after_lease_without_lost_attempt(self):
        self.job()
        self.db.lose_ack = True
        with self.assertRaises(RuntimeError):
            self.run_jobs()
        row = self.db.rows['gamification_user_jobs']['job']
        self.assertEqual((row['status'], row['attempts']), ('running', 1))
        self.assertEqual(self.run_jobs(), 0)
        self.run_jobs(now=self.now + timedelta(milliseconds=tasks.LEASE_MS))
        row = self.db.rows['gamification_user_jobs']['job']
        self.assertEqual((row['status'], row['attempts']), ('complete', 2))

    def test_failures_back_off_then_exhaust_and_next_daily_job_can_recover(self):
        self.job()
        def fail(*args):
            raise RuntimeError('injected outage')
        with self.assertLogs(tasks.logger, logging.ERROR) as logs:
            for attempt in range(tasks.MAX_ATTEMPTS):
                self.run_jobs(now=self.now + timedelta(milliseconds=attempt * tasks.RETRY_MS), effect=fail)
        row = self.db.rows['gamification_user_jobs']['job']
        self.assertEqual((row['status'], row['attempts']), ('failed', tasks.MAX_ATTEMPTS))
        self.assertEqual(row['last_error'], 'reconciliation_attempts_exhausted')
        self.assertTrue(any('exhausted retries' in text for text in logs.output))
        self.job('next-day')
        self.assertEqual(self.run_jobs(now=self.now + timedelta(days=1)), 1)
        self.assertEqual(self.db.rows['gamification_user_jobs']['next-day']['status'], 'complete')

    def test_old_completion_cannot_overwrite_a_newer_lease(self):
        self.job()
        def replace_claim(*args):
            current = dict(self.db.rows['gamification_user_jobs']['job'])
            current.update(fence=current['fence'] + 1, lease_owner='new-worker')
            self.db.seed('gamification_user_jobs', 'job', current)
        self.run_jobs(effect=replace_claim)
        row = self.db.rows['gamification_user_jobs']['job']
        self.assertEqual((row['status'], row['lease_owner']), ('running', 'new-worker'))

    def test_epoch_change_finishes_obsolete_job_without_recreating_data(self):
        from src.services.app_data_privacy import AppDataDeletionError
        self.job()
        def cleared(*args):
            self.db.seed('users', 'owner', {'app_data_epoch': 1})
            raise AppDataDeletionError(409, 'cleared')
        self.run_jobs(effect=cleared)
        self.assertEqual(self.db.rows['gamification_user_jobs']['job']['status'], 'complete')
        self.assertEqual(self.db.rows['users']['owner'], {'app_data_epoch': 1})

    def test_schedule_uses_utc_at_dst_and_iso_year_boundary(self):
        for day in range(730):
            instant = datetime(2025, 1, 1, 4, 14, tzinfo=timezone.utc) + timedelta(days=day)
            self.assertEqual(tasks.due_runs(instant), tasks.due_runs(instant.astimezone(ZoneInfo('America/New_York'))))
            self.assertEqual(tasks.due_runs(instant), tasks.due_runs(instant.astimezone(ZoneInfo('Pacific/Auckland'))))
        before = tasks.due_runs(datetime(2027, 1, 4, 4, 14, tzinfo=timezone.utc))
        after = tasks.due_runs(datetime(2027, 1, 4, 4, 15, tzinfo=timezone.utc))
        self.assertEqual(before[1][0], 'weekly-2026-W53')
        self.assertEqual(after[1][0], 'weekly-2027-W01')

    def test_scheduler_failure_does_not_block_reconciliation_or_retention(self):
        with patch.object(tasks, 'run_maintenance_page', side_effect=RuntimeError('outage')), patch.object(tasks, 'process_reconciliation_jobs', return_value=2) as reconcile, patch.object(tasks, 'prune_reconciliation_jobs', return_value=3) as prune, self.assertLogs(tasks.logger, logging.ERROR):
            result = tasks.maintenance_pass(self.db, 'worker', self.now)
        self.assertEqual(result, {'schedule': False, 'reconcile': 2, 'prune': 3})
        reconcile.assert_called_once()
        prune.assert_called_once()

    def test_projection_failure_does_not_block_privacy_jobs(self):
        source = Path(tasks.__file__).with_name('gamification_runner.py').read_text()
        function = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'foreground_pass')
        projection, deletion = Mock(side_effect=RuntimeError('outage')), Mock()
        scope = {'process_pending': projection, 'process_deletion_jobs': deletion, 'logger': Mock()}
        exec(compile(ast.Module(body=[function], type_ignores=[]), '<runner>', 'exec'), scope)
        scope['foreground_pass'](self.db, 'bucket', 'worker')
        deletion.assert_called_once_with(self.db, 'bucket', limit=2, max_records=100)

    def test_stale_week_or_lease_cannot_publish_catalog(self):
        marker = 'activation-v2'
        ref = self.db.collection('gamification_jobs').document('weekly-2026-W53')
        self.db.seed('gamification_jobs', ref.id, {'status': 'running', 'lease_owner': 'worker', 'fence': 2})
        self.db.seed('gamification_jobs', marker, {'latest_weekly_run': 'weekly-2027-W01'})
        job = {'lease_owner': 'worker', 'fence': 2}
        self.assertIsNone(actual_weekly_generation(self.db, '2026-W53', job_ref=ref, job=job))
        self.db.seed('gamification_jobs', marker, {'latest_weekly_run': 'weekly-2026-W53'})
        self.assertIsNone(actual_weekly_generation(self.db, '2026-W53', job_ref=ref, job={'lease_owner': 'worker', 'fence': 1}))
        self.assertNotIn('challenges', self.db.rows)

    def test_malformed_feedback_dates_do_not_poison_account_or_use_edit_time(self):
        for value in (None, True, float('nan'), float('inf'), -float('inf'), 10**40, 'invalid', {}):
            self.assertIsNone(tasks.feedback_creation_instant({'created_at': value, 'updatedAt': 1800000000000}))
        created = tasks.feedback_creation_instant({'created_at': '2026-01-01T00:00:00', 'updatedAt': 1800000000000})
        self.assertEqual(created, datetime(2026, 1, 1, tzinfo=timezone.utc))

    def test_explicit_pending_feedback_is_repaired_before_cache_failure_and_expiry(self):
        import sys
        from types import ModuleType, SimpleNamespace
        order = []
        def module(name, **attrs):
            result = ModuleType(name)
            result.__dict__.update(attrs)
            return result
        async def derived(*args, **kwargs):
            order.append('derived')
            raise RuntimeError('cache dependency unavailable')
        async def cold(*args, **kwargs):
            order.append('cold')
        async def role(*args, **kwargs):
            order.append('role')
        async def expire(*args, **kwargs):
            order.append('expire')
        settle = Mock(side_effect=lambda *args, **kwargs: order.append('feedback'))
        actions = Mock(side_effect=lambda *args, **kwargs: order.append('actions'))
        replacements = {
            'src.services.cpw_service': module('cpw', cpw_service=SimpleNamespace(recalculate_all_cpw_for_user=derived)),
            'src.services.gws_service': module('gws', gws_service=None),
            'src.services.ai_fit_score_service': module('ai', ai_fit_score_service=None),
            'src.services.challenge_service': module('challenge', challenge_service=SimpleNamespace(check_cold_start_progress=cold, expire_old_challenges=expire)),
            'src.services.addiction_service': module('addiction', addiction_service=SimpleNamespace(check_and_update_role=role)),
            'src.services.challenge_actions': module('actions', reconcile_action_challenges=actions),
            'src.services.feedback_rewards': module('feedback', settle_feedback_reward=settle),
        }
        self.db.seed('outfit_feedback', 'new-pending', {'user_id': 'owner', 'reward_pending': True})
        self.db.seed('outfit_feedback', 'legacy-unmarked', {'user_id': 'owner'})
        self.db.seed('outfit_feedback', 'already-settled', {'user_id': 'owner', 'reward_pending': False})
        with patch.dict(sys.modules, replacements), self.assertRaises(RuntimeError):
            asyncio.run(tasks.reconcile_user(self.db, 'owner', 0, 0))
        settle.assert_called_once_with(self.db, 'owner', 'new-pending', expected_epoch=0)
        self.assertEqual(order, ['feedback', 'cold', 'role', 'actions', 'expire', 'derived'])

    def test_missing_item_error_does_not_misclassify_live_account_as_cleared(self):
        from src.services.app_data_privacy import AppDataDeletionError
        self.job()
        def item_was_deleted(*args):
            raise AppDataDeletionError(404, 'Wardrobe item no longer exists')
        with self.assertLogs(tasks.logger, logging.ERROR):
            self.run_jobs(effect=item_was_deleted)
        row = self.db.rows['gamification_user_jobs']['job']
        self.assertEqual(row['status'], 'pending')
        self.assertEqual(row['last_error'], 'reconciliation_failed')
