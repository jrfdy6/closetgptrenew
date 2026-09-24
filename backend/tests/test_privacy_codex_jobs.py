"""Codex queue, dispatch, final artifacts and wardrobe publication stay fenced."""
from contextlib import ExitStack
from copy import deepcopy
import importlib.util
from pathlib import Path
from types import ModuleType
import unittest
from unittest.mock import patch

from google.cloud.firestore_v1.base_query import FieldFilter
from src.services import app_data_privacy as privacy
from test_app_data_privacy import Collection, Database, Transaction, transactional


class CodexJobPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.db = Database({'users/owner': {'app_data_epoch': 3}, 'users/other': {'app_data_epoch': 3}})
        config = ModuleType('src.config.firebase')
        config.db, config.firebase_initialized = self.db, True
        self.stack.enter_context(patch.dict('sys.modules', {'src.config.firebase': config}))
        source = Path(__file__).resolve().parents[1] / 'src/services/ai_runtime/codex_jobs.py'
        spec = importlib.util.spec_from_file_location('src.services.ai_runtime.isolated_codex_jobs_privacy', source)
        self.jobs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.jobs)
        self.stack.enter_context(patch.object(self.jobs, '_require_db', return_value=self.db))
        self.stack.enter_context(patch.object(privacy.firestore, 'transactional', transactional))
        # The production claim API supports positional filters and txn.get(query).
        # Adapt the shared offline store without replacing any application logic.
        original_where = Collection.where
        def where(collection, *args, filter=None):
            return original_where(collection, filter=filter or FieldFilter(*args))
        self.stack.enter_context(patch.object(Collection, 'where', where))
        self.stack.enter_context(patch.object(Transaction, 'get', lambda txn, query: query.stream(), create=True))
        self.context = self.stack.enter_context(patch.object(self.jobs, '_build_job_context', return_value={
            'workspace_slug': 'easyoutfitapp', 'selected_item_ids': ['shirt'], 'selected_item_count': 1,
            'prompt': 'Private garment context'}))

    @property
    def user(self):
        return self.db.rows['users/owner']

    def seed_job(self, job_id='job', **changes):
        data = {'requested_by': 'owner', 'app_data_epoch': 3, 'job_kind': self.jobs.DEFAULT_JOB_KIND,
                'workspace_slug': 'easyoutfitapp', 'status': 'running', 'claimed_by': 'worker',
                'created_at_ms': 1, 'context_packet': {}, 'result_payload': None, 'artifacts': []}
        data.update(changes)
        self.db.rows[f'codex_jobs/{job_id}'] = data
        return data

    def queue(self):
        return self.jobs.queue_codex_job(requested_by='owner', job_kind=self.jobs.DEFAULT_JOB_KIND,
                                        request_payload={'note': 'Test only'})

    def complete(self, job_id='job', **changes):
        arguments = {'job_id': job_id, 'worker_id': 'worker', 'model': 'fixture-model',
                     'result_payload': {'summary': 'Private result'}, 'raw_output': '{"result":true}',
                     'command_stdout': 'done', 'command_stderr': None,
                     'artifacts': [{'artifact_id': 'report', 'content': 'Private artifact'}]}
        arguments.update(changes)
        return self.jobs.complete_codex_job(**arguments)

    def claim(self):
        return self.jobs.claim_next_codex_job(worker_id='worker', workspace_slug='easyoutfitapp')

    def seed_upload_job(self):
        self.seed_job(status='completed', job_kind=self.jobs.UPLOAD_IMAGE_ANALYSIS_JOB_KIND,
                      context_packet={'item_id': 'shirt', 'file_name': 'shirt.jpg'},
                      result_payload={'name': 'Blue shirt', 'type': 'shirt', 'dominantColors': [{'name': 'blue', 'hex': '#0000ff'}]})
        self.db.rows['wardrobe/shirt'] = {'userId': 'owner', 'name': 'Processing item',
                                         'imageUrl': 'https://example.invalid/original.jpg', 'metadata': {}}

    def test_queue_pins_current_epoch_and_commits_real_context_once(self):
        result = self.queue()
        stored = self.db.rows['codex_jobs/' + result['id']]
        self.assertEqual(stored['app_data_epoch'], 3)
        self.assertEqual(stored['requested_by'], 'owner')
        self.assertEqual(stored['status'], 'pending')
        self.assertEqual(stored['context_packet']['selected_item_ids'], ['shirt'])
        self.context.assert_called_once()

    def test_missing_account_and_active_deletion_stop_queue_before_context_reads(self):
        for state in ('missing', 'pending', 'running', 'failed'):
            self.db.rows['users/owner'] = {'app_data_epoch': 3}
            if state == 'missing':
                del self.db.rows['users/owner']
            else:
                self.user['app_data_deletion'] = {'status': state}
            before = deepcopy(self.db.rows)
            with self.assertRaises(privacy.AppDataDeletionError):
                self.queue()
            self.assertEqual(self.db.rows, before)
        self.context.assert_not_called()

    def test_clear_during_context_build_prevents_enqueue_at_final_transaction(self):
        def clear(*args, **kwargs):
            self.user['app_data_epoch'] = 4
            return {'workspace_slug': 'easyoutfitapp', 'prompt': 'Old context'}
        self.context.side_effect = clear
        with self.assertRaises(privacy.AppDataDeletionError):
            self.queue()
        self.assertFalse(any(path.startswith('codex_jobs/') for path in self.db.rows))

    def test_claim_skips_missing_account_deletion_and_stale_epoch_jobs(self):
        self.seed_job('a-missing', status='pending', claimed_by=None, requested_by='missing')
        self.seed_job('b-deleting', status='pending', claimed_by=None, requested_by='other')
        self.db.rows['users/other']['app_data_deletion'] = {'status': 'running'}
        self.seed_job('c-old', status='pending', claimed_by=None, app_data_epoch=2)
        self.seed_job('d-current', status='pending', claimed_by=None)
        result = self.claim()
        self.assertEqual(result['id'], 'd-current')
        self.assertEqual(result['claimed_by'], 'worker')
        self.assertEqual(result['status'], 'running')
        for key in ('a-missing', 'b-deleting', 'c-old'):
            self.assertNotEqual(self.db.rows['codex_jobs/' + key]['status'], 'pending')

    def test_claim_without_eligible_owner_retires_stale_work_without_dispatch(self):
        self.seed_job(status='pending', app_data_epoch=1)
        self.assertIsNone(self.claim())
        self.assertNotEqual(self.db.rows['codex_jobs/job']['status'], 'pending')

    def test_twenty_five_stale_jobs_cannot_starve_a_valid_later_job(self):
        for index in range(25):
            self.seed_job(f'{index:02d}-stale', status='pending', claimed_by=None, app_data_epoch=2,
                          context_packet={'private': 'old context'}, request_payload={'private': 'old request'},
                          result_payload={'private': 'old result'}, artifacts=[{'content': 'old artifact'}])
        self.seed_job('26-valid', status='pending', claimed_by=None)
        claimed = self.claim() or self.claim()
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed['id'], '26-valid')
        for index in range(25):
            row = self.db.rows[f'codex_jobs/{index:02d}-stale']
            self.assertNotEqual(row['status'], 'pending')
            for field in ('context_packet', 'request_payload', 'result_payload', 'artifacts'):
                self.assertFalse(row.get(field), field)

    def test_completion_rejects_missing_account_active_clear_and_old_epoch_without_artifacts(self):
        for state in ('missing', 'pending', 'running', 'failed', 'old_epoch'):
            self.db.rows['users/owner'] = {'app_data_epoch': 3}
            self.seed_job()
            if state == 'missing':
                del self.db.rows['users/owner']
            elif state == 'old_epoch':
                self.user['app_data_epoch'] = 4
            else:
                self.user['app_data_deletion'] = {'status': state}
            before = deepcopy(self.db.rows)
            with self.assertRaises(privacy.AppDataDeletionError):
                self.complete()
            self.assertEqual(self.db.rows, before)

    def test_final_completion_transaction_rechecks_epoch_after_initial_job_read(self):
        self.seed_job()
        original_transaction = self.db.transaction
        def clear_before_transaction():
            self.user['app_data_epoch'] = 4
            return original_transaction()
        with patch.object(self.db, 'transaction', side_effect=clear_before_transaction):
            with self.assertRaises(privacy.AppDataDeletionError):
                self.complete()
        self.assertEqual(self.db.rows['codex_jobs/job']['status'], 'running')
        self.assertFalse(any('/artifacts/' in key for key in self.db.rows))

    def test_same_epoch_result_and_all_artifacts_commit_in_one_transaction(self):
        self.seed_job()
        commits = []
        original_commit = Transaction.commit
        def record(txn):
            commits.append(deepcopy(txn.writes))
            original_commit(txn)
        with patch.object(Transaction, 'commit', record):
            result = self.complete()
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['result_payload']['summary'], 'Private result')
        self.assertEqual(len(commits), 1)
        paths = [path for _, path, _ in commits[0]]
        self.assertIn('codex_jobs/job', paths)
        self.assertEqual(sum('/artifacts/' in path for path in paths), 3)
        self.assertEqual(len(result['artifacts']), 3)
        self.assertEqual(self.jobs.get_job_artifact_content(job_id='job', artifact_id='report'), 'Private artifact')

    def test_commit_failure_cannot_leave_orphan_artifacts_or_completed_job(self):
        self.seed_job()
        before = deepcopy(self.db.rows)
        self.db.fail_once = True
        with self.assertRaisesRegex(RuntimeError, 'Firestore outage'):
            self.complete()
        self.assertEqual(self.db.rows, before)
        self.assertEqual(self.complete()['status'], 'completed')

    def test_wrong_worker_terminal_job_and_artifact_overflow_cannot_mutate(self):
        for changes, arguments in (({'claimed_by': 'other-worker'}, {}),
                                   ({'status': 'completed'}, {}),
                                   ({}, {'artifacts': [{'content': str(index)} for index in range(101)]})):
            self.seed_job(**changes)
            before = deepcopy(self.db.rows)
            with self.assertRaises(ValueError):
                self.complete(**arguments)
            self.assertEqual(self.db.rows, before)

    def test_cancel_and_fail_also_obey_current_account_epoch(self):
        for action in (lambda: self.jobs.cancel_codex_job(job_id='job', requested_by='owner'),
                       lambda: self.jobs.fail_codex_job(job_id='job', worker_id='worker', error_message='failure')):
            self.seed_job(app_data_epoch=2)
            before = deepcopy(self.db.rows)
            with self.assertRaises(privacy.AppDataDeletionError):
                action()
            self.assertEqual(self.db.rows, before)

    def test_completed_upload_sync_preserves_original_and_applies_same_epoch_analysis(self):
        self.seed_upload_job()
        self.jobs.sync_completed_upload_analysis_to_wardrobe('job')
        item = self.db.rows['wardrobe/shirt']
        self.assertEqual(item['name'], 'Blue shirt')
        self.assertEqual(item['imageUrl'], 'https://example.invalid/original.jpg')
        self.assertEqual(item['metadata']['codex_analysis']['job_id'], 'job')

    def test_sync_stale_missing_or_clearing_account_cannot_publish_item_changes(self):
        for state in ('old_epoch', 'missing', 'running'):
            self.db.rows['users/owner'] = {'app_data_epoch': 3}
            self.seed_upload_job()
            if state == 'missing':
                del self.db.rows['users/owner']
            elif state == 'old_epoch':
                self.user['app_data_epoch'] = 4
            else:
                self.user['app_data_deletion'] = {'status': state}
            before = deepcopy(self.db.rows)
            with self.assertRaises(privacy.AppDataDeletionError):
                self.jobs.sync_completed_upload_analysis_to_wardrobe('job')
            self.assertEqual(self.db.rows, before)

    def test_sync_checks_current_epoch_after_initial_job_and_item_reads(self):
        self.seed_upload_job()
        original_transaction = self.db.transaction
        def clear_before_transaction():
            self.user['app_data_epoch'] = 4
            return original_transaction()
        with patch.object(self.db, 'transaction', side_effect=clear_before_transaction):
            with self.assertRaises(privacy.AppDataDeletionError):
                self.jobs.sync_completed_upload_analysis_to_wardrobe('job')
        self.assertEqual(self.db.rows['wardrobe/shirt']['name'], 'Processing item')

    def test_deleted_missing_foreign_or_conflicting_owner_item_is_never_updated(self):
        for changes in ({'deleted': True}, {'deletedAt': 123}, {'isDeleted': True},
                        {'userId': 'other'}, {'user_id': 'other'}, {'ownerId': 'other'}, {'firebase_uid': 'other'}):
            self.seed_upload_job()
            self.db.rows['wardrobe/shirt'].update(changes)
            before = deepcopy(self.db.rows)
            try:
                self.jobs.sync_completed_upload_analysis_to_wardrobe('job')
            except (privacy.AppDataDeletionError, ValueError):
                pass
            self.assertEqual(self.db.rows, before, changes)
        self.seed_upload_job()
        del self.db.rows['wardrobe/shirt']
        self.jobs.sync_completed_upload_analysis_to_wardrobe('job')
        self.assertNotIn('wardrobe/shirt', self.db.rows)

    def test_merge_completed_analysis_also_rejects_old_epoch_and_foreign_requester(self):
        self.seed_upload_job()
        item = {'codex_job_id': 'job', 'name': 'Original'}
        self.assertEqual(self.jobs.merge_completed_upload_analysis_into_item_data(requested_by='other', item_data=item), item)
        self.user['app_data_epoch'] = 4
        with self.assertRaises(privacy.AppDataDeletionError):
            self.jobs.merge_completed_upload_analysis_into_item_data(requested_by='owner', item_data=item)


if __name__ == '__main__':
    unittest.main()
