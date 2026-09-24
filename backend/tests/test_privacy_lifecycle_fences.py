"""Epoch changes fence paid image work, publication, and raw uploads."""
from copy import deepcopy
import unittest
from unittest.mock import patch

import test_flatlay_lifecycle as flatlay_tests
import test_garment_lifecycle as garment_tests
import test_image_upload_original_contract as upload_tests
from src.services.app_data_privacy import AppDataDeletionError


class ImagePrivacyFenceTests(unittest.TestCase):
    def test_garment_delete_blocks_claim_original_result_recovery_and_retry(self):
        lifecycle = garment_tests.lifecycle
        db = garment_tests.Database()
        with patch.object(lifecycle.firestore, 'transactional', garment_tests.transactional):
            job = lifecycle.claim_garment(db, 'shirt', 'worker', now=100)
            self.assertEqual(job['app_data_epoch'], 0)
            db.records['users']['owner'].update(app_data_epoch=1, app_data_deletion={'status': 'pending'})
            before = deepcopy(db.records)
            self.assertIsNone(lifecycle.claim_garment(db, 'shirt', 'worker', now=101))
            self.assertFalse(lifecycle.publish_original(db, 'shirt', job['attempt_id'], {
                'originalStoragePath': f"items/shirt/attempts/{job['attempt_id']}/original.png", 'originalUrl': 'https://assets.test/original'}, now=102))
            self.assertFalse(lifecycle.finish_garment(db, 'shirt', job['attempt_id'], error_code='processing_failed', now=103))
            lifecycle.recover_expired_garments(db, now=600)
            with self.assertRaises(lifecycle.GarmentRetryError):
                lifecycle.retry_garment(db, 'shirt', 'owner', job['attempt_id'], now=104)
            self.assertEqual(before, db.records)
            # Completion of erasure does not make a pre-clear worker valid again.
            db.records['users']['owner']['app_data_deletion']['status'] = 'complete'
            self.assertFalse(lifecycle.finish_garment(db, 'shirt', job['attempt_id'], error_code='processing_failed', now=105))

    def test_every_legacy_owner_alias_supports_garment_processing_and_flatlays(self):
        for alias in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId'):
            with self.subTest(alias=alias):
                db = garment_tests.Database()
                item = db.records['wardrobe']['shirt']
                item.pop('userId')
                item[alias] = 'owner'
                with patch.object(garment_tests.lifecycle.firestore, 'transactional', garment_tests.transactional):
                    job = garment_tests.lifecycle.claim_garment(db, 'shirt', 'worker', now=100)
                self.assertEqual(job['user_id'], 'owner')
                db = flatlay_tests.Database()
                for item in db.records['wardrobe'].values():
                    item.pop('userId', None)
                    item.pop('user_id', None)
                    item[alias] = 'owner'
                with patch.object(flatlay_tests.lifecycle.firestore, 'transactional', flatlay_tests.transactional):
                    self.assertEqual(flatlay_tests.lifecycle.reserve_request(db, 'look', 'owner', now=1100)['flat_lay_status'], 'pending')

    def test_any_conflicting_or_empty_owner_alias_blocks_garment_and_flatlay_work(self):
        for alias in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId'):
            for invalid in ('other', '', False, 123):
                with self.subTest(alias=alias, invalid=invalid):
                    item = {'userId': 'owner', 'user_id': 'owner', 'imageUrl': 'https://assets.test/a', alias: invalid}
                    self.assertIsNone(garment_tests.lifecycle._owner(item))
                    self.assertFalse(flatlay_tests.lifecycle._available_garment(item, 'owner'))

    def test_deleted_outfit_or_clearing_user_cannot_reserve_a_credit(self):
        lifecycle = flatlay_tests.lifecycle
        for field in ('deleted', 'deletedAt', 'isDeleted', 'account'):
            db = flatlay_tests.Database()
            if field == 'account':
                db.records['users']['owner']['app_data_deletion'] = {'status': 'failed'}
            else:
                db.records['outfits']['look'][field] = True
            before = deepcopy(db.records)
            with patch.object(lifecycle.firestore, 'transactional', flatlay_tests.transactional):
                with self.assertRaises(lifecycle.FlatlayRequestError):
                    lifecycle.reserve_request(db, 'look', 'owner', now=1100)
            self.assertEqual(before, db.records)

    def test_flatlay_reservation_retry_cannot_capture_post_clear_epoch(self):
        lifecycle = flatlay_tests.lifecycle
        db = flatlay_tests.Database()
        def retry_after_clear(callback):
            def run(txn):
                callback(txn)
                db.records['users']['owner']['app_data_epoch'] = 1
                return callback(flatlay_tests.Transaction(db))
            return run
        with patch.object(lifecycle.firestore, 'transactional', retry_after_clear):
            with self.assertRaises(lifecycle.FlatlayRequestError) as error:
                lifecycle.reserve_request(db, 'look', 'owner', now=1100)
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)
        self.assertNotIn('flat_lay_requests', db.records)

    def test_late_flatlay_result_refunds_once_without_publishing_after_clear(self):
        lifecycle = flatlay_tests.lifecycle
        db = flatlay_tests.Database()
        with patch.object(lifecycle.firestore, 'transactional', flatlay_tests.transactional):
            reserved = lifecycle.reserve_request(db, 'look', 'owner', now=1100)
            request = lifecycle.claim_request(db, 'look', now=1110)
            self.assertEqual(request['app_data_epoch'], 0)
            db.records['users']['owner'].update(app_data_epoch=1, app_data_deletion={'status': 'pending'})
            outfit = deepcopy(db.records['outfits']['look'])
            self.assertFalse(lifecycle.admit_provider_request(db, 'look', reserved['request_id'], [], now=1111))
            self.assertTrue(lifecycle.finish_request(db, 'look', reserved['request_id'], url='https://assets.test/late.png', now=1112))
            self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)
            self.assertEqual(db.records['outfits']['look'], outfit)
            self.assertEqual(db.records['flat_lay_requests']['look']['error_code'], 'app_data_deleted')
            self.assertFalse(lifecycle.finish_request(db, 'look', reserved['request_id'], url='https://assets.test/late.png', now=1113))
            self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)

    def test_soft_deleted_outfit_cannot_receive_completion_projection(self):
        lifecycle = flatlay_tests.lifecycle
        db = flatlay_tests.Database()
        with patch.object(lifecycle.firestore, 'transactional', flatlay_tests.transactional):
            reserved = lifecycle.reserve_request(db, 'look', 'owner', now=1100)
            db.records['outfits']['look']['deleted'] = True
            outfit = deepcopy(db.records['outfits']['look'])
            result = lifecycle.claim_request(db, 'look', now=1110)
            self.assertEqual(result['preflight_error'], 'outfit_unavailable')
            lifecycle.finish_request(db, 'look', reserved['request_id'], url='https://assets.test/late.png', now=1111)
            self.assertEqual(db.records['outfits']['look'], outfit)
            self.assertEqual(db.records['users']['owner']['quotas']['flatlaysRemaining'], 7)


class RawUploadPrivacyTests(upload_tests.OriginalUploadContractTests):
    def test_clear_during_upload_deletes_just_uploaded_generation_and_returns_409(self):
        self.privacy.side_effect = [0, 0, AppDataDeletionError(409, 'Data changed')]
        response = self.upload()
        self.assertEqual(response.status_code, 409)
        self.blob.delete.assert_called_once_with(if_generation_match=self.blob.generation)
        self.blob.make_public.assert_not_called()
        self.assertNotIn('image_url', response.json())

    def test_clear_before_upload_never_touches_storage(self):
        self.privacy.side_effect = AppDataDeletionError(409, 'Data clearing')
        self.assertEqual(self.upload().status_code, 409)
        self.storage.assert_not_called()


if __name__ == '__main__':
    unittest.main()
