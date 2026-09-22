"""No-network tests of weekly accounting and create-once initialization."""
import copy
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from firebase_admin import firestore
from src.services.account_bootstrap import ensure_user_account
from src.services.subscription_utils import QuotaNeedsReview, WEEKLY_ALLOWANCE_SECONDS, apply_subscription_entitlement, current_quota
from src.services import flatlay_lifecycle as lifecycle
from test_subscription_read_repair import Database, transactional

ROOT = Path(__file__).resolve().parents[1]


def account(tier='tier1', remaining=1, highest=1, start=1000):
    return {'subscription': {'role': tier}, 'quotas': {
        'flatlaysRemaining': remaining, 'lastRefillAt': start,
        'highestAllowanceGranted': highest, 'highestAllowanceInferred': False}}


class CreditPolicyTests(unittest.TestCase):
    def test_worker_and_api_helpers_identical(self):
        self.assertEqual((ROOT/'src/services/subscription_utils.py').read_bytes(),
                         (ROOT/'worker/subscription_utils.py').read_bytes())

    def test_upgrade_only_grants_new_high_water_once(self):
        user = account(remaining=0)
        user['quotas'] = apply_subscription_entitlement(user, 'tier2', 1100)
        user['subscription']['role'] = 'tier2'
        self.assertEqual(user['quotas']['flatlaysRemaining'], 6)
        self.assertEqual(user['quotas']['lastRefillAt'], 1000)
        user['quotas']['flatlaysRemaining'] -= 2
        for tier in ('tier1', 'tier2', 'tier1', 'tier2'):
            user['quotas'] = apply_subscription_entitlement(user, tier, 1200)
            user['subscription']['role'] = tier
        self.assertEqual(user['quotas']['flatlaysRemaining'], 4)
        user['quotas'] = apply_subscription_entitlement(user, 'tier3', 1300)
        self.assertEqual(user['quotas']['flatlaysRemaining'], 27)
        self.assertEqual(user['quotas']['highestAllowanceGranted'], 30)

    def test_downgrade_preserves_credits_until_next_reset(self):
        user = account('tier3', remaining=24, highest=30)
        user['quotas'] = apply_subscription_entitlement(user, 'tier1', 1500)
        user['subscription']['role'] = 'tier1'
        self.assertEqual(current_quota(user, 1000 + WEEKLY_ALLOWANCE_SECONDS - 1)['flatlaysRemaining'], 24)
        reset = current_quota(user, 1000 + WEEKLY_ALLOWANCE_SECONDS)
        self.assertEqual(reset['flatlaysRemaining'], 1)
        self.assertEqual(reset['highestAllowanceGranted'], 1)

    def test_invoice_notification_does_not_refill_expired_period(self):
        user = account('tier2', remaining=0, highest=7)
        now = 1000 + 3 * WEEKLY_ALLOWANCE_SECONDS
        for _ in range(5):
            user['quotas'] = apply_subscription_entitlement(user, 'tier2', now)
        self.assertEqual(user['quotas']['flatlaysRemaining'], 0)
        self.assertEqual(user['quotas']['lastRefillAt'], 1000)
        reset = current_quota(user, now)
        self.assertEqual(reset['flatlaysRemaining'], 7)
        self.assertEqual(reset['lastRefillAt'], now)

    def test_upgrade_after_old_period_does_not_double_grant(self):
        user = account(remaining=0)
        now = 1000 + WEEKLY_ALLOWANCE_SECONDS
        user['quotas'] = apply_subscription_entitlement(user, 'tier3', now)
        user['subscription']['role'] = 'tier3'
        self.assertEqual(user['quotas']['flatlaysRemaining'], 0)
        self.assertEqual(current_quota(user, now)['flatlaysRemaining'], 30)

    def test_legacy_inference_changes_no_balance_or_anchor_and_is_flagged(self):
        user = {'subscription': {'role': 'tier2'}, 'quotas': {'flatlaysRemaining': 3, 'lastRefillAt': 1000}}
        quota = current_quota(user, 1100)
        self.assertEqual(quota['flatlaysRemaining'], 3)
        self.assertEqual(quota['lastRefillAt'], 1000)
        self.assertEqual(quota['highestAllowanceGranted'], 7)
        self.assertTrue(quota['highestAllowanceInferred'])
        self.assertNotIn('highestAllowanceGranted', user['quotas'])
        self.assertEqual(apply_subscription_entitlement(user, 'tier3', 1100)['flatlaysRemaining'], 26)
        self.assertFalse(current_quota(user, 1000 + WEEKLY_ALLOWANCE_SECONDS)['highestAllowanceInferred'])

    def test_unknown_data_cannot_mint_and_input_is_unchanged(self):
        for fields in ({'flatlaysRemaining': -1}, {'flatlaysRemaining': 31}, {'flatlaysRemaining': True},
                       {'flatlaysRemaining': 1.5}, {'lastRefillAt': None}, {'lastRefillAt': 99999999999},
                       {'highestAllowanceGranted': 0}, {'highestAllowanceGranted': 31}):
            with self.subTest(fields=fields):
                user = account(); user['quotas'].update(fields)
                before = copy.deepcopy(user)
                with self.assertRaises(QuotaNeedsReview):
                    current_quota(user, 1100)
                with self.assertRaises(QuotaNeedsReview):
                    apply_subscription_entitlement(user, 'tier3', 1100)
                self.assertEqual(user, before)

    def test_billing_backed_expired_cancellation_refills_free_even_before_read_repair(self):
        user = account('tier3', remaining=0, highest=30)
        user.update(billing={'stripeCustomerId': 'cus_fixture'})
        user['subscription'].update(status='canceled', currentPeriodEnd=1100, cancelAtPeriodEnd=True)
        self.assertEqual(current_quota(user, 1000 + WEEKLY_ALLOWANCE_SECONDS)['flatlaysRemaining'], 1)
        user['billing'] = {}
        self.assertEqual(current_quota(user, 1000 + WEEKLY_ALLOWANCE_SECONDS)['flatlaysRemaining'], 30)


class BootstrapConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.decorator = patch.object(firestore, 'transactional', transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    def test_concurrent_first_sign_ins_create_one_allowance(self):
        del self.db.records['users']['owner']
        with ThreadPoolExecutor(max_workers=8) as pool:
            users = list(pool.map(lambda _: ensure_user_account(self.db, 'owner', email='owner@example.invalid', now=1000), range(20)))
        self.assertEqual(self.db.commits, 1)
        self.assertTrue(all(user['quotas']['flatlaysRemaining'] == 1 for user in users))
        self.assertEqual(users[0]['quotas']['highestAllowanceGranted'], 1)

    def test_existing_uncertain_data_returned_without_reconstruction(self):
        self.db.records['users']['owner'] = {'name': 'Legacy', 'subscription': {'tier': 'tier3'}}
        before = copy.deepcopy(self.db.records['users']['owner'])
        self.assertEqual(ensure_user_account(self.db, 'owner', now=1100), before)
        self.assertEqual(self.db.commits, 0)

    def test_sign_in_racing_debit_cannot_restore_credit(self):
        self.db.records['users']['owner'] = account()
        snapshot_taken, resume = threading.Event(), threading.Event()
        def hold_first_read(collection, key):
            if collection == 'users' and threading.current_thread().name.startswith('signin') and not snapshot_taken.is_set():
                snapshot_taken.set()
                if not resume.wait(5):
                    raise AssertionError('Reservation did not complete')
        self.db.after_read = hold_first_read
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix='signin') as pool:
            read = pool.submit(ensure_user_account, self.db, 'owner', now=1100)
            self.assertTrue(snapshot_taken.wait(5))
            try:
                lifecycle.reserve_request(self.db, 'look', 'owner', now=1100)
            finally:
                resume.set()
            user = read.result(timeout=5)
        self.assertEqual(user['quotas']['flatlaysRemaining'], 0)
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 0)
        self.assertEqual(self.db.conflicts, 1)

    def test_upgrade_racing_debit_retries_against_current_balance(self):
        self.db.records['users']['owner'] = account()
        snapshot_taken, resume = threading.Event(), threading.Event()
        def hold_first_read(collection, key):
            if collection == 'users' and threading.current_thread().name.startswith('upgrade') and not snapshot_taken.is_set():
                snapshot_taken.set()
                if not resume.wait(5):
                    raise AssertionError('Reservation did not complete')
        self.db.after_read = hold_first_read
        def upgrade():
            ref = self.db.collection('users').document('owner')
            @firestore.transactional
            def reconcile(txn):
                user = ref.get(transaction=txn).to_dict()
                quota = apply_subscription_entitlement(user, 'tier2', 1100)
                txn.update(ref, {'subscription.role': 'tier2', 'quotas': quota})
            reconcile(self.db.transaction())
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix='upgrade') as pool:
            applying = pool.submit(upgrade)
            self.assertTrue(snapshot_taken.wait(5))
            try:
                request = lifecycle.reserve_request(self.db, 'look', 'owner', now=1100)
            finally:
                resume.set()
            applying.result(timeout=5)
        user = self.db.records['users']['owner']
        self.assertEqual(self.db.conflicts, 1)
        self.assertEqual(user['quotas']['flatlaysRemaining'], 6)
        self.assertEqual(user['quotas']['highestAllowanceGranted'], 7)
        lifecycle.finish_request(self.db, 'look', request['request_id'], error='failed', now=1110)
        self.assertEqual(user['quotas']['flatlaysRemaining'], 7)

    def test_competing_outfits_cannot_spend_the_same_last_credit(self):
        self.db.records['users']['owner'] = account()
        self.db.records['outfits']['second'] = copy.deepcopy(self.db.records['outfits']['look'])
        def reserve(outfit_id):
            try:
                return lifecycle.reserve_request(self.db, outfit_id, 'owner', now=1100)['credit_status']
            except lifecycle.FlatlayRequestError as error:
                return error.status_code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reserve, ['look', 'second']))
        self.assertCountEqual(results, ['reserved', 403])
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 0)
        self.assertEqual(len(self.db.records[lifecycle.REQUESTS_COLLECTION]), 1)

    def test_unverified_or_invalid_uid_rejected(self):
        for uid in ('', None, 'users/owner'):
            with self.assertRaises(ValueError):
                ensure_user_account(self.db, uid, now=1100)
