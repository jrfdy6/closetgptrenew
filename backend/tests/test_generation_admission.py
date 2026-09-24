"""Credential-free HTTP tests of the actual active route with mocked external collaborators."""
import ast
import copy
import io
import json
import logging
import sys
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel
from src.routes import outfit_generation_contract as contract
from src.utils import outfit_admission as admission
from src.custom_types.wardrobe import ClothingItem, ClothingType


class Store:
    def __init__(self):
        self.rows = {'wardrobe': {}, 'outfits': {}}
        self.writes = []
        self.fail_reads = self.fail_writes = False
    def collection(self, name):
        return Collection(self, name)
    def get_all(self, references):
        if self.fail_reads:
            raise RuntimeError('read failed')
        return references


class Collection:
    def __init__(self, store, name):
        self.store, self.name = store, name
    def document(self, item_id):
        return Document(self.store, self.name, item_id)
    def where(self, *args, **kwargs):
        return self
    def order_by(self, *args, **kwargs):
        return self
    def limit(self, *args, **kwargs):
        return self
    def stream(self):
        return []


class Document:
    def __init__(self, store, collection, item_id):
        self.store, self.collection, self.id = store, collection, item_id
    @property
    def exists(self):
        return self.id in self.store.rows[self.collection]
    def to_dict(self):
        return copy.deepcopy(self.store.rows[self.collection].get(self.id))
    def set(self, data):
        if self.store.fail_writes:
            raise RuntimeError('write failed')
        self.store.rows[self.collection][self.id] = copy.deepcopy(data)
        self.store.writes.append(copy.deepcopy(data))


class Item(SimpleNamespace):
    metadata = None
    def dict(self):
        return vars(self).copy()


def module(name, **members):
    value = ModuleType(name)
    vars(value).update(members)
    return value


def garment(item_id, kind, **overrides):
    return {'id': item_id, 'type': kind, 'name': f'Real {kind}', 'imageUrl': f'https://example.test/{item_id}.jpg',
            'userId': 'owner', 'occasion': ['Casual'], 'color': 'navy', **overrides}


class CategoryTests(unittest.TestCase):
    def test_real_generation_model_accepts_legacy_persisted_shapes(self):
        original = garment('dress', 'shirt-dress', material=['cotton', 'linen'], season='summer',
                           style='Classic', createdAt='2026-09-22T14:00:00Z', updatedAt='2026-09-22T14:00:00Z', lastWorn=None)
        prepared = admission.normalize_stored_garment(original, {kind.value for kind in ClothingType})
        model = ClothingItem(**prepared)
        self.assertEqual(model.type, ClothingType.DRESS)
        self.assertEqual(model.material, 'cotton, linen')
        self.assertEqual(model.season, ['summer'])
        self.assertEqual(model.createdAt, 1790085600000)
        self.assertEqual(original['material'], ['cotton', 'linen'])

    def test_shared_frontend_backend_category_contract(self):
        fixtures = json.loads((Path(__file__).resolve().parent / 'fixtures/onboarding-readiness-fixtures.json').read_text())
        for row in fixtures['aliases']:
            with self.subTest(row=row):
                self.assertEqual(admission.classify_garment({'type': row['type']}), row['category'])
        for row in fixtures['combinations']:
            with self.subTest(name=row['name']):
                self.assertEqual(admission.has_complete_combination(row['items']), row['hasCoverage'])

    def test_does_not_guess_categories_from_names(self):
        self.assertEqual(admission.classify_garment({'name': 'Nike shoe shirt dress'}), 'unknown')
        self.assertEqual(admission.classify_garment({'type': 'other', 'analysis': {'category': 'jumpsuit'}}), 'one-piece')

    def test_required_item_is_checked_even_for_complete_look(self):
        wardrobe = [garment('dress', 'dress'), garment('shoes', 'shoes')]
        with self.assertRaises(admission.InvalidGeneratedOutfit):
            admission.validate_generated_items(wardrobe, wardrobe, 'required')


class ActiveGenerationAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.wardrobe = [garment('shirt', 'shirt'), garment('pants', 'pants'), garment('shoes', 'shoes')]
        self.seed(self.wardrobe)
        self.robust = SimpleNamespace(generate_outfit=AsyncMock(return_value=SimpleNamespace(
            items=copy.deepcopy(self.wardrobe), confidence=.8, metadata={})))
        self.engine = SimpleNamespace(get_user_preference_from_existing_data=AsyncMock(
            return_value=SimpleNamespace(total_interactions=0, data_source='test')))
        self.readiness = Mock(return_value={'ready': True, 'app_data_epoch': 4})
        self.persist = Mock(side_effect=self.persist_record)
        patched = patch.dict(sys.modules, {
            'src.config.firebase': module('src.config.firebase', db=self.store),
            'src.services.outfit_creation_admission': module('src.services.outfit_creation_admission',
                require_outfit_creation_ready=self.readiness, persist_created_outfit=self.persist),
            'src.services.robust_outfit_generation_service': module('src.services.robust_outfit_generation_service',
                RobustOutfitGenerationService=lambda: self.robust, GenerationContext=SimpleNamespace),
            'src.custom_types.wardrobe': module('src.custom_types.wardrobe', ClothingItem=Item, ClothingType=ClothingType),
            'src.utils.outfit_analysis': module('src.utils.outfit_analysis', generate_outfit_analysis=AsyncMock(return_value={})),
            'src.utils.semantic_compatibility': module('src.utils.semantic_compatibility',
                occasion_matches=lambda occasion, tags: occasion in tags),
        })
        patched.start()
        self.addCleanup(patched.stop)
        path = Path(__file__).resolve().parents[1] / 'src/routes/existing_data_personalized_outfits.py'
        nodes = [node for node in ast.parse(path.read_text()).body if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef)) and
                 node.name in {'OutfitGenerationRequest', 'OutfitResponse', 'generate_personalized_outfit_from_existing_data'}]
        self.ns = {**vars(contract), **vars(admission), '__package__': 'src.routes',
                   'BaseModel': BaseModel, 'Dict': Dict, 'List': List, 'Optional': Optional, 'Any': Any,
                   'router': APIRouter(), 'HTTPException': HTTPException, 'Depends': Depends, 'Request': Request,
                   'get_current_user_id': lambda: 'owner', 'logger': logging.getLogger('admission-tests'),
                   'time': time, 'uuid4': uuid4, 'personalization_engine': self.engine,
                   'ROBUST_SERVICE_AVAILABLE': True, 'robust_service': self.robust,
                   'ROBUST_SERVICE_RETRY_COOLDOWN_SECONDS': 30, '_last_robust_init_failure_at': 0}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), self.ns)
        app = FastAPI()
        app.include_router(self.ns['router'])
        self.client = TestClient(app)

    def persist_record(self, db, user_id, outfit_id, record, readiness, *, require_complete=True):
        # The shared service owns transactional admission; these route tests
        # verify its contract, error propagation and authoritative response.
        record = copy.deepcopy(record)
        wardrobe = admission.load_owned_wardrobe(db, record['items'], user_id)
        record['items'] = admission.validate_generated_items(record['items'], wardrobe, record.get('baseItemId'))
        db.collection('outfits').document(outfit_id).set(record)
        return record

    def seed(self, items):
        self.store.rows['wardrobe'] = {item['id']: copy.deepcopy(item) for item in items}

    def generate(self, **overrides):
        body = {'occasion': 'Casual', 'style': 'Classic', 'mood': 'Calm',
                'weather': {'temperature': 72}, 'wardrobe': copy.deepcopy(self.wardrobe), **overrides}
        with redirect_stdout(io.StringIO()):
            return self.client.post('/generate-personalized', json=body)

    def test_onboarding_gate_rejects_before_provider_or_wardrobe_reads(self):
        detail = {'code': 'onboarding_required', 'resume': '/onboarding', 'stage': 'capsule',
                  'profile_complete': True, 'capsule': {'usable_count': 9}}
        self.readiness.side_effect = HTTPException(status_code=409, detail=detail)
        self.store.fail_reads = True
        response = self.generate()
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(response.json()['detail'], detail)
        self.readiness.assert_called_once_with(self.store, 'owner')
        self.robust.generate_outfit.assert_not_called()
        self.engine.get_user_preference_from_existing_data.assert_not_called()
        self.persist.assert_not_called()

    def test_accepted_legacy_readiness_and_epoch_are_passed_to_final_fence(self):
        self.readiness.return_value = {'ready': True, 'legacy': True, 'app_data_epoch': 7}
        response = self.generate()
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIs(self.persist.call_args.args[4], self.readiness.return_value)
        self.assertTrue(self.persist.call_args.kwargs['require_complete'])

    def test_concurrent_deletion_fence_is_not_wrapped_as_save_failure(self):
        detail = {'code': 'app_data_changed', 'resume': '/onboarding'}
        self.persist.side_effect = HTTPException(status_code=409, detail=detail)
        response = self.generate()
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(response.json()['detail'], detail)
        self.assertEqual(self.store.writes, [])

    def test_response_uses_items_returned_by_final_transaction(self):
        def persist_after_edit(*args, **kwargs):
            self.store.rows['wardrobe']['shirt']['name'] = 'Updated saved shirt'
            return self.persist_record(*args, **kwargs)
        self.persist.side_effect = persist_after_edit
        response = self.generate()
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['items'][0]['name'], 'Updated saved shirt')
        self.assertEqual(response.json()['items'], self.store.writes[0]['items'])

    def test_empty_and_incomplete_wardrobe_never_generate_or_save(self):
        for items in ([], self.wardrobe[:2]):
            response = self.generate(wardrobe=items)
            self.assertEqual(response.status_code, 422, response.text)
        self.robust.generate_outfit.assert_not_called()
        self.assertEqual(self.store.writes, [])

    def test_client_cannot_spoof_categories_ownership_or_images(self):
        request = copy.deepcopy(self.wardrobe)
        request[0].update(userId='foreign', name='Forged', imageUrl='https://untrusted.test/image', type='dress')
        self.robust.generate_outfit.return_value.items = request
        response = self.generate(wardrobe=request)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['items'], self.wardrobe)
        self.assertEqual(self.store.writes[0]['items'], self.wardrobe)
        self.assertEqual(self.robust.generate_outfit.call_args.args[0].wardrobe[0].name, 'Real shirt')

    def test_missing_foreign_unowned_conflicting_and_unusable_records_are_rejected(self):
        for updates in ({'userId': 'foreign'}, {'userId': 'owner', 'user_id': 'foreign'}, {'userId': None},
                        {'deleted': True}, {'imageUrl': ''}):
            with self.subTest(updates=updates):
                self.seed(self.wardrobe)
                self.store.rows['wardrobe']['shirt'].update(updates)
                response = self.generate()
                self.assertEqual(response.status_code, 422, response.text)
        self.seed(self.wardrobe[1:])
        self.assertEqual(self.generate().status_code, 422)
        self.robust.generate_outfit.assert_not_called()
        self.assertEqual(self.store.writes, [])

    def test_unusable_old_candidates_do_not_block_remaining_complete_wardrobe(self):
        incomplete = garment('old-item', 'shirt', imageUrl='')
        self.seed([*self.wardrobe, incomplete])
        response = self.generate(wardrobe=[*self.wardrobe, incomplete])
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(self.robust.generate_outfit.call_args.args[0].wardrobe), 3)

    def test_legacy_user_id_records_are_accepted(self):
        for item in self.store.rows['wardrobe'].values():
            item.pop('userId')
            item['user_id'] = 'owner'
        self.assertEqual(self.generate().status_code, 200)

    def test_empty_incomplete_unknown_and_duplicate_generated_results_never_save(self):
        for items in ([], self.wardrobe[:2], [*self.wardrobe, {'id': 'foreign'}], [*self.wardrobe, self.wardrobe[0]]):
            with self.subTest(items=items):
                self.robust.generate_outfit.return_value.items = items
                response = self.generate()
                self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.store.writes, [])

    def test_missing_required_item_is_rejected_or_repaired_from_owned_records(self):
        response = self.generate(baseItemId='absent')
        self.assertEqual(response.status_code, 422, response.text)
        self.robust.generate_outfit.assert_not_called()
        alternate = garment('alternate', 'shirt')
        self.seed([*self.wardrobe, alternate])
        self.robust.generate_outfit.return_value.items = [alternate, *self.wardrobe[1:]]
        response = self.generate(wardrobe=[*self.wardrobe, alternate], baseItemId='shirt')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([item['id'] for item in response.json()['items']], ['shirt', 'pants', 'shoes'])

    def test_valid_two_piece_outfit_does_not_require_three_or_ten_items(self):
        self.wardrobe = [garment('dress', 'dress'), garment('shoes', 'shoes')]
        self.seed(self.wardrobe)
        self.robust.generate_outfit.return_value.items = self.wardrobe
        response = self.generate()
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(self.store.writes[0]['items']), 2)
        self.assertEqual(self.store.writes[0]['weather'], {'temperature': 72})

    def test_failed_generator_can_use_complete_one_piece_fallback(self):
        self.wardrobe = [garment('dress', 'dress'), garment('shoes', 'sneakers')]
        self.seed(self.wardrobe)
        self.robust.generate_outfit.side_effect = RuntimeError('provider unavailable')
        response = self.generate()
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual({item['id'] for item in self.store.writes[0]['items']}, {'dress', 'shoes'})

    def test_failed_generator_and_incomplete_filtered_fallback_do_not_save(self):
        self.store.rows['wardrobe']['shoes']['occasion'] = ['Formal']
        self.robust.generate_outfit.side_effect = RuntimeError('provider unavailable')
        response = self.generate()
        self.assertEqual(response.status_code, 422, response.text)
        self.assertEqual(self.store.writes, [])

    def test_datastore_failures_report_errors_not_saved_results(self):
        self.store.fail_reads = True
        self.assertEqual(self.generate().status_code, 503)
        self.robust.generate_outfit.assert_not_called()
        self.store.fail_reads = False
        self.store.fail_writes = True
        response = self.generate()
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(self.store.writes, [])


if __name__ == '__main__':
    unittest.main()
