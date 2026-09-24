"""TVE derived writes cannot restore cleared data or overwrite a newer wear."""
import asyncio
import copy
import sys
from types import ModuleType
from unittest.mock import patch

from test_outfit_wear import WearTestFixture
from src.services.app_data_privacy import AppDataDeletionError
# Load this provider-free dependency before patch.dict restores sys.modules.
# Otherwise a package attribute can outlive its removed module and split mocks.
from src.services import wardrobe_persistence

firebase = ModuleType('src.config.firebase')
firebase.db = None
with patch.dict(sys.modules, {'src.config.firebase': firebase}):
    from src.services.tve_service import TVEService


class TVEEpochTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        self.service = TVEService()
        self.service.db = self.db
        self.ref = self.db.collection('wardrobe').document('dress')
        self.original = copy.deepcopy(self.db.rows['wardrobe']['dress'])

    def write(self):
        self.service._write_derived_item('owner', self.ref, {'current_tve': 30.0}, 0,
                                        self.original, {}, None)

    def test_owner_epoch_and_unchanged_wear_allow_derived_write(self):
        self.write()
        self.assertEqual(self.db.rows['wardrobe']['dress']['current_tve'], 30)

    def test_clear_fences_existing_item_even_if_storage_cleanup_is_pending(self):
        self.db.rows['users']['owner']['app_data_epoch'] = 1
        with self.assertRaises(AppDataDeletionError):
            self.write()
        self.assertNotIn('current_tve', self.db.rows['wardrobe']['dress'])

    def test_transaction_retry_never_recaptures_new_epoch(self):
        def clear(database):
            database.seed('users', 'owner', {'app_data_epoch': 1})
        self.db.before_commit = clear
        with self.assertRaises(AppDataDeletionError):
            self.write()
        self.assertNotIn('current_tve', self.db.rows['wardrobe']['dress'])

    def test_concurrent_wear_and_profile_change_force_recalculation(self):
        for mutation in ('wearCount', 'current_tve', 'spending_ranges', 'gender'):
            with self.subTest(mutation=mutation):
                self.db.rows['wardrobe']['dress'] = copy.deepcopy(self.original)
                self.db.rows['users']['owner'] = {'xp': 0}
                if mutation in ('wearCount', 'current_tve'):
                    self.db.rows['wardrobe']['dress'][mutation] = 123
                else:
                    self.db.rows['users']['owner'][mutation] = {'tops': '$250-$500'} if mutation == 'spending_ranges' else 'Female'
                before = copy.deepcopy(self.db.rows)
                with self.assertRaises(RuntimeError):
                    self.write()
                self.assertEqual(self.db.rows, before)

    def test_foreign_conflicting_owner_or_deleted_item_never_gets_updated(self):
        for patch_value in ({'userId': 'other'}, {'uid': 'other'}, {'deletedAt': 1}):
            self.db.rows['wardrobe']['dress'] = {**self.original, **patch_value}
            with self.assertRaises(ValueError):
                self.write()
            self.assertNotIn('current_tve', self.db.rows['wardrobe']['dress'])

    def test_explicit_maintenance_epoch_failure_propagates(self):
        self.db.rows['users']['owner']['app_data_epoch'] = 1
        with self.assertLogs('src.services.tve_service', 'ERROR'), self.assertRaises(AppDataDeletionError):
            asyncio.run(self.service.calculate_wardrobe_tve('owner', expected_epoch=0))
