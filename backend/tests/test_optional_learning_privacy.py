"""Optional telemetry/learning uses the real privacy writer with an offline store."""
import asyncio
from contextlib import ExitStack
import copy
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from src.services import app_data_privacy as privacy


class Document:
    def __init__(self, db, collection, key):
        self.db, self.collection, self.id = db, collection, key

    def get(self, transaction=None):
        if self.db.unavailable:
            raise RuntimeError('offline database failure')
        self.db.reads.append((self.collection, self.id))
        value = copy.deepcopy(self.db.records.get(self.collection, {}).get(self.id))
        return SimpleNamespace(id=self.id, exists=value is not None, to_dict=lambda: copy.deepcopy(value))

    def set(self, *args, **kwargs):
        raise AssertionError('Optional writes must use the transactional policy helper')


class Collection:
    def __init__(self, db, name, filters=()):
        self.db, self.name, self.filters = db, name, filters

    def document(self, key=None):
        if key is None:
            self.db.counter += 1
            key = f'event-{self.db.counter}'
        return Document(self.db, self.name, key)

    def where(self, field, operator, value):
        return Collection(self.db, self.name, (*self.filters, (field, value)))

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, *args):
        return self

    def stream(self):
        self.db.queries.append(self.name)
        return [Document(self.db, self.name, key).get()
                for key, data in self.db.records.get(self.name, {}).items()
                if all(data.get(field) == value for field, value in self.filters)]


class Transaction:
    def __init__(self, db):
        self.db, self.writes = db, []

    def set(self, ref, payload, merge=False):
        self.writes.append((ref, copy.deepcopy(payload), merge))

    def commit(self):
        for ref, payload, merge in self.writes:
            collection = self.db.records.setdefault(ref.collection, {})
            collection[ref.id] = {**(collection.get(ref.id, {}) if merge else {}), **payload}
            self.db.writes.append((ref.collection, ref.id, copy.deepcopy(payload)))


def transactional(function):
    def run(transaction):
        result = function(transaction)
        transaction.commit()
        return result
    return run


class Database:
    def __init__(self):
        self.records = {'users': {'owner': {'app_data_epoch': 0}}}
        self.reads, self.queries, self.writes = [], [], []
        self.counter, self.unavailable = 0, False

    def collection(self, name):
        return Collection(self, name)

    def transaction(self):
        return Transaction(self)


def load_service(name):
    source = Path(__file__).resolve().parents[1] / 'src/services' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(f'src.services.isolated_{name}', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OptionalLearningPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.db = Database()
        firebase = ModuleType('src.config.firebase')
        firebase.db = self.db
        self.stack.enter_context(patch.dict('sys.modules', {'src.config.firebase': firebase}))
        self.stack.enter_context(patch.object(privacy.firestore, 'transactional', transactional))
        self.analytics = load_service('analytics_service')
        self.items_module = load_service('item_analytics_service')
        self.items = self.items_module.ItemAnalyticsService()
        self.preferences_module = load_service('user_preference_service')
        self.preferences = self.preferences_module.UserPreferenceService()
        self.existing_module = load_service('existing_data_personalization')
        self.existing = self.existing_module.ExistingDataPersonalizationEngine()
        self.outfit = {'id': 'look', 'style': 'Casual', 'occasion': 'Weekend',
                       'items': [{'id': 'shirt', 'color': 'blue'}]}

    @property
    def user(self):
        return self.db.records['users']['owner']

    def settings(self, **kwargs):
        self.user.setdefault('privacy', {}).update(kwargs)

    def event(self):
        return self.analytics.AnalyticsEvent(user_id='owner', event_type='item_interaction',
                                             item_id='shirt', interaction_type='view')

    def sync_interaction(self):
        return self.analytics.log_item_interaction('owner', 'shirt', self.analytics.ItemInteractionType.VIEW)

    def async_interaction(self):
        return asyncio.run(self.items.track_item_interaction('owner', 'shirt', 'view'))

    def test_default_telemetry_opt_out_suppresses_both_writers_and_derived_learning(self):
        with patch.object(self.analytics, 'update_item_favorite_score_async') as sync_score, \
                patch.object(self.items, '_update_item_favorite_score', new_callable=AsyncMock) as async_score:
            self.assertIsNone(self.sync_interaction())
            self.assertIsNone(self.async_interaction())
            sync_score.assert_not_called()
            async_score.assert_not_called()
        self.assertEqual(self.db.writes, [])

    def test_opted_in_telemetry_commits_with_current_epoch_without_forcing_personalization(self):
        self.settings(share_analytics=True, allow_personalization=False)
        self.user['app_data_epoch'] = 3
        self.assertIsNotNone(self.sync_interaction())
        self.assertIsNotNone(self.async_interaction())
        self.assertEqual({name for name, _, _ in self.db.writes}, {'analytics_events', 'item_analytics'})
        for _, _, payload in self.db.writes:
            self.assertEqual(payload['app_data_epoch'], 3)
            self.assertEqual(payload['user_id'], 'owner')

    def test_collection_opt_out_and_active_deletion_override_telemetry_opt_in(self):
        for settings, state in (({'share_analytics': True, 'allow_data_collection': False}, {}),
                                ({'share_analytics': True}, {'status': 'pending'}),
                                ({'share_analytics': True}, {'status': 'failed'})):
            self.user['privacy'] = settings
            self.user['app_data_deletion'] = state
            self.assertIsNone(self.sync_interaction())
            self.assertIsNone(self.async_interaction())
        self.assertEqual(self.db.writes, [])

    def test_anonymous_telemetry_has_no_owner_policy_and_is_not_persisted(self):
        event = self.analytics.AnalyticsEvent(event_type='page_view')
        self.assertIsNone(self.analytics.log_analytics_event(event))
        self.assertEqual(self.db.writes, [])
        self.assertEqual(self.db.reads, [])

    def test_personalization_opt_out_stops_score_reads_and_derived_writes(self):
        self.settings(allow_personalization=False, share_analytics=True)
        self.analytics.update_item_favorite_score_async('owner', 'shirt')
        asyncio.run(self.items._update_item_favorite_score('owner', 'shirt'))
        self.assertEqual(self.analytics.get_user_favorites('owner'), [])
        self.assertEqual(asyncio.run(self.items.get_user_favorites('owner')), [])
        self.assertEqual(self.db.queries, [])
        self.assertEqual(self.db.writes, [])

    def test_old_favorite_scores_are_not_returned_after_a_new_data_epoch(self):
        self.user['app_data_epoch'] = 2
        self.db.records['item_favorite_scores'] = {'owner_shirt': {
            'user_id': 'owner', 'item_id': 'shirt', 'app_data_epoch': 1, 'total_score': 0.8}}
        self.db.records['wardrobe'] = {'shirt': {'userId': 'owner', 'name': 'Shirt'}}
        self.assertEqual(self.analytics.get_user_favorites('owner'), [])
        self.assertEqual(asyncio.run(self.items.get_user_favorites('owner')), [])
        self.assertNotIn(('wardrobe', 'shirt'), self.db.reads)

    def test_allowed_favorite_learning_is_written_through_policy_transaction(self):
        self.settings(share_analytics=True)
        with patch.object(self.analytics, 'get_user_profile', return_value=None), \
                patch.object(self.items, '_get_user_profile', new_callable=AsyncMock, return_value=None):
            self.assertIsNotNone(self.sync_interaction())
            self.assertIsNotNone(self.async_interaction())
        scores = [payload for name, _, payload in self.db.writes if name == 'item_favorite_scores']
        self.assertEqual(len(scores), 2)
        self.assertTrue(all(value['app_data_epoch'] == 0 for value in scores))

    def test_telemetry_write_rechecks_revoked_sharing_and_never_starts_favorite_learning(self):
        for module, call in ((self.analytics, self.sync_interaction),
                             (self.items_module, self.async_interaction)):
            self.settings(share_analytics=True)
            def revoke_before_write(*args, **kwargs):
                self.settings(share_analytics=False)
                return privacy.write_optional_record(*args, **kwargs)
            with patch.object(module, 'write_optional_record', side_effect=revoke_before_write), \
                    patch.object(self.analytics, 'update_item_favorite_score_async') as score, \
                    patch.object(self.items, '_update_item_favorite_score', new_callable=AsyncMock) as async_score:
                self.assertIsNone(call())
                score.assert_not_called()
                async_score.assert_not_called()
        self.assertEqual(self.db.writes, [])

    def test_telemetry_to_learning_keeps_original_epoch_across_completed_clear(self):
        for module, call in ((self.analytics, self.sync_interaction), (self.items_module, self.async_interaction)):
            self.user['app_data_epoch'] = 0
            self.settings(share_analytics=True)
            self.db.writes.clear()
            def clear_after_event(*args, **kwargs):
                written = privacy.write_optional_record(*args, **kwargs)
                if written and kwargs['kind'] == 'telemetry':
                    self.user['app_data_epoch'] = 1
                    self.db.records.pop('analytics_events', None)
                    self.db.records.pop('item_analytics', None)
                return written
            with patch.object(module, 'write_optional_record', side_effect=clear_after_event):
                self.assertIsNotNone(call())
            self.assertTrue(all(name in {'analytics_events', 'item_analytics'} for name, _, _ in self.db.writes))
            self.assertNotIn('item_favorite_scores', self.db.records)

    def test_preference_read_ignores_old_cache_after_opt_out(self):
        self.preferences._cache['owner'] = {'cached_at': datetime.now(timezone.utc),
                                             'data': {'preferred_colors': ['private-red']}}
        self.settings(allow_personalization=False)
        prefs = asyncio.run(self.preferences.get_preferences('owner'))
        self.assertEqual(prefs['preferred_colors'], [])
        self.assertFalse(prefs['personalization_enabled'])
        self.assertNotIn('owner', self.preferences._cache)
        self.assertTrue(all(collection == 'users' for collection, _ in self.db.reads))
        self.assertEqual(self.db.writes, [])

    def test_preference_read_does_not_reuse_cache_after_completed_data_clear(self):
        self.preferences._cache['owner'] = {'cached_at': datetime.now(timezone.utc),
                                             'data': {'preferred_colors': ['old-red']}}
        self.user['app_data_epoch'] = 2
        prefs = asyncio.run(self.preferences.get_preferences('owner'))
        self.assertEqual(prefs['preferred_colors'], [])
        self.assertEqual(prefs['app_data_epoch'], 2)
        self.assertEqual(self.db.records['user_preferences']['owner']['app_data_epoch'], 2)

    def test_existing_preference_from_old_epoch_is_not_returned(self):
        self.user['app_data_epoch'] = 1
        self.db.records['user_preferences'] = {'owner': {'user_id': 'owner', 'preferred_colors': ['old-red'], 'app_data_epoch': 0}}
        prefs = asyncio.run(self.preferences.get_preferences('owner'))
        self.assertEqual(prefs['preferred_colors'], [])
        self.assertFalse(prefs['personalization_enabled'])
        self.assertEqual(self.db.writes, [])

    def test_default_personalization_can_learn_without_telemetry_opt_in(self):
        result = asyncio.run(self.preferences.update_from_rating('owner', self.outfit, rating=5))
        self.assertEqual(result['total_feedback_count'], 1)
        stored = self.db.records['user_preferences']['owner']
        self.assertEqual(stored['preferred_colors'], ['blue'])
        self.assertEqual(stored['app_data_epoch'], 0)
        self.assertEqual({name for name, _, _ in self.db.writes}, {'user_preferences'})

    def test_saved_rating_epoch_must_match_before_loading_or_learning_preferences(self):
        self.user['app_data_epoch'] = 2
        denied = asyncio.run(self.preferences.update_from_rating('owner', self.outfit, rating=5, expected_epoch=1))
        self.assertFalse(denied['personalization_enabled'])
        self.assertEqual(self.db.writes, [])
        self.assertTrue(all(collection == 'users' for collection, _ in self.db.reads))
        allowed = asyncio.run(self.preferences.update_from_rating('owner', self.outfit, rating=5, expected_epoch=2))
        self.assertEqual(allowed['total_feedback_count'], 1)
        self.assertEqual(self.db.records['user_preferences']['owner']['app_data_epoch'], 2)

    def learning_calls(self):
        return (
            lambda: self.preferences.update_from_rating('owner', self.outfit, rating=5),
            lambda: self.preferences.update_from_wear('owner', self.outfit),
            lambda: self.preferences.update_from_item_favorite('owner', {'id': 'shirt', 'color': 'blue'}, True),
        )

    def test_all_learning_mutations_are_noops_when_personalization_is_disabled(self):
        self.settings(allow_personalization=False)
        for call in self.learning_calls():
            result = asyncio.run(call())
            self.assertFalse(result['personalization_enabled'])
            self.assertEqual(result['messages'], [])
            self.assertEqual(result['learning_messages'], [])
        self.assertEqual(self.db.writes, [])
        self.assertTrue(all(collection == 'users' for collection, _ in self.db.reads))

    def test_all_learning_writes_recheck_privacy_after_the_input_read(self):
        for call in self.learning_calls():
            self.settings(allow_personalization=True)
            initial = asyncio.run(self.preferences.get_preferences('owner'))
            self.db.writes.clear()
            def revoke_before_write(*args, **kwargs):
                self.settings(allow_personalization=False)
                return privacy.write_optional_record(*args, **kwargs)
            with patch.object(self.preferences_module, 'write_optional_record', side_effect=revoke_before_write):
                result = asyncio.run(call())
            self.assertFalse(result['personalization_enabled'])
            self.assertEqual(self.db.writes, [])
            self.assertEqual(self.db.records['user_preferences']['owner']['total_feedback_count'], 0)

    def test_learning_cannot_resurrect_preferences_after_data_clear_finishes(self):
        asyncio.run(self.preferences.get_preferences('owner'))
        self.db.writes.clear()
        def clear_before_write(*args, **kwargs):
            self.user['app_data_epoch'] += 1
            self.db.records.pop('user_preferences', None)
            self.assertEqual(kwargs['expected_epoch'], 0)
            return privacy.write_optional_record(*args, **kwargs)
        with patch.object(self.preferences_module, 'write_optional_record', side_effect=clear_before_write):
            result = asyncio.run(self.preferences.update_from_rating('owner', self.outfit, rating=5))
        self.assertFalse(result['personalization_enabled'])
        self.assertNotIn('user_preferences', self.db.records)
        self.assertEqual(self.db.writes, [])

    def test_learning_summary_rechecks_settings_and_epoch_for_previously_loaded_preferences(self):
        prefs = {'user_id': 'owner', 'total_feedback_count': 12, 'preferred_colors': ['private-red'], 'app_data_epoch': 0}
        self.settings(allow_personalization=False)
        self.assertEqual(self.preferences.generate_learning_summary(prefs)['insights'], [])
        self.settings(allow_personalization=True)
        self.user['app_data_epoch'] = 1
        self.assertEqual(self.preferences.generate_learning_summary(prefs)['insights'], [])

    def test_missing_or_unavailable_account_never_enables_personalized_reads(self):
        for unavailable in (False, True):
            self.db.unavailable = unavailable
            self.db.records['users'].clear()
            prefs = asyncio.run(self.preferences.get_preferences('owner'))
            self.assertFalse(prefs['personalization_enabled'])
            existing = asyncio.run(self.existing.get_user_preference_from_existing_data('owner'))
            self.assertEqual(existing.total_interactions, 0)
            self.assertEqual(self.analytics.get_user_favorites('owner'), [])
            self.assertEqual(asyncio.run(self.items.get_user_favorites('owner')), [])
        self.assertEqual(self.db.queries, [])
        self.assertEqual(self.db.writes, [])

    def test_existing_data_engine_and_individual_readers_obey_opt_out(self):
        self.settings(allow_personalization=False)
        preference = asyncio.run(self.existing.get_user_preference_from_existing_data('owner'))
        self.assertEqual(preference.data_source, 'personalization_disabled')
        self.assertEqual(asyncio.run(self.existing._get_wardrobe_preferences('owner'))['interactions'], 0)
        self.assertEqual(asyncio.run(self.existing._get_outfit_preferences('owner'))['interactions'], 0)
        self.assertIsNone(asyncio.run(self.existing._get_user_style_profile('owner')))
        self.assertEqual(asyncio.run(self.existing._get_item_analytics('owner'))['interactions'], 0)
        status = asyncio.run(self.existing.get_personalization_status_from_existing_data('owner'))
        self.assertFalse(status['personalization_enabled'])
        self.assertEqual(self.db.queries, [])

    def test_existing_preferences_cannot_rank_after_opt_out_or_data_clear(self):
        self.db.records['wardrobe'] = {
            f'shirt-{i}': {'userId': 'owner', 'favorite': True, 'color': 'blue'} for i in range(3)}
        preference = asyncio.run(self.existing.get_user_preference_from_existing_data('owner'))
        self.assertEqual(preference.total_interactions, 3)
        self.assertEqual(preference.app_data_epoch, 0)
        looks = [{'id': 'plain'}, {'id': 'blue', 'colors': ['blue']}]
        ranked = self.existing.rank_outfits_by_existing_preferences('owner', copy.deepcopy(looks), preference)
        self.assertEqual(ranked[0]['id'], 'blue')
        self.settings(allow_personalization=False)
        self.assertEqual(self.existing.rank_outfits_by_existing_preferences('owner', copy.deepcopy(looks), preference), looks)
        self.settings(allow_personalization=True)
        self.user['app_data_epoch'] = 1
        self.assertEqual(self.existing.rank_outfits_by_existing_preferences('owner', copy.deepcopy(looks), preference), looks)


if __name__ == '__main__':
    unittest.main()
