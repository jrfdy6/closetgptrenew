"""No-network regressions for subscription reads racing real quota operations."""

import ast
import copy
import logging
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Optional
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from firebase_admin import firestore
from pydantic import BaseModel

from src.services import flatlay_lifecycle as lifecycle
from src.services.subscription_read_repair import read_subscription_user
from src.services.subscription_utils import current_quota, QuotaNeedsReview
from src.services.account_bootstrap import ensure_user_account

ROOT = Path(__file__).resolve().parents[1]


class Conflict(Exception):
    pass


class Document:
    def __init__(self, db, collection, key):
        self.db, self.collection, self.key = db, collection, key

    def get(self, transaction=None):
        with self.db.lock:
            if transaction:
                if transaction.writes:
                    raise AssertionError('Read after write in transaction')
                if transaction.version is None:
                    transaction.version = self.db.version
            value = copy.deepcopy(self.db.records.get(self.collection, {}).get(self.key))
        if self.db.after_read:
            self.db.after_read(self.collection, self.key)
        return SimpleNamespace(exists=value is not None, to_dict=lambda: copy.deepcopy(value))


class Transaction:
    def __init__(self, db):
        self.db, self.version, self.writes = db, None, []

    def update(self, ref, fields):
        self.writes.append(('update', ref, dict(fields)))

    def set(self, ref, fields):
        self.writes.append(('set', ref, copy.deepcopy(fields)))

    def commit(self):
        with self.db.lock:
            if self.version != self.db.version:
                self.db.conflicts += 1
                raise Conflict()
            for kind, ref, fields in self.writes:
                records = self.db.records.setdefault(ref.collection, {})
                if kind == 'set':
                    records[ref.key] = fields
                    continue
                for path, value in fields.items():
                    target = records[ref.key]
                    parts = path.split('.')
                    for part in parts[:-1]:
                        target = target.setdefault(part, {})
                    if value is firestore.DELETE_FIELD:
                        target.pop(parts[-1], None)
                    else:
                        target[parts[-1]] = copy.deepcopy(value)
            if self.writes:
                self.db.version += 1
                self.db.commits += 1


def transactional(callback):
    def run(transaction):
        for _ in range(8):
            attempt = Transaction(transaction.db)
            result = callback(attempt)
            try:
                attempt.commit()
            except Conflict:
                continue
            return result
        raise AssertionError('Transaction did not converge')
    return run


class Database:
    def __init__(self):
        self.records = {
            'users': {'owner': {
                'subscription': {'role': 'tier1', 'status': 'canceled',
                                 'currentPeriodEnd': 900, 'cancelAtPeriodEnd': True},
                'billing': {'stripeCustomerId': 'customer-fixture'},
                'quotas': {'flatlaysRemaining': 1, 'lastRefillAt': 1000},
            }},
            'outfits': {'look': {'user_id': 'owner', 'items': [{'id': 'shirt'}]}},
            'wardrobe': {'shirt': {'userId': 'owner'}},
        }
        self.lock = threading.RLock()
        self.version = self.commits = self.conflicts = 0
        self.after_read = None

    def collection(self, name):
        return SimpleNamespace(document=lambda key: Document(self, name, key))

    def transaction(self):
        return Transaction(self)


class SubscriptionReadRepairTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.decorator = patch.object(firestore, 'transactional', transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    @property
    def user(self):
        return self.db.records['users']['owner']

    def read(self, **kwargs):
        return read_subscription_user(self.db, 'owner', now=1100, **kwargs)

    def reserve(self):
        return lifecycle.reserve_request(self.db, 'look', 'owner', now=1100)

    def test_repeated_expired_canceled_reads_preserve_spent_credit_and_period(self):
        self.user['quotas']['flatlaysRemaining'] = 0
        first = self.read()
        self.assertEqual(first['quotas'], {'flatlaysRemaining': 0, 'lastRefillAt': 1000, 'highestAllowanceGranted': 1, 'highestAllowanceInferred': True})
        self.assertEqual(first['subscription']['currentPeriodEnd'], 0)
        self.assertFalse(first['subscription']['cancelAtPeriodEnd'])
        self.assertEqual(first['subscription']['status'], 'canceled')
        for _ in range(10):
            self.assertEqual(self.read(), first)
        self.assertEqual(self.db.commits, 1)

    def test_actual_downgrade_preserves_existing_and_uncertain_balances_without_refilling(self):
        for balance, expected in ((7, 7), (1, 1), (0, 0), (-2, -2), ('invalid', 'invalid')):
            with self.subTest(balance=balance):
                self.db = Database()
                self.user['subscription']['role'] = 'tier2'
                self.user['quotas']['flatlaysRemaining'] = balance
                result = self.read()
                self.assertEqual(result['subscription']['role'], 'tier1')
                self.assertEqual(result['quotas']['flatlaysRemaining'], expected)
                self.assertEqual(result['quotas']['lastRefillAt'], 1000)

    def test_downgrade_remembers_old_paid_high_water_before_removing_role(self):
        from src.services.subscription_utils import apply_subscription_entitlement
        self.user['subscription']['role'] = 'tier3'
        self.user['quotas']['flatlaysRemaining'] = 2
        result = self.read()
        self.assertEqual(result['subscription']['role'], 'tier1')
        self.assertEqual(result['quotas']['highestAllowanceGranted'], 30)
        self.assertEqual(apply_subscription_entitlement(result, 'tier3', 1110)['flatlaysRemaining'], 2)

    def test_missing_quota_does_not_mint_an_allowance_or_start_a_period(self):
        del self.user['quotas']
        result = self.read()
        self.assertNotIn('quotas', result)
        self.assertNotIn('quotas', self.user)

    def test_valid_premium_or_not_yet_expired_cancellation_is_unchanged(self):
        self.user['subscription'].update(role='tier2', currentPeriodEnd=1200)
        before = copy.deepcopy(self.user)
        self.assertEqual(self.read(), before)
        self.assertEqual(self.db.commits, 0)
        self.user['subscription'].update(currentPeriodEnd=900, status='active', cancelAtPeriodEnd=False)
        before = copy.deepcopy(self.user)
        self.assertEqual(self.read(), before)
        self.assertEqual(self.db.commits, 0)

    def test_unbacked_premium_is_report_only_not_automatically_reset(self):
        self.user['subscription'].update(role='tier2', stripeSubscriptionId='fixture', tier='tier2')
        self.user['billing'] = {}
        self.user['quotas']['flatlaysRemaining'] = 0
        before = copy.deepcopy(self.user)
        self.assertEqual(self.read(reset_unbacked_premium=True), before)
        self.assertEqual(self.user, before)
        self.assertEqual(self.db.commits, 0)

    def test_reservation_after_downgrade_stays_spent_through_later_reads(self):
        self.read()
        request = self.reserve()
        self.assertEqual(self.read()['quotas'], {'flatlaysRemaining': 0, 'lastRefillAt': 1000, 'highestAllowanceGranted': 1, 'highestAllowanceInferred': True})
        self.assertEqual(request['credit_status'], 'reserved')
        lifecycle.finish_request(self.db, 'look', request['request_id'], now=1120, url='https://example.invalid/result')
        self.assertEqual(self.read()['quotas']['flatlaysRemaining'], 0)

    def test_expiry_read_retries_if_reservation_debits_after_its_snapshot(self):
        snapshot_taken = threading.Event()
        resume_read = threading.Event()

        def hold_first_read(collection, key):
            if (collection == 'users' and threading.current_thread().name.startswith('downgrade')
                    and not snapshot_taken.is_set()):
                snapshot_taken.set()
                if not resume_read.wait(5):
                    raise AssertionError('Concurrent reservation did not finish')

        self.db.after_read = hold_first_read
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix='downgrade') as pool:
            reading = pool.submit(self.read)
            self.assertTrue(snapshot_taken.wait(5))
            try:
                request = self.reserve()
            finally:
                resume_read.set()
            result = reading.result(timeout=5)
        self.assertEqual(self.db.conflicts, 1)
        self.assertEqual(result['quotas'], {'flatlaysRemaining': 0, 'lastRefillAt': 1000, 'highestAllowanceGranted': 1, 'highestAllowanceInferred': True})
        ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual(ledger['quota_period_start'], 1000)
        self.assertEqual(ledger['credit_status'], 'reserved')
        # Preserving the period also lets a later proven failure refund once.
        self.assertTrue(lifecycle.finish_request(self.db, 'look', request['request_id'], now=1120,
                                               error='fixture failure', error_code='generation_failed'))
        self.assertEqual(self.read()['quotas'], {'flatlaysRemaining': 1, 'lastRefillAt': 1000, 'highestAllowanceGranted': 1, 'highestAllowanceInferred': True})
        self.assertFalse(lifecycle.finish_request(self.db, 'look', request['request_id'], now=1130,
                                                error='duplicate', error_code='generation_failed'))
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 1)

    def test_missing_user_returns_none_without_writes(self):
        del self.db.records['users']['owner']
        self.assertIsNone(self.read())
        self.assertEqual(self.db.commits, 0)

    def endpoint_client(self):
        tree = ast.parse((ROOT / 'src/routes/payments.py').read_text())
        names = {'SubscriptionResponse', 'get_current_subscription'}
        nodes = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef))
                 and node.name in names]
        env = {'router': APIRouter(), 'Depends': Depends, 'HTTPException': HTTPException,
               'get_current_user_id': lambda: 'owner', 'BaseModel': BaseModel, 'Optional': Optional,
               'db': self.db, 'read_subscription_user': read_subscription_user,
               'current_quota': current_quota, 'QuotaNeedsReview': QuotaNeedsReview,
               'ensure_user_account': ensure_user_account,
               'DEFAULT_ROLE': 'tier1', 'ROLE_LIMITS': {'tier1': 1, 'tier2': 7, 'tier3': 30},
               'datetime': SimpleNamespace(now=lambda tz: datetime.fromtimestamp(1100, tz)),
               'timezone': timezone, 'logger': logging.getLogger(__name__)}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'subscription_endpoint_under_test', 'exec'), env)
        app = FastAPI()
        app.include_router(env['router'], prefix='/api/payments')
        return TestClient(app)

    def test_current_subscription_http_returns_repaired_not_stale_balance(self):
        self.user['subscription']['role'] = 'tier2'
        self.user['quotas']['flatlaysRemaining'] = 7
        with self.endpoint_client() as client:
            response = client.get('/api/payments/subscription/current')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['role'], 'tier1')
        self.assertEqual(response.json()['flatlays_remaining'], 7)
        self.assertEqual(self.user['quotas']['lastRefillAt'], 1000)

    def test_current_subscription_http_does_not_replenish_zero(self):
        self.user['quotas']['flatlaysRemaining'] = 0
        with self.endpoint_client() as client:
            for _ in range(3):
                response = client.get('/api/payments/subscription/current')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['flatlays_remaining'], 0)
        self.assertEqual(self.db.commits, 1)

    def test_current_subscription_previews_due_refill_without_persisting_it(self):
        self.user['quotas'].update(flatlaysRemaining=0, lastRefillAt=1)
        # Fixture endpoint clock is 1100; use a custom pure helper that checks
        # the same quota at the actual weekly boundary, without writes.
        from src.services.subscription_utils import WEEKLY_ALLOWANCE_SECONDS
        before = copy.deepcopy(self.user['quotas'])
        preview = current_quota(self.user, 1 + WEEKLY_ALLOWANCE_SECONDS)
        self.assertEqual(preview['flatlaysRemaining'], 1)
        self.assertEqual(self.user['quotas'], before)

    def test_current_subscription_unknown_quota_returns_review_state_without_minting(self):
        self.user['quotas'] = {'flatlaysRemaining': 0}
        with self.endpoint_client() as client:
            response = client.get('/api/payments/subscription/current')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['flatlays_remaining'], 0)
        self.assertTrue(response.json()['quota_review_required'])
        self.assertEqual(self.user['quotas'], {'flatlaysRemaining': 0})

    def test_feature_access_uses_same_repair_and_preserves_quota(self):
        tree = ast.parse((ROOT / 'src/services/subscription_feature_access.py').read_text())
        node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'check_feature_access')
        # Avoid initializing Firebase or Stripe while executing the actual function.
        import typing
        env = {'Tuple': typing.Tuple, 'Optional': Optional, 'Dict': typing.Dict, 'Any': typing.Any,
               'db': self.db, 'read_subscription_user': read_subscription_user,
               'current_quota': current_quota, 'QuotaNeedsReview': QuotaNeedsReview,
               'ensure_user_account': ensure_user_account,
               'FEATURE_ACCESS_MATRIX': {'flatlay_generation': ['tier1', 'tier2', 'tier3']},
               'ACTIVE_STATUSES': ['active', 'trialing'], 'logger': logging.getLogger(__name__)}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'feature_access_under_test', 'exec'), env)
        self.user['quotas']['flatlaysRemaining'] = 0
        for _ in range(3):
            allowed, error, info = env['check_feature_access']('owner', 'flatlay_generation', require_active=False)
            self.assertTrue(allowed, error)
            self.assertEqual(info['flatlays_remaining'], 0)
        self.assertEqual(self.user['quotas']['lastRefillAt'], 1000)
        self.assertEqual(self.db.commits, 1)


if __name__ == '__main__':
    unittest.main()
