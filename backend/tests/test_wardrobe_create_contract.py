"""Credential-free tests for actual upload creation and its transaction boundary."""

import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from src.services import wardrobe_persistence as persistence


class RetryConflict(Exception):
    pass


class Document:
    def __init__(self, db, key):
        self.db, self.key = db, key

    def get(self, transaction=None):
        value = deepcopy(self.db.records.get(self.key))
        transaction.version = self.db.version
        return SimpleNamespace(exists=value is not None, to_dict=lambda: value)


class Transaction:
    def __init__(self, db):
        self.db, self.version, self.pending = db, None, None

    def create(self, reference, value):
        self.pending = (reference.key, deepcopy(value))

    def commit(self):
        if self.db.before_commit:
            callback, self.db.before_commit = self.db.before_commit, None
            callback()
        if self.db.version != self.version:
            raise RetryConflict()
        if self.pending:
            key, value = self.pending
            if key in self.db.records:
                raise AssertionError('Create cannot overwrite')
            self.db.records[key] = value
            self.db.version += 1
            self.db.writes += 1


class Database:
    def __init__(self, records=None):
        self.records, self.version, self.writes = deepcopy(records or {}), 0, 0
        self.before_commit = None

    def collection(self, name):
        assert name == 'wardrobe'
        return SimpleNamespace(document=lambda key: Document(self, key))

    def transaction(self):
        return Transaction(self)


def transactional(callback):
    def run(transaction):
        for _ in range(3):
            attempt = Transaction(transaction.db)
            result = callback(attempt)
            try:
                attempt.commit()
            except RetryConflict:
                continue
            return result
        raise AssertionError('No transaction convergence')
    return run


ITEM = {'id': 'upload-1', 'name': 'Shirt', 'type': 'shirt', 'color': 'white', 'imageUrl': 'https://images.example.test/shirt.jpg'}


class CreationTests(unittest.TestCase):
    def setUp(self):
        decorator = patch.object(persistence.firestore, 'transactional', transactional)
        decorator.start()
        self.addCleanup(decorator.stop)

    def test_create_uses_verified_owner_and_acknowledges_actual_persisted_record(self):
        db = Database()
        saved = persistence.create_owned_wardrobe_item(db, 'owner', {**ITEM, 'userId': 'spoofed', 'user_id': 'other'}, now='now')
        self.assertEqual(db.records['upload-1'], saved)
        self.assertEqual(saved['userId'], 'owner')
        self.assertNotIn('user_id', saved)
        self.assertEqual(db.writes, 1)

    def test_owned_retry_does_not_reset_worker_results_or_edit_history(self):
        original = {**ITEM, 'userId': 'owner', 'name': 'Edited shirt', 'wearCount': 8, 'backgroundRemovedUrl': '/cutout.png', 'processing_status': 'completed'}
        db = Database({'upload-1': original})
        saved = persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(saved, original)
        self.assertEqual(db.records['upload-1'], original)
        self.assertEqual(db.writes, 0)

    def test_foreign_and_ambiguous_ownership_cannot_be_overwritten(self):
        for ownership in ({'userId': 'other'}, {'user_id': 'other'}, {'userId': 'owner', 'user_id': 'other'}, {}):
            original = {**ITEM, **ownership}
            db = Database({'upload-1': original})
            with self.assertRaises(persistence.WardrobeOwnershipConflict):
                persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
            self.assertEqual(db.records['upload-1'], original)
            self.assertEqual(db.writes, 0)

    def test_concurrent_foreign_create_retries_read_and_rejects_without_overwrite(self):
        db = Database()
        foreign = {**ITEM, 'userId': 'other'}
        def race():
            db.records['upload-1'] = foreign
            db.version += 1
        db.before_commit = race
        with self.assertRaises(persistence.WardrobeOwnershipConflict):
            persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(db.records['upload-1'], foreign)
        self.assertEqual(db.writes, 0)

    def test_legacy_owned_retry_preserves_database_shape_and_returns_canonical_owner(self):
        original = {**ITEM, 'user_id': 'owner'}
        db = Database({'upload-1': original})
        saved = persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(saved['userId'], 'owner')
        self.assertEqual(db.records['upload-1'], original)
        self.assertEqual(db.writes, 0)

    def test_invalid_identifiers_cannot_address_arbitrary_document_paths(self):
        for item_id in ('', 'x/y/z', '.', '..', 123):
            with self.assertRaises(ValueError):
                persistence.create_owned_wardrobe_item(Database(), 'owner', {**ITEM, 'id': item_id})


def load_route():
    source = Path(__file__).parents[1] / 'app.py'
    route = next(node for node in ast.parse(source.read_text()).body if isinstance(node, ast.AsyncFunctionDef) and node.name == 'add_wardrobe_item_direct')
    route.decorator_list = []
    route.args.defaults = []
    namespace = {'HTTPException': HTTPException}
    exec(compile(ast.Module(body=[route], type_ignores=[]), str(source), 'exec'), namespace)
    return namespace[route.name]


class EndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_storage_failure_is_not_http_200_success(self):
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}), patch.object(persistence, 'create_owned_wardrobe_item', side_effect=RuntimeError('offline')):
            with self.assertRaises(HTTPException) as failure:
                await load_route()(ITEM, 'owner')
            self.assertEqual(failure.exception.status_code, 503)

    async def test_foreign_identifier_has_explicit_conflict_status(self):
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}), patch.object(persistence, 'create_owned_wardrobe_item', side_effect=persistence.WardrobeOwnershipConflict()):
            with self.assertRaises(HTTPException) as failure:
                await load_route()(ITEM, 'owner')
            self.assertEqual(failure.exception.status_code, 409)


if __name__ == '__main__':
    unittest.main()
