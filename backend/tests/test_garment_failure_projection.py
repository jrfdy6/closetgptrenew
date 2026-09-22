"""Child JSON -> actual supervisor/coordinator -> real lifecycle projection.

Storage, network and inference boundaries are injected in disposable subprocesses.
Firestore transactions use the existing deterministic fake; no live services run.
"""
import base64
from pathlib import Path
import os
import sys
import unittest
from unittest.mock import Mock, patch

from PIL import Image
from worker import garment_lifecycle as lifecycle
from worker.coordinator import GarmentRun, WorkerCoordinator
from worker.garment_errors import SAFE_FAILURE_CODES, garment_failure_code
from worker.garment_job import png_bytes
from worker.process_supervisor import JobProcess, read_json
from tests.test_garment_lifecycle import Database, transactional

BACKEND = Path(__file__).resolve().parents[1]
CHILD = '''
import sys
from worker import garment_job as job
manifest, result, progress, mode, supplied_code = sys.argv[1:]
def fail(*args, **kwargs):
    raise job.GarmentJobError(supplied_code)
def uploader(bucket_name):
    if mode == 'storage':
        return fail
    return lambda image, path: 'https://assets.invalid/' + path
job.firebase_uploader = uploader
real_process = job.process_garment
def process(payload, **kwargs):
    if mode == 'download':
        kwargs['download'] = fail
    elif mode == 'inference':
        kwargs['remove_background'] = fail
    elif mode == 'unexpected':
        raise RuntimeError(supplied_code)
    return real_process(payload, **kwargs)
job.process_garment = process
sys.argv = ['garment_job', '--manifest', manifest, '--result', result, '--progress', progress]
raise SystemExit(job.main())
'''


class GarmentFailureProjectionTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.photo = 'data:image/png;base64,' + base64.b64encode(
            png_bytes(Image.new('RGBA', (10, 8), (30, 60, 90, 255)))).decode()
        self.item['imageUrl'] = self.photo
        self.decorator = patch.object(lifecycle.firestore, 'transactional', transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    @property
    def item(self):
        return self.db.records['wardrobe']['shirt']

    @property
    def job(self):
        return self.db.records[lifecycle.JOBS_COLLECTION]['shirt']

    def coordinator(self, claim, process, now):
        coordinator = WorkerCoordinator(
            expire_flatlays=lambda: None, recover_garments=lambda: None,
            garment_candidates=lambda: [], claim_garment=Mock(), start_garment=Mock(),
            publish_original=lambda item, attempt, fields: lifecycle.publish_original(
                self.db, item, attempt, fields, now=now),
            finish_garment=lambda item, attempt, **kwargs: lifecycle.finish_garment(
                self.db, item, attempt, now=now, **kwargs),
            flatlay_candidates=lambda: [], start_flatlay=Mock(),
        )
        coordinator.garment = GarmentRun(claim, process)
        return coordinator

    def actual_failure(self, mode='image', supplied_code='', now=100):
        claim = lifecycle.claim_garment(self.db, 'shirt', 'worker', now=now)
        self.assertIsNotNone(claim)
        process = JobProcess({'item_id': 'shirt', 'attempt_id': claim['attempt_id'],
                              'image_url': self.item['imageUrl']},
                             command=[sys.executable, '-c', CHILD, '{manifest}', '{result}', '{progress}',
                                      mode, supplied_code], timeout_seconds=5,
                             env={'PATH': os.environ.get('PATH', ''), 'PYTHONPATH': str(BACKEND)})
        try:
            process.process.wait(timeout=5)
            envelope = read_json(process.result_path)
            log = process.log_path.read_text()
            self.assertEqual(process.process.returncode, 1)
            self.assertEqual(set(envelope), {'status', 'error_code'})
            self.assertIn(envelope['error_code'], SAFE_FAILURE_CODES)
            coordinator = self.coordinator(claim, process, now + 1)
            coordinator.tick()
            self.assertIsNone(coordinator.garment)
            self.assertEqual(self.item['processing_error_code'], envelope['error_code'])
            return claim, envelope, log
        finally:
            process.close()

    def test_unsupported_source_is_terminal_with_replace_photo_guidance(self):
        source = 'file:///not-read/private-photo.jpg'
        self.item['imageUrl'] = source
        claim, envelope, _ = self.actual_failure()
        self.assertEqual(envelope['error_code'], 'invalid_image')
        self.assert_invalid_photo_terminal(claim, source)

    def test_unreadable_source_bytes_are_terminal_with_replace_photo_guidance(self):
        source = 'data:image/png;base64,' + base64.b64encode(b'not an image').decode()
        self.item['imageUrl'] = source
        claim, envelope, _ = self.actual_failure()
        self.assertEqual(envelope['error_code'], 'invalid_image')
        self.assert_invalid_photo_terminal(claim, source)
        # Replacing the photo is distinct source work and can claim a new run.
        self.item.update(imageUrl=self.photo, processing_status='pending')
        replacement = lifecycle.claim_garment(self.db, 'shirt', 'worker', now=300)
        self.assertEqual(replacement['attempt_count'], 1)
        self.assertNotEqual(replacement['generation_id'], claim['generation_id'])

    def assert_invalid_photo_terminal(self, claim, source):
        self.assertEqual(self.item['processing_status'], 'failed')
        self.assertEqual(self.item['processing_attempt_count'], 1)
        self.assertIsNone(self.item['processing_next_attempt_at'])
        self.assertFalse(self.item['processing_retryable'])
        self.assertEqual(self.item['processing_retry_action'], 'replace_photo')
        self.assertEqual(self.item['processing_error'], "We couldn't read this photo. Try another photo of this item.")
        self.assertEqual(self.item['imageUrl'], source)
        self.assertIsNone(lifecycle.claim_garment(self.db, 'shirt', 'worker', now=200))
        with self.assertRaises(lifecycle.GarmentRetryError) as caught:
            lifecycle.retry_garment(self.db, 'shirt', 'owner', claim['attempt_id'], now=201)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIn('Choose another photo', caught.exception.detail)

    def test_transient_download_inference_and_storage_keep_bounded_retry_guidance(self):
        cases = (('download', 'source_download_failed', 'processing_failed'),
                 ('inference', 'fallback_inference_failed', 'processing_failed'),
                 ('storage', 'asset_upload_failed', 'invalid_result'))
        for mode, raw_code, code in cases:
            with self.subTest(mode=mode):
                self.db = Database()
                self.item['imageUrl'] = self.photo
                for count, now in enumerate((100, 200, 400), 1):
                    _, envelope, _ = self.actual_failure(mode, raw_code, now)
                    self.assertEqual(envelope['error_code'], code)
                    self.assertEqual(self.item['processing_attempt_count'], count)
                    self.assertEqual(self.item['imageUrl'], self.photo)
                    self.assertIn('Your original photo is still available.', self.item['processing_error'])
                    self.assertEqual(self.item['processing_status'], 'failed' if count == 3 else 'pending')
                    if count < 3:
                        self.assertIsNotNone(self.item['processing_next_attempt_at'])
                self.assertEqual(self.item['processing_retry_action'], 'retry_item')
                self.assertTrue(self.item['processing_retryable'])
                self.assertIsNone(self.item['processing_next_attempt_at'])
                self.assertIsNone(lifecycle.claim_garment(self.db, 'shirt', 'worker', now=600))

    def test_producer_unknown_and_untyped_errors_never_expose_exception_text(self):
        secret = 'https://private.invalid/photo?token=synthetic-secret'
        for mode in ('download', 'unexpected'):
            with self.subTest(mode=mode):
                self.db = Database()
                self.item['imageUrl'] = self.photo
                _, envelope, log = self.actual_failure(mode, secret)
                self.assertEqual(envelope['error_code'], 'processing_failed')
                self.assertNotIn(secret, log)
                self.assertNotIn(secret, str(self.item))

    def test_consumer_unknown_legacy_missing_or_malformed_codes_are_safe(self):
        cases = (({'status': 'failed', 'error_code': 'https://private.invalid?token=secret'}, 'processing_failed'),
                 ({'status': 'failed', 'error_code': ['not', 'a', 'code']}, 'processing_failed'),
                 ({'status': 'failed', 'error': 'source_image_invalid'}, 'invalid_image'),
                 ({'status': 'failed'}, 'worker_crashed'))
        for envelope, expected in cases:
            with self.subTest(envelope=envelope):
                self.db = Database()
                self.item['imageUrl'] = self.photo
                claim = lifecycle.claim_garment(self.db, 'shirt', 'worker', now=100)
                process = Mock()
                process.poll.return_value = {'status': 'failed', 'result': envelope, 'progress': {}}
                process.read_progress.return_value = {}
                coordinator = self.coordinator(claim, process, 101)
                coordinator.tick()
                self.assertIsNone(coordinator.garment)
                self.assertEqual(self.item['processing_error_code'], expected)
                self.assertNotIn('secret', str(self.item))
                process.close.assert_called_once()

    def test_all_emitted_codes_have_existing_lifecycle_guidance(self):
        self.assertLessEqual(SAFE_FAILURE_CODES, lifecycle.ERRORS.keys())
        self.assertEqual(garment_failure_code(None), 'processing_failed')
        self.assertEqual(garment_failure_code('invalid_item_id'), 'invalid_identifier')


if __name__ == '__main__':
    unittest.main()
