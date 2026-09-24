"""A stalled first cutout cannot block originals for later selected garments.

Uses a real hanging garment subprocess, real original normalization/reference
loading and real request transactions over a storage/database double. Only the
paid provider and final preview upload are replaced. No cloud credentials run.
"""
import ast
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import sys
import threading
import unittest
from unittest.mock import Mock, patch

import requests
from PIL import Image
from tests.test_flatlay_lifecycle import Database, transactional
from src.services import flatlay_lifecycle as api_lifecycle
from worker import flatlay_lifecycle as lifecycle
from worker import garment_lifecycle as garments
from worker.coordinator import WorkerCoordinator
from worker.flatlay_original_preparation import prepare_request_originals
from worker.flatlay_reference_images import ReferenceImageError, prepare_original_references
from worker.original_source import DEFAULT_BUCKET_NAME
from worker.process_supervisor import JobProcess


class Blob:
    def __init__(self, bucket, path):
        self.bucket, self.path = bucket, path

    def reload(self, **kwargs):
        record = self.bucket.objects[self.path]
        self.size, self.generation = len(record['data']), record['generation']

    def download_as_bytes(self, *, if_generation_match, **kwargs):
        record = self.bucket.objects[self.path]
        assert int(record['generation']) == if_generation_match
        return record['data']

    def upload_from_string(self, data, *, if_generation_match, content_type, **kwargs):
        assert if_generation_match == 0 and self.path not in self.bucket.objects
        assert content_type == 'image/png'
        self.bucket.objects[self.path] = {'data': data, 'generation': 456}


class Bucket:
    name = DEFAULT_BUCKET_NAME

    def __init__(self):
        self.objects = {}

    def blob(self, path):
        return Blob(self, path)


class LocalFlatlayCall:
    """Run the real flatlay body concurrently; its I/O is deterministic/in-memory."""
    def __init__(self, function):
        self.error = None
        def run():
            try:
                function()
            except BaseException as error:
                self.error = error
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def poll(self):
        if self.thread.is_alive():
            return None
        if self.error:
            raise self.error
        return {'status': 'succeeded'}

    def close(self):
        self.thread.join(timeout=3)

    def terminate(self, reason):
        self.close()


class StalledCutoutFlatlayTests(unittest.TestCase):
    def test_later_raw_photos_reach_provider_while_first_cutout_is_still_stalled(self):
        db, bucket = Database(), Bucket()
        db.records['outfits']['look']['items'] = [{'id': name} for name in ('hoodie', 'chinos', 'shoes')]
        db.records['wardrobe'] = {'white-tee': {
            'userId': 'owner', 'imageUrl': f'https://storage.googleapis.com/{bucket.name}/wardrobe/owner/white-tee.jpg',
            'processing_status': 'pending',
        }}
        expected = {}
        for name, color in (('hoodie', (25, 50, 70)), ('chinos', (175, 150, 120)), ('shoes', (80, 45, 35))):
            source = BytesIO()
            Image.new('RGB', (40, 60), color).save(source, format='JPEG')
            raw = source.getvalue()
            path = f'wardrobe/owner/{name}.jpg'
            bucket.objects[path] = {'data': raw, 'generation': 123}
            expected[name] = Image.open(BytesIO(raw)).convert('RGBA').tobytes()
            db.records['wardrobe'][name] = {
                'userId': 'owner', 'imageUrl': f'https://storage.googleapis.com/{bucket.name}/{path}',
                'processing_status': 'pending',
            }
        # Cover a pending private job too: neither it nor unadopted later items
        # has a normalized original or a completed cutout.
        db.records['garment_processing_jobs'] = {'chinos': {
            'user_id': 'owner', 'status': 'pending',
            'source_fingerprint': garments.garment_source_fingerprint(db.records['wardrobe']['chinos']),
        }}
        provider = Mock(return_value=Image.new('RGBA', (512, 512), 'white'))
        prepared = Mock(wraps=prepare_request_originals)
        namespace = {
            'db': db, 'bucket': bucket, 'openai_client': object(),
            'requests': requests, 'ReferenceImageError': ReferenceImageError,
            'time': SimpleNamespace(time=lambda: 1200),
            'claim_request': lambda database, outfit_id: lifecycle.claim_request(database, outfit_id, now=1200),
            'finish_request': lambda database, outfit_id, request_id, **kwargs: lifecycle.finish_request(
                database, outfit_id, request_id, now=1201, **kwargs),
            'admit_provider_request': lambda database, outfit_id, request_id, reports: lifecycle.admit_provider_request(
                database, outfit_id, request_id, reports, now=1200),
            'prepare_request_originals': prepared, 'prepare_original_references': prepare_original_references,
            'generate_original_reference_flatlay': provider,
            'upload_flatlay_image': Mock(return_value='https://assets.invalid/completed-preview'),
            'metrics': {key: 0 for key in ('flat_lay_skipped', 'flat_lay_processed', 'flat_lay_openai',
                                         'flat_lay_failed', 'flat_lay_openai_failed')},
        }
        tree = ast.parse((Path(__file__).resolve().parents[1] / 'worker/main.py').read_text())
        nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                 and node.name in ('FlatlayGenerationError', 'process_outfit_flat_lay')]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'real_flatlay_flow', 'exec'), namespace)
        pending, jobs, flatlays = ['look'], [], []

        def start_garment(claim):
            job = JobProcess({}, command=[sys.executable, '-c', 'import time; time.sleep(60)'], timeout_seconds=10)
            jobs.append(job)
            return job

        def start_flatlay(outfit_id):
            pending.remove(outfit_id)
            job = LocalFlatlayCall(lambda: namespace['process_outfit_flat_lay'](outfit_id))
            flatlays.append(job)
            return job

        coordinator = WorkerCoordinator(
            expire_flatlays=Mock(), recover_garments=Mock(),
            garment_candidates=lambda: ['white-tee', 'hoodie', 'chinos', 'shoes'],
            claim_garment=lambda item_id: garments.claim_garment(db, item_id, 'worker', now=1200),
            start_garment=start_garment, publish_original=Mock(), finish_garment=Mock(),
            flatlay_candidates=lambda: list(pending), start_flatlay=start_flatlay,
        )
        with patch.object(lifecycle.firestore, 'transactional', transactional), \
                patch.object(requests, 'get', side_effect=AssertionError('No source URL fetching')), \
                patch.object(requests, 'post', side_effect=AssertionError('No paid network call')):
            reserved = api_lifecycle.reserve_request(db, 'look', 'owner', now=1190)
            try:
                coordinator.tick()
                flatlays[0].thread.join(timeout=3)
                self.assertIsNotNone(flatlays[0].poll())
                self.assertIsNone(jobs[0].poll(), 'flatlay must finish while first garment is still running')
                provider.assert_called_once()
                prepared.assert_called_once()
                references, outfit_id = provider.call_args.args
                self.assertEqual(outfit_id, 'look')
                self.assertEqual({reference['id'] for reference in references}, set(expected))
                for reference in references:
                    actual = Image.open(BytesIO(reference['image_bytes'])).convert('RGBA')
                    self.assertEqual(actual.tobytes(), expected[reference['id']])
                request = db.records[lifecycle.REQUESTS_COLLECTION]['look']
                self.assertEqual(request['status'], 'done')
                self.assertEqual(request['credit_status'], 'consumed')
                self.assertEqual(request['provider_admitted_at'], 1200)
                self.assertEqual(len(request['prepared_originals']), 3)
                self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)
                self.assertEqual(db.records['garment_processing_jobs']['white-tee']['status'], 'processing')
                self.assertEqual(db.records['garment_processing_jobs']['chinos']['status'], 'pending')
                self.assertNotIn('hoodie', db.records['garment_processing_jobs'])
                self.assertFalse(any('/attempts/' in path or path == 'items/hoodie/original.png'
                                     for path in bucket.objects))
                self.assertEqual(lifecycle.reserve_request(db, 'look', 'owner', now=1202)['request_id'], reserved['request_id'])
                namespace['process_outfit_flat_lay']('look')
                self.assertEqual(provider.call_count, 1)
                self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 6)
            finally:
                coordinator.close()


if __name__ == '__main__':
    unittest.main()
