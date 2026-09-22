"""Credential-free tests of the real extracted garment pipeline's evidence pixels."""
import ast
import base64
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
from PIL import Image
from worker.garment_job import (GarmentJobError, constrain_original_reference_image,
                                generate_thumbnail, png_bytes, process_garment)
from worker.flatlay_reference_images import ReferenceImageError

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'items/garment/attempts/attempt-1'


class CleanGarmentProcessingTests(unittest.TestCase):
    def setUp(self):
        self.uploads = {}
        self.remove = Mock()
        self.progress = Mock()

    def capture_upload(self, image, path):
        self.uploads[path] = image.copy()
        return f'https://assets.invalid/{path}'

    def process(self, source):
        payload = {'item_id': 'garment', 'attempt_id': 'attempt-1',
                   'image_url': 'data:image/png;base64,' + base64.b64encode(png_bytes(source)).decode()}
        return process_garment(payload, upload=self.capture_upload, progress=self.progress,
                               remove_background=self.remove)

    def fixture(self):
        image = Image.new('RGBA', (8, 6), (0, 0, 0, 0))
        image.putpixel((3, 2), (17, 55, 91, 255))
        image.putpixel((4, 2), (39, 80, 115, 128))
        return image

    def test_transparent_upload_preserves_exact_source_rgb_and_alpha_in_clean_assets(self):
        source = self.fixture()
        result = self.process(source)
        for filename in ('original.png', 'nobg.png', 'processed.png'):
            with self.subTest(filename=filename):
                actual = self.uploads[f'{PREFIX}/{filename}']
                self.assertEqual(actual.size, source.size)
                self.assertEqual(actual.tobytes(), source.tobytes())
        self.remove.assert_not_called()
        self.assertEqual(result['backgroundRemovedUrl'], f'https://assets.invalid/{PREFIX}/nobg.png')
        self.assertEqual(result['processing_mode'], 'preserved')
        self.assertNotIn('imageUrl', result)

    def test_background_removed_pixels_are_saved_without_crop_whitening_or_shadow(self):
        cutout = self.fixture()
        self.remove.return_value = (png_bytes(cutout), 'alpha')
        original = Image.new('RGBA', cutout.size, (19, 29, 41, 255))
        self.process(original)
        self.assertEqual(self.uploads[f'{PREFIX}/original.png'].tobytes(), original.tobytes())
        self.assertEqual(self.uploads[f'{PREFIX}/nobg.png'].tobytes(), cutout.tobytes())
        self.assertEqual(self.uploads[f'{PREFIX}/processed.png'].tobytes(), cutout.tobytes())
        self.remove.assert_called_once()

    def test_thumbnail_does_not_apply_alpha_twice(self):
        image = Image.new('RGBA', (4, 2), (30, 60, 90, 128))
        thumbnail = generate_thumbnail(image, size=(4, 4))
        self.assertEqual(thumbnail.getpixel((1, 1)), (30, 60, 90, 128))
        self.assertEqual(thumbnail.getpixel((0, 0))[3], 0)
        self.assertEqual(image.getpixel((1, 1)), (30, 60, 90, 128))

    def test_original_reference_keeps_detail_before_working_resize(self):
        image = Image.new('RGBA', (3000, 12), (30, 60, 90, 128))
        result = self.process(image)
        self.assertEqual(self.uploads[f'{PREFIX}/original.png'].size, (3000, 12))
        self.assertEqual(self.uploads[f'{PREFIX}/nobg.png'].width, 2048)
        self.assertEqual(self.uploads[f'{PREFIX}/processed.png'].width, 1024)
        self.assertEqual(result['original_size'], '3000x12')

    def test_empty_background_removal_is_not_published_as_success(self):
        self.remove.return_value = (png_bytes(Image.new('RGBA', (8, 6), (0, 0, 0, 0))), 'alpha')
        with self.assertRaisesRegex(GarmentJobError, 'background_removal_invalid'):
            self.process(Image.new('RGBA', (8, 6), (30, 40, 50, 255)))
        self.assertNotIn(f'{PREFIX}/nobg.png', self.uploads)
        self.assertNotIn(f'{PREFIX}/processed.png', self.uploads)
        # A later timeout/failure still leaves recoverable canonical evidence.
        self.progress.assert_called_once_with({'originalStoragePath': f'{PREFIX}/original.png',
                                               'originalUrl': f'https://assets.invalid/{PREFIX}/original.png'})

    def test_large_original_is_bounded_proportionally_before_storage(self):
        source = Image.new('RGBA', (30, 10), (19, 55, 83, 255))
        bounded = constrain_original_reference_image(source, max_pixels=100, max_bytes=10000)
        self.assertLessEqual(bounded.width * bounded.height, 100)
        self.assertEqual(bounded.size, (10, 3))
        self.assertEqual(bounded.getpixel((0, 0)), (19, 55, 83, 255))
        self.assertEqual(source.size, (30, 10))

    def test_encoded_original_size_is_checked_not_only_source_dimensions(self):
        pixels = np.random.default_rng(123).integers(0, 256, (40, 40, 4), dtype=np.uint8)
        source = Image.fromarray(pixels, 'RGBA')
        bounded = constrain_original_reference_image(source, max_pixels=1600, max_bytes=1500)
        self.assertLess(len(png_bytes(bounded)), 1500)
        self.assertLess(bounded.width, source.width)

    def test_quality_defaults_to_omitted_and_accepts_explicit_enum(self):
        # This unrelated flatlay configuration remains in main; loading its
        # single pure definition avoids live Firebase/provider initialization.
        tree = ast.parse((ROOT / 'worker/main.py').read_text())
        definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                       and node.name == 'get_openai_image_edit_runtime_config']
        env = {'os': SimpleNamespace(environ={}), 'ReferenceImageError': ReferenceImageError,
               'OPENAI_IMAGE_EDIT_API_URL': 'https://provider.invalid', 'OPENAI_IMAGE_EDIT_MODEL': 'gpt-image-1',
               'OPENAI_IMAGE_EDIT_TIMEOUT_SECONDS': 120}
        exec(compile(ast.Module(body=definitions, type_ignores=[]), 'runtime_config', 'exec'), env)
        self.assertIsNone(env['get_openai_image_edit_runtime_config']()['quality'])
        for quality in ('low', 'medium', 'high', 'auto'):
            env['os'].environ['EASYOUTFIT_OPENAI_IMAGE_EDIT_QUALITY'] = quality
            self.assertEqual(env['get_openai_image_edit_runtime_config']()['quality'], quality)
        env['os'].environ['EASYOUTFIT_OPENAI_IMAGE_EDIT_QUALITY'] = 'unpriced-ultra'
        with self.assertRaises(ReferenceImageError):
            env['get_openai_image_edit_runtime_config']()


if __name__ == '__main__':
    unittest.main()
