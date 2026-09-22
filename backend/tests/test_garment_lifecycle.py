"""Credential-free tests of garment transactions, fences and finite retry runs."""
import copy
import functools
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch

from worker import garment_lifecycle as lifecycle


class Snapshot:
    def __init__(self, value):
        self.exists = value is not None
        self.value = copy.deepcopy(value)

    def to_dict(self):
        return copy.deepcopy(self.value)


class Document:
    def __init__(self, db, collection, key):
        self.db, self.collection, self.id = db, collection, key

    def get(self, transaction=None):
        if transaction and transaction.writes:
            raise AssertionError("Firestore cannot read after transaction writes")
        return Snapshot(self.db.records.get(self.collection, {}).get(self.id))


class Transaction:
    def __init__(self, db):
        self.db, self.writes = db, []

    def set(self, ref, fields):
        self.writes.append(("set", ref, copy.deepcopy(fields)))

    def update(self, ref, fields):
        self.writes.append(("update", ref, copy.deepcopy(fields)))

    def commit(self):
        if self.db.fail_commit:
            raise RuntimeError("simulated commit failure")
        for kind, ref, fields in self.writes:
            collection = self.db.records.setdefault(ref.collection, {})
            if kind == "set":
                collection[ref.id] = fields
            else:
                collection[ref.id].update(fields)


def transactional(fn):
    @functools.wraps(fn)
    def wrapped(txn):
        with txn.db.lock:
            result = fn(txn)
            if txn.db.before_retry:
                action, txn.db.before_retry = txn.db.before_retry, None
                action(txn.db)
                txn = Transaction(txn.db)
                result = fn(txn)
            txn.commit()
            return result
    return wrapped


class Collection:
    def __init__(self, db, name, filters=(), limit=None):
        self.db, self.name, self.filters, self.maximum = db, name, filters, limit

    def document(self, key):
        return Document(self.db, self.name, key)

    def where(self, *, filter):
        return Collection(self.db, self.name, (*self.filters, filter), self.maximum)

    def limit(self, limit):
        return Collection(self.db, self.name, self.filters, limit)

    def stream(self, *, timeout, retry):
        assert timeout == 10
        assert retry is None
        rows = sorted(self.db.records.get(self.name, {}).items())
        for query in self.filters:
            assert query.op_string == "<="
            rows = [(key, item) for key, item in rows if isinstance(item.get(query.field_path), (int, float))
                    and item[query.field_path] <= query.value]
        for key, item in rows[:self.maximum]:
            yield SimpleNamespace(id=key, to_dict=lambda item=item: copy.deepcopy(item))


class Database:
    def __init__(self):
        self.records = {"wardrobe": {"shirt": {
            "userId": "owner", "imageUrl": "https://example.test/my-shirt.jpg", "name": "Favorite shirt",
            "category": "Tops", "updatedAt": 50, "processing_status": "pending", "tags": ["work"],
        }}}
        self.lock = threading.RLock()
        self.fail_commit, self.before_retry = False, None

    def collection(self, name):
        return Collection(self, name)

    def transaction(self):
        return Transaction(self)


class GarmentLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.decorator = patch.object(lifecycle.firestore, "transactional", transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    @property
    def item(self):
        return self.db.records["wardrobe"]["shirt"]

    @property
    def job(self):
        return self.db.records[lifecycle.JOBS_COLLECTION]["shirt"]

    def claim(self, now=100):
        return lifecycle.claim_garment(self.db, "shirt", "worker-a", now=now)

    def original(self, job):
        return {"originalStoragePath": f"items/shirt/attempts/{job['attempt_id']}/original.png",
                "originalUrl": "https://assets.test/original.png"}

    def result(self, job):
        prefix = f"items/shirt/attempts/{job['attempt_id']}"
        return {
            "backgroundRemovedStoragePath": f"{prefix}/nobg.png", "backgroundRemovedUrl": "https://assets.test/nobg.png",
            "processedStoragePath": f"{prefix}/processed.png", "processedUrl": "https://assets.test/processed.png",
            "thumbnailStoragePath": f"{prefix}/thumbnail.png", "thumbnailUrl": "https://assets.test/thumbnail.png",
            "processing_mode": "alpha", "processing_time": 4.2, "original_size": "600x800", "processed_size": "300x400",
        }

    def fail(self, job, now=110, error="worker_crashed"):
        return lifecycle.finish_garment(self.db, "shirt", job["attempt_id"], error_code=error, now=now)

    def exhaust(self):
        for now in (100, 200, 400):
            job = self.claim(now)
            self.assertTrue(self.fail(job, now + 1))
        return job

    def test_claim_commits_attempt_before_work_and_returns_snapshot(self):
        original = copy.deepcopy(self.item)
        claimed = self.claim()
        self.assertEqual(claimed["attempt_count"], 1)
        self.assertEqual(claimed["expires_at"], 460)
        self.assertEqual(claimed["lease_expires_at"], 460)
        self.assertEqual(claimed["item"], original)
        self.assertEqual(self.item["processing_status"], "processing")
        self.assertEqual(self.job["attempt_id"], claimed["attempt_id"])
        self.assertEqual(self.job["attempts"][0]["status"], "processing")

    def test_duplicate_claims_only_one_attempt(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.claim(), range(20)))
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(self.job["attempt_count"], 1)

    def test_failed_commit_never_claims_or_mutates_projection(self):
        self.db.fail_commit = True
        with self.assertRaises(RuntimeError):
            self.claim()
        self.assertNotIn(lifecycle.JOBS_COLLECTION, self.db.records)
        self.assertEqual(self.item["processing_status"], "pending")

    def test_transaction_retry_commits_single_attempt_and_reloads_item(self):
        self.db.before_retry = lambda db: db.records["wardrobe"]["shirt"].update(name="Edited concurrently", updatedAt=60)
        claimed = self.claim()
        self.assertEqual(claimed["item"]["name"], "Edited concurrently")
        self.assertEqual(self.job["attempt_count"], 1)
        self.assertEqual(len(self.job["attempts"]), 1)

    def test_legacy_retry_count_is_adopted_once_and_public_reset_cannot_buy_attempts(self):
        self.item["processing_retry_count"] = 2
        claimed = self.claim()
        self.assertEqual(claimed["attempt_count"], 3)
        self.fail(claimed)
        self.item.update(processing_status="pending", processing_retry_count=0, processing_attempt_count=0)
        self.assertIsNone(self.claim(1000))
        self.assertEqual(self.job["attempt_count"], 3)
        self.assertEqual(self.item["processing_status"], "failed")

    def test_legacy_exhausted_or_malformed_count_stops_and_has_owned_retry_token(self):
        for value in (3, 50, "garbage"):
            with self.subTest(value=value):
                self.db = Database()
                self.item["processing_retry_count"] = value
                self.assertIsNone(self.claim())
                self.assertEqual(self.item["processing_status"], "failed")
                token = self.job["attempt_id"]
                self.assertTrue(token)
                self.assertTrue(lifecycle.retry_garment(self.db, "shirt", "owner", token, now=101)["success"])

    def test_new_job_requires_pending_and_real_owned_source(self):
        for updates in ({"processing_status": "codex_pending"}, {"processing_status": "done"},
                        {"imageUrl": None}, {"userId": None}, {"user_id": "other"}, {"deleted": True}):
            with self.subTest(updates=updates):
                self.db = Database()
                self.item.update(updates)
                self.assertIsNone(self.claim())
                if not updates.get("imageUrl", True):
                    self.assertEqual(self.job["status"], "failed")
                    self.assertEqual(self.item["processing_status"], "failed")
                else:
                    self.assertNotIn(lifecycle.JOBS_COLLECTION, self.db.records)

    def test_missing_photo_reports_visible_failure_without_fake_processing_attempts(self):
        self.item.pop("imageUrl")
        self.assertIsNone(self.claim())
        self.assertEqual(self.job["status"], "failed")
        self.assertEqual(self.job["attempt_count"], 0)
        self.assertEqual(self.item["processing_error_code"], "invalid_image")
        self.item.update(imageUrl="https://example.test/fixed.jpg", processing_status="pending")
        self.assertEqual(self.claim(101)["attempt_count"], 1)

    def test_unsafe_storage_identifier_becomes_visible_terminal_failure(self):
        self.db.records["wardrobe"]["old item id"] = copy.deepcopy(self.item)
        self.assertIsNone(lifecycle.claim_garment(self.db, "old item id", "worker-a", now=100))
        row = self.db.records["wardrobe"]["old item id"]
        self.assertEqual(row["processing_status"], "failed")
        self.assertEqual(row["processing_error_code"], "invalid_identifier")
        self.assertEqual(row["processing_retry_action"], "replace_item")
        self.assertFalse(row["processing_retryable"])
        self.assertEqual(row["imageUrl"], self.item["imageUrl"])

    def test_worker_progress_changes_do_not_invalidate_its_own_fence(self):
        claimed = self.claim()
        self.item["processing_arbitrary_progress"] = 95
        self.assertTrue(lifecycle.publish_original(self.db, "shirt", claimed["attempt_id"], self.original(claimed), now=101))
        self.assertTrue(lifecycle.finish_garment(self.db, "shirt", claimed["attempt_id"], result=self.result(claimed), now=102))
        self.assertEqual(self.item["processing_status"], "done")
        self.assertEqual(self.job["attempts"][0]["status"], "done")
        self.assertNotIn("lease_expires_at", self.job)

    def test_finish_preserves_original_source_and_all_user_fields(self):
        before = copy.deepcopy(self.item)
        claimed = self.claim()
        result = {**self.result(claimed), "userId": "thief", "name": "stale name", "imageUrl": "bad", "category": "bad", "tags": []}
        self.assertTrue(lifecycle.publish_original(self.db, "shirt", claimed["attempt_id"], self.original(claimed), now=101))
        self.assertTrue(lifecycle.finish_garment(self.db, "shirt", claimed["attempt_id"], result=result, now=102))
        for key in ("userId", "name", "imageUrl", "category", "updatedAt", "tags"):
            self.assertEqual(self.item[key], before[key])
        self.assertEqual(self.item["backgroundRemovedUrl"], result["backgroundRemovedUrl"])
        self.assertEqual(self.job["original"], self.original(claimed))
        self.assertEqual(self.item["processing_attempt_count"], 1)

    def test_failed_processing_keeps_published_original_and_existing_image(self):
        claimed = self.claim()
        lifecycle.publish_original(self.db, "shirt", claimed["attempt_id"], self.original(claimed), now=101)
        self.fail(claimed)
        self.assertEqual(self.item["imageUrl"], "https://example.test/my-shirt.jpg")
        self.assertEqual(self.item["originalUrl"], "https://assets.test/original.png")
        self.assertEqual(self.item["processing_status"], "pending")
        self.assertEqual(self.job["next_attempt_at"], 140)
        self.assertIsNone(self.claim(139))
        self.assertEqual(self.claim(140)["attempt_count"], 2)

    def test_published_original_provenance_survives_auto_retry_crash_before_republication(self):
        first = self.claim()
        original = self.original(first)
        lifecycle.publish_original(self.db, "shirt", first["attempt_id"], original, now=101)
        self.fail(first, now=102)
        second = self.claim(200)
        self.assertNotEqual(second["attempt_id"], first["attempt_id"])
        # Simulate a child crashing before it can read/upload/publish any photo.
        self.fail(second, now=201)
        self.assertEqual(self.job["original"], original)
        self.assertEqual(self.job["original_attempt_id"], first["attempt_id"])
        self.assertEqual(self.job["original_source_fingerprint"], first["source_fingerprint"])
        self.assertEqual(self.item["originalUrl"], original["originalUrl"])

    def test_explicit_retry_retains_valid_same_source_original_provenance(self):
        first = self.claim()
        original = self.original(first)
        lifecycle.publish_original(self.db, "shirt", first["attempt_id"], original, now=101)
        self.fail(first, now=102)
        for now in (200, 400):
            last = self.claim(now)
            self.fail(last, now=now + 1)
        self.item.update(name="Changed description", updatedAt=450)
        lifecycle.retry_garment(self.db, "shirt", "owner", last["attempt_id"], now=500)
        self.assertEqual(self.job["original"], original)
        self.assertEqual(self.job["original_attempt_id"], first["attempt_id"])
        self.assertEqual(self.job["original_source_fingerprint"], first["source_fingerprint"])
        retry = self.claim(501)
        self.assertNotEqual(retry["generation_id"], first["generation_id"])
        self.fail(retry, now=502)
        self.assertEqual(self.job["original"], original)

    def test_new_photo_clears_original_provenance_during_invalidation_and_new_claim(self):
        first = self.claim()
        lifecycle.publish_original(self.db, "shirt", first["attempt_id"], self.original(first), now=101)
        self.item.update(imageUrl="https://example.test/new-photo.jpg", updatedAt=102)
        self.assertFalse(self.fail(first, now=103))
        for key in ("original", "original_attempt_id", "original_source_fingerprint"):
            self.assertNotIn(key, self.job)
        second = self.claim(104)
        for key in ("original", "original_attempt_id", "original_source_fingerprint"):
            self.assertNotIn(key, second)
        lifecycle.publish_original(self.db, "shirt", second["attempt_id"], self.original(second), now=105)
        self.assertEqual(self.job["original_attempt_id"], second["attempt_id"])
        self.assertEqual(self.job["original_source_fingerprint"], second["source_fingerprint"])

    def test_owner_change_cannot_inherit_original_from_finished_or_processing_job(self):
        for done in (False, True):
            with self.subTest(done=done):
                self.db = Database()
                first = self.claim()
                lifecycle.publish_original(self.db, "shirt", first["attempt_id"], self.original(first), now=101)
                if done:
                    lifecycle.finish_garment(self.db, "shirt", first["attempt_id"], result=self.result(first), now=102)
                self.item.update(userId="other", processing_status="pending")
                self.assertIsNone(self.claim(103))
                for key in ("original", "original_attempt_id", "original_source_fingerprint"):
                    self.assertNotIn(key, self.job)

    def test_bounded_failure_after_three_attempts_and_restart(self):
        last = self.exhaust()
        self.assertEqual(self.job["status"], "failed")
        self.assertEqual(self.job["attempt_count"], 3)
        self.assertTrue(self.item["processing_retryable"])
        self.assertIsNone(self.claim(100000))
        self.assertFalse(self.fail(last, now=100000))
        self.assertEqual(len(self.job["attempts"]), 3)

    def test_expiry_recovers_after_restart_and_no_attempt_is_refunded(self):
        first = self.claim()
        self.assertEqual(lifecycle.recover_expired_garments(self.db, now=459)["examined"], 0)
        self.assertEqual(lifecycle.recover_expired_garments(self.db, now=460)["recovered"], 1)
        self.assertEqual(self.job["attempt_count"], 1)
        second = self.claim(490)
        self.assertEqual(second["attempt_count"], 2)
        self.assertNotEqual(first["attempt_id"], second["attempt_id"])
        self.assertFalse(lifecycle.finish_garment(self.db, "shirt", first["attempt_id"], result=self.result(first), now=491))
        self.assertEqual(self.job["attempt_id"], second["attempt_id"])

    def test_three_expired_leases_become_terminal_and_leave_scan(self):
        for start in (100, 500, 1000):
            self.claim(start)
            result = lifecycle.recover_expired_garments(self.db, now=start + 360)
        self.assertEqual(result["failed"], 1)
        self.assertEqual(self.job["status"], "failed")
        self.assertEqual(self.item["processing_status"], "failed")
        self.assertEqual(lifecycle.recover_expired_garments(self.db, now=9999)["examined"], 0)

    def test_finish_after_deadline_cannot_win_before_recovery_scan(self):
        first = self.claim()
        self.assertFalse(lifecycle.finish_garment(self.db, "shirt", first["attempt_id"], result=self.result(first), now=460))
        self.assertEqual(self.job["status"], "pending")
        self.assertEqual(self.job["error_code"], "worker_timeout")
        self.assertNotIn("backgroundRemovedUrl", self.item)

    def test_original_after_deadline_cannot_publish(self):
        first = self.claim()
        self.assertFalse(lifecycle.publish_original(self.db, "shirt", first["attempt_id"], self.original(first), now=460))
        self.assertNotIn("originalUrl", self.item)

    def test_source_change_fences_old_worker_and_gets_new_budget(self):
        old = self.exhaust()
        self.item.update(imageUrl="https://example.test/new-shirt.jpg", processing_status="pending")
        new = self.claim(1000)
        self.assertEqual(new["attempt_count"], 1)
        self.assertNotEqual(new["generation_id"], old["generation_id"])
        self.assertFalse(lifecycle.publish_original(self.db, "shirt", old["attempt_id"], self.original(old), now=1001))
        self.assertFalse(lifecycle.finish_garment(self.db, "shirt", old["attempt_id"], result=self.result(old), now=1001))
        self.assertEqual(self.job["attempt_id"], new["attempt_id"])

    def test_replacing_completed_photo_clears_old_assets_and_new_publication_is_not_self_fenced(self):
        first = self.claim()
        lifecycle.publish_original(self.db, "shirt", first["attempt_id"], self.original(first), now=101)
        lifecycle.finish_garment(self.db, "shirt", first["attempt_id"], result=self.result(first), now=102)
        self.item.update(imageUrl="https://example.test/new-photo.jpg", updatedAt=103, processing_status="pending",
                         background_removed_url="https://assets.test/old-cutout.png", thumbnail_url="https://assets.test/old-thumb.png")
        second = self.claim(104)
        self.assertEqual(second["item"]["imageUrl"], "https://example.test/new-photo.jpg")
        for key in ("backgroundRemovedUrl", "background_removed_url", "thumbnailUrl", "thumbnail_url",
                    "originalUrl", "originalStoragePath", "processedUrl"):
            self.assertIsNone(self.item[key])
        self.assertFalse(self.item["backgroundRemoved"])
        new_original = {**self.original(second), "originalUrl": "https://assets.test/new-original.png"}
        self.assertTrue(lifecycle.publish_original(self.db, "shirt", second["attempt_id"], new_original, now=105))
        self.assertTrue(self.fail(second, now=106))
        self.assertEqual(self.item["imageUrl"], "https://example.test/new-photo.jpg")
        self.assertEqual(self.item["originalUrl"], "https://assets.test/new-original.png")
        self.assertIsNone(self.item["backgroundRemovedUrl"])
        self.assertIsNone(self.item["thumbnailUrl"])
        third = self.claim(136)
        self.assertTrue(lifecycle.finish_garment(self.db, "shirt", third["attempt_id"], result=self.result(third), now=137))

    def test_source_invalidation_clears_old_assets_but_metadata_edit_keeps_same_photo_assets(self):
        for source_changed in (False, True):
            with self.subTest(source_changed=source_changed):
                self.db = Database()
                self.item.update(backgroundRemovedUrl="https://assets.test/existing-cutout.png",
                                 thumbnailUrl="https://assets.test/existing-thumb.png", backgroundRemoved=True)
                first = self.claim()
                lifecycle.publish_original(self.db, "shirt", first["attempt_id"], self.original(first), now=101)
                if source_changed:
                    self.item.update(imageUrl="https://example.test/replacement.jpg", updatedAt=102)
                else:
                    self.item.update(name="New description", updatedAt=102)
                self.assertFalse(self.fail(first, now=103))
                if source_changed:
                    self.assertIsNone(self.item["backgroundRemovedUrl"])
                    self.assertIsNone(self.item["thumbnailUrl"])
                    self.assertIsNone(self.item["originalUrl"])
                    self.assertFalse(self.item["backgroundRemoved"])
                    self.assertEqual(self.item["imageUrl"], "https://example.test/replacement.jpg")
                else:
                    self.assertEqual(self.item["backgroundRemovedUrl"], "https://assets.test/existing-cutout.png")
                    self.assertEqual(self.item["thumbnailUrl"], "https://assets.test/existing-thumb.png")
                    self.assertEqual(self.item["originalUrl"], self.original(first)["originalUrl"])
                    self.assertTrue(self.item["backgroundRemoved"])
                next_job = self.claim(134)
                self.assertTrue(lifecycle.publish_original(self.db, "shirt", next_job["attempt_id"], self.original(next_job), now=135))

    def test_metadata_edit_fences_result_without_resetting_attempt_budget(self):
        old = self.claim()
        self.item.update(name="My new name")  # Even without updatedAt.
        edited = copy.deepcopy(self.item)
        self.assertFalse(lifecycle.finish_garment(self.db, "shirt", old["attempt_id"], result=self.result(old), now=101))
        self.assertEqual(self.item["name"], edited["name"])
        self.assertEqual(self.item["updatedAt"], edited["updatedAt"])
        self.assertEqual(self.item["processing_status"], "pending")
        new = self.claim(131)
        self.assertEqual(new["attempt_count"], 2)
        self.assertEqual(new["generation_id"], old["generation_id"])
        self.assertTrue(lifecycle.finish_garment(self.db, "shirt", new["attempt_id"], result=self.result(new), now=132))
        self.assertEqual(self.item["name"], "My new name")

    def test_replacement_during_third_attempt_requeues_and_resets_only_new_photo_budget(self):
        for now in (100, 200):
            self.fail(self.claim(now), now + 1)
        old = self.claim(400)
        self.item.update(imageUrl="https://example.test/new-photo.jpg", updatedAt=401)
        self.assertFalse(self.fail(old, now=402))
        self.assertEqual(self.item["processing_status"], "pending")
        new = self.claim(403)
        self.assertEqual(new["attempt_count"], 1)
        self.assertNotEqual(new["generation_id"], old["generation_id"])

    def test_metadata_edit_on_third_attempt_is_terminal_without_another_automatic_run(self):
        for now in (100, 200):
            self.fail(self.claim(now), now + 1)
        old = self.claim(400)
        self.item["name"] = "New name"
        self.assertFalse(self.fail(old, now=402))
        self.assertEqual(self.item["processing_status"], "failed")
        self.assertIsNone(self.claim(99999))
        self.assertEqual(self.item["name"], "New name")

    def test_user_edit_during_original_publication_transaction_cannot_be_overwritten(self):
        job = self.claim()
        self.db.before_retry = lambda db: db.records["wardrobe"]["shirt"].update(updatedAt=101, imageUrl="https://example.test/new.jpg")
        self.assertFalse(lifecycle.publish_original(self.db, "shirt", job["attempt_id"], self.original(job), now=101))
        self.assertIsNone(self.item.get("originalUrl"))
        self.assertEqual(self.item["imageUrl"], "https://example.test/new.jpg")

    def test_owner_changes_conflicts_and_deletion_fence_finish_without_mutating_latest_item(self):
        for updates in ({"userId": "other"}, {"user_id": "other"}, {"deletedAt": 101}):
            with self.subTest(updates=updates):
                self.db = Database()
                job = self.claim()
                self.item.update(updates)
                edited = copy.deepcopy(self.item)
                self.assertFalse(lifecycle.finish_garment(self.db, "shirt", job["attempt_id"], result=self.result(job), now=102))
                self.assertEqual(self.item, edited)
                self.assertEqual(self.job["status"], "cancelled")
                self.assertIsNone(self.claim(1000))
        self.db = Database()
        job = self.claim()
        self.db.records["wardrobe"].pop("shirt")
        self.assertFalse(self.fail(job))
        self.assertNotIn("shirt", self.db.records["wardrobe"])

    def test_stale_worker_cannot_change_new_attempt_original_or_status(self):
        first = self.claim()
        self.fail(first)
        second = self.claim(200)
        second_original = {**self.original(second), "originalUrl": "https://assets.test/new-original.png"}
        lifecycle.publish_original(self.db, "shirt", second["attempt_id"], second_original, now=201)
        before = copy.deepcopy(self.item)
        self.assertFalse(lifecycle.publish_original(self.db, "shirt", first["attempt_id"], self.original(first), now=202))
        self.assertFalse(self.fail(first, 202))
        self.assertEqual(self.item, before)

    def test_unsafe_or_wrong_attempt_asset_paths_rejected(self):
        job = self.claim()
        for path in ("items/shirt/original.png", "items/other/attempts/x/original.png", "../original.png"):
            original = {**self.original(job), "originalStoragePath": path}
            self.assertFalse(lifecycle.publish_original(self.db, "shirt", job["attempt_id"], original, now=101))
        result = {**self.result(job), "thumbnailStoragePath": "items/shirt/thumbnail.png"}
        self.assertTrue(lifecycle.finish_garment(self.db, "shirt", job["attempt_id"], result=result, now=101))
        self.assertEqual(self.job["error_code"], "invalid_result")
        self.assertNotIn("thumbnailUrl", self.item)

    def test_error_text_is_sanitized_and_never_stores_tracebacks_or_provider_secrets(self):
        job = self.claim()
        self.fail(job, error="private key and stack trace")
        self.assertEqual(self.job["error_code"], "processing_failed")
        self.assertNotIn("private key", str(self.db.records))

    def test_owned_retry_is_finite_and_returns_truthful_idempotent_ack_after_claim(self):
        old = self.exhaust()
        result = lifecycle.retry_garment(self.db, "shirt", "owner", old["attempt_id"], now=500)
        self.assertFalse(result["idempotent"])
        self.assertEqual(self.job["manual_retry_count"], 1)
        duplicate = lifecycle.retry_garment(self.db, "shirt", "owner", old["attempt_id"], now=501)
        self.assertTrue(duplicate["idempotent"])
        self.assertEqual(result["generation_id"], duplicate["generation_id"])
        new = self.claim(502)
        self.assertEqual(new["attempt_count"], 1)
        duplicate = lifecycle.retry_garment(self.db, "shirt", "owner", old["attempt_id"], now=503)
        self.assertTrue(duplicate["idempotent"])
        self.assertEqual(duplicate["status"], "processing")
        self.assertEqual(duplicate["attempt_count"], 1)
        self.assertEqual(self.job["attempt_id"], new["attempt_id"])
        self.assertEqual(self.job["attempt_count"], 1)

    def test_lost_retry_ack_after_completed_and_failed_run_never_restarts_work(self):
        old = self.exhaust()
        lifecycle.retry_garment(self.db, "shirt", "owner", old["attempt_id"], now=500)
        for now in (501, 600, 800):
            self.fail(self.claim(now), now + 1)
        last_attempt = self.job["attempt_id"]
        reply = lifecycle.retry_garment(self.db, "shirt", "owner", old["attempt_id"], now=900)
        self.assertTrue(reply["idempotent"])
        self.assertEqual(reply["status"], "failed")
        self.assertEqual(reply["attempt_count"], 3)
        self.assertEqual(self.job["attempt_id"], last_attempt)
        fresh = lifecycle.retry_garment(self.db, "shirt", "owner", last_attempt, now=901)
        self.assertFalse(fresh["idempotent"])
        new = self.claim(902)
        lifecycle.finish_garment(self.db, "shirt", new["attempt_id"], result=self.result(new), now=903)
        reply = lifecycle.retry_garment(self.db, "shirt", "owner", last_attempt, now=904)
        self.assertTrue(reply["idempotent"])
        self.assertEqual(reply["status"], "done")
        self.assertEqual(self.job["attempt_count"], 1)

    def test_wrong_owner_missing_item_stale_token_and_active_job_cannot_retry(self):
        job = self.claim()
        for owner, token, expected in (("other", job["attempt_id"], 404), ("owner", "wrong", 409), ("owner", job["attempt_id"], 409)):
            with self.subTest(owner=owner, token=token):
                with self.assertRaises(lifecycle.GarmentRetryError) as error:
                    lifecycle.retry_garment(self.db, "shirt", owner, token, now=101)
                self.assertEqual(error.exception.status_code, expected)
        self.db.records["wardrobe"].pop("shirt")
        with self.assertRaises(lifecycle.GarmentRetryError) as error:
            lifecycle.retry_garment(self.db, "shirt", "owner", job["attempt_id"], now=101)
        self.assertEqual(error.exception.status_code, 404)

    def test_unavailable_pending_jobs_are_retired_and_cannot_saturate_due_queue(self):
        for mode in ("deleted_document", "deleted_field", "conflicting_owner", "new_owner"):
            with self.subTest(mode=mode):
                self.db = Database()
                job = self.claim()
                lifecycle.publish_original(self.db, "shirt", job["attempt_id"], self.original(job), now=101)
                self.fail(job, now=102)
                self.assertEqual(self.job["status"], "pending")
                if mode == "deleted_document":
                    self.db.records["wardrobe"].pop("shirt")
                elif mode == "deleted_field":
                    self.item["deleted"] = True
                elif mode == "conflicting_owner":
                    self.item["user_id"] = "other"
                else:
                    self.item["userId"] = "other"
                latest = copy.deepcopy(self.db.records["wardrobe"])
                self.assertIsNone(self.claim(200))
                self.assertEqual(self.job["status"], "cancelled")
                self.assertIsNone(self.job["next_attempt_at"])
                self.assertNotIn("lease_expires_at", self.job)
                self.assertEqual(self.db.records["wardrobe"], latest)
                self.assertIsNone(self.claim(201))
                self.assertIsNone(self.job["next_attempt_at"])

    def test_recovery_query_is_bounded_and_only_active_leases_remain(self):
        original = copy.deepcopy(self.item)
        for key in ("shirt", "shirt2", "shirt3"):
            if key != "shirt":
                self.db.records["wardrobe"][key] = copy.deepcopy(original)
            lifecycle.claim_garment(self.db, key, "worker-a", now=100)
        first = lifecycle.recover_expired_garments(self.db, now=500, limit=2)
        second = lifecycle.recover_expired_garments(self.db, now=500, limit=2)
        self.assertEqual(first["examined"], 2)
        self.assertEqual(second["examined"], 1)
        self.assertEqual(first["recovered"] + second["recovered"], 3)

    def test_recovery_does_not_overwrite_newer_user_edit_and_counts_deleted_job(self):
        self.claim()
        self.item.update(category="Outerwear", updatedAt=400)
        before = copy.deepcopy(self.item)
        self.assertEqual(lifecycle.recover_expired_garments(self.db, now=500)["recovered"], 1)
        self.assertEqual(self.item["category"], before["category"])
        self.assertEqual(self.item["updatedAt"], before["updatedAt"])
        self.assertEqual(self.item["processing_status"], "pending")
        self.claim(600)
        self.db.records["wardrobe"].pop("shirt")
        self.assertEqual(lifecycle.recover_expired_garments(self.db, now=1000)["cancelled"], 1)

    def test_done_job_does_not_reprocess_when_public_pending_is_forged(self):
        job = self.claim()
        lifecycle.finish_garment(self.db, "shirt", job["attempt_id"], result=self.result(job), now=101)
        self.item.update(processing_status="pending", processing_retry_count=0)
        self.assertIsNone(self.claim(102))
        self.assertEqual(self.item["processing_status"], "done")
        self.assertEqual(self.job["attempt_count"], 1)

    def test_fingerprint_binds_owner_and_photo_but_not_metadata_or_worker_original(self):
        fingerprint = lifecycle.garment_source_fingerprint(self.item)
        self.item.update(name="new", updatedAt=99, originalUrl="https://assets.test/one")
        self.assertEqual(lifecycle.garment_source_fingerprint(self.item), fingerprint)
        self.item["imageUrl"] = "https://assets.test/two"
        self.assertNotEqual(lifecycle.garment_source_fingerprint(self.item), fingerprint)


if __name__ == "__main__":
    unittest.main()
