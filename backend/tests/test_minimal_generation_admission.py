"""Credential-free HTTP admission tests for the retained minimal generator."""
import ast
import copy
import logging
import sys
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.routes import outfit_generation_contract as contract
from src.utils import outfit_admission as admission
from test_generation_admission import Store, garment, module


class MinimalGenerationAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.wardrobe = [garment('shirt', 'shirt'), garment('pants', 'pants'), garment('shoes', 'shoes')]
        self.store.rows['wardrobe'] = {item['id']: copy.deepcopy(item) for item in self.wardrobe}
        self.readiness = Mock(return_value={'ready': True, 'app_data_epoch': 4})
        self.persist = Mock(side_effect=self.persist_record)
        self.engine = SimpleNamespace(get_user_preference=Mock(return_value=SimpleNamespace(interaction_count=0)))
        patched = patch.dict(sys.modules, {
            'src.config.firebase': module('src.config.firebase', db=self.store),
            'src.services.outfit_creation_admission': module('src.services.outfit_creation_admission',
                require_outfit_creation_ready=self.readiness, persist_created_outfit=self.persist),
        })
        patched.start()
        self.addCleanup(patched.stop)
        path = Path(__file__).resolve().parents[1] / 'src/routes/simple_personalized_outfits_minimal.py'
        nodes = [node for node in ast.parse(path.read_text()).body
                 if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef)) and node.name in {
                     'OutfitGenerationRequest', 'OutfitResponse', 'generate_personalized_outfit'}]
        self.ns = {**vars(contract), **vars(admission), '__package__': 'src.routes',
                   'BaseModel': BaseModel, 'Dict': Dict, 'List': List, 'Optional': Optional, 'Any': Any,
                   'router': APIRouter(), 'HTTPException': HTTPException, 'Depends': Depends,
                   'get_current_user_id': lambda: 'owner', 'logger': logging.getLogger('minimal-admission-tests'),
                   'time': time, 'uuid4': uuid4, 'personalization_engine': self.engine}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), self.ns)
        app = FastAPI()
        app.include_router(self.ns['router'])
        self.client = TestClient(app)

    def persist_record(self, db, user_id, outfit_id, record, readiness, *, require_complete=True):
        record = copy.deepcopy(record)
        wardrobe = admission.load_owned_wardrobe(db, record['items'], user_id)
        record['items'] = admission.validate_generated_items(record['items'], wardrobe, record.get('baseItemId'))
        db.collection('outfits').document(outfit_id).set(record)
        return record

    def generate(self, **overrides):
        return self.client.post('/generate-personalized', json={
            'occasion': 'Casual', 'style': 'Classic', 'mood': 'Calm',
            'wardrobe': copy.deepcopy(self.wardrobe), **overrides})

    def test_gate_denies_before_preference_or_wardrobe_work(self):
        detail = {'code': 'onboarding_required', 'resume': '/onboarding', 'stage': 'quiz',
                  'profile_complete': False, 'capsule': {'usable_count': 10}}
        self.readiness.side_effect = HTTPException(status_code=409, detail=detail)
        self.store.fail_reads = True
        response = self.generate()
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(response.json()['detail'], detail)
        self.engine.get_user_preference.assert_not_called()
        self.persist.assert_not_called()

    def test_legacy_ready_account_saves_and_passes_epoch_to_final_fence(self):
        self.readiness.return_value = {'ready': True, 'legacy': True, 'app_data_epoch': 6}
        response = self.generate()
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(self.store.writes), 1)
        self.assertEqual(response.json()['items'], self.store.writes[0]['items'])
        self.assertEqual(self.store.writes[0]['user_id'], 'owner')
        self.assertIs(self.persist.call_args.args[4], self.readiness.return_value)
        self.assertTrue(self.persist.call_args.kwargs['require_complete'])

    def test_client_metadata_does_not_control_selection_or_saved_items(self):
        forged = copy.deepcopy(self.wardrobe)
        forged[0].update(userId='foreign', name='Forged dress', type='dress',
                         imageUrl='https://untrusted.test/photo', metadata={'fabric': 'forged'})
        response = self.generate(wardrobe=forged)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual({item['id']: item for item in response.json()['items']},
                         {item['id']: item for item in self.wardrobe})
        self.assertEqual(self.store.writes[0]['items'], response.json()['items'])

    def test_unowned_or_missing_candidates_reject_before_selection(self):
        for item in ({'userId': 'foreign'}, {'user_id': 'foreign'}, {'imageUrl': ''}, {'deleted': True}):
            with self.subTest(item=item):
                self.store.rows['wardrobe']['shirt'] = {**self.wardrobe[0], **item}
                response = self.generate()
                self.assertEqual(response.status_code, 422, response.text)
        self.store.rows['wardrobe'].pop('shirt')
        self.assertEqual(self.generate().status_code, 422)
        self.engine.get_user_preference.assert_not_called()
        self.persist.assert_not_called()

    def test_required_item_is_resolved_and_preserved(self):
        self.assertEqual(self.generate(baseItemId='missing').status_code, 422)
        alternate = garment('alternate', 'shirt', name='Alternate shirt')
        self.store.rows['wardrobe']['alternate'] = alternate
        response = self.generate(wardrobe=[*self.wardrobe, alternate], baseItemId='alternate')
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()['baseItemId'], 'alternate')
        self.assertEqual({item['id'] for item in response.json()['items']}, {'alternate', 'pants', 'shoes'})
        self.assertEqual(self.store.writes[0]['baseItemId'], 'alternate')

    def test_personalization_cannot_insert_foreign_or_incomplete_result(self):
        self.engine.get_user_preference.return_value.interaction_count = 3
        for items in ([{'id': 'foreign'}], self.wardrobe[:2]):
            self.engine.rank_outfits_by_preference = Mock(return_value=[{'id': 'ranked', 'items': items}])
            response = self.generate()
            self.assertEqual(response.status_code, 422, response.text)
        self.persist.assert_not_called()

    def test_concurrent_deletion_returns_conflict_without_saved_success(self):
        self.persist.side_effect = HTTPException(status_code=409, detail={'code': 'app_data_changed'})
        response = self.generate()
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(response.json()['detail']['code'], 'app_data_changed')
        self.assertEqual(self.store.writes, [])

    def test_latest_transaction_items_are_returned(self):
        def edited_record(*args, **kwargs):
            self.store.rows['wardrobe']['shirt']['name'] = 'Latest stored shirt'
            return self.persist_record(*args, **kwargs)
        self.persist.side_effect = edited_record
        response = self.generate()
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(next(item['name'] for item in response.json()['items'] if item['id'] == 'shirt'),
                         'Latest stored shirt')

    def test_unavailable_datastore_and_failed_save_do_not_report_success(self):
        self.store.fail_reads = True
        self.assertEqual(self.generate().status_code, 503)
        self.store.fail_reads = False
        self.store.fail_writes = True
        response = self.generate()
        self.assertEqual(response.status_code, 503, response.text)
        self.assertEqual(self.store.writes, [])

    def test_same_second_generations_have_distinct_persisted_ids(self):
        with patch.object(time, 'time', return_value=1234):
            first, second = self.generate(), self.generate()
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertNotEqual(first.json()['id'], second.json()['id'])
        self.assertEqual(len(self.store.rows['outfits']), 2)


if __name__ == '__main__':
    unittest.main()
