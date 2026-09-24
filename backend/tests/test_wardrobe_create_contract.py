"""Credential-free tests for actual upload creation and its transaction boundary."""

import ast
import asyncio
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import unittest
import threading
from unittest.mock import patch

from fastapi import HTTPException
from src.services import wardrobe_persistence as persistence
from src.auth.verified_identity import reject_identity_overrides


class RetryConflict(Exception):
    pass


class Document:
    def __init__(self, db, key, collection="wardrobe"):
        self.db, self.key, self.collection = db, key, collection

    def get(self, transaction=None):
        store = self.db.records if self.collection == "wardrobe" else self.db.users if self.collection == "users" else self.db.asset_owners
        value = deepcopy(store.get(self.key))
        if transaction is not None:
            transaction.version = self.db.version
        return SimpleNamespace(exists=value is not None, to_dict=lambda: value)


class Transaction:
    def __init__(self, db):
        self.db, self.version, self.pending = db, None, []

    def create(self, reference, value):
        self.pending.append(('create', reference, deepcopy(value)))

    def update(self, reference, value):
        self.pending.append(('update', reference, deepcopy(value)))

    def commit(self):
        if self.db.before_commit:
            callback, self.db.before_commit = self.db.before_commit, None
            callback()
        if self.db.version != self.version:
            raise RetryConflict()
        for kind, reference, value in self.pending:
            store = self.db.records if reference.collection == 'wardrobe' else self.db.users if reference.collection == 'users' else self.db.asset_owners
            if kind == 'create':
                if reference.key in store:
                    raise AssertionError('Create cannot overwrite')
                store[reference.key] = value
            else:
                store[reference.key].update(value)
            self.db.version += 1
            self.db.writes += int(reference.collection == 'wardrobe')


class Database:
    def __init__(self, records=None):
        self.records, self.version, self.writes = deepcopy(records or {}), 0, 0
        self.before_commit = None
        self.asset_owners = {}
        self.users = {'owner': {'app_data_epoch': 0, 'wardrobeItemCount': 0}, 'other': {'app_data_epoch': 0}}

    def collection(self, name):
        assert name in ('wardrobe', 'wardrobe_asset_owners', 'users')
        return SimpleNamespace(document=lambda key: Document(self, key, name))

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

    def test_asset_owner_reservation_prevents_foreign_reuse_after_item_delete(self):
        db = Database()
        persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(db.asset_owners['upload-1'], {'user_id': 'owner'})
        del db.records['upload-1']
        with self.assertRaises(persistence.WardrobeOwnershipConflict):
            persistence.create_owned_wardrobe_item(db, 'other', ITEM)
        self.assertNotIn('upload-1', db.records)
        self.assertEqual(db.asset_owners['upload-1'], {'user_id': 'owner'})
        self.assertEqual(persistence.create_owned_wardrobe_item(db, 'owner', ITEM)['userId'], 'owner')

    def test_first_create_increments_count_once_and_replay_preserves_it(self):
        db = Database()
        persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(db.users['owner']['wardrobeItemCount'], 1)
        persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(db.users['owner']['wardrobeItemCount'], 1)

    def test_completed_deletion_during_transaction_retry_cannot_adopt_new_epoch(self):
        db = Database()
        def clear_during_commit():
            db.users['owner']['app_data_epoch'] = 1
            db.version += 1
        db.before_commit = clear_during_commit
        from src.services.app_data_privacy import AppDataDeletionError
        with self.assertRaises(AppDataDeletionError):
            persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertNotIn('upload-1', db.records)
        self.assertEqual(db.asset_owners, {})
        self.assertEqual(db.users['owner']['wardrobeItemCount'], 0)

    def test_owned_retry_does_not_reset_worker_results_or_edit_history(self):
        original = {**ITEM, 'userId': 'owner', 'name': 'Edited shirt', 'wearCount': 8, 'backgroundRemovedUrl': '/cutout.png', 'processing_status': 'completed'}
        db = Database({'upload-1': original})
        saved = persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(saved, original)
        self.assertEqual(db.records['upload-1'], original)
        self.assertEqual(db.writes, 0)

    def test_new_upload_cannot_plant_secondary_owner_aliases(self):
        original = {**ITEM, 'metadata': {'visualAttributes': {'material': 'cotton'}},
                    'analysis': {'confidence': 0.9}, 'contentHash': 'original-photo'}
        for alias in ('user_id', 'firebase_uid', 'uid', 'ownerId'):
            for value in ('other', 'owner', '', None):
                with self.subTest(alias=alias, value=value):
                    db = Database()
                    saved = persistence.create_owned_wardrobe_item(db, 'owner', {**original, alias: value})
                    self.assertEqual(saved['userId'], 'owner')
                    self.assertNotIn(alias, saved)
                    self.assertEqual(saved['metadata'], original['metadata'])
                    self.assertEqual(saved['analysis'], original['analysis'])
                    self.assertEqual(saved['imageUrl'], original['imageUrl'])
                    self.assertEqual(saved['contentHash'], original['contentHash'])

    def test_every_conflicting_stored_alias_prevents_an_ack_without_changing_the_record(self):
        for alias in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId'):
            for value in ('other', '', 123, False, {'uid': 'owner'}):
                with self.subTest(alias=alias, value=value):
                    original = {**ITEM, 'userId': 'owner', alias: value, 'wearCount': 8,
                                'backgroundRemovedUrl': '/finished-original.png'}
                    db = Database({'upload-1': original})
                    with self.assertRaises(persistence.WardrobeOwnershipConflict):
                        persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
                    self.assertEqual(db.records['upload-1'], original)
                    self.assertEqual(db.writes, 0)

    def test_matching_legacy_aliases_are_preserved_on_idempotent_ack(self):
        original = {**ITEM, 'userId': 'owner', 'user_id': 'owner', 'firebase_uid': 'owner',
                    'uid': 'owner', 'ownerId': 'owner', 'metadata': {'workerResult': 'done'},
                    'wearCount': 8, 'processing_status': 'completed', 'backgroundRemovedUrl': '/original-cutout.png'}
        db = Database({'upload-1': original})
        self.assertEqual(persistence.create_owned_wardrobe_item(db, 'owner', ITEM), original)
        self.assertEqual(db.records['upload-1'], original)
        self.assertEqual(db.writes, 0)

    def test_concurrent_conflicting_alias_is_rejected_after_transaction_retry(self):
        db = Database()
        conflicting = {**ITEM, 'userId': 'owner', 'firebase_uid': 'other', 'wearCount': 8}
        def race():
            db.records['upload-1'] = conflicting
            db.version += 1
        db.before_commit = race
        with self.assertRaises(persistence.WardrobeOwnershipConflict):
            persistence.create_owned_wardrobe_item(db, 'owner', ITEM)
        self.assertEqual(db.records['upload-1'], conflicting)
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
            with self.assertRaises(persistence.WardrobeInputError):
                persistence.create_owned_wardrobe_item(Database(), 'owner', {**ITEM, 'id': item_id})


def load_route():
    source = Path(__file__).parents[1] / 'app.py'
    route = next(node for node in ast.parse(source.read_text()).body if isinstance(node, ast.AsyncFunctionDef) and node.name == 'add_wardrobe_item_direct')
    route.decorator_list = []
    route.args.defaults = []
    namespace = {'HTTPException': HTTPException, 'reject_wardrobe_identity_overrides': reject_identity_overrides}
    exec(compile(ast.Module(body=[route], type_ignores=[]), str(source), 'exec'), namespace)
    return namespace[route.name]


class EndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_transaction_does_not_block_other_work_on_the_request_loop(self):
        release = threading.Event()
        def slow_transaction(*_args):
            # This callback can only run if the request loop remains free while
            # the synchronous storage operation waits in its worker thread.
            if not release.wait(timeout=1):
                raise RuntimeError('The transaction blocked the event loop')
            return {**ITEM, 'userId': 'owner', 'wearCount': 8}
        timer = asyncio.get_running_loop().call_later(0.02, release.set)
        try:
            with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}), patch.object(persistence, 'create_owned_wardrobe_item', side_effect=slow_transaction):
                result = await load_route()(ITEM, {'uid': 'owner'})
            self.assertTrue(result['success'])
            self.assertEqual(result['item']['wearCount'], 8)
        finally:
            release.set()
            timer.cancel()

    async def test_known_input_validation_is_422(self):
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}):
            with self.assertRaises(HTTPException) as failure:
                await load_route()({**ITEM, 'id': 'invalid/path'}, {'uid': 'owner'})
            self.assertEqual(failure.exception.status_code, 422)
            self.assertEqual(failure.exception.detail, 'Invalid wardrobe item ID')

    async def test_sdk_transaction_exhaustion_is_retryable_503_not_input_422(self):
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}), patch.object(persistence, 'create_owned_wardrobe_item', side_effect=ValueError('Failed to commit transaction in 5 attempts: private details')):
            with self.assertRaises(HTTPException) as failure:
                await load_route()(ITEM, {'uid': 'owner'})
            self.assertEqual(failure.exception.status_code, 503)
            self.assertNotIn('private details', failure.exception.detail)

    async def test_storage_failure_is_not_http_200_success(self):
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}), patch.object(persistence, 'create_owned_wardrobe_item', side_effect=RuntimeError('offline')):
            with self.assertRaises(HTTPException) as failure:
                await load_route()(ITEM, {'uid': 'owner'})
            self.assertEqual(failure.exception.status_code, 503)

    async def test_foreign_identifier_has_explicit_conflict_status(self):
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Database())}), patch.object(persistence, 'create_owned_wardrobe_item', side_effect=persistence.WardrobeOwnershipConflict()):
            with self.assertRaises(HTTPException) as failure:
                await load_route()(ITEM, {'uid': 'owner'})
            self.assertEqual(failure.exception.status_code, 409)


if __name__ == '__main__':
    unittest.main()
