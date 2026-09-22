"""Actual HTTP boundary + optimistic transaction doubles; no cloud credentials."""
import ast
import asyncio
import copy
import functools
import logging
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict, Optional
from unittest.mock import Mock, patch

from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

from src.auth import verified_user
from src.services import outfit_wear as wear


class Conflict(Exception):
    pass


class Snapshot:
    def __init__(self, data):
        self.exists, self.data = data is not None, copy.deepcopy(data)

    def to_dict(self):
        return copy.deepcopy(self.data)


class Document:
    def __init__(self, db, collection, item_id):
        self.db, self.collection, self.id = db, collection, item_id
        self.path = (collection, item_id)

    def get(self, transaction):
        if transaction.writes:
            raise AssertionError("Read after write violates Firestore transaction ordering")
        with self.db.lock:
            if self.db.fail_read:
                raise RuntimeError("private read failure")
            transaction.versions[self.path] = self.db.versions.get(self.path, 0)
            return Snapshot(self.db.rows.get(self.collection, {}).get(self.id))


class Collection:
    def __init__(self, db, name):
        self.db, self.name = db, name

    def document(self, item_id):
        return Document(self.db, self.name, item_id)


class Transaction:
    def __init__(self, db):
        self.db, self.versions, self.writes = db, {}, []

    def set(self, reference, data):
        self.writes.append(("set", reference, copy.deepcopy(data)))

    def update(self, reference, data):
        self.writes.append(("update", reference, copy.deepcopy(data)))

    def commit(self):
        with self.db.lock:
            if any(self.db.versions.get(key, 0) != version for key, version in self.versions.items()):
                self.db.conflicts += 1
                raise Conflict()
            staged = copy.deepcopy(self.db.rows)
            for index, (kind, reference, data) in enumerate(self.writes):
                if index == self.db.fail_at_write:
                    raise RuntimeError("private partial commit failure")
                collection = staged.setdefault(reference.collection, {})
                if kind == "set":
                    collection[reference.id] = data
                else:
                    collection[reference.id].update(data)
            self.db.rows = staged
            for _, reference, _ in self.writes:
                self.db.versions[reference.path] = self.db.versions.get(reference.path, 0) + 1
            if self.writes and self.db.lose_ack:
                self.db.lose_ack = False
                raise RuntimeError("connection lost after atomic commit")


def transactional(fn):
    @functools.wraps(fn)
    def run(txn):
        for attempt in range(10):
            result = fn(txn)
            if attempt == 0 and txn.db.barrier:
                txn.db.barrier.wait(timeout=5)
            with txn.db.lock:
                hook, txn.db.before_commit = txn.db.before_commit, None
                if hook:
                    hook(txn.db)
            try:
                txn.commit()
                return result
            except Conflict:
                txn = Transaction(txn.db)
        raise AssertionError("Test transaction exhausted contention retries")
    return run


class Database:
    def __init__(self):
        self.rows, self.versions = {}, {}
        self.lock = threading.RLock()
        self.fail_read, self.lose_ack = False, False
        self.fail_at_write, self.before_commit, self.barrier = None, None, None
        self.conflicts = 0

    def collection(self, name):
        return Collection(self, name)

    def transaction(self):
        return Transaction(self)

    def seed(self, collection, key, value):
        self.rows.setdefault(collection, {})[key] = copy.deepcopy(value)
        self.versions[(collection, key)] = self.versions.get((collection, key), 0) + 1


class WearTestFixture(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.now = datetime(2026, 9, 22, 2, 30, tzinfo=timezone.utc)
        self.items = [self.garment("dress", "dress"), self.garment("shoes", "shoes")]
        for item in self.items:
            self.db.seed("wardrobe", item["id"], item)
        self.db.seed("outfits", "look", {
            "user_id": "owner", "name": "My saved look", "items": self.items,
            "wearCount": 4, "occasion": "Dinner", "mood": "Relaxed",
            "weather": {"temperature": 72, "source": "manual", "fallback": False},
        })
        decorator = patch.object(wear.firestore, "transactional", transactional)
        decorator.start()
        self.addCleanup(decorator.stop)

    @staticmethod
    def garment(item_id, kind):
        return {"id": item_id, "userId": "owner", "type": kind, "name": "Saved " + item_id,
                "imageUrl": "https://example.test/" + item_id, "wearCount": 6}

    def record(self, key="request-1", outfit_id="look", now=None, zone="America/New_York"):
        return wear.mark_outfit_worn(self.db, outfit_id, "owner", key, zone, now=now or self.now)


class OutfitWearTests(WearTestFixture):
    def test_two_piece_dress_and_shoes_commits_consistent_counts_history_and_receipts(self):
        result = self.record()
        self.assertEqual(result["wear_date"], "2026-09-21")
        self.assertEqual(result["wear_count"], 5)
        self.assertEqual(result["garment_wear_counts"], {"dress": 7, "shoes": 7})
        self.assertFalse(result["already_recorded"])
        self.assertEqual(len(self.db.rows[wear.RECEIPTS_COLLECTION]), 2)
        history = self.db.rows["outfit_history"][result["event_id"]]
        self.assertEqual(history["date_worn"], int(self.now.timestamp() * 1000))
        self.assertEqual(history["weather"], self.db.rows["outfits"]["look"]["weather"])
        self.assertEqual(history["occasion"], "Dinner")
        self.assertEqual({item["id"] for item in history["items"]}, {"dress", "shoes"})
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWearDate"], "2026-09-21")
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], result["last_worn"])
        self.assertEqual(set(self.db.rows), {"wardrobe", "outfits", "outfit_history", wear.RECEIPTS_COLLECTION})

    def test_repeated_key_and_new_key_same_day_share_one_event(self):
        first, retry, second_key = self.record(), self.record(), self.record("request-2")
        self.assertEqual({r["event_id"] for r in (first, retry, second_key)}, {first["event_id"]})
        self.assertTrue(retry["already_recorded"])
        self.assertTrue(second_key["already_recorded"])
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["wearCount"], 7)

    def test_same_key_replays_after_midnight_new_key_can_log_new_day(self):
        first = self.record()
        tomorrow = self.now + timedelta(days=1)
        retry = self.record(now=tomorrow)
        self.assertEqual(retry["event_id"], first["event_id"])
        self.assertEqual(retry["wear_date"], "2026-09-21")
        second = self.record("tomorrow-request", now=tomorrow)
        self.assertEqual(second["wear_date"], "2026-09-22")
        self.assertEqual(second["wear_count"], 6)
        self.assertEqual(len(self.db.rows["outfit_history"]), 2)

    def test_delayed_receipt_replays_original_event_but_current_counters(self):
        first = self.record()
        latest = self.record("next-day", now=self.now + timedelta(days=1))
        delayed = self.record()
        self.assertEqual(delayed["event_id"], first["event_id"])
        self.assertEqual(delayed["date_worn"], first["date_worn"])
        self.assertEqual(delayed["wear_date"], first["wear_date"])
        self.assertEqual(delayed["event_wear_count"], 5)
        self.assertEqual(delayed["event_garment_wear_counts"], {"dress": 7, "shoes": 7})
        self.assertEqual(delayed["wear_count"], 6)
        self.assertEqual(delayed["garment_wear_counts"], {"dress": 8, "shoes": 8})
        self.assertEqual(delayed["last_worn"], latest["last_worn"])
        self.assertEqual(delayed["last_wear_date"], latest["wear_date"])

    def test_default_utc_and_invalid_timezones(self):
        result = wear.mark_outfit_worn(self.db, "look", "owner", "utc-request", now=self.now)
        self.assertEqual((result["timezone"], result["wear_date"]), ("UTC", "2026-09-22"))
        for zone in ("Made/Up", "/etc/passwd", "", None):
            with self.subTest(zone=zone), self.assertRaises(wear.OutfitWearError) as caught:
                self.record(zone=zone)
            self.assertEqual(caught.exception.status_code, 422)

    def test_legacy_adapter_uses_owner_outfit_and_one_server_utc_day(self):
        self.db.seed("outfits", "other", self.db.rows["outfits"]["look"])
        first = wear.mark_legacy_outfit_worn(self.db, "look", "owner", now=self.now)
        retry = wear.mark_legacy_outfit_worn(self.db, "look", "owner", now=self.now + timedelta(hours=1))
        other = wear.mark_legacy_outfit_worn(self.db, "other", "owner", now=self.now)
        tomorrow = wear.mark_legacy_outfit_worn(self.db, "look", "owner", now=self.now + timedelta(days=1))
        self.assertEqual((first["timezone"], first["wear_date"]), ("UTC", "2026-09-22"))
        self.assertEqual(first["event_id"], retry["event_id"])
        self.assertTrue(retry["already_recorded"])
        self.assertNotEqual(first["event_id"], other["event_id"])
        self.assertEqual(tomorrow["wear_date"], "2026-09-23")
        self.assertEqual(tomorrow["wear_count"], 6)
        self.assertEqual(len(self.db.rows["outfit_history"]), 3)

    def test_same_key_cannot_be_reused_for_another_outfit(self):
        self.record()
        self.db.seed("outfits", "other", self.db.rows["outfits"]["look"])
        with self.assertRaises(wear.OutfitWearError) as caught:
            self.record(outfit_id="other")
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)

    def test_lost_acknowledgment_is_recovered_without_second_increment(self):
        self.db.lose_ack = True
        with self.assertRaises(RuntimeError):
            self.record()
        retry = self.record()
        self.assertTrue(retry["already_recorded"])
        self.assertEqual(retry["wear_count"], 5)
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["wearCount"], 7)

    def test_no_partial_state_at_each_possible_transaction_write_failure(self):
        before = copy.deepcopy(self.db.rows)
        # outfit + two garments + history + day receipt + key receipt
        for fail_at in range(6):
            self.db.fail_at_write = fail_at
            with self.subTest(fail_at=fail_at), self.assertRaises(RuntimeError):
                self.record()
            self.assertEqual(self.db.rows, before)
        self.db.fail_at_write = None
        self.assertEqual(self.record()["wear_count"], 5)

    def test_concurrent_same_day_keys_retry_to_one_event(self):
        self.db.barrier = threading.Barrier(8)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda index: self.record(f"request-{index}"), range(8)))
        self.assertGreater(self.db.conflicts, 0)
        self.assertEqual(sum(not result["already_recorded"] for result in results), 1)
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)
        self.assertEqual(self.db.rows["wardrobe"]["shoes"]["wearCount"], 7)

    def test_concurrent_different_looks_sharing_garments_increment_each_event_once(self):
        self.db.seed("outfits", "other", self.db.rows["outfits"]["look"])
        self.db.barrier = threading.Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda name: self.record("key-" + name, outfit_id=name), ("look", "other")))
        self.assertGreater(self.db.conflicts, 0)
        self.assertEqual(len(self.db.rows["outfit_history"]), 2)
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["wearCount"], 8)
        self.assertEqual([result["wear_count"] for result in results], [5, 5])

    def test_conflicting_ownership_on_retry_discards_all_first_attempt_writes(self):
        def change_owner(db):
            data = {**db.rows["wardrobe"]["shoes"], "userId": "other"}
            db.seed("wardrobe", "shoes", data)
        self.db.before_commit = change_owner
        with self.assertRaises(wear.OutfitWearError) as caught:
            self.record()
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.db.rows["outfits"]["look"]["wearCount"], 4)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_receipt_replay_survives_later_garment_deletion(self):
        first = self.record()
        del self.db.rows["wardrobe"]["dress"]
        replay = self.record()
        self.assertEqual(replay["event_id"], first["event_id"])
        self.assertEqual(replay["garment_wear_counts"], {"shoes": 7})
        self.assertEqual(replay["event_garment_wear_counts"], {"dress": 7, "shoes": 7})

    def test_missing_foreign_conflicting_and_deleted_outfit_are_hidden_404(self):
        for updates in ({"user_id": "foreign"}, {"user_id": "owner", "userId": "foreign"},
                        {"user_id": None}, {"deleted": True}):
            with self.subTest(updates=updates):
                old = copy.deepcopy(self.db.rows["outfits"]["look"])
                self.db.rows["outfits"]["look"].update(updates)
                with self.assertRaises(wear.OutfitWearError) as caught:
                    self.record()
                self.assertEqual((caught.exception.status_code, caught.exception.detail), (404, "Outfit not found"))
                self.db.rows["outfits"]["look"] = old
        with self.assertRaises(wear.OutfitWearError) as caught:
            self.record(outfit_id="missing")
        self.assertEqual(caught.exception.status_code, 404)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_legacy_owner_aliases_and_item_id_lists_remain_supported(self):
        self.db.rows["outfits"]["look"].update(user_id=None, userId="owner", items=["dress", "shoes"])
        self.db.rows["wardrobe"]["dress"].update(userId=None, user_id="owner")
        self.assertEqual(self.record()["wear_count"], 5)

    def test_invalid_missing_foreign_or_incomplete_garments_have_no_writes(self):
        original = copy.deepcopy(self.db.rows)
        cases = [[], ["dress"], ["dress", "dress", "shoes"], ["dress", "missing"], ["../dress", "shoes"],
                 [False, "shoes"], [{"type": "dress"}, "shoes"]]
        for items in cases:
            self.db.rows = copy.deepcopy(original)
            self.db.rows["outfits"]["look"]["items"] = items
            before = copy.deepcopy(self.db.rows)
            with self.subTest(items=items), self.assertRaises(wear.OutfitWearError):
                self.record()
            self.assertEqual(self.db.rows, before)
        for updates in ({"userId": "foreign"}, {"userId": "owner", "user_id": "foreign"},
                        {"imageUrl": ""}, {"type": "other"}, {"deleted": True}, {"wearCount": -1}):
            self.db.rows = copy.deepcopy(original)
            self.db.rows["wardrobe"]["dress"].update(updates)
            before = copy.deepcopy(self.db.rows)
            with self.subTest(updates=updates), self.assertRaises(wear.OutfitWearError):
                self.record()
            self.assertEqual(self.db.rows, before)


def actual_wear_app():
    """Compile the real decorated endpoint/model without booting unrelated AI SDKs."""
    path = Path(__file__).resolve().parents[1] / "src/routes/outfits/routes.py"
    nodes = [node for node in ast.parse(path.read_text()).body
             if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name in {"OutfitWearRequest", "mark_outfit_as_worn"}]
    namespace = {
        "__package__": "src.routes.outfits", "router": APIRouter(), "BaseModel": BaseModel,
        "ConfigDict": ConfigDict, "Field": Field, "Depends": Depends, "HTTPException": HTTPException,
        "Body": Body, "Request": Request, "Optional": Optional,
        "JSONResponse": JSONResponse, "verified_user_id": verified_user.verified_user_id,
        "logger": logging.getLogger("wear-api-test"),
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    registry_tree = ast.parse((path.parents[3] / "app.py").read_text())
    registry = next(node for node in registry_tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "ROUTERS" for target in node.targets))
    prefix = dict(ast.literal_eval(registry.value))["src.routes.outfits"]
    init = (path.parent / "__init__.py").read_text()
    assert "from .routes import router" in init
    app = FastAPI()
    app.include_router(namespace["router"], prefix=prefix)
    return app


class OutfitWearApiTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        firebase = ModuleType("src.config.firebase")
        firebase.db = self.db
        module_patch = patch.dict("sys.modules", {"src.config.firebase": firebase})
        module_patch.start()
        self.addCleanup(module_patch.stop)
        auth_patch = patch.object(verified_user.auth, "verify_id_token", return_value={"uid": "owner"})
        self.verify = auth_patch.start()
        self.addCleanup(auth_patch.stop)
        self.client = TestClient(actual_wear_app())

    def post(self, body=None, token="real-token", outfit_id="look"):
        headers = {} if token is None else {"Authorization": "Bearer " + token}
        return self.client.post("/api/outfits/" + outfit_id + "/worn", headers=headers,
                                json=body if body is not None else {"idempotency_key": "http-request", "timezone": "America/New_York"})

    def test_http_real_route_uses_strict_auth_and_transaction(self):
        response = self.post()
        self.assertEqual(response.status_code, 200, response.text)
        self.verify.assert_called_once_with("real-token", check_revoked=True)
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        self.assertEqual(response.json()["wear_count"], 5)
        self.assertEqual(self.post().json()["event_id"], response.json()["event_id"])
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)

    def test_http_old_client_omitted_body_uses_the_same_owned_transaction(self):
        headers = {"Authorization": "Bearer real-token"}
        self.db.lose_ack = True
        failed_ack = self.client.post("/api/outfits/look/worn", headers=headers)
        self.assertEqual(failed_ack.status_code, 503)
        retry = self.client.post("/api/outfits/look/worn", headers=headers)
        self.assertEqual(retry.status_code, 200, retry.text)
        self.assertEqual(retry.json()["timezone"], "UTC")
        self.assertEqual(retry.json()["wear_count"], 5)
        self.assertTrue(retry.json()["already_recorded"])
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["wearCount"], 7)
        self.assertEqual(self.client.post("/api/outfits/look/worn").status_code, 401)
        self.db.rows["outfits"]["look"]["user_id"] = "foreign"
        self.assertEqual(self.client.post("/api/outfits/look/worn", headers=headers).status_code, 404)

    def test_http_supplied_null_or_bad_key_does_not_use_legacy_adapter(self):
        for content in ("null", "{}", '{"idempotency_key":null}', '{"idempotency_key":""}',
                        '{"timezone":"UTC"}', " "):
            with self.subTest(content=content):
                response = self.client.post("/api/outfits/look/worn", content=content,
                                            headers={"Authorization": "Bearer real-token", "Content-Type": "application/json"})
                self.assertEqual(response.status_code, 422, response.text)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_http_missing_fake_or_revoked_auth_never_reads_or_writes(self):
        for token in (None, "", "test", "TEST", "with spaces"):
            self.assertEqual(self.post(token=token).status_code, 401)
        self.verify.assert_not_called()
        self.verify.side_effect = verified_user.auth.RevokedIdTokenError("private revoked reason")
        response = self.post()
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("private", response.text)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_http_verification_failure_fails_closed(self):
        self.verify.side_effect = RuntimeError("private verification failure")
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_http_invalid_verified_uid_rejected(self):
        for claims in ({}, {"uid": ""}, {"uid": 4}, {"uid": None}, None):
            self.verify.return_value = claims
            self.assertEqual(self.post().status_code, 401)

    def test_http_rejects_missing_malformed_or_extra_authority(self):
        for body in ({}, {"idempotency_key": ""}, {"idempotency_key": " "}, {"idempotency_key": 5},
                     {"idempotency_key": "a" * 129}, {"idempotency_key": "bad/key"},
                     {"idempotency_key": "valid", "timezone": "Invalid/Zone"},
                     {"idempotency_key": "valid", "user_id": "other"},
                     {"idempotency_key": "valid", "wear_date": "2001-01-01"},
                     {"idempotency_key": "valid", "items": ["forged"]}):
            with self.subTest(body=body):
                response = self.post(body)
                self.assertEqual(response.status_code, 422, response.text)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_http_missing_foreign_and_invalid_garment_failures_preserved(self):
        self.assertEqual(self.post(outfit_id="missing").status_code, 404)
        self.db.rows["outfits"]["look"]["user_id"] = "foreign"
        self.assertEqual(self.post().status_code, 404)
        self.db.rows["outfits"]["look"]["user_id"] = "owner"
        self.db.rows["wardrobe"]["dress"]["userId"] = "foreign"
        self.assertEqual(self.post().status_code, 409)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_http_read_and_write_failure_are_visible_retryable_without_false_success(self):
        self.db.fail_read = True
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)
        self.assertNotIn("success", response.json())
        self.db.fail_read = False
        self.db.fail_at_write = 3
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("outfit_history", self.db.rows)
        self.assertEqual(self.db.rows["outfits"]["look"]["wearCount"], 4)

    def test_http_ambiguous_commit_response_can_retry_same_key(self):
        self.db.lose_ack = True
        self.assertEqual(self.post().status_code, 503)
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["already_recorded"])
        self.assertEqual(response.json()["wear_count"], 5)
        self.assertEqual(len(self.db.rows["outfit_history"]), 1)


class WearHistoryCompatibilityTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / "src/routes/outfit_history.py"
        selected = {"parse_last_worn", "calculate_worn_outfits_this_week", "update_outfit_history_entry", "delete_outfit_history_entry"}
        nodes = [node for node in ast.parse(path.read_text()).body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in selected]
        self.reference = Mock()
        self.reference.get.return_value = Snapshot({"user_id": "owner", "wear_operation_version": 1})
        self.database = Mock()
        self.database.collection.return_value.document.return_value = self.reference
        self.namespace = {
            "__package__": "src.routes", "router": APIRouter(), "Depends": Depends,
            "get_current_user": lambda: SimpleNamespace(id="owner"), "UserProfile": Any,
            "Dict": Dict, "Any": Any, "HTTPException": HTTPException,
            "datetime": datetime, "timedelta": timedelta, "timezone": timezone,
            "logger": logging.getLogger("history-compatibility"), "get_db": lambda: self.database,
        }
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), self.namespace)
        app = FastAPI()
        app.include_router(self.namespace["router"], prefix="/api/outfit-history")
        self.client = TestClient(app)

    def test_numeric_milliseconds_seconds_and_existing_dates_parse_as_utc(self):
        timestamp = datetime(2026, 9, 22, 16, tzinfo=timezone.utc)
        for value in (int(timestamp.timestamp() * 1000), timestamp.timestamp(), timestamp,
                      timestamp.isoformat(), "2026-09-22T16:00:00Z"):
            with self.subTest(value=value):
                self.assertEqual(self.namespace["parse_last_worn"](value), timestamp)
        for value in (float("nan"), float("inf"), True, "invalid"):
            self.assertIsNone(self.namespace["parse_last_worn"](value))

    def test_existing_week_reader_counts_numeric_new_events(self):
        recent = int(datetime.now(timezone.utc).timestamp() * 1000)
        doc = SimpleNamespace(id="wear-v1-event", to_dict=lambda: {"outfit_id": "look", "date_worn": recent})
        self.database.collection.return_value.where.return_value.stream.return_value = [doc]
        firebase = ModuleType("src.config.firebase")
        firebase.db = self.database
        with patch.dict("sys.modules", {"src.config.firebase": firebase}):
            self.assertEqual(asyncio.run(self.namespace["calculate_worn_outfits_this_week"]("owner")), 1)

    def test_managed_history_cannot_be_edited_or_deleted_through_legacy_api(self):
        for record, entry_id in (({"user_id": "owner", "wear_operation_version": 1}, "arbitrary"),
                                 ({"user_id": "owner"}, "wear-v1-event")):
            self.reference.get.return_value = Snapshot(record)
            for method in ("patch", "delete"):
                with self.subTest(method=method, entry_id=entry_id):
                    kwargs = {"json": {"notes": "changed"}} if method == "patch" else {}
                    response = getattr(self.client, method)("/api/outfit-history/" + entry_id, **kwargs)
                    self.assertEqual(response.status_code, 409, response.text)
        self.reference.update.assert_not_called()
        self.reference.delete.assert_not_called()

    def test_history_missing_or_foreign_errors_stay_errors_without_mutation(self):
        for record, expected in ((None, 404), ({"user_id": "foreign"}, 403)):
            self.reference.get.return_value = Snapshot(record)
            self.assertEqual(self.client.patch("/api/outfit-history/entry", json={}).status_code, expected)
            self.assertEqual(self.client.delete("/api/outfit-history/entry").status_code, expected)
        self.reference.update.assert_not_called()
        self.reference.delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
