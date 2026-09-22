"""Real upload handler/HTTP boundary with fake Storage and no account access."""

import ast
import importlib.util
from pathlib import Path
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


def load_upload_app():
    # Only the legacy auth collaborator is injected. Execute the actual router
    # module, decorators, multipart parsing and upload handler without booting
    # the unrelated application Firebase/AI services.
    auth = ModuleType('src.auth.auth_service')
    auth.get_current_user_id = lambda: 'verified-owner'
    backend = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location(
        'isolated_upload_original_route', backend / 'src/routes/image_upload_minimal.py')
    route = importlib.util.module_from_spec(spec)
    with patch.dict('sys.modules', {'src.auth.auth_service': auth}):
        spec.loader.exec_module(route)

    # Keep the actual application mount contract in the test as well.
    tree = ast.parse((backend / 'app.py').read_text())
    registrations = next(ast.literal_eval(node.value) for node in tree.body
                         if isinstance(node, ast.Assign) and any(
                             isinstance(target, ast.Name) and target.id == 'ROUTERS'
                             for target in node.targets))
    mounts = [prefix for module, prefix in registrations
              if module == 'src.routes.image_upload_minimal']
    assert mounts == ['/api/image']
    app = FastAPI()
    app.include_router(route.router, prefix=mounts[0])
    return route, TestClient(app)


class OriginalUploadContractTests(unittest.TestCase):
    def setUp(self):
        self.route, self.client = load_upload_app()
        self.blob = Mock(public_url='https://storage.example/wardrobe/verified-owner/original.jpg')
        self.bucket = Mock(name='fake-bucket')
        self.bucket.blob.return_value = self.blob
        storage_patch = patch.object(self.route.storage, 'bucket', return_value=self.bucket)
        self.storage = storage_patch.start()
        self.addCleanup(storage_patch.stop)

    def upload(self, contents=b'original-photo-bytes', content_type='image/jpeg'):
        return self.client.post('/api/image/upload',
                                files={'file': ('shirt.jpg', contents, content_type)})

    def test_saved_original_is_the_only_successful_photo(self):
        response = self.upload()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'success': True, 'image_url': self.blob.public_url,
            'filename': 'shirt.jpg', 'size': len(b'original-photo-bytes'),
        })
        self.blob.upload_from_string.assert_called_once_with(
            b'original-photo-bytes', content_type='image/jpeg')
        self.blob.make_public.assert_called_once_with()
        path = self.bucket.blob.call_args.args[0]
        self.assertTrue(path.startswith('wardrobe/verified-owner/'))

    def test_upload_or_visibility_failure_cannot_return_a_placeholder_or_success(self):
        for method in ('upload_from_string', 'make_public'):
            with self.subTest(method=method):
                self.blob.reset_mock(side_effect=True)
                getattr(self.blob, method).side_effect = RuntimeError('private provider exception')
                response = self.upload()
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json(), {
                    'success': False, 'code': 'upload_unavailable',
                    'error': 'Your photo upload could not be confirmed. Please try again.',
                    'retryable': True,
                })
                self.assertEqual(response.headers['Retry-After'], '5')
                self.assertEqual(response.headers['Cache-Control'], 'private, no-store')
                self.assertNotIn('private provider exception', response.text)
                self.assertNotIn('image_url', response.json())
                self.assertNotIn('picsum', response.text)
                self.assertNotIn('fallback', response.json())
                self.blob.upload_from_string.assert_called_once()
                if method == 'upload_from_string':
                    self.blob.make_public.assert_not_called()

    def test_retry_after_failed_upload_can_confirm_the_real_original(self):
        self.blob.upload_from_string.side_effect = [RuntimeError('unavailable'), None]
        failed = self.upload()
        retried = self.upload()
        self.assertEqual(failed.status_code, 503)
        self.assertFalse(failed.json()['success'])
        self.assertEqual(retried.status_code, 200)
        self.assertTrue(retried.json()['success'])
        self.assertEqual(retried.json()['image_url'], self.blob.public_url)
        self.assertEqual(self.blob.upload_from_string.call_count, 2)

    def test_missing_storage_is_not_reported_as_a_saved_photo(self):
        self.storage.side_effect = RuntimeError('private storage config')
        response = self.upload()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('private storage config', response.text)
        self.assertNotIn('image_url', response.json())
        self.blob.upload_from_string.assert_not_called()

    def test_empty_and_non_image_inputs_never_reach_storage(self):
        for contents, content_type in ((b'', 'image/jpeg'), (b'not-an-image', 'text/plain')):
            with self.subTest(content_type=content_type, empty=not contents):
                response = self.upload(contents, content_type)
                self.assertEqual(response.status_code, 400)
                self.assertNotIn('image_url', response.json())
        self.storage.assert_not_called()


if __name__ == '__main__':
    unittest.main()
