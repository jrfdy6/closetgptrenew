"""Credential-free image processing regressions: preserve garment evidence pixels."""
import ast
import base64
import unittest
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import requests
from PIL import Image, ImageOps, UnidentifiedImageError
from concurrent.futures import TimeoutError
from worker.flatlay_reference_images import ReferenceImageError, MAX_IMAGE_BYTES, MAX_IMAGE_PIXELS

ROOT = Path(__file__).resolve().parents[1]


def png_bytes(image):
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


class CleanGarmentProcessingTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((ROOT / 'worker/main.py').read_text())
        names = {'process_item', 'resize_image', 'generate_thumbnail', 'decode_data_uri',
                 'get_openai_image_edit_runtime_config', 'constrain_original_reference_image'}
        definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        self.uploads = {}
        self.doc_ref = SimpleNamespace(update=Mock())
        self.future = SimpleNamespace(result=Mock(), cancel=Mock())
        self.env = {
            'Image': Image, 'ImageOps': ImageOps, 'UnidentifiedImageError': UnidentifiedImageError,
            'BytesIO': BytesIO, 'base64': base64, 'np': np, 'requests': requests, 'TimeoutError': TimeoutError,
            'time': SimpleNamespace(time=lambda: 1200),
            'db': SimpleNamespace(collection=lambda _name: SimpleNamespace(document=lambda _key: self.doc_ref)),
            'MAX_RETRIES': 3, 'MAX_IMAGE_BYTES': 5 * 1024 * 1024, 'MAX_OUTPUT_WIDTH': 1024,
            'MAX_OUTPUT_HEIGHT': 1024, 'THUMBNAIL_SIZE': 512, 'ALPHA_TIMEOUT_SECONDS': 240,
            'FIRESTORE_COLLECTION': 'wardrobe', 'metrics': {'failed': 0, 'processed': 0},
            'mark_failure': Mock(), 'upload_png': self.capture_upload,
            'alpha_executor': SimpleNamespace(submit=Mock(return_value=self.future)), '_alpha_matting': Mock(),
            'remove': Mock(), 'remove_hangers': Mock(), 'smooth_edges': Mock(),
            'add_material_shadow': Mock(), 'apply_light_gradient': Mock(),
            'ReferenceImageError': ReferenceImageError,
            'MAX_REFERENCE_IMAGE_BYTES': MAX_IMAGE_BYTES, 'MAX_REFERENCE_IMAGE_PIXELS': MAX_IMAGE_PIXELS,
            'os': SimpleNamespace(environ={}), 'OPENAI_IMAGE_EDIT_API_URL': 'https://provider.invalid',
            'OPENAI_IMAGE_EDIT_MODEL': 'gpt-image-1', 'OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS': 120,
        }
        exec(compile(ast.Module(body=definitions, type_ignores=[]), 'worker_image_processing_under_test', 'exec'), self.env)

    def capture_upload(self, image, path):
        self.uploads[path] = image.copy()
        return f'https://assets.invalid/{path}'

    def process(self, source):
        data = {'imageUrl': 'data:image/png;base64,' + base64.b64encode(png_bytes(source)).decode()}
        self.env['process_item']('garment', data)

    def fixture(self):
        image = Image.new('RGBA', (8, 6), (0, 0, 0, 0))
        image.putpixel((3, 2), (17, 55, 91, 255))
        image.putpixel((4, 2), (39, 80, 115, 128))
        return image

    def test_transparent_upload_preserves_exact_source_rgb_and_alpha_in_clean_assets(self):
        source = self.fixture()
        self.process(source)
        for filename in ('original.png', 'nobg.png', 'processed.png'):
            with self.subTest(filename=filename):
                actual = self.uploads[f'items/garment/{filename}']
                self.assertEqual(actual.size, source.size)
                self.assertEqual(actual.tobytes(), source.tobytes())
        self.env['alpha_executor'].submit.assert_not_called()
        for name in ('smooth_edges', 'add_material_shadow', 'apply_light_gradient', 'remove_hangers'):
            self.env[name].assert_not_called()
        update = self.doc_ref.update.call_args.args[0]
        self.assertEqual(update['backgroundRemovedUrl'], 'https://assets.invalid/items/garment/nobg.png')
        self.assertEqual(update['processing_status'], 'done')

    def test_background_removed_pixels_are_saved_without_crop_whitening_or_shadow(self):
        cutout = self.fixture()
        self.future.result.return_value = png_bytes(cutout)
        original = Image.new('RGBA', cutout.size, (19, 29, 41, 255))
        self.process(original)
        self.assertEqual(self.uploads['items/garment/original.png'].tobytes(), original.tobytes())
        self.assertEqual(self.uploads['items/garment/nobg.png'].tobytes(), cutout.tobytes())
        self.assertEqual(self.uploads['items/garment/processed.png'].tobytes(), cutout.tobytes())
        self.env['alpha_executor'].submit.assert_called_once()
        self.env['remove_hangers'].assert_not_called()
        self.env['apply_light_gradient'].assert_not_called()

    def test_thumbnail_does_not_apply_alpha_twice(self):
        image = Image.new('RGBA', (4, 2), (30, 60, 90, 128))
        thumbnail = self.env['generate_thumbnail'](image, size=(4, 4))
        self.assertEqual(thumbnail.getpixel((1, 1)), (30, 60, 90, 128))
        self.assertEqual(thumbnail.getpixel((0, 0))[3], 0)
        self.assertEqual(image.getpixel((1, 1)), (30, 60, 90, 128))

    def test_original_reference_keeps_detail_before_working_resize(self):
        image = Image.new('RGBA', (3000, 12), (30, 60, 90, 128))
        self.process(image)
        self.assertEqual(self.uploads['items/garment/original.png'].size, (3000, 12))
        self.assertEqual(self.uploads['items/garment/nobg.png'].width, 2048)
        self.assertEqual(self.uploads['items/garment/processed.png'].width, 1024)
        self.assertEqual(self.doc_ref.update.call_args.args[0]['original_size'], '3000x12')

    def test_empty_background_removal_is_not_published_as_success(self):
        self.future.result.return_value = png_bytes(Image.new('RGBA', (8, 6), (0, 0, 0, 0)))
        self.process(Image.new('RGBA', (8, 6), (30, 40, 50, 255)))
        self.env['mark_failure'].assert_called_once()
        self.assertNotIn('items/garment/nobg.png', self.uploads)
        self.assertNotIn('items/garment/processed.png', self.uploads)
        self.doc_ref.update.assert_not_called()

    def test_large_original_is_bounded_proportionally_before_storage(self):
        source = Image.new('RGBA', (30, 10), (19, 55, 83, 255))
        bounded = self.env['constrain_original_reference_image'](source, max_pixels=100, max_bytes=10000)
        self.assertLessEqual(bounded.width * bounded.height, 100)
        self.assertEqual(bounded.size, (10, 3))
        self.assertEqual(bounded.getpixel((0, 0)), (19, 55, 83, 255))
        self.assertEqual(source.size, (30, 10))

    def test_encoded_original_size_is_checked_not_only_source_dimensions(self):
        # A small random RGBA PNG exceeds this synthetic limit until downsampled.
        pixels = np.random.default_rng(123).integers(0, 256, (40, 40, 4), dtype=np.uint8)
        source = Image.fromarray(pixels, 'RGBA')
        bounded = self.env['constrain_original_reference_image'](source, max_pixels=1600, max_bytes=1500)
        self.assertLess(len(png_bytes(bounded)), 1500)
        self.assertLess(bounded.width, source.width)

    def test_quality_defaults_to_omitted_and_accepts_explicit_enum(self):
        self.assertIsNone(self.env['get_openai_image_edit_runtime_config']()['quality'])
        for quality in ('low', 'medium', 'high', 'auto'):
            self.env['os'].environ['EASYOUTFIT_OPENAI_IMAGE_EDIT_QUALITY'] = quality
            self.assertEqual(self.env['get_openai_image_edit_runtime_config']()['quality'], quality)
        self.env['os'].environ['EASYOUTFIT_OPENAI_IMAGE_EDIT_QUALITY'] = 'unpriced-ultra'
        with self.assertRaises(ReferenceImageError):
            self.env['get_openai_image_edit_runtime_config']()


if __name__ == '__main__':
    unittest.main()
