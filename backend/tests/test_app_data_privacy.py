"""No credentials: deletion pages, consent policy, retries, and storage/account fences."""
from copy import deepcopy
import functools
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.services import app_data_privacy as privacy


class Snapshot:
    def __init__(self, ref):
        self.reference, self.id = ref, ref.id
        self.value = deepcopy(ref.db.rows.get(ref.path))
        self.exists = self.value is not None
    def to_dict(self):
        return deepcopy(self.value)


class Document:
    def __init__(self, db, path):
        self.db, self.path, self.id = db, path, path.split('/')[-1]
    def get(self, transaction=None):
        if transaction and transaction.writes:
            raise AssertionError('Firestore reads must precede transaction writes')
        return Snapshot(self)
    def collection(self, name):
        return Collection(self.db, self.path + '/' + name)
    def collections(self):
        prefix = self.path + '/'
        names = sorted({key[len(prefix):].split('/')[0] for key in self.db.rows if key.startswith(prefix)})
        return [self.collection(name) for name in names]


class Collection:
    def __init__(self, db, path, filters=(), maximum=None, cursor=None):
        self.db, self.path, self.id = db, path, path.split('/')[-1]
        self.filters, self.maximum, self.cursor = filters, maximum, cursor
    def document(self, key):
        return Document(self.db, self.path + '/' + key)
    def where(self, *, filter):
        return Collection(self.db, self.path, self.filters + (filter,), self.maximum, self.cursor)
    def limit(self, maximum):
        return Collection(self.db, self.path, self.filters, maximum, self.cursor)
    def order_by(self, _field):
        return self
    def start_after(self, cursor):
        return Collection(self.db, self.path, self.filters, self.maximum, cursor['__name__'].id)
    def stream(self):
        prefix = self.path + '/'
        paths = sorted(key for key in self.db.rows if key.startswith(prefix) and '/' not in key[len(prefix):])
        found = []
        for path in paths:
            doc = Document(self.db, path)
            value = self.db.rows[path]
            if self.cursor and doc.id <= self.cursor:
                continue
            if all(value.get(item.field_path) == item.value for item in self.filters):
                found.append(doc.get())
        return iter(found[:self.maximum])


class Transaction:
    def __init__(self, db):
        self.db, self.writes = db, []
    def create(self, ref, data):
        if ref.path in self.db.rows:
            raise RuntimeError('already exists')
        self.set(ref, data)
    def set(self, ref, data, merge=False):
        self.writes.append(('update' if merge else 'set', ref.path, deepcopy(data)))
    def update(self, ref, data):
        self.writes.append(('update', ref.path, deepcopy(data)))
    def delete(self, ref):
        self.writes.append(('delete', ref.path, None))
    def commit(self):
        if self.db.fail_once:
            self.db.fail_once = False
            raise RuntimeError('simulated Firestore outage')
        for kind, path, data in self.writes:
            if kind == 'delete':
                self.db.rows.pop(path, None)
            elif kind == 'set':
                self.db.rows[path] = data
            else:
                row = self.db.rows[path]
                for key, value in data.items():
                    target = row
                    parts = key.split('.')
                    for part in parts[:-1]:
                        target = target.setdefault(part, {})
                    target[parts[-1]] = value


def transactional(callback):
    @functools.wraps(callback)
    def run(txn, *args, **kwargs):
        result = callback(txn, *args, **kwargs)
        txn.commit()
        return result
    return run


class Database:
    def __init__(self, rows=None):
        self.rows = deepcopy(rows or {})
        self.fail_once = False
    def collection(self, name):
        return Collection(self, name)
    def transaction(self):
        return Transaction(self)


class Bucket:
    def __init__(self, names=()):
        self.names = {name: 1 for name in names}
        self.fail = False
        self.before_list = None
    def list_blobs(self, *, prefix, max_results):
        if self.fail:
            raise RuntimeError('storage outage')
        if self.before_list:
            self.before_list()
        rows = []
        for name in sorted(self.names):
            if not name.startswith(prefix):
                continue
            generation = self.names[name]
            def delete(*, if_generation_match, name=name, generation=generation):
                assert if_generation_match == generation == self.names[name]
                del self.names[name]
            rows.append(SimpleNamespace(name=name, generation=generation, delete=delete))
        return rows[:max_results]


class PrivacyTests(unittest.TestCase):
    def setUp(self):
        self.decorator = patch.object(privacy.firestore, 'transactional', transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)
        self.user = {'email': 'fake@example.invalid', 'subscription': {'role': 'tier2'},
                     'quotas': {'flatlaysRemaining': 4, 'lastRefillAt': 1000},
                     'billing': {'customer_id': 'fake'}, 'privacy': {'share_analytics': False},
                     'stylePersona': {'secret': 'private'}, 'quizAnswers': {'secret': 'private'},
                     'measurements': {'secret': 'private'}, 'avatarUrl': '/shared-avatar.png'}
        self.db = Database({'users/owner': self.user, 'users/other': {'name': 'Other'},
                            'wardrobe/shirt': {'userId': 'owner'}, 'wardrobe/foreign': {'userId': 'other'},
                            'outfits/look': {'user_id': 'owner'}, 'outfits/foreign': {'user_id': 'other'},
                            'users/owner/quiz/history': {'answers': ['private']},
                            'codex_jobs/job': {'requested_by': 'owner', 'status': 'running'},
                            'codex_jobs/job/artifacts/photo': {'content': 'private'}})
        self.bucket = Bucket(['wardrobe/owner/raw.jpg', 'items/shirt/attempts/a/original.png',
                              'flat_lays/outfit_look/request.png', 'flat_lays/outfit_look.png',
                              'flat_lays/outfit_look.png-other', 'wardrobe/other/raw.jpg', 'avatars/shared.png'])
    def request(self, scope='all'):
        return privacy.request_app_data_deletion(self.db, 'owner', scope, now=1000)
    def run_to_end(self, job_id, now=1700, bucket=None, max_records=2):
        for _ in range(300):
            result = privacy.process_deletion_job(self.db, bucket or self.bucket, job_id, now=now, max_records=max_records)
            if result['status'] in {'complete', 'failed'}:
                return result
        self.fail('Deletion did not converge')

    def test_request_is_idempotent_and_immediately_blocks_old_or_new_app_writes(self):
        first = self.request()
        self.assertEqual(first, self.request())
        self.assertEqual(first['epoch'], 1)
        for expected in (None, 0, 1):
            with self.assertRaises(privacy.AppDataDeletionError):
                privacy.require_app_data_writable(self.db, 'owner', expected_epoch=expected)
        with self.assertRaises(privacy.AppDataDeletionError):
            self.request('outfits')
        self.assertEqual(self.db.rows['users/owner']['quotas'], self.user['quotas'])

    def test_full_clear_deletes_photos_nested_content_and_profile_but_retains_authority(self):
        job = self.request()
        result = self.run_to_end(job['job_id'])
        self.assertEqual(result['status'], 'complete', self.db.rows[privacy.JOBS + '/' + job['job_id']])
        user = self.db.rows['users/owner']
        for field in ('email', 'subscription', 'quotas', 'billing', 'privacy'):
            self.assertEqual(user[field], self.user[field])
        for field in ('stylePersona', 'quizAnswers', 'measurements', 'avatarUrl'):
            self.assertNotIn(field, user)
        self.assertFalse(user['onboardingCompleted'])
        self.assertIn('wardrobe/foreign', self.db.rows)
        self.assertIn('outfits/foreign', self.db.rows)
        self.assertNotIn('wardrobe/shirt', self.db.rows)
        self.assertNotIn('outfits/look', self.db.rows)
        self.assertFalse(any(key.startswith('codex_jobs/job') for key in self.db.rows))
        self.assertFalse(any(key.startswith('users/owner/') for key in self.db.rows))
        self.assertEqual(set(self.bucket.names), {'wardrobe/other/raw.jpg', 'avatars/shared.png', 'flat_lays/outfit_look.png-other'})
        self.assertEqual(privacy.require_app_data_writable(self.db, 'owner'), 1)
        with self.assertRaises(privacy.AppDataDeletionError):
            privacy.require_app_data_writable(self.db, 'owner', expected_epoch=0)
        before = deepcopy(self.db.rows)
        privacy.process_deletion_job(self.db, self.bucket, job['job_id'], now=1800)
        self.assertEqual(before, self.db.rows)

    def test_storage_outage_fails_honestly_and_retry_resumes_same_job_epoch(self):
        job = self.request()
        self.bucket.fail = True
        result = self.run_to_end(job['job_id'])
        self.assertEqual(result['status'], 'failed')
        self.assertFalse(result['completed'])
        self.assertEqual(self.request()['job_id'], job['job_id'])
        self.bucket.fail = False
        self.assertEqual(self.run_to_end(job['job_id'])['status'], 'complete')
        self.assertEqual(self.db.rows['users/owner']['app_data_epoch'], 1)

    def test_every_receipt_page_scrubbed_and_pending_preview_refunded_once(self):
        for index in range(7):
            self.db.rows[f'reward_ledger/{index}'] = {'user_id': 'owner', 'operation_id': str(index),
                                                    'result': {'xp_awarded': 3}, 'metadata': {'photo': 'private'}}
        self.db.rows['flat_lay_requests/look'] = {'user_id': 'owner', 'outfit_id': 'look', 'request_id': 'request',
                                                'status': 'pending', 'credit_status': 'reserved',
                                                'quota_period_start': 1000, 'items': [{'id': 'shirt'}]}
        job = self.request()
        self.assertEqual(self.run_to_end(job['job_id'])['status'], 'complete')
        self.assertEqual(self.db.rows['users/owner']['quotas']['flatlaysRemaining'], 5)
        ledger = self.db.rows['flat_lay_requests/look']
        self.assertEqual(ledger['credit_status'], 'refunded')
        self.assertNotIn('items', ledger)
        for index in range(7):
            value = self.db.rows[f'reward_ledger/{index}']
            self.assertNotIn('metadata', value)
            self.assertEqual(value['data_cleared_epoch'], 1)
        privacy.process_deletion_job(self.db, self.bucket, job['job_id'], now=1800)
        self.assertEqual(self.db.rows['users/owner']['quotas']['flatlaysRemaining'], 5)

    def test_storage_cleanup_waits_until_old_image_processes_are_drained(self):
        job = self.request()
        for _ in range(150):
            result = privacy.process_deletion_job(self.db, self.bucket, job['job_id'], now=1001, max_records=100)
        self.assertEqual(result['status'], 'running')
        self.assertIn('wardrobe/owner/raw.jpg', self.bucket.names)
        self.assertEqual(self.run_to_end(job['job_id'])['status'], 'complete')

    def test_stale_lease_cannot_delete_storage_or_mark_new_state_failed(self):
        job = self.request()
        ref = privacy.JOBS + '/' + job['job_id']
        self.db.rows[ref]['phase'] = len(privacy._collections('all')) + 2
        self.db.rows[ref + '/assets/a'] = {'prefix': 'wardrobe/owner/'}
        def lose_lease():
            self.db.rows[ref]['lease_token'] = 'new-worker'
        self.bucket.before_list = lose_lease
        privacy.process_deletion_job(self.db, self.bucket, job['job_id'], now=1700)
        self.assertIn('wardrobe/owner/raw.jpg', self.bucket.names)
        self.assertEqual(self.db.rows[ref]['lease_token'], 'new-worker')
        self.assertNotEqual(self.db.rows[ref]['status'], 'failed')

    def test_analytics_clear_leaves_financial_ledger_and_saved_content(self):
        self.db.rows['flat_lay_requests/look'] = {'user_id': 'owner', 'status': 'pending', 'credit_status': 'reserved'}
        self.db.rows['analytics_events/a'] = {'user_id': 'owner'}
        before = deepcopy(self.db.rows['flat_lay_requests/look'])
        job = self.request('analytics')
        self.assertEqual(self.run_to_end(job['job_id'])['status'], 'complete')
        self.assertNotIn('analytics_events/a', self.db.rows)
        self.assertIn('wardrobe/shirt', self.db.rows)
        self.assertEqual(self.db.rows['flat_lay_requests/look'], before)

    def test_unknown_scope_missing_user_and_conflicting_owner_fail_closed(self):
        with self.assertRaises(privacy.AppDataDeletionError):
            self.request('everything-else')
        with self.assertRaises(privacy.AppDataDeletionError):
            privacy.request_app_data_deletion(self.db, 'missing', now=1000)
        self.db.rows['wardrobe/shirt']['user_id'] = 'other'
        result = self.run_to_end(self.request()['job_id'])
        self.assertEqual(result['status'], 'failed')
        self.assertIn('wardrobe/shirt', self.db.rows)

    def test_all_legacy_owner_alias_records_are_cleared(self):
        for alias in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId'):
            self.db.rows[f'wardrobe/legacy-{alias}'] = {alias: 'owner'}
        self.assertEqual(self.run_to_end(self.request()['job_id'])['status'], 'complete')
        self.assertFalse(any(key.startswith('wardrobe/legacy-') for key in self.db.rows))

    def test_deleted_item_receipt_preserves_photo_ownership_and_cleans_orphan_assets(self):
        del self.db.rows['wardrobe/shirt']
        self.db.rows['wardrobe_deletion_receipts/receipt'] = {'user_id': 'owner', 'item_id': 'shirt'}
        self.assertEqual(self.run_to_end(self.request()['job_id'])['status'], 'complete')
        self.assertNotIn('items/shirt/attempts/a/original.png', self.bucket.names)
        self.assertEqual(self.db.rows['wardrobe_asset_owners/shirt'], {'user_id': 'owner'})
        self.assertNotIn('wardrobe_deletion_receipts/receipt', self.db.rows)

    def test_conflicting_photo_reservation_holds_erasure_instead_of_deleting_foreign_assets(self):
        self.db.rows['wardrobe_asset_owners/shirt'] = {'user_id': 'other'}
        result = self.run_to_end(self.request()['job_id'])
        self.assertEqual(result['status'], 'failed')
        self.assertIn('items/shirt/attempts/a/original.png', self.bucket.names)
        self.assertEqual(self.db.rows['wardrobe_asset_owners/shirt'], {'user_id': 'other'})

    def test_orphaned_direct_subcollection_is_erased_even_without_parent_document(self):
        self.db.rows['user_challenges/owner/active/challenge'] = {'user_id': 'owner', 'progress': 1}
        self.assertEqual(self.run_to_end(self.request()['job_id'])['status'], 'complete')
        self.assertFalse(any(key.startswith('user_challenges/owner') for key in self.db.rows))

    def test_mirror_exact_and_rules_server_authority(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual((root / 'src/services/app_data_privacy.py').read_bytes(), (root / 'worker/app_data_privacy.py').read_bytes())
        rules = (root.parent / 'frontend/firestore.rules').read_text()
        for collection in ('wardrobe', 'outfits', 'outfit_history', 'profiles', 'daily_outfit_suggestions'):
            block = rules.split(f'match /{collection}/', 1)[1].split('\n    }', 1)[0]
            self.assertIn('allow write: if false;', block)
        self.assertIn("['name', 'updatedAt', 'updated_at']", rules)


if __name__ == '__main__':
    unittest.main()
