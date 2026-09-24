"""Original normalization from exact owned Storage objects; no HTTP/inference."""
import copy
from hashlib import sha256
from io import BytesIO
import unittest
from unittest.mock import Mock, patch

from PIL import Image, ImageOps
from worker import flatlay_original_preparation as preparation
from worker.original_source import DEFAULT_BUCKET_NAME, request_original_path
from worker.flatlay_reference_images import ReferenceImageError


def encoded(image, format='PNG', **kwargs):
    stream = BytesIO()
    image.save(stream, format=format, **kwargs)
    return stream.getvalue()


class PreconditionFailed(Exception):
    pass


class Blob:
    def __init__(self, data=b'', *, size=None, generation=987, download_error=None, upload_error=None):
        self.data = data
        self.size = len(data) if size is None else size
        self.generation = generation
        self.download_error = download_error
        self.upload_error = upload_error
        self.reads, self.downloads, self.uploads = [], [], []
        self.make_public = Mock(side_effect=AssertionError('An original must stay private'))

    def reload(self, **kwargs):
        self.reads.append(kwargs)

    def download_as_bytes(self, **kwargs):
        self.downloads.append(kwargs)
        if self.download_error:
            raise self.download_error
        return self.data

    def upload_from_string(self, data, **kwargs):
        self.uploads.append((data, kwargs))
        if self.upload_error:
            raise self.upload_error
        self.data = data


class Bucket:
    name = DEFAULT_BUCKET_NAME

    def __init__(self, blobs=None):
        self.blobs = blobs or {}
        self.paths = []

    def blob(self, path):
        self.paths.append(path)
        return self.blobs.setdefault(path, Blob())


class RequestOriginalPreparationTests(unittest.TestCase):
    def setUp(self):
        self.source_path = 'wardrobe/owner/my-shirt.jpg'
        self.target_path = request_original_path('shirt', 'request-1')
        self.image = Image.new('RGB', (25, 17), (35, 70, 105))
        self.raw = encoded(self.image, 'JPEG', quality=95)
        self.request = {'user_id': 'owner', 'request_id': 'request-1', 'items': [{
            'id': 'shirt', 'imageUrl': 'https://never-follow.invalid/private.jpg',
            'originalStoragePath': self.target_path,
            'originalPreparation': {'bucket': DEFAULT_BUCKET_NAME, 'sourceStoragePath': self.source_path},
        }]}
        self.bucket = Bucket({self.source_path: Blob(self.raw)})

    def assert_error(self, code, request=None, bucket=None):
        with self.assertRaises(ReferenceImageError) as error:
            preparation.prepare_request_originals(self.request if request is None else request,
                                                  self.bucket if bucket is None else bucket)
        self.assertEqual(error.exception.code, code)
        self.assertNotIn('secret', str(error.exception))
        self.assertNotIn('https://', str(error.exception))

    def assert_no_uploads(self):
        self.assertFalse(any(blob.uploads for blob in self.bucket.blobs.values()))

    def test_jpeg_pixels_normalize_once_to_private_immutable_png_with_report(self):
        with patch('requests.get', side_effect=AssertionError('No HTTP source loads')), \
             patch('worker.garment_job.isolated_remove', side_effect=AssertionError('No inference')):
            reports = preparation.prepare_request_originals(self.request, self.bucket)
        self.assertEqual(self.bucket.paths, [self.source_path, self.target_path])
        source, target = self.bucket.blobs[self.source_path], self.bucket.blobs[self.target_path]
        self.assertEqual(source.reads, [{'timeout': 30, 'retry': None}])
        self.assertEqual(source.downloads, [{'timeout': 30, 'retry': None, 'if_generation_match': 987}])
        self.assertEqual(target.uploads[0][1], {'content_type': 'image/png', 'if_generation_match': 0,
                                              'predefined_acl': 'private', 'timeout': 20, 'retry': None})
        target.make_public.assert_not_called()
        with Image.open(BytesIO(self.raw)) as decoded, Image.open(BytesIO(target.data)) as output:
            self.assertEqual(output.format, 'PNG')
            self.assertEqual(output.mode, 'RGBA')
            self.assertEqual(output.tobytes(), decoded.convert('RGBA').tobytes())
        self.assertEqual(reports, [{'id': 'shirt', 'sourceStoragePath': self.source_path,
                                  'sourceGeneration': '987', 'originalStoragePath': self.target_path,
                                  'sha256': sha256(target.data).hexdigest()}])
        self.assertEqual(self.request['items'][0]['imageUrl'], 'https://never-follow.invalid/private.jpg')

    def test_rgba_png_preserves_exact_colors_transparency_and_dimensions(self):
        image = Image.new('RGBA', (5, 7), (25, 50, 100, 128))
        image.putpixel((2, 3), (41, 81, 121, 255))
        self.bucket.blobs[self.source_path] = Blob(encoded(image), generation='456')
        reports = preparation.prepare_request_originals(self.request, self.bucket)
        with Image.open(BytesIO(self.bucket.blobs[self.target_path].data)) as output:
            self.assertEqual(output.size, image.size)
            self.assertEqual(output.tobytes(), image.tobytes())
        self.assertEqual(reports[0]['sourceGeneration'], '456')

    def test_exif_orientation_is_normalized_without_styling(self):
        exif = self.image.getexif()
        exif[274] = 6
        raw = encoded(self.image, 'JPEG', exif=exif)
        self.bucket.blobs[self.source_path] = Blob(raw)
        preparation.prepare_request_originals(self.request, self.bucket)
        with Image.open(BytesIO(raw)) as original, Image.open(BytesIO(self.bucket.blobs[self.target_path].data)) as output:
            self.assertEqual(output.size, (17, 25))
            self.assertEqual(output.tobytes(), ImageOps.exif_transpose(original).convert('RGBA').tobytes())

    def test_existing_canonical_originals_are_skipped_without_storage_access(self):
        self.request['items'] = [{'id': 'shirt', 'originalStoragePath': 'items/shirt/attempts/a/original.png'}]
        self.assertEqual(preparation.prepare_request_originals(self.request, self.bucket), [])
        self.assertEqual(self.bucket.paths, [])

    def test_invalid_bucket_user_source_and_target_paths_fail_before_any_io(self):
        cases = []
        for source in ('wardrobe/other/photo.jpg', 'wardrobe/owner/../photo.jpg', 'wardrobe/owner/nested/photo.jpg',
                       'wardrobe/owner/%2e%2e.jpg', 'wardrobe/owner/photo.jpg%3Ftoken=secret',
                       'https://outside.invalid/photo.jpg', 'items/shirt/original.png', 12):
            request = copy.deepcopy(self.request)
            request['items'][0]['originalPreparation']['sourceStoragePath'] = source
            cases.append((request, 'invalid_original_preparation'))
        for bucket_name in ('another-bucket', None, 12):
            request = copy.deepcopy(self.request)
            request['items'][0]['originalPreparation']['bucket'] = bucket_name
            cases.append((request, 'invalid_original_preparation'))
        for owner in ('../owner', 'other', None, 12):
            request = copy.deepcopy(self.request)
            request['user_id'] = owner
            cases.append((request, 'invalid_original_preparation'))
        for target in ('items/other/flatlay-requests/request-1/original.png',
                       'items/shirt/flatlay-requests/other-request/original.png',
                       'items/shirt/attempts/request-1/original.png', None):
            request = copy.deepcopy(self.request)
            request['items'][0]['originalStoragePath'] = target
            cases.append((request, 'invalid_original_path'))
        for request, code in cases:
            with self.subTest(request=request):
                self.assert_error(code, request)
        self.assertEqual(self.bucket.paths, [])
        wrong_bucket = Bucket()
        wrong_bucket.name = 'another-bucket'
        self.assert_error('invalid_original_preparation', bucket=wrong_bucket)
        self.assertEqual(wrong_bucket.paths, [])

    def test_invalid_request_id_and_duplicate_items_fail_before_io(self):
        self.request['request_id'] = '../outside'
        self.assert_error('invalid_original_path')
        self.request['request_id'] = 'request-1'
        self.request['items'].append(copy.deepcopy(self.request['items'][0]))
        self.assert_error('duplicate_reference_id')
        self.assertEqual(self.bucket.paths, [])

    def test_source_generation_race_and_bad_metadata_fail_without_upload(self):
        for generation in (None, True, 'not-a-generation', '-1', '0', '1' * 40, '١٢٣'):
            with self.subTest(generation=generation):
                self.bucket.blobs[self.source_path] = Blob(self.raw, generation=generation)
                self.assert_error('original_source_unavailable')
                self.assertEqual(self.bucket.blobs[self.source_path].downloads, [])
        source = Blob(self.raw, generation=123, download_error=PreconditionFailed('secret storage url'))
        self.bucket.blobs[self.source_path] = source
        self.assert_error('original_source_unavailable')
        self.assertEqual(source.downloads[0]['if_generation_match'], 123)
        self.assert_no_uploads()

    def test_source_metadata_and_actual_bytes_are_bounded(self):
        for size, code in ((False, 'invalid_original_image'), (0, 'invalid_original_image'),
                           (preparation.MAX_DOWNLOAD_BYTES + 1, 'original_image_too_large')):
            self.bucket.blobs[self.source_path] = Blob(self.raw, size=size)
            self.assert_error(code)
            self.assertEqual(self.bucket.blobs[self.source_path].downloads, [])
        self.bucket.blobs[self.source_path] = Blob(self.raw, size=len(self.raw) + 1)
        self.assert_error('original_image_changed')
        self.bucket.blobs[self.source_path] = Blob(b'invalid image')
        self.assert_error('invalid_original_image')
        self.assert_no_uploads()

    def test_animated_and_fully_transparent_sources_are_rejected(self):
        animated = encoded(self.image, save_all=True, append_images=[Image.new('RGB', self.image.size, 'white')])
        self.bucket.blobs[self.source_path] = Blob(animated)
        self.assert_error('animated_original_image')
        self.bucket.blobs[self.source_path] = Blob(encoded(Image.new('RGBA', (5, 7), (0, 0, 0, 0))))
        self.assert_error('empty_original_image')
        self.assert_no_uploads()

    def add_second(self, data=None):
        self.request['items'].append({'id': 'shoes', 'originalStoragePath': request_original_path('shoes', 'request-1'),
                                     'originalPreparation': {'bucket': DEFAULT_BUCKET_NAME,
                                                             'sourceStoragePath': 'wardrobe/owner/shoes.png'}})
        self.bucket.blobs['wardrobe/owner/shoes.png'] = Blob(self.raw if data is None else data)

    def test_all_sources_validate_before_any_upload_and_no_partial_report(self):
        self.add_second(b'invalid image')
        self.assert_error('invalid_original_image')
        self.assert_no_uploads()
        self.assertEqual(self.bucket.paths, [self.source_path, 'wardrobe/owner/shoes.png'])

    def test_cumulative_byte_and_pixel_limits_apply_to_prepared_originals(self):
        self.add_second()
        with patch.object(preparation, 'MAX_TOTAL_REFERENCE_BYTES', 1):
            self.assert_error('reference_images_too_large')
        with patch.object(preparation, 'MAX_TOTAL_REFERENCE_PIXELS', self.image.width * self.image.height):
            self.assert_error('reference_images_dimensions_too_large')
        self.assert_no_uploads()

    def test_immutable_precondition_and_other_upload_failures_are_safe(self):
        for error in (PreconditionFailed('secret existing object'), RuntimeError('secret network failure')):
            self.bucket.blobs[self.target_path] = Blob(upload_error=error)
            self.assert_error('original_preparation_failed')
            target = self.bucket.blobs[self.target_path]
            self.assertEqual(target.uploads[0][1]['if_generation_match'], 0)
            self.assertEqual(target.uploads[0][1]['retry'], None)
            target.make_public.assert_not_called()


if __name__ == '__main__':
    unittest.main()
