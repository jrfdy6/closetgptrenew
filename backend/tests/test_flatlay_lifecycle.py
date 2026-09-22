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
    def __init__(self, db, name, filters=(), order=None, maximum=None):
        self.db, self.name = db, name
        self.filters, self.order, self.maximum = filters, order, maximum

    def document(self, key):
        return Document(self.db, self.name, key)

    def where(self, *, filter):
        return Collection(self.db, self.name, (*self.filters, filter), self.order, self.maximum)

    def order_by(self, field):
        return Collection(self.db, self.name, self.filters, field, self.maximum)

    def limit(self, maximum):
        return Collection(self.db, self.name, self.filters, self.order, maximum)

    def stream(self):
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
        for key, row in rows[:self.maximum]:
            yield SimpleNamespace(id=key, to_dict=lambda row=row: copy.deepcopy(row))


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

    def test_done_legacy_preview_is_returned_without_spending(self):
        self.db.records['outfits']['look'].update(flat_lay_status='done', flat_lay_url='https://assets.invalid/done')
        self.assertEqual(self.reserve()['flat_lay_url'], 'https://assets.invalid/done')
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

    def test_new_policy_preserves_high_water_through_downgrade_and_refund(self):
        user = self.db.records['users']['owner']
        user['quotas'].update(highestAllowanceGranted=7, highestAllowanceInferred=False)
        request = self.reserve()
        user['subscription']['role'] = 'tier1'
        self.assertTrue(self.finish(request['request_id'], error='failed'))
        self.assertEqual(user['quotas']['flatlaysRemaining'], 7)
        self.assertEqual(user['quotas']['highestAllowanceGranted'], 7)
        self.assertEqual(user['quotas']['lastRefillAt'], 1000)

    def test_proven_legacy_refund_can_complete_after_prior_downgrade(self):
        request = self.reserve()
        user = self.db.records['users']['owner']
        user['subscription']['role'] = 'tier1'
        user['quotas'].pop('highestAllowanceGranted')
        user['quotas'].pop('highestAllowanceInferred')
        self.assertTrue(self.finish(request['request_id'], error='failed'))
        self.assertEqual(user['quotas']['flatlaysRemaining'], 7)
        self.assertEqual(user['quotas']['highestAllowanceGranted'], 7)
        self.assertTrue(user['quotas']['highestAllowanceInferred'])

    def test_refund_cannot_exceed_a_recorded_grant(self):
        user = self.db.records['users']['owner']
        user['quotas'].update(highestAllowanceGranted=7, highestAllowanceInferred=False)
        request = self.reserve()
        user['quotas']['flatlaysRemaining'] = 7  # Evidence of an inconsistent prior write.
        self.assertTrue(self.finish(request['request_id'], error='failed'))
        self.assertEqual(user['quotas']['flatlaysRemaining'], 7)
        self.assertEqual(self.db.records[lifecycle.REQUESTS_COLLECTION]['look']['credit_status'], 'refund_needs_review')

    def test_unknown_quota_denies_new_request_without_writing_or_charging(self):
        user = self.db.records['users']['owner']
        del user['quotas']['lastRefillAt']
        before = copy.deepcopy(self.db.records)
        with self.assertRaises(lifecycle.FlatlayRequestError) as raised:
            self.reserve()
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(self.db.records, before)

    def test_unknown_quota_at_refund_finishes_for_review_without_guessing_balance(self):
        request = self.reserve()
        user = self.db.records['users']['owner']
        del user['quotas']['lastRefillAt']
        before = copy.deepcopy(user)
        self.assertTrue(self.finish(request['request_id'], error='failed'))
        self.assertEqual(user, before)
        ledger = self.db.records[lifecycle.REQUESTS_COLLECTION]['look']
        self.assertEqual(ledger['credit_status'], 'refund_needs_review')
        self.assertFalse(ledger['retryable'])
        self.assertFalse(self.finish(request['request_id'], error='again'))

    def test_refund_after_downgrade_and_rollover_uses_new_tier_without_extra_credit(self):
        request = self.reserve()
        user = self.db.records['users']['owner']
        user['subscription']['role'] = 'tier1'
        lifecycle.finish_request(self.db, 'look', request['request_id'], error='failed',
                                 now=1000 + lifecycle.WEEK_SECONDS)
        self.assertEqual(user['quotas']['flatlaysRemaining'], 1)
        self.assertEqual(user['quotas']['highestAllowanceGranted'], 1)

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

    def test_legacy_camelcase_metadata_preview_is_preserved(self):
        self.db.records['outfits']['look']['metadata'] = {'flatLayStatus': 'done', 'flatLayUrl': 'https://assets.invalid/legacy'}
        self.assertEqual(self.reserve()['flat_lay_url'], 'https://assets.invalid/legacy')
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

    def test_fabricated_browser_state_cannot_forge_ledger_or_refund(self):
        self.db.records['outfits']['look'].update(flat_lay_status='pending', flat_lay_request_id='forged',
                                                flat_lay_credit_status='reserved')
        self.assertIsNone(self.claim())
        self.assertFalse(self.finish('forged', error='fake refund'))
        self.assertEqual(self.remaining(), 7)


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
        tree = ast.parse((ROOT / 'worker/main.py').read_text())
        node = next(node.value for node in ast.walk(tree)
                    if isinstance(node, ast.Assign) and
                    any(isinstance(target, ast.Name) and target.id == 'outfit_pending' for target in node.targets))
        db = Database()
        db.records[lifecycle.REQUESTS_COLLECTION] = {
            'a-newest': {'status': 'pending', 'queued_at': 2000},
            'z-oldest': {'status': 'pending', 'queued_at': 1000},
            'a-active': {'status': 'processing', 'queued_at': None},
            'a-terminal': {'status': 'done', 'queued_at': None},
        }
        self.env['db'] = db
        result = eval(compile(ast.Expression(node), 'worker_queue_under_test', 'eval'), self.env)
        self.assertEqual([doc.id for doc in result], ['z-oldest'])

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
