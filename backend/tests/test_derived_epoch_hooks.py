"""Offline derived-cache writes cannot cross a reset, retry, or item owner boundary."""
from contextlib import ExitStack
from copy import deepcopy
import functools
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

from google.cloud.firestore_v1 import FieldFilter
from src.services import app_data_privacy as privacy
from test_app_data_privacy import Collection, Database, transactional


class DerivedEpochHookTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.db = Database({
            'users/owner': {'app_data_epoch': 3, 'spending_ranges': {'tops': '$100-$250'}},
            'wardrobe/a': {'userId': 'owner', 'type': 'shirt', 'wearCount': 2},
            'wardrobe/b': {'userId': 'owner', 'type': 'shirt', 'wearCount': 5},
        })
        config = ModuleType('src.config.firebase')
        config.db = self.db
        self.stack.enter_context(patch.dict('sys.modules', {'src.config.firebase': config}))
        self.stack.enter_context(patch.object(privacy.firestore, 'transactional', transactional))
        original_where = Collection.where
        def where(collection, *args, filter=None):
            return original_where(collection, filter=filter or FieldFilter(*args))
        self.stack.enter_context(patch.object(Collection, 'where', where))
        self.cpw_module = self.load('cpw_service')
        self.ai_module = self.load('ai_fit_score_service')
        self.cpw = self.cpw_module.CPWService()
        self.ai = self.ai_module.AIFitScoreService()
        self.tve = SimpleNamespace(calculate_wardrobe_tve=AsyncMock(return_value={'total_tve': 200, 'total_wardrobe_cost': 1000}))
        self.utilization = SimpleNamespace(calculate_utilization_percentage=AsyncMock(return_value={'utilization_percentage': 50}))
        self.ai_component = SimpleNamespace(calculate_ai_fit_score=AsyncMock(return_value=60))
        self.events = SimpleNamespace(log_gamification_event=AsyncMock(return_value=True))
        modules = {}
        for name, service in [('tve_service', self.tve), ('utilization_service', self.utilization),
                              ('ai_fit_score_service', self.ai_component), ('gamification_service', self.events)]:
            module = ModuleType('src.services.' + name)
            setattr(module, name, service)
            modules['src.services.' + name] = module
        self.stack.enter_context(patch.dict('sys.modules', modules))
        self.gws_module = self.load('gws_service')
        self.gws = self.gws_module.GWSService()
        for module in [self.cpw_module, self.ai_module, self.gws_module]:
            self.stack.enter_context(patch.object(module, 'logger'))

    def load(self, name):
        path = Path(__file__).resolve().parents[1] / 'src/services' / (name + '.py')
        spec = importlib.util.spec_from_file_location('src.services.isolated_derived_' + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @property
    def user(self):
        return self.db.rows['users/owner']

    def clear(self):
        self.user['app_data_epoch'] += 1

    def retry_once(self, change):
        def decorate(callback):
            @functools.wraps(callback)
            def run(txn, *args, **kwargs):
                callback(txn, *args, **kwargs)
                # The first transaction attempt conflicts and is discarded.
                change()
                replacement = self.db.transaction()
                result = callback(replacement, *args, **kwargs)
                replacement.commit()
                return result
            return run
        return patch.object(privacy.firestore, 'transactional', decorate)

    async def test_cpw_preserves_formula_and_accepts_each_consistent_owner_alias(self):
        for alias in privacy.OWNER_KEYS:
            with self.subTest(alias=alias):
                self.db.rows['wardrobe/a'] = {alias: 'owner', 'type': 'shirt', 'wearCount': 2}
                self.assertEqual(await self.cpw.calculate_item_cpw('owner', 'a', expected_epoch=3), 87.5)
                self.assertEqual(self.db.rows['wardrobe/a']['cpw'], 87.5)

    async def test_cpw_rejects_missing_foreign_conflicting_and_deleted_items(self):
        records = [None, {'type': 'shirt'}, {'userId': 'other'}, {'userId': 'owner', 'deleted_at': 1}]
        records += [{'userId': 'owner', alias: 'other'} for alias in privacy.OWNER_KEYS]
        for item in records:
            with self.subTest(item=item):
                self.db.rows.pop('wardrobe/a', None)
                if item is not None:
                    self.db.rows['wardrobe/a'] = deepcopy(item)
                before = deepcopy(self.db.rows)
                with self.assertRaises(privacy.AppDataDeletionError):
                    await self.cpw.calculate_item_cpw('owner', 'a', expected_epoch=3)
                self.assertEqual(self.db.rows, before)

    async def test_cpw_captures_before_transaction_and_rejects_clear(self):
        original = self.db.transaction
        def transaction():
            self.clear()
            return original()
        with patch.object(self.db, 'transaction', transaction):
            with self.assertRaises(privacy.AppDataDeletionError):
                await self.cpw.calculate_item_cpw('owner', 'a', expected_epoch=3)
        self.assertNotIn('cpw', self.db.rows['wardrobe/a'])

    async def test_cpw_retry_recomputes_from_fresh_item_with_same_epoch(self):
        with self.retry_once(lambda: self.db.rows['wardrobe/a'].update(wearCount=5)):
            self.assertEqual(await self.cpw.calculate_item_cpw('owner', 'a', expected_epoch=3), 35)
        self.assertEqual(self.db.rows['wardrobe/a']['cpw'], 35)

    async def test_cpw_retry_cannot_adopt_new_epoch_or_changed_owner(self):
        for change in [self.clear, lambda: self.db.rows['wardrobe/a'].update(ownerId='other')]:
            self.user['app_data_epoch'] = 3
            self.db.rows['wardrobe/a'] = {'userId': 'owner', 'type': 'shirt', 'wearCount': 2}
            with self.retry_once(change):
                with self.assertRaises(privacy.AppDataDeletionError):
                    await self.cpw.calculate_item_cpw('owner', 'a', expected_epoch=3)
            self.assertNotIn('cpw', self.db.rows['wardrobe/a'])

    async def test_all_cpw_batches_pin_one_epoch_even_with_default_arguments(self):
        for method, args in [('recalculate_all_cpw_for_user', ()), ('recalculate_items_cpw', (['a', 'b'],)),
                             ('calculate_wardrobe_average_cpw', ())]:
            with self.subTest(method=method):
                self.user['app_data_epoch'] = 3
                for item in ['a', 'b']:
                    self.db.rows['wardrobe/' + item].pop('cpw', None)
                original = self.cpw.calculate_item_cpw
                seen = []
                async def update(uid, item_id, *, expected_epoch=None):
                    seen.append(expected_epoch)
                    result = await original(uid, item_id, expected_epoch=expected_epoch)
                    if len(seen) == 1:
                        self.clear()
                    return result
                with patch.object(self.cpw, 'calculate_item_cpw', update):
                    await getattr(self.cpw, method)('owner', *args)
                self.assertEqual(seen, [3, 3])
                self.assertNotIn('cpw', self.db.rows['wardrobe/b'])

    async def test_cpw_explicit_batch_propagates_failure_and_default_item_is_compatible(self):
        self.db.fail_once = True
        with self.assertRaises(RuntimeError):
            await self.cpw.recalculate_all_cpw_for_user('owner', expected_epoch=3)
        self.assertNotIn('cpw', self.db.rows['wardrobe/a'])
        self.db.fail_once = True
        self.assertIsNone(await self.cpw.calculate_item_cpw('owner', 'a'))

    async def test_gws_formula_and_one_epoch_propagation(self):
        with patch.object(self.gws, '_calculate_revived_items_score', AsyncMock(return_value=.5)) as revived:
            self.assertEqual(await self.gws.calculate_gws('owner', expected_epoch=3), 43)
        self.assertEqual(self.user['gws'], 43)
        self.tve.calculate_wardrobe_tve.assert_awaited_once_with('owner', expected_epoch=3)
        self.ai_component.calculate_ai_fit_score.assert_awaited_once_with('owner', expected_epoch=3)
        revived.assert_awaited_once_with('owner', expected_epoch=3)

    async def test_gws_clear_during_components_prevents_final_write(self):
        async def revived(*args, **kwargs):
            self.clear()
            return .5
        with patch.object(self.gws, '_calculate_revived_items_score', revived):
            with self.assertRaises(privacy.AppDataDeletionError):
                await self.gws.calculate_gws('owner', expected_epoch=3)
        self.assertNotIn('gws', self.user)

    async def test_gws_default_call_still_pins_epoch(self):
        async def revived(*args, **kwargs):
            self.clear()
            return .5
        with patch.object(self.gws, '_calculate_revived_items_score', revived):
            self.assertEqual(await self.gws.calculate_gws('owner'), 0)
        self.assertNotIn('gws', self.user)
        self.tve.calculate_wardrobe_tve.assert_awaited_once_with('owner', expected_epoch=3)

    async def test_gws_transaction_retry_keeps_captured_epoch(self):
        with patch.object(self.gws, '_calculate_revived_items_score', AsyncMock(return_value=.5)):
            with self.retry_once(self.clear):
                with self.assertRaises(privacy.AppDataDeletionError):
                    await self.gws.calculate_gws('owner', expected_epoch=3)
        self.assertNotIn('gws', self.user)

    async def test_same_epoch_profile_write_retries_preserve_scores(self):
        with patch.object(self.gws, '_calculate_revived_items_score', AsyncMock(return_value=.5)):
            with self.retry_once(lambda: None):
                self.assertEqual(await self.gws.calculate_gws('owner', expected_epoch=3), 43)
        self.feedback_fixture()
        with self.retry_once(lambda: None):
            self.assertEqual(await self.ai.update_score_from_feedback('owner', {}, expected_epoch=3), 64)
        self.assertEqual(self.user['gws'], 43)
        self.assertEqual(self.user['ai_fit_score'], 64)
        self.events.log_gamification_event.assert_awaited_once()

    async def test_gws_explicit_component_errors_are_retryable(self):
        self.utilization.calculate_utilization_percentage.return_value = {'error': 'fixture outage'}
        with self.assertRaises(RuntimeError):
            await self.gws.calculate_gws('owner', expected_epoch=3)
        self.assertNotIn('gws', self.user)
        self.utilization.calculate_utilization_percentage.return_value = {'utilization_percentage': 50}
        for component in [self.tve.calculate_wardrobe_tve, self.ai_component.calculate_ai_fit_score]:
            component.side_effect = RuntimeError('fixture outage')
            with self.assertRaises(RuntimeError):
                await self.gws.calculate_gws('owner', expected_epoch=3)
            component.side_effect = None
        with patch.object(Collection, 'stream', side_effect=RuntimeError('fixture outage')):
            with self.assertRaises(RuntimeError):
                await self.gws._calculate_revived_items_score('owner', expected_epoch=3)
        self.assertNotIn('gws', self.user)

    def feedback_fixture(self):
        for index in range(5):
            self.db.rows[f'outfit_feedback/{index}'] = {'user_id': 'owner', 'feedback_type': 'love', 'rating': 5}
        for index in range(3):
            self.db.rows[f'outfits/{index}'] = {'user_id': 'owner', 'wasSuccessful': True}

    async def test_ai_fit_formula_is_preserved(self):
        self.assertEqual(await self.ai.calculate_ai_fit_score('owner', expected_epoch=3), 18)
        self.feedback_fixture()
        self.assertEqual(await self.ai.calculate_ai_fit_score('owner', expected_epoch=3), 64)
        self.assertNotIn('ai_fit_score', self.user)

    async def test_ai_fit_clear_during_calculation_is_rejected(self):
        async def confidence(*args, **kwargs):
            self.clear()
            return .5
        with patch.object(self.ai, 'get_average_prediction_confidence', confidence):
            with self.assertRaises(privacy.AppDataDeletionError):
                await self.ai.calculate_ai_fit_score('owner', expected_epoch=3)

    async def test_ai_fit_explicit_helper_failures_propagate(self):
        with patch.object(Collection, 'stream', side_effect=RuntimeError('fixture outage')):
            for method in ['get_feedback_count', 'analyze_preference_consistency', 'get_average_prediction_confidence', 'calculate_ai_fit_score']:
                with self.subTest(method=method):
                    with self.assertRaises(RuntimeError):
                        await getattr(self.ai, method)('owner', expected_epoch=3)
            self.assertEqual(await self.ai.get_feedback_count('owner'), 0)
            self.assertEqual(await self.ai.analyze_preference_consistency('owner'), .5)
            self.assertEqual(await self.ai.get_average_prediction_confidence('owner'), .5)
            self.assertEqual(await self.ai.calculate_ai_fit_score('owner'), 0)

    async def test_feedback_update_guards_profile_and_pins_optional_event(self):
        self.feedback_fixture()
        score = await self.ai.update_score_from_feedback('owner', {'rating': 5}, expected_epoch=3)
        self.assertEqual(score, 64)
        self.assertEqual(self.user['ai_fit_score'], 64)
        call = self.events.log_gamification_event.await_args.kwargs
        self.assertEqual(call['metadata']['app_data_epoch'], 3)
        self.assertEqual(call['metadata']['new_score'], 64)

    async def test_feedback_clear_after_calculation_prevents_write_and_event(self):
        async def calculate(*args, **kwargs):
            self.clear()
            return 64
        with patch.object(self.ai, 'calculate_ai_fit_score', calculate):
            with self.assertRaises(privacy.AppDataDeletionError):
                await self.ai.update_score_from_feedback('owner', {}, expected_epoch=3)
        self.assertNotIn('ai_fit_score', self.user)
        self.events.log_gamification_event.assert_not_awaited()

    async def test_feedback_transaction_retry_cannot_adopt_new_epoch(self):
        with self.retry_once(self.clear):
            with self.assertRaises(privacy.AppDataDeletionError):
                await self.ai.update_score_from_feedback('owner', {}, expected_epoch=3)
        self.assertNotIn('ai_fit_score', self.user)
        self.events.log_gamification_event.assert_not_awaited()

    async def test_feedback_default_call_does_not_swallow_guard_into_a_write(self):
        async def calculate(*args, **kwargs):
            self.clear()
            return 64
        with patch.object(self.ai, 'calculate_ai_fit_score', calculate):
            self.assertEqual(await self.ai.update_score_from_feedback('owner', {}), 0)
        self.assertNotIn('ai_fit_score', self.user)
        self.events.log_gamification_event.assert_not_awaited()

    async def test_all_hooks_reject_missing_blocked_and_stale_accounts_before_work(self):
        methods = [lambda: self.cpw.calculate_item_cpw('owner', 'a', expected_epoch=3),
                   lambda: self.cpw.recalculate_all_cpw_for_user('owner', expected_epoch=3),
                   lambda: self.gws.calculate_gws('owner', expected_epoch=3),
                   lambda: self.ai.calculate_ai_fit_score('owner', expected_epoch=3),
                   lambda: self.ai.update_score_from_feedback('owner', {}, expected_epoch=3)]
        for state in ['missing', 'pending', 'running', 'failed', 'stale']:
            for method in methods:
                self.db.rows['users/owner'] = {'app_data_epoch': 4 if state == 'stale' else 3}
                if state == 'missing':
                    del self.db.rows['users/owner']
                elif state != 'stale':
                    self.user['app_data_deletion'] = {'status': state}
                before = deepcopy(self.db.rows)
                with self.assertRaises(privacy.AppDataDeletionError):
                    await method()
                self.assertEqual(self.db.rows, before)
        self.utilization.calculate_utilization_percentage.assert_not_awaited()
        self.events.log_gamification_event.assert_not_awaited()


if __name__ == '__main__':
    unittest.main()
