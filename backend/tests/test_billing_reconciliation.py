"""No-credential billing regressions: real handlers, transactional state, fake Stripe."""
import ast
import copy
import functools
import hashlib
import hmac
import json
import os
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
import stripe as stripe_sdk

from src.services import billing_reconciliation as billing
from src.services.billing_portal import BillingPortalConfigurationError, create_subscription_update_confirmation


class Snapshot:
    def __init__(self, key, value):
        self.id = key
        self.exists = value is not None
        self.value = copy.deepcopy(value)

    def to_dict(self):
        return copy.deepcopy(self.value)


class Document:
    def __init__(self, db, collection, key):
        self.db, self.collection, self.id = db, collection, key

    def get(self, transaction=None):
        if transaction and transaction.writes:
            raise AssertionError('Firestore prohibits reads after writes')
        with self.db.lock:
            return Snapshot(self.id, self.db.records.get(self.collection, {}).get(self.id))


class Query:
    def __init__(self, db, collection, field=None, value=None, maximum=None):
        self.db, self.collection = db, collection
        self.field, self.value, self.maximum = field, value, maximum

    def document(self, key):
        return Document(self.db, self.collection, key)

    def where(self, *, filter):
        return Query(self.db, self.collection, filter.field_path, filter.value, self.maximum)

    def limit(self, maximum):
        return Query(self.db, self.collection, self.field, self.value, maximum)

    def stream(self):
        with self.db.lock:
            rows = copy.deepcopy(self.db.records.get(self.collection, {}))
        result = []
        for key, value in rows.items():
            field_value = value
            if self.field:
                for part in self.field.split('.'):
                    field_value = field_value.get(part, {})
                if field_value != self.value:
                    continue
            result.append(Snapshot(key, value))
        return iter(result[:self.maximum])


class Transaction:
    def __init__(self, db):
        self.db = db
        self.writes = []

    def update(self, ref, fields):
        self.writes.append(('update', ref, copy.deepcopy(fields)))

    def set(self, ref, fields):
        self.writes.append(('set', ref, copy.deepcopy(fields)))

    def commit(self):
        if self.db.fail_completion and any(ref.collection == billing.EVENTS_COLLECTION for _, ref, _ in self.writes):
            raise RuntimeError('simulated atomic commit failure')
        records = copy.deepcopy(self.db.records)
        for kind, ref, fields in self.writes:
            collection = records.setdefault(ref.collection, {})
            if kind == 'set':
                collection[ref.id] = fields
            else:
                for key, value in fields.items():
                    parts = key.split('.')
                    node = collection[ref.id]
                    for part in parts[:-1]:
                        node = node.setdefault(part, {})
                    node[parts[-1]] = value
        self.db.records = records


def transactional(fn):
    @functools.wraps(fn)
    def wrapper(transaction):
        with transaction.db.lock:
            transaction.db.in_transaction.active = True
            try:
                result = fn(transaction)
                transaction.commit()
                return result
            finally:
                transaction.db.in_transaction.active = False
    return wrapper


class Database:
    def __init__(self):
        self.records = {'users': {'owner': {
            'billing': {'stripeCustomerId': 'cus_owner'},
            'subscription': {'role': 'tier1', 'status': 'active'},
            'quotas': {'flatlaysRemaining': 0, 'lastRefillAt': 1000, 'highestAllowanceGranted': 1},
        }}}
        self.lock = threading.RLock()
        self.in_transaction = threading.local()
        self.fail_completion = False

    def collection(self, collection):
        return Query(self, collection)

    def transaction(self):
        return Transaction(self)


def subscription(key='sub_current', price='price_pro', status='active', **values):
    return {'id': key, 'customer': 'cus_owner', 'created': 500, 'status': status,
            'current_period_end': 5000, 'items': {'data': [{'id': 'si_current', 'price': {'id': price}, 'quantity': 1}]},
            **values}


class Stripe:
    def __init__(self, db):
        self.db = db
        self.subscriptions = {'sub_current': subscription()}
        self.customer = {'id': 'cus_owner', 'metadata': {'user_id': 'owner'}}
        self.customer_hook = None
        self.subscription_hook = None
        self.calls = 0
        self.Customer = SimpleNamespace(retrieve=self.retrieve_customer)
        self.Subscription = SimpleNamespace(retrieve=self.retrieve_subscription, list=self.list_subscriptions)

    def check(self):
        if getattr(self.db.in_transaction, 'active', False):
            raise AssertionError('Stripe network request inside retryable transaction')
        self.calls += 1

    def retrieve_customer(self, key):
        self.check()
        if self.customer_hook:
            self.customer_hook()
        return copy.deepcopy(self.customer)

    def retrieve_subscription(self, key):
        self.check()
        result = copy.deepcopy(self.subscriptions[key])
        if self.subscription_hook:
            self.subscription_hook(key)
        return result

    def list_subscriptions(self, **kwargs):
        self.check()
        return {'data': copy.deepcopy(list(self.subscriptions.values())), 'has_more': False}


class BillingTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.stripe = Stripe(self.db)
        self.now = 1100
        self.price_ids = {'tier2': 'price_pro', 'tier3': 'price_premium', 'tier2_yearly': 'price_pro_year'}
        self.patch = patch.object(billing.firestore, 'transactional', transactional)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    @property
    def user(self):
        return self.db.records['users']['owner']

    def event(self, event_id='evt_one', event_type='customer.subscription.updated', sub='sub_current'):
        obj = {'id': sub, 'customer': 'cus_owner', 'subscription': sub,
               'mode': 'subscription', 'metadata': {'user_id': 'attacker', 'role': 'tier3'}}
        return {'id': event_id, 'type': event_type, 'data': {'object': obj}}

    def run_event(self, event=None):
        return billing.reconcile_stripe_event(self.db, self.stripe, event or self.event(), self.price_ids,
                                              clock=lambda: self.now)

    def test_duplicate_event_and_distinct_event_for_same_state_do_not_regrant_spent_credit(self):
        self.run_event()
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 6)
        self.user['quotas']['flatlaysRemaining'] = 3
        calls = self.stripe.calls
        self.assertTrue(self.run_event()['duplicate'])
        self.assertEqual(self.stripe.calls, calls)
        self.run_event(self.event('evt_two'))
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 3)
        self.assertEqual(self.user['quotas']['lastRefillAt'], 1000)
        self.assertEqual(self.user['subscription']['role'], 'tier2')
        self.assertNotIn('attacker', self.db.records['users'])

    def test_upgrade_downgrade_upgrade_cycle_grants_each_allowance_increase_once(self):
        self.run_event()
        self.user['quotas']['flatlaysRemaining'] = 4
        self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_premium'
        self.run_event(self.event('evt_two'))
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 27)
        self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_pro'
        self.run_event(self.event('evt_three'))
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 27)
        self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_premium'
        self.run_event(self.event('evt_four'))
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 27)
        self.assertEqual(self.user['quotas']['lastRefillAt'], 1000)

    def test_invoice_cannot_refill_expired_week_or_restore_canceled_subscription(self):
        self.now = 1000 + 7 * 86400
        self.user['subscription'].update(role='tier2', status='active')
        self.user['quotas']['highestAllowanceGranted'] = 7
        before = copy.deepcopy(self.user['quotas'])
        self.stripe.subscriptions['sub_current'].update(status='canceled', current_period_end=1200)
        self.run_event(self.event(event_type='invoice.payment_succeeded'))
        self.assertEqual(self.user['quotas'], before)
        self.assertEqual(self.user['subscription']['role'], 'tier1')
        self.assertEqual(self.user['subscription']['status'], 'canceled')

    def test_cancellation_keeps_remaining_paid_credits_and_week_anchor(self):
        self.user['subscription']['role'] = 'tier3'
        self.user['quotas'].update(flatlaysRemaining=22, highestAllowanceGranted=30)
        self.stripe.subscriptions['sub_current'].update(status='canceled')
        self.run_event(self.event(event_type='customer.subscription.deleted'))
        self.assertEqual(self.user['subscription']['role'], 'tier1')
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 22)
        self.assertEqual(self.user['quotas']['lastRefillAt'], 1000)

    def test_cancellation_scheduled_in_future_keeps_paid_access(self):
        self.stripe.subscriptions['sub_current'].update(cancel_at_period_end=True)
        self.run_event()
        self.assertEqual(self.user['subscription']['role'], 'tier2')
        self.now = 5001
        self.run_event(self.event('evt_later'))
        self.assertEqual(self.user['subscription']['role'], 'tier1')
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 6)

    def test_paginated_subscription_history_finds_current_replacement(self):
        self.stripe.subscriptions['sub_old'] = subscription('sub_old', status='canceled')
        pages = [
            {'data': [copy.deepcopy(self.stripe.subscriptions['sub_old'])], 'has_more': True},
            {'data': [copy.deepcopy(self.stripe.subscriptions['sub_current'])], 'has_more': False},
        ]
        self.stripe.Subscription.list = Mock(side_effect=pages)
        self.run_event(self.event(sub='sub_old'))
        self.assertEqual(self.user['subscription']['stripeSubscriptionId'], 'sub_current')
        self.assertEqual(self.stripe.Subscription.list.call_args.kwargs['starting_after'], 'sub_old')

    def test_renewal_invoice_is_not_weekly_refill(self):
        self.user['subscription']['role'] = 'tier2'
        self.user['quotas']['highestAllowanceGranted'] = 7
        for event_type in ('invoice.payment_succeeded', 'invoice.payment_failed'):
            self.run_event(self.event(event_id=event_type, event_type=event_type))
            self.assertEqual(self.user['quotas']['flatlaysRemaining'], 0)
            self.assertEqual(self.user['subscription']['status'], 'active')

    def test_old_subscription_notification_reconciles_current_replacement(self):
        self.stripe.subscriptions['sub_old'] = subscription('sub_old', status='canceled', created=100)
        self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_premium'
        self.run_event(self.event(event_type='customer.subscription.deleted', sub='sub_old'))
        self.assertEqual(self.user['subscription']['stripeSubscriptionId'], 'sub_current')
        self.assertEqual(self.user['subscription']['role'], 'tier3')
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 29)

    def test_event_price_and_role_are_not_authority(self):
        event = self.event()
        event['data']['object']['items'] = {'data': [{'price': {'id': 'price_premium'}}]}
        self.run_event(event)
        self.assertEqual(self.user['subscription']['role'], 'tier2')

    def test_unknown_price_and_duplicate_active_subscriptions_do_not_change_account(self):
        before = copy.deepcopy(self.user)
        self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_unknown'
        with self.assertRaises(billing.BillingReconciliationError):
            self.run_event()
        self.assertEqual(self.user, before)
        self.stripe.subscriptions['sub_current'] = subscription()
        self.stripe.subscriptions['sub_second'] = subscription('sub_second')
        with self.assertRaises(billing.BillingReconciliationError):
            self.run_event()
        self.assertEqual(self.user, before)
        self.assertNotIn(billing.EVENTS_COLLECTION, self.db.records)

    def test_user_mapping_is_unique_and_corroborates_customer_identity(self):
        before = copy.deepcopy(self.user)
        self.stripe.customer['metadata']['user_id'] = 'other'
        with self.assertRaises(billing.BillingReconciliationError):
            self.run_event()
        self.assertEqual(self.user, before)
        self.stripe.customer['metadata']['user_id'] = 'owner'
        self.db.records['users']['other'] = copy.deepcopy(self.user)
        with self.assertRaises(billing.BillingReconciliationError):
            self.run_event()
        self.assertEqual(self.user, before)

    def test_unknown_or_mismatched_customer_mapping_never_uses_event_metadata(self):
        self.user['billing']['stripeCustomerId'] = 'different'
        with self.assertRaises(billing.BillingReconciliationError):
            self.run_event()
        self.user['billing']['stripeCustomerId'] = 'cus_owner'
        self.db.records[billing.CUSTOMERS_COLLECTION] = {'cus_owner': {'user_id': 'other'}}
        with self.assertRaises(billing.BillingReconciliationError):
            self.run_event()

    def test_legacy_customer_without_identity_proof_is_not_promoted_to_trusted_mapping(self):
        self.stripe.customer['metadata'] = {}
        before = copy.deepcopy(self.user)
        with self.assertRaisesRegex(billing.BillingReconciliationError, 'unverified'):
            self.run_event()
        with self.assertRaisesRegex(billing.BillingReconciliationError, 'unverified'):
            billing.bind_checkout_customer(self.db, 'owner', self.stripe.customer)
        self.assertEqual(self.user, before)
        self.assertNotIn(billing.CUSTOMERS_COLLECTION, self.db.records)
        self.db.records[billing.CUSTOMERS_COLLECTION] = {'cus_owner': {'user_id': 'owner'}}
        self.run_event()
        self.assertEqual(self.user['subscription']['role'], 'tier2')

    def test_atomic_commit_failure_retries_and_grants_only_once(self):
        before = copy.deepcopy(self.user)
        self.db.fail_completion = True
        with self.assertRaises(RuntimeError):
            self.run_event()
        self.assertEqual(self.user, before)
        self.assertNotIn(billing.EVENTS_COLLECTION, self.db.records)
        self.db.fail_completion = False
        self.run_event()
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 6)
        self.assertEqual(self.db.records[billing.EVENTS_COLLECTION]['evt_one']['status'], 'completed')

    def test_invalid_legacy_quota_is_preserved_and_flagged_without_dropping_entitlement(self):
        self.user['quotas'] = {'flatlaysRemaining': 'invalid', 'lastRefillAt': 1000}
        self.run_event()
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 'invalid')
        self.assertEqual(self.user['subscription']['role'], 'tier2')
        self.assertTrue(self.db.records[billing.EVENTS_COLLECTION]['evt_one']['quota_needs_review'])

    def test_debit_during_stripe_call_is_preserved_by_fresh_commit_read(self):
        self.user['quotas']['flatlaysRemaining'] = 1
        def debit():
            self.user['quotas']['flatlaysRemaining'] = 0
        self.stripe.customer_hook = debit
        self.run_event()
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 6)

    def test_concurrent_event_retries_after_account_lease_instead_of_reading_stale_stripe(self):
        entered, release = threading.Event(), threading.Event()
        def hold():
            entered.set()
            self.assertTrue(release.wait(5))
        self.stripe.customer_hook = hold
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.run_event)
            self.assertTrue(entered.wait(5))
            with self.assertRaisesRegex(billing.BillingReconciliationError, 'already in progress'):
                self.run_event(self.event('evt_two'))
            release.set()
            first.result(timeout=5)
        self.stripe.customer_hook = None
        self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_premium'
        self.run_event(self.event('evt_two'))
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 29)
        self.assertEqual(self.user['subscription']['role'], 'tier3')

    def test_expired_lease_owner_cannot_overwrite_newer_entitlement(self):
        entered, release = threading.Event(), threading.Event()
        first_thread = [None]
        calls = [0]
        def hold_snapshot(key):
            if threading.get_ident() == first_thread[0]:
                calls[0] += 1
                if calls[0] == 2:
                    entered.set()
                    self.assertTrue(release.wait(5))
        self.stripe.subscription_hook = hold_snapshot
        def first_event():
            first_thread[0] = threading.get_ident()
            return self.run_event()
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(first_event)
            self.assertTrue(entered.wait(5))
            self.now += billing.LEASE_SECONDS + 1
            self.stripe.subscriptions['sub_current']['items']['data'][0]['price']['id'] = 'price_premium'
            self.run_event(self.event('evt_two'))
            release.set()
            with self.assertRaisesRegex(billing.BillingReconciliationError, 'lease expired'):
                first.result(timeout=5)
        self.assertEqual(self.user['subscription']['role'], 'tier3')
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 29)
        self.assertNotIn('evt_one', self.db.records[billing.EVENTS_COLLECTION])
        self.run_event()
        self.assertEqual(self.user['quotas']['flatlaysRemaining'], 29)

    def test_modern_invoice_parent_subscription_supported(self):
        event = self.event(event_type='invoice.payment_succeeded')
        event['data']['object'].pop('subscription')
        event['data']['object']['parent'] = {'subscription_details': {'subscription': 'sub_current'}}
        self.run_event(event)
        self.assertEqual(self.user['subscription']['role'], 'tier2')

    def test_customer_binding_rejects_overwriting_different_customer_or_owner(self):
        with self.assertRaises(billing.BillingReconciliationError):
            billing.bind_checkout_customer(self.db, 'owner', {'id': 'cus_other', 'metadata': {'user_id': 'owner'}})
        self.db.records[billing.CUSTOMERS_COLLECTION] = {'cus_owner': {'user_id': 'other'}}
        with self.assertRaises(billing.BillingReconciliationError):
            billing.bind_checkout_customer(self.db, 'owner', self.stripe.customer)
        self.assertEqual(self.user['billing']['stripeCustomerId'], 'cus_owner')


class PaymentHTTPTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((Path(__file__).parents[1] / 'src/routes/payments.py').read_text())
        wanted = {'stripe_webhook', 'create_portal_session', 'create_checkout_session', 'SubscriptionUpgradeRequest'}
        nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name in wanted]
        self.reconcile = Mock(return_value={'status': 'success'})
        self.db = Database()
        self.stripe = SimpleNamespace(Webhook=stripe_sdk.Webhook, error=stripe_sdk.error)
        env = {'APIRouter': APIRouter, 'Depends': Depends, 'Request': Request,
               'BaseModel': BaseModel, 'HTTPException': HTTPException, 'os': os,
               'logger': Mock(), 'router': APIRouter(),
               'STRIPE_AVAILABLE': True, 'stripe': self.stripe, 'db': self.db,
               'STRIPE_PRICE_IDS': {'tier2': 'price_pro', 'tier3': 'price_premium', 'tier2_yearly': 'price_pro_year', 'tier3_yearly': 'price_premium_year'}, 'FRONTEND_URL': 'https://example.test',
               'reconcile_stripe_event': self.reconcile, 'BillingReconciliationError': billing.BillingReconciliationError,
               'run_in_threadpool': run_in_threadpool, 'get_current_user_id': lambda: 'owner',
               'bind_checkout_customer': billing.bind_checkout_customer,
               'user_for_customer': billing.user_for_customer,
               'verify_customer_identity': billing.verify_customer_identity,
               'resolve_checkout_customer_id': billing.resolve_checkout_customer_id,
               'BillingPortalConfigurationError': BillingPortalConfigurationError,
               'create_subscription_update_confirmation': create_subscription_update_confirmation}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'payments_under_test', 'exec'), env)
        app = FastAPI()
        app.include_router(env['router'])
        self.client = TestClient(app)
        self.env_patch = patch.dict(os.environ, {'STRIPE_WEBHOOK_SECRET': 'whsec_fixture'})
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def signed(self, payload=None):
        data = payload or {'id': 'evt_one', 'object': 'event', 'type': 'customer.subscription.updated', 'data': {'object': {}}}
        body = json.dumps(data).encode()
        timestamp = int(time.time())
        signature = hmac.new(b'whsec_fixture', str(timestamp).encode() + b'.' + body, hashlib.sha256).hexdigest()
        return self.client.post('/webhook', content=body, headers={'stripe-signature': f't={timestamp},v1={signature}'})

    def test_real_stripe_signature_verification_accepts_original_body(self):
        self.assertEqual(self.signed().status_code, 200)
        self.reconcile.assert_called_once()

    def test_invalid_signature_never_reconciles(self):
        response = self.client.post('/webhook', json={'id': 'evt_one'}, headers={'stripe-signature': 'invalid'})
        self.assertEqual(response.status_code, 400)
        self.reconcile.assert_not_called()

    def test_missing_signature_is_bad_request_and_never_reconciles(self):
        self.assertEqual(self.client.post('/webhook', json={'id': 'evt_one'}).status_code, 400)
        self.reconcile.assert_not_called()

    def test_processing_failure_returns_retryable_non_success(self):
        for failure in (RuntimeError('connection lost'), billing.BillingReconciliationError('busy')):
            self.reconcile.side_effect = failure
            self.assertEqual(self.signed().status_code, 503)

    def test_portal_missing_customer_does_not_repair_or_refill_account(self):
        self.db.records['users']['owner']['billing'] = {}
        self.db.records['users']['owner']['subscription']['role'] = 'tier3'
        before = copy.deepcopy(self.db.records)
        self.assertEqual(self.client.post('/checkout/create-portal-session').status_code, 400)
        self.assertEqual(self.db.records, before)

    def test_portal_rejects_legacy_customer_without_private_or_metadata_proof(self):
        self.stripe.Customer = SimpleNamespace(retrieve=Mock(return_value={'id': 'cus_owner', 'metadata': {}}))
        portal = Mock()
        self.stripe.billing_portal = SimpleNamespace(Session=SimpleNamespace(create=portal))
        before = copy.deepcopy(self.db.records)
        self.assertEqual(self.client.post('/checkout/create-portal-session').status_code, 409)
        portal.assert_not_called()
        self.assertEqual(self.db.records, before)

    def test_checkout_rejects_unverified_legacy_customer_before_opening_session(self):
        customer = stripe_sdk.Customer.construct_from({'id': 'cus_owner', 'metadata': {}}, 'sk_test_unused')
        self.stripe.Customer = SimpleNamespace(retrieve=Mock(return_value=customer))
        with patch.object(billing.firestore, 'transactional', transactional):
            response = self.client.post('/checkout/create-session', json={'role': 'tier2'})
        self.assertEqual(response.status_code, 409)
        self.assertNotIn(billing.CUSTOMERS_COLLECTION, self.db.records)

    def configure_paid_checkout(self, current=None):
        customer = stripe_sdk.Customer.construct_from({'id': 'cus_owner', 'metadata': {'user_id': 'owner'}}, 'sk_test_unused')
        self.stripe.Customer = SimpleNamespace(retrieve=Mock(return_value=customer), create=Mock())
        self.current_subscription = current or subscription()
        self.stripe.Subscription = SimpleNamespace(
            list=Mock(return_value=SimpleNamespace(auto_paging_iter=lambda: iter([self.current_subscription]))),
            retrieve=Mock(side_effect=lambda sub_id: copy.deepcopy(self.current_subscription)),
        )
        self.create_checkout = Mock(return_value=SimpleNamespace(url='https://checkout.test', id='cs_one'))
        self.stripe.checkout = SimpleNamespace(Session=SimpleNamespace(create=self.create_checkout))
        self.portal_config = {
            'id': 'bpc_default', 'active': True, 'is_default': True,
            'features': {'subscription_update': {
                'enabled': True, 'default_allowed_updates': ['price'],
                'products': [{'product': 'prod_pro', 'prices': ['price_pro', 'price_pro_year']},
                             {'product': 'prod_premium', 'prices': ['price_premium', 'price_premium_year']}],
                'proration_behavior': 'always_invoice', 'schedule_at_period_end': {'conditions': []},
            }},
        }
        self.create_portal = Mock(return_value=SimpleNamespace(url='https://billing.test/portal', id='bps_one'))
        self.stripe.billing_portal = SimpleNamespace(
            Configuration=SimpleNamespace(list=Mock(side_effect=lambda **kw: {'data': [copy.deepcopy(self.portal_config)], 'has_more': False})),
            Session=SimpleNamespace(create=self.create_portal),
        )

    def checkout(self, **values):
        with patch.object(billing.firestore, 'transactional', transactional):
            return self.client.post('/checkout/create-session', json={'role': 'tier3', **values})

    def test_existing_paid_user_checkout_confirms_requested_price_on_existing_item(self):
        self.configure_paid_checkout()
        response = self.checkout(interval='year')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['checkout_url'], 'https://billing.test/portal')
        self.create_checkout.assert_not_called()
        request = self.create_portal.call_args.kwargs
        self.assertEqual(request['customer'], 'cus_owner')
        self.assertEqual(request['configuration'], 'bpc_default')
        self.assertEqual(request['flow_data']['type'], 'subscription_update_confirm')
        self.assertEqual(request['flow_data']['subscription_update_confirm'], {
            'subscription': 'sub_current',
            'items': [{'id': 'si_current', 'price': 'price_premium_year', 'quantity': 1}],
        })
        self.assertEqual(request['flow_data']['after_completion']['redirect']['return_url'], 'https://example.test/subscription')

    def test_disabled_or_incompatible_portal_config_is_503_without_duplicate_checkout(self):
        for change in ({'enabled': False}, {'default_allowed_updates': []}, {'products': []},
                       {'proration_behavior': 'none'}, {'schedule_at_period_end': {'conditions': [{'type': 'decreasing_item_amount'}]}}):
            with self.subTest(change=change):
                self.configure_paid_checkout()
                self.portal_config['features']['subscription_update'].update(change)
                response = self.checkout()
                self.assertEqual(response.status_code, 503)
                self.assertIn('temporarily unavailable', response.json()['detail'])
                self.create_checkout.assert_not_called()
                self.create_portal.assert_not_called()

    def test_existing_subscriber_state_or_identity_mismatch_never_opens_new_checkout(self):
        for change in ({'status': 'past_due'}, {'status': 'incomplete'}, {'customer': 'cus_other'},
                       {'items': {'data': []}}, {'schedule': 'sub_sched_pending'}):
            with self.subTest(change=change):
                self.configure_paid_checkout(subscription(**change))
                self.assertEqual(self.checkout().status_code, 409)
                self.create_checkout.assert_not_called()
                self.create_portal.assert_not_called()

    def test_historical_customer_alias_reuses_customer_and_past_trial(self):
        for path in ('top', 'subscription'):
            with self.subTest(path=path):
                self.configure_paid_checkout(subscription(status='canceled', trial_end=500))
                user = self.db.records['users']['owner']
                user['billing'] = {}
                user.pop('stripeCustomerId', None)
                user['subscription'].pop('stripeCustomerId', None)
                if path == 'top':
                    user['stripeCustomerId'] = 'cus_owner'
                else:
                    user['subscription']['stripeCustomerId'] = 'cus_owner'
                response = self.checkout()
                self.assertEqual(response.status_code, 200)
                self.stripe.Customer.create.assert_not_called()
                self.assertEqual(self.create_checkout.call_args.kwargs['customer'], 'cus_owner')
                self.assertNotIn('trial_period_days', self.create_checkout.call_args.kwargs['subscription_data'])
                self.assertEqual(self.db.records['users']['owner']['billing']['stripeCustomerId'], 'cus_owner')

    def test_historical_subscription_only_resolves_customer_without_repeating_trial(self):
        self.configure_paid_checkout(subscription(status='canceled', trial_end=500))
        user = self.db.records['users']['owner']
        user['billing'] = {}
        user['stripeSubscriptionId'] = 'sub_current'
        self.assertEqual(self.checkout().status_code, 200)
        self.stripe.Customer.create.assert_not_called()
        self.stripe.Subscription.retrieve.assert_called_with('sub_current')
        self.assertNotIn('trial_period_days', self.create_checkout.call_args.kwargs['subscription_data'])

    def test_conflicting_historical_customer_aliases_require_review(self):
        self.configure_paid_checkout()
        self.db.records['users']['owner']['stripeCustomerId'] = 'cus_other'
        self.assertEqual(self.checkout().status_code, 409)
        self.stripe.Customer.create.assert_not_called()
        self.create_checkout.assert_not_called()
        self.create_portal.assert_not_called()

    def test_checkout_rejects_unconfigured_role_and_invalid_interval(self):
        for body in ({'role': 'tier1'}, {'role': 'tier2', 'interval': 'day'}, {'role': 'tier4'}):
            self.assertEqual(self.client.post('/checkout/create-session', json=body).status_code, 400)


if __name__ == '__main__':
    unittest.main()
