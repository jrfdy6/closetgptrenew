"""Bounded garment stages with injected storage and no model/provider invocation."""
import base64
from contextlib import redirect_stderr
from io import BytesIO
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image
from worker import garment_job
from worker.garment_job import (
    ALPHA_TIMEOUT_SECONDS, FALLBACK_TIMEOUT_SECONDS, WHOLE_JOB_TIMEOUT_SECONDS,
    GarmentJobError, _run_inference, download_image,
    firebase_uploader, infer, isolated_remove, normalize_source, png_bytes, process_garment,
)
from worker.process_supervisor import JobProcess


class GarmentJobTests(unittest.TestCase):
    def setUp(self):
        self.original = Image.new('RGBA', (20, 15), (35, 65, 95, 255))
        self.original_bytes = png_bytes(self.original)
        self.payload = {'item_id': 'tee', 'attempt_id': 'attempt-id', 'image_url': 'https://assets.invalid/tee.jpg'}
        self.uploads = []
        self.progress = []

    def upload(self, image, path):
        self.uploads.append((path, image.copy()))
        return 'https://assets.invalid/' + path

    def test_original_is_uploaded_once_and_acknowledged_before_inference_failure(self):
        def fail(_source):
            self.assertEqual(len(self.uploads), 1)
            self.assertEqual(self.progress, [{'originalStoragePath': 'items/tee/attempts/attempt-id/original.png',
                                             'originalUrl': 'https://assets.invalid/items/tee/attempts/attempt-id/original.png'}])
            raise GarmentJobError('fallback_inference_failed')
        with self.assertRaisesRegex(GarmentJobError, 'fallback_inference_failed'):
            process_garment(self.payload, upload=self.upload, progress=self.progress.append,
                             download=lambda _: self.original_bytes, remove_background=fail)
        self.assertEqual(len(self.uploads), 1)
        self.assertEqual(self.uploads[0][1].tobytes(), self.original.tobytes())

    def test_alpha_and_fallback_production_budgets_and_fresh_attempts(self):
        self.assertEqual((ALPHA_TIMEOUT_SECONDS, FALLBACK_TIMEOUT_SECONDS, WHOLE_JOB_TIMEOUT_SECONDS),
                         (240, 60, 360))
        calls = []
        def inference(mode, source, output, timeout):
            calls.append((mode, timeout))
            self.assertEqual(source.read_bytes(), self.original_bytes)
            if mode == 'alpha':
                output.write_bytes(b'partial output must not leak into fallback')
                raise GarmentJobError('alpha_inference_failed', diagnostics=[{
                    'stage': 'alpha_removal', 'category': 'runtime_error'}])
            self.assertFalse(output.exists())
            return self.original_bytes
        output, mode = isolated_remove(self.original_bytes, run_inference=inference)
        self.assertEqual(output, self.original_bytes)
        self.assertEqual(mode, 'fast')
        self.assertEqual(calls, [('alpha', 240), ('fallback', 60)])

    def test_corrupt_and_empty_alpha_trigger_fallback_but_invalid_fallback_fails(self):
        invalids = (b'not a png', png_bytes(Image.new('RGBA', (10, 10), (0, 0, 0, 0))))
        for invalid in invalids:
            with self.subTest(invalid=invalid[:10]):
                inference = Mock(side_effect=[invalid, self.original_bytes])
                self.assertEqual(isolated_remove(self.original_bytes, run_inference=inference),
                                 (self.original_bytes, 'fast'))
                self.assertEqual(inference.call_args.args[0], 'fallback')
                self.assertEqual(inference.call_args.args[3], 60)
                with self.assertRaisesRegex(GarmentJobError, 'background_removal_invalid'):
                    isolated_remove(self.original_bytes, run_inference=Mock(return_value=invalid))

    def test_alpha_and_fallback_hangs_really_terminate_then_later_job_runs(self):
        children = []
        def factory(payload, **kwargs):
            # Short test budgets only. Production stage selection still supplies
            # 240/60; the factory substitutes deterministic sleeping processes.
            child = JobProcess(payload, command=[sys.executable, '-c', 'import time; time.sleep(30)'],
                               timeout_seconds=.15, env=kwargs['env'])
            children.append(child)
            return child
        def inference(mode, source, output, timeout):
            self.assertEqual(timeout, 240 if mode == 'alpha' else 60)
            return _run_inference(mode, source, output, timeout, job_factory=factory)
        with self.assertRaisesRegex(GarmentJobError, 'fallback_inference_failed'):
            isolated_remove(self.original_bytes, run_inference=inference)
        self.assertEqual(len(children), 2)
        for child in children:
            self.assertIsNotNone(child.process.returncode)
            self.assertFalse(child.workdir.exists())
            with self.assertRaises(ProcessLookupError):
                os.kill(child.pid, 0)
        followup = JobProcess({}, command=[sys.executable, '-c', 'pass'], timeout_seconds=2)
        try:
            followup.process.wait(timeout=2)
            self.assertEqual(followup.poll()['status'], 'succeeded')
        finally:
            followup.close()

    def test_inference_child_does_not_receive_provider_key(self):
        child = Mock()
        child.poll.return_value = {'status': 'failed'}
        factory = Mock(return_value=child)
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'OPENAI_API_KEY': 'private-test-marker'}):
            with self.assertRaises(GarmentJobError):
                _run_inference('alpha', Path(directory) / 'in', Path(directory) / 'out', 240, job_factory=factory)
        self.assertNotIn('OPENAI_API_KEY', factory.call_args.kwargs['env'])
        child.close.assert_called_once()

    def test_inference_import_removal_and_output_failures_have_safe_distinct_stages(self):
        secret = 'https://private.invalid/model?token=secret'
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / 'source.png', Path(directory) / 'output.png'
            source.write_bytes(self.original_bytes)
            with patch.dict(sys.modules, {'rembg': None}), self.assertRaises(GarmentJobError) as caught:
                infer('alpha', str(source), str(output))
            self.assertEqual(caught.exception.diagnostics, [{'stage': 'alpha_import', 'category': 'dependency_missing'}])
            rembg = SimpleNamespace(remove=Mock(side_effect=RuntimeError(secret)))
            with patch.dict(sys.modules, {'rembg': rembg}), self.assertRaises(GarmentJobError) as caught:
                infer('fallback', str(source), str(output))
            self.assertEqual(caught.exception.diagnostics, [{'stage': 'fallback_removal', 'category': 'runtime_error'}])
            rembg.remove = Mock(return_value=self.original_bytes)
            with patch.dict(sys.modules, {'rembg': rembg}), patch.object(Path, 'write_bytes', side_effect=PermissionError(secret)), self.assertRaises(GarmentJobError) as caught:
                infer('alpha', str(source), str(output))
            self.assertEqual(caught.exception.diagnostics, [{'stage': 'alpha_output', 'category': 'permission_denied'}])
            self.assertNotIn(secret, str(caught.exception.diagnostics))

    def test_inference_supervisor_failures_are_classified_without_child_logs(self):
        cases = (({'status': 'timed_out', 'returncode': -9}, 'process_timeout'),
                 ({'status': 'failed', 'returncode': -9}, 'process_crashed'),
                 ({'status': 'failed', 'returncode': 0}, 'process_no_result'),
                 ({'status': 'failed', 'returncode': 0, 'result': {'status': 'failed'}}, 'process_failed'),
                 ({'status': 'succeeded', 'result': {'status': 'succeeded'}}, 'output_missing'))
        with tempfile.TemporaryDirectory() as directory:
            for summary, category in cases:
                with self.subTest(category=category):
                    child = Mock()
                    child.poll.return_value = summary
                    with self.assertRaises(GarmentJobError) as caught:
                        _run_inference('fallback', Path(directory) / 'in', Path(directory) / 'out',
                                       60, job_factory=Mock(return_value=child))
                    self.assertEqual(str(caught.exception), 'fallback_inference_failed')
                    self.assertEqual(caught.exception.diagnostics,
                                     [{'stage': 'fallback_process', 'category': category}])
                    child.close.assert_called_once()

    def test_raising_exception_accessors_cannot_replace_safe_job_failure_envelope(self):
        secret = 'https://private.invalid/model?token=secret'
        class HTTPError(Exception):
            @property
            def response(self):
                raise RuntimeError(secret)

            @property
            def diagnostics(self):
                raise RuntimeError(secret)

        with tempfile.TemporaryDirectory() as directory:
            manifest, result, progress = (Path(directory) / name for name in ('manifest', 'result', 'progress'))
            manifest.write_text(json.dumps(self.payload))
            stderr = StringIO()
            argv = ['job', '--manifest', str(manifest), '--result', str(result), '--progress', str(progress)]
            with patch.object(sys, 'argv', argv), patch.object(garment_job, 'firebase_uploader', side_effect=HTTPError(secret)), redirect_stderr(stderr):
                self.assertEqual(garment_job.main(), 1)
            envelope = json.loads(result.read_text())
            self.assertEqual(envelope['error_code'], 'processing_failed')
            self.assertEqual(envelope['diagnostics'], [{'stage': 'storage_setup', 'category': 'http_error'}])
            self.assertEqual(stderr.getvalue().strip(), 'processing_failed')
            self.assertNotIn(secret, str(envelope))

    def test_optional_inference_manifest_io_failure_preserves_success_and_failure_exit(self):
        secret = 'https://private.invalid/model?token=secret'
        argv = ['job', '--infer', 'alpha', 'input', 'output', 'result']
        for failure in (None, RuntimeError(secret)):
            stderr = StringIO()
            with self.subTest(failure=bool(failure)), patch.object(sys, 'argv', argv), \
                    patch.object(garment_job, 'infer', side_effect=failure), \
                    patch.object(garment_job, 'atomic_json', side_effect=OSError(secret)), redirect_stderr(stderr):
                self.assertEqual(garment_job.main(), 1 if failure else 0)
            self.assertNotIn(secret, stderr.getvalue())
            self.assertNotIn('Traceback', stderr.getvalue())

    def test_job_module_import_never_initializes_rembg_or_firebase(self):
        result = subprocess.run([sys.executable, '-c',
                                 'import sys; from worker import garment_job; '
                                 'assert "rembg" not in sys.modules; assert "firebase_admin" not in sys.modules'],
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_attempt_paths_cannot_escape_item_and_attempt_namespace(self):
        for key in ('item_id', 'attempt_id'):
            for value in ('../other', 'x/y', '', '..', '/root'):
                with self.subTest(key=key, value=value), self.assertRaises(GarmentJobError):
                    process_garment({**self.payload, key: value}, upload=self.upload)
        self.assertEqual(self.uploads, [])

    def test_source_download_has_finite_timeouts_streaming_and_byte_limit(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.headers = {}
        response.iter_content.return_value = iter([b'x' * 6, b'y' * 6])
        with patch('requests.get', return_value=response) as get, patch('worker.garment_job.MAX_DOWNLOAD_BYTES', 10):
            with self.assertRaisesRegex(GarmentJobError, 'source_too_large'):
                download_image('https://assets.invalid/private?token=secret')
        self.assertEqual(get.call_args.kwargs, {'timeout': (5, 20), 'stream': True})

    def test_download_failure_does_not_leak_source_url_or_secret(self):
        with patch('requests.get', side_effect=RuntimeError('https://private.invalid?token=secret')):
            with self.assertRaises(GarmentJobError) as caught:
                download_image('https://private.invalid?token=secret')
        self.assertEqual(str(caught.exception), 'source_download_failed')

    def test_data_uri_and_dimension_validation_are_bounded(self):
        source = 'data:image/png;base64,' + base64.b64encode(self.original_bytes).decode()
        self.assertEqual(download_image(source), self.original_bytes)
        for bad in ('data:image/png;base64,!!!!', 'file:///etc/passwd', 'data:image/png,abc'):
            with self.assertRaises(GarmentJobError):
                download_image(bad)
        with patch('worker.garment_job.MAX_SOURCE_PIXELS', 100):
            with self.assertRaisesRegex(GarmentJobError, 'source_dimensions_too_large'):
                normalize_source(self.original_bytes)

    def test_exif_orientation_is_normalized_before_original_is_saved(self):
        image = Image.new('RGB', (7, 11), (10, 20, 30))
        exif = image.getexif()
        exif[274] = 6
        buffer = BytesIO()
        image.save(buffer, format='JPEG', exif=exif)
        normalized = normalize_source(buffer.getvalue())
        self.assertEqual(normalized.size, (11, 7))
        self.assertEqual(normalized.mode, 'RGBA')

    def test_storage_is_immutable_and_operations_have_no_unbounded_retry(self):
        blob = Mock()
        blob.public_url = 'https://assets.invalid/safe.png'
        bucket = Mock()
        bucket.blob.return_value = blob
        firebase = SimpleNamespace(get_app=lambda: 'app', storage=SimpleNamespace(bucket=Mock(return_value=bucket)),
                                   credentials=Mock())
        with patch.dict(sys.modules, {'firebase_admin': firebase}):
            uploader = firebase_uploader('test-bucket')
            result = uploader(self.original, 'items/tee/attempts/a/original.png')
        self.assertEqual(result, blob.public_url)
        self.assertEqual(blob.upload_from_string.call_args.kwargs,
                         {'content_type': 'image/png', 'if_generation_match': 0, 'timeout': 20, 'retry': None})
        blob.make_public.assert_called_once_with(timeout=20, retry=None)


if __name__ == '__main__':
    unittest.main()
