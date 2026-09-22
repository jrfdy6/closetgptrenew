"""No-credential regression tests for quota/queue transactions and worker failures."""
import ast
import copy
import functools
import os
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from PIL import Image
from src.services import flatlay_lifecycle as lifecycle
from worker.flatlay_reference_images import ReferenceImageError
from worker import flatlay_lifecycle as worker_lifecycle
from worker.original_source import DEFAULT_BUCKET_NAME

ROOT = Path(__file__).resolve().parents[1]


class Snapshot:
    def __init__(self, value):
        self.exists = value is not None
        self.value = copy.deepcopy(value)

    def to_dict(self):
        return copy.deepcopy(self.value)


class Document:
    def __init__(self, db, collection, key):
        self.db, self.collection, self.id = db, collection, key

    def get(self, transaction=None):
        if transaction and transaction.writes:
            raise AssertionError('Firestore does not allow reads after transactional writes')
        return Snapshot(self.db.records.get(self.collection, {}).get(self.id))


class Transaction:
    def __init__(self, db):
        self.db = db
        self.writes = []

    def update(self, ref, fields):
        self.writes.append(('update', ref, copy.deepcopy(fields)))

    def set(self, ref, fields):
        self.writes.append(('set', ref, copy.deepcopy(fields)))

    def commit(self):
        if self.db.fail_commit:
            raise RuntimeError('simulated failed transaction')
        for kind, ref, fields in self.writes:
            collection = self.db.records.setdefault(ref.collection, {})
            if kind == 'set':
                collection[ref.id] = fields
            else:
                data = collection[ref.id]
                for key, value in fields.items():
                    parts = key.split('.')
                    node = data
                    for part in parts[:-1]:
                        node = node.setdefault(part, {})
                    node[parts[-1]] = value


def transactional(fn):
    @functools.wraps(fn)
    def wrapper(transaction):
        with transaction.db.lock:
            result = fn(transaction)
            transaction.commit()
            return result
    return wrapper


class Collection:
    def __init__(self, db, name, filters=(), order=None, maximum=None, cursor=None):
        self.db, self.name = db, name
        self.filters, self.order, self.maximum = filters, order, maximum
        self.cursor = cursor

    def document(self, key):
        return Document(self.db, self.name, key)

    def where(self, *, filter):
        return Collection(self.db, self.name, (*self.filters, filter), self.order, self.maximum, self.cursor)

    def order_by(self, field):
        return Collection(self.db, self.name, self.filters, field, self.maximum, self.cursor)

    def limit(self, maximum):
        return Collection(self.db, self.name, self.filters, self.order, maximum, self.cursor)

    def start_after(self, snapshot):
        return Collection(self.db, self.name, self.filters, self.order, self.maximum, snapshot)

    def stream(self, **_kwargs):
        rows = sorted(self.db.records.get(self.name, {}).items())
        for field, operator, expected in self.filters:
            if operator == '==':
                rows = [(key, row) for key, row in rows if row.get(field) == expected]
            else:
                rows = [(key, row) for key, row in rows
                        if isinstance(row.get(field), (int, float)) and
                        ((operator == '>=' and row[field] >= expected) or
                         (operator == '<=' and row[field] <= expected))]
        if self.order:
            rows.sort(key=lambda entry: entry[1][self.order])
        if self.cursor is not None:
            position = (self.cursor.to_dict()[self.order], self.cursor.id)
            rows = [(key, row) for key, row in rows if (row[self.order], key) > position]
        for key, row in rows[:self.maximum]:
            yield SimpleNamespace(id=key, to_dict=lambda row=copy.deepcopy(row): copy.deepcopy(row))


class Database:
    def __init__(self):
        self.records = {
            'users': {'owner': {'subscription': {'role': 'tier2'}, 'quotas': {'flatlaysRemaining': 7, 'lastRefillAt': 1000}}},
            'outfits': {'look': {'user_id': 'owner', 'items': [{'id': 'shirt'}, {'id': 'pants'}, {'id': 'shirt'}]}},
            'wardrobe': {'shirt': {'userId': 'owner', 'name': 'My shirt', 'imageUrl': 'https://assets.invalid/shirt'},
                         'pants': {'user_id': 'owner', 'name': 'My pants'}},
        }
        self.lock = threading.RLock()
        self.fail_commit = False

    def collection(self, name):
        return Collection(self, name)

    def transaction(self):
        return Transaction(self)


class FlatlayLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.decorator = patch.object(lifecycle.firestore, 'transactional', transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    def reserve(self, **kwargs):
        return lifecycle.reserve_request(self.db, 'look', 'owner', now=1100, **kwargs)

    def claim(self, now=1110):
        return lifecycle.claim_request(self.db, 'look', now=now)

    def remaining(self):
        return self.db.records['users']['owner']['quotas']['flatlaysRemaining']

    def finish(self, request_id, **kwargs):
        return lifecycle.finish_request(self.db, 'look', request_id, now=1120, **kwargs)

    def test_worker_and_api_contracts_stay_identical(self):
        self.assertEqual((ROOT / 'worker/flatlay_lifecycle.py').read_bytes(),
                         (ROOT / 'src/services/flatlay_lifecycle.py').read_bytes())

    def test_nonclaimable_oldest_ledger_does_not_starve_next_valid_request(self):
        from test_worker_coordinator import Process, flatlay_candidates_under_test
        from worker.coordinator import WorkerCoordinator
        self.db.records['outfits']['next-look'] = copy.deepcopy(self.db.records['outfits']['look'])
        worker_lifecycle.reserve_request(self.db, 'look', 'owner', now=1100)
        worker_lifecycle.reserve_request(self.db, 'next-look', 'owner', now=1101)
        ledger = self.db.records[worker_lifecycle.REQUESTS_COLLECTION]
        ledger['look']['outfit_id'] = 'different-outfit'
        held_before = copy.deepcopy(ledger['look'])
        outfit_before = copy.deepcopy(self.db.records['outfits']['look'])
        quota_before = copy.deepcopy(self.db.records['users']['owner']['quotas'])
        attempts = []

        def start_flatlay(identifier):
            # The real transaction remains the only authority to claim. A
            # declined child exits without touching the held record.
            claim = worker_lifecycle.claim_request(self.db, identifier, now=1110)
            attempts.append((identifier, claim))
            process = Process()
            process.outcome = {'status': 'succeeded'}
            return process

        coordinator = WorkerCoordinator(
            expire_flatlays=Mock(), recover_garments=Mock(), garment_candidates=lambda: [],
            claim_garment=Mock(), start_garment=Mock(), publish_original=Mock(), finish_garment=Mock(),
            flatlay_candidates=flatlay_candidates_under_test(self.db), start_flatlay=start_flatlay,
        )
        self.addCleanup(coordinator.close)
        coordinator.tick()
        coordinator.tick()
        self.assertEqual([identifier for identifier, _ in attempts], ['look', 'next-look'])
        self.assertIsNone(attempts[0][1])
        self.assertEqual(attempts[1][1]['outfit_id'], 'next-look')
        self.assertEqual(ledger['next-look']['status'], 'processing')
        self.assertEqual(ledger['look'], held_before)
        self.assertEqual(self.db.records['outfits']['look'], outfit_before)
        self.assertEqual(self.db.records['users']['owner']['quotas'], quota_before)

    def test_projection_reconciliation_cannot_claim_pending_paid_work(self):
        reserved = self.reserve()
        self.assertIsNone(lifecycle.claim_request(self.db, 'look', now=1110, allow_claim=False))
        request = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual(request['status'], 'pending')
        self.assertEqual(request['request_id'], reserved['request_id'])
        self.assertEqual(self.remaining(), 6)

    def test_original_path_comes_from_private_publication_and_is_immutable_in_request(self):
        from src.services.garment_lifecycle import garment_source_fingerprint
        garment = self.db.records['wardrobe']['shirt']
        garment['originalStoragePath'] = 'items/other/attempts/stolen/original.png'
        private_path = 'items/shirt/attempts/first-attempt/original.png'
        self.db.records['garment_processing_jobs'] = {'shirt': {
            'user_id': 'owner', 'attempt_id': 'first-attempt', 'original_attempt_id': 'first-attempt',
            'source_fingerprint': garment_source_fingerprint(garment),
            'original_source_fingerprint': garment_source_fingerprint(garment),
            'original': {'originalStoragePath': private_path, 'originalUrl': 'https://assets.invalid/original'},
        }}
        self.reserve()
        self.db.records['garment_processing_jobs']['shirt']['attempt_id'] = 'later-attempt'
        request = self.claim()
        self.assertEqual(request['items'][0]['originalStoragePath'], private_path)
        self.assertEqual(request['items'][1]['originalStoragePath'], 'items/pants/original.png')

    def test_missing_changed_or_foreign_private_original_never_reserves_credit(self):
        from src.services.garment_lifecycle import garment_source_fingerprint
        item = self.db.records['wardrobe']['shirt']
        valid = {'user_id': 'owner', 'attempt_id': 'attempt-one', 'original_attempt_id': 'attempt-one',
                 'source_fingerprint': garment_source_fingerprint(item),
                 'original_source_fingerprint': garment_source_fingerprint(item),
                 'original': {'originalStoragePath': 'items/shirt/attempts/attempt-one/original.png'}}
        cases = [
            {**valid, 'original': {}}, {**valid, 'user_id': 'other'},
            {**valid, 'source_fingerprint': 'previous-image'},
            {**valid, 'original': {'originalStoragePath': 'items/pants/attempts/attempt-one/original.png'}},
            {**valid, 'original': {'originalStoragePath': 'https://attacker.invalid/photo'}},
        ]
        for job in cases:
            with self.subTest(job=job):
                self.db.records['garment_processing_jobs'] = {'shirt': job}
                with self.assertRaises(lifecycle.FlatlayRequestError) as caught:
                    self.reserve()
                self.assertEqual(caught.exception.status_code, 422)
                self.assertEqual(self.remaining(), 7)
                self.assertNotIn('look', self.db.records.get(lifecycle.REQUESTS_COLLECTION, {}))

    def test_previous_attempt_original_remains_available_after_later_crash(self):
        from src.services.garment_lifecycle import garment_source_fingerprint
        garment = self.db.records['wardrobe']['shirt']
        original_path = 'items/shirt/attempts/first-attempt/original.png'
        self.db.records['garment_processing_jobs'] = {'shirt': {
            'user_id': 'owner', 'attempt_id': 'third-attempt', 'status': 'failed',
            'source_fingerprint': garment_source_fingerprint(garment),
            'original_source_fingerprint': garment_source_fingerprint(garment),
            'original_attempt_id': 'first-attempt',
            'original': {'originalStoragePath': original_path},
        }}
        self.reserve()
        self.assertEqual(self.claim()['items'][0]['originalStoragePath'], original_path)

    def test_legacy_original_path_does_not_trust_public_path_field(self):
        self.db.records['wardrobe']['shirt']['originalStoragePath'] = 'items/other/original.png'
        self.reserve()
        self.assertEqual(self.claim()['items'][0]['originalStoragePath'], 'items/shirt/original.png')

    def test_concurrent_requests_reserve_exactly_one_credit_and_snapshot_unique_owned_assets(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.reserve(), range(20)))
        self.assertEqual(self.remaining(), 6)
        self.assertEqual(len({result['request_id'] for result in results}), 1)
        self.assertTrue(all(result['flat_lay_status'] == 'pending' for result in results))
        ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual([item['id'] for item in ledger['items']], ['shirt', 'pants'])
        self.assertEqual(ledger['items'][0]['imageUrl'], 'https://assets.invalid/shirt')
        self.assertEqual(self.db.records['users']['owner']['quotas']['lastRefillAt'], 1000)

    def test_quota_denial_and_failed_commit_do_not_enqueue_or_charge(self):
        self.db.records['users']['owner']['quotas']['flatlaysRemaining'] = 0
        with self.assertRaises(lifecycle.FlatlayRequestError) as ctx:
            self.reserve()
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)
        self.db.records['users']['owner']['quotas']['flatlaysRemaining'] = 7
        self.db.fail_commit = True
        with self.assertRaises(RuntimeError):
            self.reserve()
        self.assertEqual(self.remaining(), 7)
        self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)
        self.assertNotIn('flat_lay_status', self.db.records['outfits']['look'])

    def test_same_owner_request_bound_to_another_outfit_cannot_reserve_or_return_preview(self):
        for status in ('pending', 'processing', 'failed', 'done'):
            with self.subTest(status=status):
                self.db = Database()
                self.reserve()
                ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
                ledger.update(outfit_id='another-look', status=status, credit_status='refunded',
                              retryable=True, url='https://assets.invalid/unrelated')
                before = copy.deepcopy(self.db.records)
                with self.assertRaises(lifecycle.FlatlayRequestError) as caught:
                    self.reserve()
                self.assertEqual(caught.exception.status_code, 409)
                self.assertEqual(self.db.records, before)

    def test_claim_and_reconciliation_leave_misbound_private_request_untouched(self):
        for status in ('pending', 'processing', 'failed', 'done'):
            for identity in ('another-look', None, ''):
                with self.subTest(status=status, identity=identity):
                    self.db = Database()
                    self.reserve()
                    self.db.records[lifecycle.REQUESTS_COLLECTION]['look'].update(
                        outfit_id=identity, status=status, url='https://assets.invalid/unrelated')
                    before = copy.deepcopy(self.db.records)
                    self.assertIsNone(self.claim())
                    self.assertIsNone(lifecycle.claim_request(self.db, 'look', now=1111, allow_claim=False))
                    self.assertEqual(self.db.records, before)

    def test_finish_does_not_publish_refund_or_expire_misbound_private_request(self):
        outcomes = (
            {'url': 'https://assets.invalid/unrelated'},
            {'error': 'Known failure'},
            {'error': 'Unknown outcome', 'error_code': 'provider_outcome_unknown', 'retryable': False},
            {'error': 'Expired', 'expired_only': True},
        )
        for status in ('pending', 'processing'):
            for identity in ('another-look', None, ''):
                for outcome in outcomes:
                    with self.subTest(status=status, identity=identity, outcome=outcome):
                        self.db = Database()
                        first = self.reserve()
                        self.db.records[lifecycle.REQUESTS_COLLECTION]['look'].update(
                            outfit_id=identity, status=status, expires_at=1110)
                        before = copy.deepcopy(self.db.records)
                        self.assertFalse(self.finish(first['request_id'], **outcome))
                        self.assertEqual(self.db.records, before)

    def test_unknown_outcome_blocks_stale_retryable_refunded_request_without_any_mutation(self):
        for code in ('provider_outcome_unknown', 'worker_outcome_unknown'):
            with self.subTest(code=code):
                self.db = Database()
                self.reserve()
                self.db.records[lifecycle.REQUESTS_COLLECTION]['look'].update(
                    status='failed', credit_status='refunded', retryable=True, error_code=code)
                before = copy.deepcopy(self.db.records)
                with self.assertRaises(lifecycle.FlatlayRequestError) as caught:
                    self.reserve()
                self.assertEqual(caught.exception.status_code, 409)
                self.assertEqual(self.db.records, before)

    def test_ledger_free_queued_projection_needs_review_for_each_legacy_alias(self):
        cases = (
            {'flat_lay_status': 'queued'}, {'flatLayStatus': 'queued'},
            {'metadata': {'flat_lay_status': 'queued'}}, {'metadata': {'flatLayStatus': 'queued'}},
            {'flat_lay_status': 'awaiting_consent', 'flatLayStatus': 'queued'},
            {'flat_lay_status': 'awaiting_consent', 'metadata': {'flatLayStatus': 'queued'}},
        )
        for projection in cases:
            with self.subTest(projection=projection):
                self.db = Database()
                self.db.records['outfits']['look'].update(projection)
                response = self.reserve()
                self.assertEqual(response['flat_lay_status'], 'failed')
                self.assertEqual(response['error_code'], 'legacy_request_needs_review')
                self.assertFalse(response['request_allowed'])
                self.assertIsNone(response['flat_lay_url'])
                self.assertEqual(self.remaining(), 7)
                self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_unknown_outfit_wrong_owner_and_conflicting_owner_never_charge(self):
        for ownership in ({'user_id': 'other'}, {'user_id': 'owner', 'userId': 'other'}):
            with self.subTest(ownership=ownership):
                self.db.records['outfits']['look'].update(ownership)
                with self.assertRaises(lifecycle.FlatlayRequestError) as ctx:
                    self.reserve()
                self.assertEqual(ctx.exception.status_code, 403)
        self.db.records['outfits'].clear()
        with self.assertRaises(lifecycle.FlatlayRequestError) as ctx:
            self.reserve()
        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(self.remaining(), 7)

    def test_missing_or_unowned_wardrobe_item_rejects_whole_request(self):
        for item in (None, {'userId': 'other'}, {'userId': 'owner', 'user_id': 'other'}):
            with self.subTest(item=item):
                self.db.records['wardrobe']['pants'] = item
                with self.assertRaises(lifecycle.FlatlayRequestError) as ctx:
                    self.reserve()
                self.assertEqual(ctx.exception.status_code, 422)
                self.assertEqual(self.remaining(), 7)
                self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_legacy_pending_failed_or_processing_has_no_guessed_debit_refund_or_retry(self):
        for state in ('pending', 'processing', 'failed', 'done'):
            with self.subTest(state=state):
                self.db.records['outfits']['look']['flat_lay_status'] = state
                response = self.reserve()
                self.assertEqual(response['flat_lay_status'], 'failed')
                self.assertFalse(response['retryable'])
                self.assertFalse(response['request_allowed'])
                self.assertEqual(response['error_code'], 'legacy_request_needs_review')
                self.assertEqual(self.remaining(), 7)
                self.assertIsNone(self.claim())
                self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_done_legacy_preview_needs_review_without_spending_or_returning_unverified_url(self):
        self.db.records['outfits']['look'].update(flat_lay_status='done', flat_lay_url='https://assets.invalid/done')
        response = self.reserve()
        self.assertEqual(response['flat_lay_status'], 'failed')
        self.assertIsNone(response['flat_lay_url'])
        self.assertEqual(response['error_code'], 'legacy_request_needs_review')
        self.assertFalse(response['request_allowed'])
        self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)
        self.assertEqual(self.remaining(), 7)

    def test_worker_claim_is_exclusive_and_does_not_reserve_again(self):
        response = self.reserve()
        with ThreadPoolExecutor(max_workers=8) as pool:
            claims = list(pool.map(lambda _: self.claim(), range(10)))
        self.assertEqual(len([claim for claim in claims if claim]), 1)
        self.assertEqual(self.remaining(), 6)
        self.assertEqual(self.reserve()['flat_lay_status'], 'processing')
        self.assertEqual(self.reserve()['request_id'], response['request_id'])

    def test_success_keeps_single_credit_consumed_and_retries_are_noops(self):
        request = self.reserve()
        self.claim()
        self.assertTrue(self.finish(request['request_id'], url='https://assets.invalid/complete'))
        self.assertFalse(self.finish(request['request_id'], error='late error'))
        self.assertEqual(self.remaining(), 6)
        repeated = self.reserve()
        self.assertEqual(repeated['flat_lay_status'], 'done')
        self.assertEqual(repeated['credit_status'], 'consumed')
        self.assertEqual(self.remaining(), 6)

    def test_failure_refunds_once_then_explicit_retry_has_new_id(self):
        first = self.reserve()
        self.claim()
        self.assertTrue(self.finish(first['request_id'], error='Image not ready'))
        self.assertFalse(self.finish(first['request_id'], error='same error'))
        self.assertEqual(self.remaining(), 7)
        second = self.reserve()
        self.assertNotEqual(first['request_id'], second['request_id'])
        self.assertEqual(self.remaining(), 6)
        self.assertFalse(self.finish(first['request_id'], url='https://assets.invalid/stale'))
        self.assertEqual(self.db.records['outfits']['look']['flat_lay_status'], 'pending')

    def test_refund_after_weekly_rollover_does_not_add_extra_allowance(self):
        request = self.reserve()
        lifecycle.finish_request(self.db, 'look', request['request_id'], error='failure', now=1000 + lifecycle.WEEK_SECONDS)
        self.assertEqual(self.remaining(), 7)
        self.assertEqual(self.db.records['users']['owner']['quotas']['lastRefillAt'], 1000 + lifecycle.WEEK_SECONDS)

    def test_unconfirmed_crash_returns_known_credit_once_but_blocks_paid_retry(self):
        request = self.reserve()
        claimed = self.claim()
        self.assertFalse(lifecycle.finish_request(self.db, 'look', request['request_id'], error='timeout', retryable=False,
                                                 now=1111, expired_only=True))
        self.assertTrue(lifecycle.finish_request(self.db, 'look', request['request_id'], error='Needs review', retryable=False,
                                                now=claimed['expires_at'], expired_only=True))
        self.assertEqual(self.remaining(), 7)
        with self.assertRaises(lifecycle.FlatlayRequestError) as ctx:
            self.reserve()
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertFalse(self.finish(request['request_id'], url='https://assets.invalid/late'))

    def test_missing_user_cannot_claim_unprovable_refund(self):
        request = self.reserve()
        self.db.records['users'].clear()
        self.finish(request['request_id'], error='Cannot complete')
        ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual(ledger['credit_status'], 'refund_needs_review')
        self.assertFalse(ledger['retryable'])

    def test_old_pending_claim_fails_before_provider(self):
        self.reserve()
        self.assertEqual(self.claim(now=3000)['preflight_error'], 'queue_timeout')

    def test_deleted_outfit_returns_reserved_credit_without_provider_work(self):
        response = self.reserve()
        self.db.records['outfits'].clear()
        claimed = self.claim()
        self.assertEqual(claimed['preflight_error'], 'outfit_unavailable')
        self.assertTrue(self.finish(response['request_id'], error='Outfit unavailable'))
        self.assertEqual(self.remaining(), 7)

    def test_legacy_camelcase_metadata_preview_cannot_bypass_identity_review(self):
        self.db.records['outfits']['look']['metadata'] = {'flatLayStatus': 'done', 'flatLayUrl': 'https://assets.invalid/legacy'}
        response = self.reserve()
        self.assertIsNone(response['flat_lay_url'])
        self.assertEqual(response['error_code'], 'legacy_request_needs_review')
        self.assertFalse(response['request_allowed'])
        self.assertIsNone(self.db.records['outfits']['look']['metadata']['flatLayUrl'])
        self.assertEqual(self.remaining(), 7)

    def test_stale_legacy_pending_projection_reconciles_from_terminal_private_ledger(self):
        response = self.reserve()
        self.claim()
        self.finish(response['request_id'], url='https://assets.invalid/finished')
        self.db.records['outfits']['look']['flat_lay_status'] = 'pending'
        self.assertIsNone(self.claim())
        outfit = self.db.records['outfits']['look']
        self.assertEqual(outfit['flat_lay_status'], 'done')
        self.assertEqual(outfit['flat_lay_url'], 'https://assets.invalid/finished')
        self.assertEqual(self.remaining(), 6)

    def test_pending_queue_index_is_cleared_on_claim_and_settlement(self):
        response = self.reserve()
        ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual(ledger['queued_at'], 1100)
        self.claim()
        self.assertIsNone(ledger['queued_at'])
        self.finish(response['request_id'], error='failure')
        self.assertIsNone(ledger['queued_at'])
        self.assertIsNone(ledger['expires_at'])

    def test_pending_item_edit_fails_preflight_and_refunds_its_one_reservation(self):
        response = self.reserve()
        self.db.records['outfits']['look']['items'] = [{'id': 'shirt'}]
        claimed = self.claim()
        self.assertEqual(claimed['preflight_error'], 'outfit_changed')
        self.assertTrue(self.finish(response['request_id'], error='Preflight failed', error_code='outfit_changed'))
        outfit = self.db.records['outfits']['look']
        self.assertEqual(outfit['flat_lay_status'], 'failed')
        self.assertEqual(outfit['flat_lay_credit_status'], 'refunded')
        self.assertTrue(outfit['flat_lay_request_allowed'])
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertEqual(self.remaining(), 7)
        self.assertFalse(self.finish(response['request_id'], error='Repeated failure'))
        self.assertEqual(self.remaining(), 7)

    def test_edit_during_provider_work_cannot_publish_old_composition(self):
        response = self.reserve()
        self.claim()
        self.db.records['outfits']['look']['items'] = [{'id': 'shirt'}]
        self.finish(response['request_id'], url='https://assets.invalid/old-two-piece', retryable=False)
        outfit = self.db.records['outfits']['look']
        self.assertEqual(outfit['flat_lay_status'], 'failed')
        self.assertEqual(outfit['flat_lay_error_code'], 'outfit_changed')
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertIsNone(outfit['metadata']['flatLayUrl'])
        self.assertEqual(self.remaining(), 7)
        self.assertTrue(outfit['flat_lay_request_allowed'])
        retried = self.reserve()
        self.assertNotEqual(retried['request_id'], response['request_id'])
        self.assertEqual(self.remaining(), 6)
        self.assertFalse(self.finish(response['request_id'], url='https://assets.invalid/late'))
        self.assertIsNone(self.db.records['outfits']['look']['flat_lay_url'])

    def test_edit_cannot_start_another_paid_request_while_current_work_is_in_flight(self):
        first = self.reserve()
        self.claim()
        self.db.records['outfits']['look']['items'] = [{'id': 'shirt'}]
        duplicate = self.reserve()
        self.assertEqual(duplicate['request_id'], first['request_id'])
        self.assertEqual(duplicate['flat_lay_status'], 'processing')
        self.assertEqual(duplicate['error_code'], 'outfit_changed')
        self.assertFalse(duplicate['request_allowed'])
        self.assertEqual(self.remaining(), 6)

    def test_done_item_edit_requires_explicit_new_request_and_new_credit(self):
        first = self.reserve()
        self.claim()
        self.finish(first['request_id'], url='https://assets.invalid/old-two-piece')
        self.assertEqual(self.remaining(), 6)
        self.db.records['outfits']['look']['items'] = [{'id': 'shirt'}]
        response = self.reserve()
        self.assertEqual(response['flat_lay_status'], 'pending')
        self.assertIsNone(response['flat_lay_url'])
        self.assertNotEqual(response['request_id'], first['request_id'])
        self.assertEqual(self.remaining(), 5)
        ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual([item['id'] for item in ledger['items']], ['shirt'])
        self.assertFalse(self.finish(first['request_id'], url='https://assets.invalid/old-two-piece'))

    def test_rename_style_and_item_reordering_do_not_invalidate_completed_preview(self):
        first = self.reserve()
        self.claim()
        self.finish(first['request_id'], url='https://assets.invalid/valid')
        self.db.records['outfits']['look'].update(
            name='Renamed', style='Edited style', items=[{'itemId': 'pants'}, {'item_id': 'shirt'}])
        response = self.reserve()
        self.assertEqual(response['request_id'], first['request_id'])
        self.assertEqual(response['flat_lay_status'], 'done')
        self.assertEqual(response['flat_lay_url'], 'https://assets.invalid/valid')
        self.assertEqual(self.remaining(), 6)

    def test_changed_items_do_not_clear_an_ambiguous_provider_hold(self):
        first = self.reserve()
        self.claim()
        self.db.records['outfits']['look']['items'] = [{'id': 'shirt'}]
        self.finish(first['request_id'], error='Needs review', error_code='provider_outcome_unknown', retryable=False)
        self.assertEqual(self.remaining(), 7)
        outfit = self.db.records['outfits']['look']
        self.assertFalse(outfit['flat_lay_request_allowed'])
        self.assertEqual(outfit['flat_lay_error_code'], 'provider_outcome_unknown')
        with self.assertRaises(lifecycle.FlatlayRequestError) as ctx:
            self.reserve()
        self.assertEqual(ctx.exception.status_code, 409)

    def test_reconciliation_never_restores_done_image_after_items_changed(self):
        first = self.reserve()
        self.claim()
        self.finish(first['request_id'], url='https://assets.invalid/old-two-piece')
        self.db.records['outfits']['look'].update(items=[{'id': 'shirt'}], flat_lay_status='pending')
        self.assertIsNone(self.claim())
        outfit = self.db.records['outfits']['look']
        self.assertEqual(outfit['flat_lay_status'], 'awaiting_consent')
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertFalse(outfit['flat_lay_requested'])
        self.assertTrue(outfit['flat_lay_request_allowed'])
        self.assertEqual(self.remaining(), 6)

    def test_same_id_photo_edit_waits_for_pending_settlement_without_another_debit(self):
        first = self.reserve()
        self.db.records['wardrobe']['shirt']['imageUrl'] = 'https://assets.invalid/replacement'
        duplicate = self.reserve()
        self.assertEqual(duplicate['request_id'], first['request_id'])
        self.assertEqual(duplicate['error_code'], 'outfit_changed')
        self.assertFalse(duplicate['request_allowed'])
        self.assertEqual(self.remaining(), 6)
        before = copy.deepcopy(self.db.records)
        self.assertIsNone(lifecycle.claim_request(self.db, 'look', now=1110, allow_claim=False))
        self.assertEqual(self.db.records, before)
        claimed = self.claim()
        self.assertEqual(claimed['preflight_error'], 'outfit_changed')
        self.assertFalse(lifecycle.admit_provider_request(self.db, 'look', first['request_id'], [], now=1111))
        self.assertTrue(self.finish(first['request_id'], error='Preflight failed', error_code='outfit_changed'))
        self.assertEqual(self.remaining(), 7)
        self.assertFalse(self.finish(first['request_id'], error='Repeated settlement'))
        self.assertEqual(self.remaining(), 7)

    def test_same_id_photo_edit_during_provider_discards_output_and_refunds_exactly_once(self):
        first = self.reserve()
        self.claim()
        self.assertTrue(lifecycle.admit_provider_request(self.db, 'look', first['request_id'], [], now=1111))
        self.db.records['wardrobe']['shirt']['imageUrl'] = 'https://assets.invalid/replacement'
        duplicate = self.reserve()
        self.assertEqual(duplicate['request_id'], first['request_id'])
        self.assertEqual(duplicate['flat_lay_status'], 'processing')
        self.assertFalse(duplicate['request_allowed'])
        self.assertEqual(self.remaining(), 6)
        # A second worker rejected at admission cannot refund the still-active
        # first call merely because the photo changed after admission.
        before = copy.deepcopy(self.db.records)
        self.assertFalse(self.finish(first['request_id'], error='Request changed', error_code='request_changed'))
        self.assertEqual(self.db.records, before)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.finish(first['request_id'], url='https://assets.invalid/stale'), range(12)))
        self.assertEqual(sum(results), 1)
        outfit = self.db.records['outfits']['look']
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertIsNone(outfit['metadata']['flatLayUrl'])
        self.assertEqual(outfit['flat_lay_error_code'], 'outfit_changed')
        self.assertEqual(outfit['flat_lay_credit_status'], 'refunded')
        self.assertTrue(outfit['flat_lay_request_allowed'])
        self.assertEqual(self.remaining(), 7)
        second = self.reserve()
        self.assertNotEqual(second['request_id'], first['request_id'])
        self.assertEqual(self.remaining(), 6)
        self.assertFalse(self.finish(first['request_id'], url='https://assets.invalid/late'))

    def test_completed_same_id_photo_edit_needs_explicit_concurrent_safe_new_credit(self):
        first = self.reserve()
        self.claim()
        self.finish(first['request_id'], url='https://assets.invalid/old-photo')
        self.db.records['wardrobe']['shirt']['imageUrl'] = 'https://assets.invalid/replacement'
        # Reconciliation invalidates even a matching done projection/request ID.
        self.assertIsNone(lifecycle.claim_request(self.db, 'look', now=1121, allow_claim=False))
        outfit = self.db.records['outfits']['look']
        self.assertEqual(outfit['flat_lay_status'], 'awaiting_consent')
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertEqual(self.remaining(), 6)
        self.assertEqual(self.db.records[lifecycle.REQUESTS_COLLECTION]['look']['status'], 'done')
        with ThreadPoolExecutor(max_workers=8) as pool:
            responses = list(pool.map(lambda _: self.reserve(), range(12)))
        self.assertEqual(len({response['request_id'] for response in responses}), 1)
        self.assertNotEqual(responses[0]['request_id'], first['request_id'])
        self.assertTrue(all(response['flat_lay_status'] == 'pending' for response in responses))
        self.assertTrue(all(response['flat_lay_url'] is None for response in responses))
        self.assertEqual(self.remaining(), 5)

    def test_missing_deleted_foreign_or_conflicting_garments_cannot_publish_confirmed_output(self):
        for mode in ('missing', 'deleted', 'owner', 'conflicting_owner'):
            with self.subTest(mode=mode):
                self.db = Database()
                first = self.reserve()
                self.claim()
                garment = self.db.records['wardrobe']['shirt']
                if mode == 'missing':
                    self.db.records['wardrobe'].pop('shirt')
                elif mode == 'deleted':
                    garment['deletedAt'] = 1112
                elif mode == 'owner':
                    garment['userId'] = 'other'
                else:
                    garment['user_id'] = 'other'
                self.finish(first['request_id'], url='https://assets.invalid/stale')
                self.assertIsNone(self.db.records['outfits']['look']['flat_lay_url'])
                self.assertEqual(self.remaining(), 7)
                with self.assertRaises(lifecycle.FlatlayRequestError):
                    self.reserve()
                self.assertEqual(self.remaining(), 7)

    def test_same_id_photo_edit_does_not_clear_unknown_provider_or_worker_outcome(self):
        for code in ('provider_outcome_unknown', 'worker_outcome_unknown'):
            with self.subTest(code=code):
                self.db = Database()
                first = self.reserve()
                self.claim()
                self.db.records['wardrobe']['shirt']['imageUrl'] = 'https://assets.invalid/replacement'
                # Unknown outcome itself forbids retry, including an accidental default True.
                self.finish(first['request_id'], error='Needs review', error_code=code)
                outfit = self.db.records['outfits']['look']
                self.assertEqual(outfit['flat_lay_error_code'], code)
                self.assertFalse(outfit['flat_lay_request_allowed'])
                self.assertEqual(self.remaining(), 7)
                with self.assertRaises(lifecycle.FlatlayRequestError):
                    self.reserve()
                self.assertEqual(self.remaining(), 7)

    def test_metadata_edits_keep_completed_source_identity(self):
        first = self.reserve()
        self.claim()
        self.finish(first['request_id'], url='https://assets.invalid/current')
        self.db.records['wardrobe']['shirt'].update(name='Renamed', category='Tops', updatedAt=1115)
        self.assertEqual(self.reserve()['flat_lay_url'], 'https://assets.invalid/current')
        self.assertEqual(self.remaining(), 6)

    def test_unverifiable_private_completed_request_is_review_only_without_refund_or_recharge(self):
        first = self.reserve()
        self.claim()
        self.finish(first['request_id'], url='https://assets.invalid/legacy')
        self.db.records[lifecycle.REQUESTS_COLLECTION]['look']['items'][0].pop('referenceSourceFingerprint')
        before = copy.deepcopy(self.db.records)
        with self.assertRaises(lifecycle.FlatlayRequestError) as caught:
            self.reserve()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.db.records, before)
        self.assertIsNone(self.claim())
        outfit = self.db.records['outfits']['look']
        self.assertEqual(outfit['flat_lay_status'], 'failed')
        self.assertEqual(outfit['flat_lay_error_code'], 'legacy_request_needs_review')
        self.assertIsNone(outfit['flat_lay_url'])
        self.assertFalse(outfit['flat_lay_request_allowed'])
        self.assertEqual(self.remaining(), 6)
        self.assertEqual(self.db.records[lifecycle.REQUESTS_COLLECTION]['look']['credit_status'], 'consumed')

    def test_unverifiable_private_pending_request_settles_known_reservation_without_provider(self):
        first = self.reserve()
        self.db.records[lifecycle.REQUESTS_COLLECTION]['look']['items'][0].pop('referenceSourceFingerprint')
        claimed = self.claim()
        self.assertEqual(claimed['preflight_error'], 'legacy_request_needs_review')
        self.assertFalse(lifecycle.admit_provider_request(self.db, 'look', first['request_id'], [], now=1111))
        self.assertTrue(self.finish(first['request_id'], error='Preflight failed', error_code=claimed['preflight_error']))
        self.assertEqual(self.remaining(), 7)
        self.assertFalse(self.db.records['outfits']['look']['flat_lay_request_allowed'])
        with self.assertRaises(lifecycle.FlatlayRequestError):
            self.reserve()

    def test_changed_source_settlement_failed_commit_is_atomic(self):
        first = self.reserve()
        self.claim()
        self.db.records['wardrobe']['shirt']['imageUrl'] = 'https://assets.invalid/replacement'
        before = copy.deepcopy(self.db.records)
        self.db.fail_commit = True
        with self.assertRaises(RuntimeError):
            self.finish(first['request_id'], url='https://assets.invalid/stale')
        self.assertEqual(self.db.records, before)
        self.db.fail_commit = False
        self.assertTrue(self.finish(first['request_id'], url='https://assets.invalid/stale'))
        self.assertEqual(self.remaining(), 7)

    def test_fabricated_browser_state_cannot_forge_ledger_or_refund(self):
        self.db.records['outfits']['look'].update(flat_lay_status='pending', flat_lay_request_id='forged',
                                                flat_lay_credit_status='reserved')
        self.assertIsNone(self.claim())
        self.assertFalse(self.finish('forged', error='fake refund'))
        self.assertEqual(self.remaining(), 7)


class FlatlayProviderAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.decorator = patch.object(worker_lifecycle.firestore, 'transactional', transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    def raw_source(self, filename='shirt.jpg'):
        return f'https://storage.googleapis.com/{DEFAULT_BUCKET_NAME}/wardrobe/owner/{filename}'

    def reserve(self, raw=True):
        if raw:
            self.db.records['wardrobe']['shirt']['imageUrl'] = self.raw_source()
        return worker_lifecycle.reserve_request(self.db, 'look', 'owner', request_id='request-one', now=1100)

    def claim(self):
        return worker_lifecycle.claim_request(self.db, 'look', now=1110)

    @property
    def ledger(self):
        return self.db.records[worker_lifecycle.REQUESTS_COLLECTION]['look']

    def reports(self):
        return [{'id': item['id'], 'sourceStoragePath': item['originalPreparation']['sourceStoragePath'],
                 'sourceGeneration': '1234567890', 'originalStoragePath': item['originalStoragePath'], 'sha256': 'a' * 64}
                for item in self.ledger['items'] if 'originalPreparation' in item]

    def admit(self, reports=None, now=1120):
        return worker_lifecycle.admit_provider_request(self.db, 'look', 'request-one',
                                                      self.reports() if reports is None else reports, now=now)

    def test_raw_original_reservation_does_not_wait_for_unstarted_garment_or_cutout(self):
        self.db.records['garment_processing_jobs'] = {'shirt': {'user_id': 'owner', 'status': 'pending'}}
        self.reserve()
        snapshot = self.claim()['items'][0]
        self.assertEqual(snapshot['originalPreparation'], {'bucket': DEFAULT_BUCKET_NAME, 'sourceStoragePath': 'wardrobe/owner/shirt.jpg'})
        self.assertEqual(snapshot['originalStoragePath'], 'items/shirt/flatlay-requests/request-one/original.png')
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)
        self.assertTrue(all(item.get('referenceSourceFingerprint') for item in self.ledger['items']))

    def test_raw_owned_upload_takes_precedence_over_unprepared_legacy_static_path(self):
        self.reserve()
        self.assertIn('originalPreparation', self.ledger['items'][0])
        self.assertEqual(self.ledger['items'][1]['originalStoragePath'], 'items/pants/original.png')
        self.assertNotIn('originalPreparation', self.ledger['items'][1])

    def test_published_private_original_takes_precedence_over_raw_preparation(self):
        from worker.garment_lifecycle import garment_source_fingerprint
        garment = self.db.records['wardrobe']['shirt']
        garment['imageUrl'] = self.raw_source()
        fingerprint = garment_source_fingerprint(garment)
        self.db.records['garment_processing_jobs'] = {'shirt': {
            'user_id': 'owner', 'source_fingerprint': fingerprint, 'original_source_fingerprint': fingerprint,
            'original_attempt_id': 'earlier-attempt', 'attempt_id': 'later-attempt',
            'original': {'originalStoragePath': 'items/shirt/attempts/earlier-attempt/original.png'},
        }}
        self.reserve()
        self.assertNotIn('originalPreparation', self.ledger['items'][0])
        self.assertEqual(self.ledger['items'][0]['originalStoragePath'], 'items/shirt/attempts/earlier-attempt/original.png')

    def test_new_source_can_prepare_independently_of_older_same_owner_job(self):
        self.db.records['garment_processing_jobs'] = {'shirt': {'user_id': 'owner', 'status': 'processing',
                                                               'source_fingerprint': 'old-image'}}
        self.reserve()
        self.assertIn('originalPreparation', self.ledger['items'][0])

    def test_owned_raw_cannot_bypass_conflicting_private_owner(self):
        self.db.records['garment_processing_jobs'] = {'shirt': {'user_id': 'other'}}
        with self.assertRaises(worker_lifecycle.FlatlayRequestError) as error:
            self.reserve()
        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)
        self.assertNotIn(worker_lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_reservation_rejects_deleted_garment_before_debit(self):
        self.db.records['wardrobe']['shirt']['deletedAt'] = 1090
        with self.assertRaises(worker_lifecycle.FlatlayRequestError):
            self.reserve()
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)

    def test_admission_is_exactly_once_with_all_preparation_proof_and_no_credit_mutation(self):
        self.reserve()
        self.claim()
        reports = self.reports()
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.admit(reports), range(20)))
        self.assertEqual(sum(results), 1)
        self.assertEqual(self.ledger['provider_admitted_at'], 1120)
        self.assertEqual(self.ledger['prepared_originals'], reports)
        self.assertEqual(self.ledger['credit_status'], 'reserved')
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)
        self.assertEqual(self.ledger['status'], 'processing')

    def test_provider_admission_cannot_run_misbound_private_request(self):
        for identity in ('another-look', None, ''):
            with self.subTest(identity=identity):
                self.db = Database()
                self.reserve()
                self.claim()
                self.ledger['outfit_id'] = identity
                before = copy.deepcopy(self.db.records)
                self.assertFalse(self.admit())
                self.assertEqual(self.db.records, before)

    def test_duplicate_rejected_admission_cannot_refund_an_active_paid_call(self):
        self.reserve()
        self.claim()
        self.assertTrue(self.admit())
        self.assertFalse(self.admit())
        before = copy.deepcopy(self.db.records)
        self.assertFalse(worker_lifecycle.finish_request(self.db, 'look', 'request-one',
                         error='Request changed', error_code='request_changed', retryable=True, now=1121))
        self.assertEqual(self.db.records, before)
        self.assertTrue(worker_lifecycle.finish_request(self.db, 'look', 'request-one',
                        url='https://assets.test/final.png', retryable=False, now=1122))
        self.assertEqual(self.ledger['status'], 'done')
        self.assertEqual(self.ledger['credit_status'], 'consumed')
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)
        self.assertFalse(worker_lifecycle.finish_request(self.db, 'look', 'request-one',
                         error='Duplicate failure', error_code='request_changed', retryable=True, now=1123))

    def test_changed_request_before_any_admission_can_refund_and_allow_explicit_retry(self):
        self.reserve()
        self.claim()
        self.db.records['wardrobe']['shirt']['imageUrl'] = self.raw_source('replacement.jpg')
        self.assertFalse(self.admit())
        self.assertTrue(worker_lifecycle.finish_request(self.db, 'look', 'request-one',
                        error='Request changed', error_code='request_changed', retryable=True, now=1121))
        self.assertEqual(self.ledger['status'], 'failed')
        self.assertEqual(self.ledger['credit_status'], 'refunded')
        self.assertTrue(self.ledger['retryable'])
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)

    def test_legacy_static_references_admit_without_raw_preparation(self):
        self.reserve(raw=False)
        self.claim()
        self.assertEqual(self.reports(), [])
        self.assertTrue(self.admit([]))

    def test_admission_rejects_missing_extra_duplicate_malformed_or_wrong_provenance_reports(self):
        self.reserve()
        self.claim()
        report = self.reports()[0]
        invalid = [[], {}, None, [report, report], [{**report, 'id': 'pants'}],
                   [{**report, 'extra': True}], [{key: value for key, value in report.items() if key != 'sha256'}],
                   [{**report, 'sourceStoragePath': 'wardrobe/other/shirt.jpg'}],
                   [{**report, 'originalStoragePath': 'items/shirt/flatlay-requests/old-request/original.png'}]]
        invalid.extend([[{**report, 'sourceGeneration': value}] for value in ('', '1.2', '-1', 123, None)])
        invalid.extend([[{**report, 'sha256': value}] for value in ('f' * 63, 'G' * 64, None)])
        for reports in invalid:
            with self.subTest(reports=reports):
                self.assertFalse(worker_lifecycle.admit_provider_request(self.db, 'look', 'request-one', reports, now=1120))
                self.assertNotIn('provider_admitted_at', self.ledger)
        self.assertTrue(self.admit())

    def test_preparation_proof_cannot_validate_malformed_or_foreign_descriptor(self):
        for change in ({'bucket': 'foreign-bucket'}, {'sourceStoragePath': 'wardrobe/other/shirt.jpg'},
                       {'sourceStoragePath': '../shirt.jpg'}, {'extra': True}):
            with self.subTest(change=change):
                self.db = Database()
                self.reserve()
                self.claim()
                self.ledger['items'][0]['originalPreparation'].update(change)
                self.assertFalse(self.admit())
                self.assertNotIn('provider_admitted_at', self.ledger)

    def test_admission_rejects_changed_missing_deleted_and_foreign_garments_without_mutation(self):
        for mode in ('photo', 'missing', 'deleted', 'owner', 'conflicting_owner'):
            with self.subTest(mode=mode):
                self.db = Database()
                self.reserve()
                self.claim()
                row = self.db.records['wardrobe']['shirt']
                if mode == 'photo':
                    row['imageUrl'] = self.raw_source('new-photo.jpg')
                elif mode == 'missing':
                    self.db.records['wardrobe'].pop('shirt')
                elif mode == 'deleted':
                    row['deleted'] = True
                elif mode == 'owner':
                    row['userId'] = 'other'
                else:
                    row['user_id'] = 'other'
                before = copy.deepcopy(self.db.records)
                self.assertFalse(self.admit())
                self.assertEqual(self.db.records, before)

    def test_admission_rejects_changed_or_unavailable_outfit(self):
        for updates in ({'items': ['shirt']}, {'user_id': 'other'}, {'userId': 'other'}, {'isDeleted': True}):
            with self.subTest(updates=updates):
                self.db = Database()
                self.reserve()
                self.claim()
                self.db.records['outfits']['look'].update(updates)
                self.assertFalse(self.admit())
                self.assertNotIn('provider_admitted_at', self.ledger)
        self.db.records['outfits'].clear()
        self.assertFalse(self.admit())

    def test_admission_rejects_wrong_state_stale_request_settlement_expiry_and_prior_admission(self):
        for changes in ({'status': 'pending'}, {'status': 'failed'}, {'credit_status': 'refunded'},
                        {'request_id': 'newer-request'}, {'expires_at': 1120}, {'expires_at': None},
                        {'expires_at': float('nan')}, {'provider_admitted_at': 0}):
            with self.subTest(changes=changes):
                self.db = Database()
                self.reserve()
                self.claim()
                self.ledger.update(changes)
                self.assertFalse(self.admit())

    def test_metadata_edits_do_not_invalidate_same_owned_source(self):
        self.reserve()
        self.claim()
        self.db.records['wardrobe']['shirt'].update(name='Edited name', updatedAt=1115, category='Top')
        self.assertTrue(self.admit())

    def test_preexisting_request_without_source_fingerprint_cannot_prove_photo_identity(self):
        self.reserve(raw=False)
        self.claim()
        for item in self.ledger['items']:
            item.pop('referenceSourceFingerprint')
        self.db.records['wardrobe']['shirt']['imageUrl'] = self.raw_source('new-photo.jpg')
        self.db.records['wardrobe']['pants']['user_id'] = 'other'
        self.assertFalse(self.admit([]))
        self.db.records['wardrobe']['pants']['user_id'] = 'owner'
        self.assertFalse(self.admit([]))
        self.db.records['wardrobe']['shirt']['imageUrl'] = 'https://assets.invalid/shirt'
        self.assertFalse(self.admit([]))
        self.assertNotIn('provider_admitted_at', self.ledger)

    def test_failed_admission_commit_cannot_claim_provider_or_mutate_credit(self):
        self.reserve()
        self.claim()
        self.db.fail_commit = True
        with self.assertRaises(RuntimeError):
            self.admit()
        self.assertNotIn('provider_admitted_at', self.ledger)
        self.assertEqual(self.ledger['credit_status'], 'reserved')
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)


class FlatlayWorkerTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((ROOT / 'worker/main.py').read_text())
        names = {'FlatlayGenerationError', 'process_outfit_flat_lay', 'generate_original_reference_flatlay',
                 '_load_image_from_openai_image_response', 'expire_stale_flatlay_requests'}
        selected = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names]
        self.now = 1200
        self.request = {'request_id': 'request-one', 'items': [{'id': 'shirt'}, {'id': 'pants'}], 'expires_at': 1400}
        self.db = object()
        self.env = {
            'db': self.db, 'bucket': object(), 'Image': Image, 'BytesIO': BytesIO, 'requests': requests,
            'ReferenceImageError': ReferenceImageError,
            'build_reference_edit_payload': Mock(return_value=[('image[]', ('shirt.png', b'original-shirt', 'image/png')), ('image[]', ('pants.png', b'original-pants', 'image/png'))]),
            'REQUESTS_COLLECTION': lifecycle.REQUESTS_COLLECTION, 'FieldFilter': lambda *args: args,
            'time': SimpleNamespace(time=lambda: self.now), 'openai_client': object(),
            'claim_request': Mock(return_value=self.request), 'finish_request': Mock(return_value=True),
            'prepare_request_originals': Mock(return_value=[]), 'admit_provider_request': Mock(return_value=True),
            'prepare_original_references': Mock(return_value=[{'id': 'shirt'}, {'id': 'pants'}]),
            'compose_flatlay_image': Mock(return_value=Image.new('RGB', (1024, 1024))),
            'upload_flatlay_image': Mock(return_value='https://assets.invalid/preview'),
            'metrics': {'flat_lay_skipped': 0, 'flat_lay_processed': 0, 'flat_lay_openai': 0,
                        'flat_lay_failed': 0, 'flat_lay_openai_failed': 0},
            'get_openai_image_edit_runtime_config': Mock(return_value={'api_url': 'https://provider.invalid/edit', 'model': 'test-model', 'timeout_seconds': 1}),
            '_build_openai_image_edit_headers': Mock(return_value={}),
        }
        exec(compile(ast.Module(body=selected, type_ignores=[]), 'worker_flow_under_test', 'exec'), self.env)
        self.enhance_real = self.env['generate_original_reference_flatlay']
        self.env['generate_original_reference_flatlay'] = Mock(return_value=Image.new('RGBA', (1024, 1024), 'white'))

    def process(self):
        self.env['process_outfit_flat_lay']('look')

    def test_duplicate_claim_never_calls_provider(self):
        self.env['claim_request'].return_value = None
        self.process()
        self.env['generate_original_reference_flatlay'].assert_not_called()
        self.env['finish_request'].assert_not_called()

    def test_changed_pending_items_stop_before_any_provider_or_upload(self):
        self.request['preflight_error'] = 'outfit_changed'
        self.process()
        self.env['prepare_original_references'].assert_not_called()
        self.env['generate_original_reference_flatlay'].assert_not_called()
        self.env['upload_flatlay_image'].assert_not_called()
        self.assertEqual(self.env['finish_request'].call_args.kwargs['error_code'], 'outfit_changed')
        self.assertTrue(self.env['finish_request'].call_args.kwargs['retryable'])

    def test_rejected_admission_never_calls_provider_and_settles_known_preprovider_failure(self):
        self.env['admit_provider_request'].return_value = False
        self.process()
        self.env['generate_original_reference_flatlay'].assert_not_called()
        self.env['upload_flatlay_image'].assert_not_called()
        self.assertEqual(self.env['finish_request'].call_args.kwargs['error_code'], 'request_changed')
        self.assertTrue(self.env['finish_request'].call_args.kwargs['retryable'])

    def test_partial_assets_stop_before_provider_and_refund_terminally(self):
        self.env['prepare_original_references'].return_value = [{'id': 'shirt'}]
        self.process()
        self.env['generate_original_reference_flatlay'].assert_not_called()
        self.env['upload_flatlay_image'].assert_not_called()
        self.assertEqual(self.env['finish_request'].call_args.kwargs['error_code'], 'missing_original_references')
        self.assertTrue(self.env['finish_request'].call_args.kwargs['retryable'])

    def test_provider_empty_response_is_failure_without_compositor_publication(self):
        self.env['_load_image_from_openai_image_response'] = Mock(return_value=None)
        self.env['generate_original_reference_flatlay'] = self.enhance_real
        self.env['prepare_original_references'].return_value = [{'id': 'shirt', 'category': 'top'}, {'id': 'pants', 'category': 'bottom'}]
        with patch.object(requests, 'post', return_value=SimpleNamespace(ok=True, json=lambda: {})) as provider:
            self.process()
        provider.assert_called_once()
        self.env['upload_flatlay_image'].assert_not_called()
        self.assertEqual(self.env['finish_request'].call_args.kwargs['error_code'], 'empty_provider_result')

    def test_reference_errors_stop_before_provider_and_keep_safe_coded_message(self):
        self.env['prepare_original_references'].side_effect = ReferenceImageError('missing_original', 'An original photo is unavailable.')
        self.process()
        self.env['generate_original_reference_flatlay'].assert_not_called()
        self.env['upload_flatlay_image'].assert_not_called()
        self.assertEqual(self.env['finish_request'].call_args.kwargs['error_code'], 'missing_original')

    def test_one_provider_call_receives_all_reference_payload_and_optional_quality(self):
        refs = [{'id': 'shirt', 'image_bytes': b'original-shirt'}, {'id': 'pants', 'image_bytes': b'original-pants'}]
        self.env['get_openai_image_edit_runtime_config'].return_value['quality'] = 'low'
        self.env['_load_image_from_openai_image_response'] = Mock(return_value=Image.new('RGBA', (1024, 1024), 'white'))
        with patch.object(requests, 'post', return_value=SimpleNamespace(ok=True, json=lambda: {})) as provider:
            self.enhance_real(refs, 'look')
        provider.assert_called_once()
        self.env['build_reference_edit_payload'].assert_called_once_with(refs, 'test-model', quality='low')
        self.assertEqual(provider.call_args.kwargs['files'], self.env['build_reference_edit_payload'].return_value)

    def test_provider_timeout_settles_and_does_not_enable_paid_retry(self):
        self.env['generate_original_reference_flatlay'].side_effect = requests.Timeout('private provider URL')
        self.process()
        finish = self.env['finish_request'].call_args.kwargs
        self.assertFalse(finish['retryable'])
        self.assertEqual(finish['error_code'], 'provider_outcome_unknown')
        self.assertNotIn('private', finish['error'])
        self.env['upload_flatlay_image'].assert_not_called()

    def test_provider_exception_and_upload_failure_are_terminal(self):
        self.env['generate_original_reference_flatlay'].side_effect = ValueError('sensitive response body')
        self.process()
        self.assertNotIn('sensitive', self.env['finish_request'].call_args.kwargs['error'])
        self.env['generate_original_reference_flatlay'].side_effect = None
        self.env['upload_flatlay_image'].return_value = None
        self.process()
        self.assertEqual(self.env['finish_request'].call_args.kwargs['error_code'], 'upload_failed')

    def test_success_uses_per_request_object_and_exactly_one_completion(self):
        self.process()
        self.env['generate_original_reference_flatlay'].assert_called_once()
        self.env['compose_flatlay_image'].assert_not_called()
        self.assertEqual(self.env['upload_flatlay_image'].call_args.kwargs['renderer_tag'], 'original_refs_v1')
        self.assertEqual(self.env['upload_flatlay_image'].call_args.kwargs['request_id'], 'request-one')
        self.env['finish_request'].assert_called_once_with(self.db, 'look', 'request-one',
                                                        url='https://assets.invalid/preview', retryable=False)

    def test_expiry_sweep_is_not_starved_by_active_jobs_and_handles_pending_expiry(self):
        db = Database()
        jobs = {f'a-active-{index:02d}': {'status': 'processing', 'expires_at': 2000, 'request_id': str(index)}
                for index in range(30)}
        jobs.update({
            'z-expired-processing': {'status': 'processing', 'expires_at': 1000, 'request_id': 'old-processing'},
            'z-expired-pending': {'status': 'pending', 'expires_at': 900, 'request_id': 'old-pending'},
            'a-terminal': {'status': 'done', 'expires_at': None, 'request_id': 'done'},
        })
        db.records[lifecycle.REQUESTS_COLLECTION] = jobs
        self.env['db'] = db
        self.env['expire_stale_flatlay_requests']()
        calls = self.env['finish_request'].call_args_list
        self.assertEqual([call.args[1] for call in calls], ['z-expired-pending', 'z-expired-processing'])
        self.assertTrue(calls[0].kwargs['retryable'])
        self.assertEqual(calls[0].kwargs['error_code'], 'queue_timeout')
        self.assertFalse(calls[1].kwargs['retryable'])
        self.assertTrue(all(call.kwargs['expired_only'] for call in calls))

    def test_pending_queue_selects_oldest_request_not_document_id(self):
        from test_worker_coordinator import flatlay_candidates_under_test
        db = Database()
        db.records[lifecycle.REQUESTS_COLLECTION] = {
            'a-newest': {'status': 'pending', 'queued_at': 2000},
            'z-oldest': {'status': 'pending', 'queued_at': 1000},
            'a-active': {'status': 'processing', 'queued_at': None},
            'a-terminal': {'status': 'done', 'queued_at': None},
        }
        candidates = flatlay_candidates_under_test(db)
        self.assertEqual(candidates(), ['z-oldest'])

    def test_null_consent_queue_was_removed(self):
        tree = ast.parse((ROOT / 'worker/main.py').read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'FieldFilter':
                self.assertFalse(any(isinstance(arg, ast.Constant) and arg.value is None for arg in node.args))

class FlatlayRequestHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from src.routes.outfits.routes import get_current_user_id, router
        cls.app = FastAPI()
        cls.app.include_router(router, prefix='/api/outfits')
        cls.auth_dependency = staticmethod(get_current_user_id)
        cls.client = TestClient(cls.app)

    def setUp(self):
        import sys
        from types import ModuleType
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop('EASYOUTFIT_FLATLAY_REQUESTS_PAUSED', None)
        self.db = Database()
        self.db.records['users']['owner']['quotas']['lastRefillAt'] = lifecycle._now()
        firebase = ModuleType('src.config.firebase')
        firebase.db = self.db
        firebase.firebase_initialized = True
        self.app.dependency_overrides[self.auth_dependency] = lambda: 'owner'
        self.addCleanup(self.app.dependency_overrides.clear)
        modules = patch.dict(sys.modules, {'src.config.firebase': firebase})
        modules.start()
        self.addCleanup(modules.stop)
        transactions = patch.object(lifecycle.firestore, 'transactional', transactional)
        transactions.start()
        self.addCleanup(transactions.stop)
        self.firebase = firebase

    def test_admission_pause_rejects_before_reservation_or_database_access(self):
        import sys
        before = copy.deepcopy(self.db.records)
        with patch.object(lifecycle, 'reserve_request') as reserve, \
                patch.dict(sys.modules, {'src.config.firebase': None}):
            for setting in ('true', '1', 'yes', 'on', ' TRUE '):
                with self.subTest(setting=setting), patch.dict(os.environ, {'EASYOUTFIT_FLATLAY_REQUESTS_PAUSED': setting}):
                    response = self.client.post('/api/outfits/look/flat-lay-request', json={})
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.headers['retry-after'], '60')
                    self.assertIn('No credit was used', response.json()['detail'])
            reserve.assert_not_called()
        self.assertEqual(self.db.records, before)

    def test_invalid_explicit_pause_setting_fails_closed(self):
        with patch.object(lifecycle, 'reserve_request') as reserve:
            for setting in ('', ' ', 'tru', '2', 'enabled'):
                with self.subTest(setting=setting), patch.dict(os.environ, {'EASYOUTFIT_FLATLAY_REQUESTS_PAUSED': setting}):
                    response = self.client.post('/api/outfits/look/flat-lay-request', json={})
                    self.assertEqual(response.status_code, 503)
                    self.assertEqual(response.headers['retry-after'], '60')
            reserve.assert_not_called()
        self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_false_pause_settings_keep_normal_reservation_path(self):
        with patch.object(lifecycle, 'reserve_request', return_value={'success': True}) as reserve:
            for setting in ('false', '0', 'no', 'off', ' FALSE '):
                with self.subTest(setting=setting), patch.dict(os.environ, {'EASYOUTFIT_FLATLAY_REQUESTS_PAUSED': setting}):
                    reserve.reset_mock()
                    response = self.client.post('/api/outfits/look/flat-lay-request', json={})
                    self.assertEqual(response.status_code, 200)
                    reserve.assert_called_once_with(self.db, 'look', 'owner')

    def test_request_http_contract_and_duplicate(self):
        first = self.client.post('/api/outfits/look/flat-lay-request', json={})
        second = self.client.post('/api/outfits/look/flat-lay-request', json={})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.json(), first.json())
        data = first.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['id'], 'look')
        self.assertEqual(data['outfit_id'], 'look')
        self.assertEqual(data['flat_lay_status'], 'pending')
        self.assertEqual(data['credit_status'], 'reserved')
        self.assertTrue(data['request_id'])
        self.assertIsNone(data['flat_lay_url'])
        self.assertIsNone(data['flat_lay_error'])
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)

    def test_auth_owner_and_no_credit_failures_use_status_without_spending(self):
        self.app.dependency_overrides[self.auth_dependency] = lambda: None
        self.assertEqual(self.client.post('/api/outfits/look/flat-lay-request').status_code, 401)
        self.app.dependency_overrides[self.auth_dependency] = lambda: 'another-user'
        self.assertEqual(self.client.post('/api/outfits/look/flat-lay-request').status_code, 403)
        self.app.dependency_overrides[self.auth_dependency] = lambda: 'owner'
        self.db.records['users']['owner']['quotas']['flatlaysRemaining'] = 0
        response = self.client.post('/api/outfits/look/flat-lay-request')
        self.assertEqual(response.status_code, 403)
        self.assertIn('credits', response.json()['detail'])
        self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_unavailable_database_and_unknown_commit_outcome_have_safe_errors(self):
        self.firebase.db = None
        self.assertEqual(self.client.post('/api/outfits/look/flat-lay-request').status_code, 503)
        self.firebase.db = self.db
        self.db.fail_commit = True
        response = self.client.post('/api/outfits/look/flat-lay-request')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('simulated', response.json()['detail'])
        self.assertEqual(self.db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)

    def test_old_detached_consume_returns_409_without_database_access(self):
        from fastapi import APIRouter, Depends, FastAPI, HTTPException
        from fastapi.testclient import TestClient
        tree = ast.parse((ROOT / 'src/routes/payments.py').read_text())
        node = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == 'consume_flatlay_quota')
        auth = lambda: 'owner'
        env = {'router': APIRouter(), 'Depends': Depends, 'HTTPException': HTTPException, 'get_current_user_id': auth}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'consume_endpoint_under_test', 'exec'), env)
        app = FastAPI()
        app.include_router(env['router'], prefix='/api/payments')
        response = TestClient(app).post('/api/payments/flatlay/consume')
        self.assertEqual(response.status_code, 409)
        self.assertIn('No credit was used', response.json()['detail'])


if __name__ == "__main__":
    unittest.main()
