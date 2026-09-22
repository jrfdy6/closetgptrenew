"""Saved result reads through the real projection and decorated HTTP route."""
import ast
import copy
import logging
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from src.auth import verified_user
from src.services import saved_outfit as saved
from src.services.flatlay_lifecycle import _source_fingerprint
from test_outfit_wear import Database, transactional


class SavedOutfitFixture(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        # Any new write during a supposedly read-only detail call fails.
        self.db.fail_at_write = 0
        self.garments = [self.garment("dress", "dress"), self.garment("shoes", "shoes")]
        for item in self.garments:
            self.db.seed("wardrobe", item["id"], item)
        self.db.seed("outfits", "look", {
            "name": "Saved dinner look", "user_id": "owner", "items": ["dress", {"id": "shoes"}],
            "style": "Minimalist", "occasion": "Dinner", "mood": "Relaxed",
            "weather": {"temperature": 72, "condition": "Unknown", "source": "estimate", "fallback": True},
            "outfitAnalysis": {"styleSynergy": "Your graphic shoes make this a partial Minimalist match."},
            "wearCount": 3, "lastWorn": 1790118000000,
            "lastWearDate": "2026-09-22", "lastWearTimezone": "America/New_York",
            "private_debug": "do-not-expose", "metadata": {"internal_provider_trace": "do-not-expose"},
        })
        decorator = patch.object(saved.firestore, "transactional", transactional)
        decorator.start()
        self.addCleanup(decorator.stop)

    @staticmethod
    def garment(item_id, kind):
        return {
            "id": item_id, "userId": "owner", "name": "Current " + item_id, "type": kind,
            "color": "navy", "imageUrl": "https://example.test/current-" + item_id + ".jpg",
            "originalStoragePath": "private/original-" + item_id, "private_analysis": "do-not-expose",
        }

    @property
    def outfit(self):
        return self.db.rows["outfits"]["look"]

    def ledger(self, **updates):
        value = {
            "user_id": "owner", "outfit_id": "look", "request_id": "request-123",
            "status": "done", "credit_status": "consumed", "url": "https://example.test/verified-flatlay.png",
            "items": [{"id": item["id"], "referenceSourceFingerprint": _source_fingerprint(item)} for item in self.garments],
            "provider_payload": "do-not-expose", **updates,
        }
        self.db.seed("flat_lay_requests", "look", value)
        return value

    def read(self):
        return saved.read_saved_outfit(self.db, "look", "owner")


class SavedOutfitProjectionTests(SavedOutfitFixture):
    def test_repeated_detail_reads_preserve_config_weather_notes_wear_and_never_write(self):
        before, versions = copy.deepcopy(self.db.rows), copy.deepcopy(self.db.versions)
        first = self.read()
        for _ in range(3):
            self.assertEqual(self.read(), first)
        self.assertEqual(self.db.rows, before)
        self.assertEqual(self.db.versions, versions)
        for key in ("style", "occasion", "mood", "weather", "outfitAnalysis", "wearCount", "lastWorn", "lastWearDate", "lastWearTimezone"):
            self.assertEqual(first[key], self.outfit[key])
        self.assertNotIn("private_debug", first)
        self.assertNotIn("internal_provider_trace", first["metadata"])
        self.assertEqual(first["flat_lay_status"], "awaiting_consent")
        self.assertTrue(first["flat_lay_request_allowed"])
        self.assertIsNone(first["flat_lay_url"])

    def test_owned_string_dictionary_and_legacy_item_aliases_resolve_current_allowlisted_garments(self):
        for items in (["dress", "shoes"], [{"id": "dress"}, {"id": "shoes"}],
                      [{"itemId": "dress"}, {"item_id": "shoes"}]):
            with self.subTest(items=items):
                self.outfit["items"] = items
                result = self.read()
                self.assertEqual([item["name"] for item in result["items"]], ["Current dress", "Current shoes"])
                self.assertTrue(result["items_available"])
                for item in result["items"]:
                    self.assertNotIn("private_analysis", item)
                    self.assertNotIn("originalStoragePath", item)
                    self.assertNotIn("userId", item)

    def test_current_owned_metadata_overrides_saved_snapshot(self):
        self.outfit["items"] = [{"id": "dress", "name": "Old dress", "color": "red", "imageUrl": "https://example.test/old.jpg"}, "shoes"]
        item = self.read()["items"][0]
        self.assertEqual((item["name"], item["color"], item["imageUrl"]),
                         ("Current dress", "navy", "https://example.test/current-dress.jpg"))

    def test_missing_current_photo_never_resurrects_any_snapshot_image_alias(self):
        image_fields = ("imageUrl", "image_url", "originalImageUrl", "originalUrl", "thumbnailUrl",
                        "backgroundRemovedUrl", "processedUrl", "flat_lay_url", "flatLayUrl")
        snapshot = {"id": "dress", "name": "Saved dress name", "type": "dress",
                    **{field: "https://obsolete.test/" + field + ".jpg" for field in image_fields}}
        self.outfit["items"] = [snapshot, "shoes"]
        current = self.db.rows["wardrobe"]["dress"]
        current.pop("imageUrl")
        current.pop("name")
        current.pop("type")
        result = self.read()
        item = result["items"][0]
        self.assertEqual((item["name"], item["type"]), ("Saved dress name", "dress"))
        for field in image_fields:
            self.assertNotIn(field, item)
        self.assertNotIn("obsolete.test", str(result))
        # An explicitly cleared canonical URL also cannot expose a different
        # stale alias from the outfit's historical item snapshot.
        self.db.rows["wardrobe"]["dress"]["imageUrl"] = ""
        result = self.read()
        self.assertEqual(result["items"][0]["imageUrl"], "")
        self.assertNotIn("obsolete.test", str(result))

    def test_foreign_missing_deleted_and_conflicting_garments_are_placeholders_without_snapshot_leaks(self):
        self.outfit["items"] = [{"id": "dress", "name": "Private snapshot name", "imageUrl": "https://private.test/old.jpg"}, "shoes"]
        original = copy.deepcopy(self.db.rows["wardrobe"]["dress"])
        for updates in (None, {"userId": "foreign"}, {"userId": "owner", "user_id": "foreign"}, {"deleted": True}):
            with self.subTest(updates=updates):
                if updates is None:
                    self.db.rows["wardrobe"].pop("dress", None)
                else:
                    self.db.rows["wardrobe"]["dress"] = {**original, **updates}
                result = self.read()
                self.assertEqual(result["items"][0], {
                    "id": "dress", "name": "Unavailable piece", "type": "", "color": "", "unavailable": True,
                })
                self.assertFalse(result["items_available"])
                self.assertNotIn("Private snapshot", str(result))
                self.assertNotIn("private.test", str(result))

    def test_unowned_missing_and_conflicting_outfits_are_hidden(self):
        for updates in ({"user_id": "foreign"}, {"user_id": "owner", "userId": "foreign"}, {"user_id": None}):
            with self.subTest(updates=updates):
                original = copy.deepcopy(self.outfit)
                self.outfit.update(updates)
                with self.assertRaises(saved.SavedOutfitNotFound):
                    self.read()
                self.db.rows["outfits"]["look"] = original
        for outfit_id in ("missing", "", "bad/id"):
            with self.assertRaises(saved.SavedOutfitNotFound):
                saved.read_saved_outfit(self.db, outfit_id, "owner")

    def test_legacy_owner_alias_is_read_without_migration(self):
        self.outfit.pop("user_id")
        self.outfit["userId"] = "owner"
        self.assertEqual(self.read()["user_id"], "owner")
        self.assertNotIn("user_id", self.outfit)

    def test_canonical_favorite_false_overrides_legacy_true_and_alias_survives_reload(self):
        self.outfit["favorite"] = True
        self.assertTrue(self.read()["isFavorite"])
        self.outfit["isFavorite"] = False
        self.assertFalse(self.read()["isFavorite"])
        self.outfit["isFavorite"] = True
        self.assertTrue(self.read()["isFavorite"])

    def test_text_only_user_feedback_survives_reload_without_rating(self):
        self.outfit.update(userFeedback="Please use softer colors next time", feedback="Older text")
        self.assertEqual(self.read()["feedback"], "Please use softer colors next time")
        self.assertNotIn("rating", self.read())
        self.outfit["userFeedback"] = ""
        self.assertEqual(self.read()["feedback"], "")
        self.outfit.pop("userFeedback")
        self.assertEqual(self.read()["feedback"], "Older text")

    def test_only_matching_owned_completed_ledger_releases_its_image(self):
        self.outfit.update(flatLayUrl="https://stale.test/alias.png", flat_lay_url="https://stale.test/other.png")
        self.outfit["metadata"]["flat_lay_url"] = "https://stale.test/metadata.png"
        self.ledger()
        result = self.read()
        self.assertEqual(result["flat_lay_url"], "https://example.test/verified-flatlay.png")
        self.assertEqual(result["flatLayUrl"], result["flat_lay_url"])
        self.assertEqual(result["flat_lay_request_id"], "request-123")
        self.assertEqual(result["flat_lay_credit_status"], "consumed")
        self.assertFalse(result["flat_lay_request_allowed"])
        self.assertNotIn("stale.test", str(result))
        self.assertNotIn("provider_payload", str(result))

    def test_pending_processing_and_unknown_request_status_hold_without_exposing_url(self):
        for status in ("pending", "processing", "unknown", "queued"):
            with self.subTest(status=status):
                self.ledger(status=status, credit_status="reserved", retryable=True)
                result = self.read()
                self.assertIsNone(result["flat_lay_url"])
                self.assertEqual(result["flat_lay_request_id"], "request-123")
                self.assertFalse(result["flat_lay_request_allowed"])

    def test_legacy_public_aliases_cannot_publish_images_or_start_duplicate_work(self):
        for location, key, value in (("root", "flatLayUrl", "https://old.test/p.png"),
                                     ("root", "flat_lay_url", "https://old.test/p.png"),
                                     ("metadata", "flatLayUrl", "https://old.test/p.png"),
                                     ("metadata", "flat_lay_url", "https://old.test/p.png"),
                                     ("root", "flatLayStatus", "pending"),
                                     ("metadata", "flat_lay_status", "done")):
            with self.subTest(location=location, key=key):
                target = self.outfit if location == "root" else self.outfit["metadata"]
                target[key] = value
                result = self.read()
                self.assertIsNone(result["flat_lay_url"])
                self.assertFalse(result["flat_lay_request_allowed"])
                self.assertEqual(result["flat_lay_error_code"], "legacy_request_needs_review")
                target.pop(key)

    def test_old_private_ledger_without_source_fingerprints_holds_even_with_matching_ids(self):
        self.ledger(items=[{"id": "dress"}, {"id": "shoes"}])
        result = self.read()
        self.assertIsNone(result["flat_lay_url"])
        self.assertFalse(result["flat_lay_request_allowed"])
        self.assertEqual(result["flat_lay_error_code"], "preview_identity_unavailable")

    def test_changed_source_hides_completed_image_and_offers_only_explicit_new_request(self):
        self.ledger()
        self.db.rows["wardrobe"]["dress"]["imageUrl"] = "https://example.test/replaced-photo.jpg"
        result = self.read()
        self.assertIsNone(result["flat_lay_url"])
        self.assertEqual(result["flat_lay_status"], "awaiting_consent")
        self.assertTrue(result["flat_lay_request_allowed"])
        self.assertEqual(result["flat_lay_error_code"], "outfit_changed")

    def test_changed_item_set_hides_completed_image(self):
        self.ledger()
        replacement = self.garment("shirt", "shirt")
        self.db.seed("wardrobe", "shirt", replacement)
        self.outfit["items"] = ["shirt", "shoes"]
        result = self.read()
        self.assertIsNone(result["flat_lay_url"])
        self.assertEqual(result["flat_lay_error_code"], "outfit_changed")

    def test_source_change_during_pending_request_stays_held_until_settlement(self):
        self.ledger(status="processing", credit_status="reserved")
        self.db.rows["wardrobe"]["dress"]["imageUrl"] = "https://example.test/new-photo.jpg"
        result = self.read()
        self.assertEqual(result["flat_lay_status"], "processing")
        self.assertIsNone(result["flat_lay_url"])
        self.assertFalse(result["flat_lay_request_allowed"])
        self.assertEqual(result["flat_lay_error_code"], "outfit_changed")

    def test_foreign_ledger_does_not_leak_url_request_identity_or_error(self):
        for updates in ({"user_id": "foreign"}, {"outfit_id": "foreign-look"}):
            with self.subTest(updates=updates):
                self.ledger(**updates, error="private provider details")
                result = self.read()
                self.assertIsNone(result["flat_lay_url"])
                self.assertIsNone(result["flat_lay_request_id"])
                self.assertFalse(result["flat_lay_request_allowed"])
                self.assertNotIn("private provider details", str(result))
                self.assertEqual(result["flat_lay_error_code"], "preview_identity_unavailable")

    def test_unknown_provider_outcomes_never_offer_retry_even_if_credit_refunded(self):
        for code in ("provider_outcome_unknown", "worker_outcome_unknown"):
            with self.subTest(code=code):
                self.ledger(status="failed", error_code=code, retryable=True, credit_status="refunded")
                result = self.read()
                self.assertFalse(result["flat_lay_request_allowed"])
                self.assertFalse(result["flat_lay_retryable"])
                self.assertIsNone(result["flat_lay_url"])

    def test_retryable_failure_requires_refunded_credit_before_explicit_retry(self):
        for credit, allowed in (("reserved", False), ("refund_needs_review", False), ("refunded", True)):
            with self.subTest(credit=credit):
                self.ledger(status="failed", error_code="preparation_failed", retryable=True, credit_status=credit)
                result = self.read()
                self.assertEqual(result["flat_lay_request_allowed"], allowed)
                self.assertIsNone(result["flat_lay_url"])

    def test_transaction_rechecks_replaced_source_before_releasing_a_completed_image(self):
        self.ledger()
        def replace_photo(db):
            db.seed("wardrobe", "dress", {**db.rows["wardrobe"]["dress"], "imageUrl": "https://example.test/new.jpg"})
        self.db.before_commit = replace_photo
        result = self.read()
        self.assertEqual(self.db.conflicts, 1)
        self.assertIsNone(result["flat_lay_url"])
        self.assertEqual(result["flat_lay_error_code"], "outfit_changed")


def actual_saved_outfit_app():
    path = Path(__file__).resolve().parents[1] / "src/routes/outfits/routes.py"
    tree = ast.parse(path.read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "get_saved_outfit"]
    assert len(nodes) == 1
    namespace = {
        "__package__": "src.routes.outfits", "router": APIRouter(), "Depends": Depends,
        "HTTPException": HTTPException, "JSONResponse": JSONResponse,
        "verified_user_id": verified_user.verified_user_id,
        "logger": logging.getLogger("saved-outfit-api-tests"),
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    registry_tree = ast.parse((path.parents[3] / "app.py").read_text())
    registry = next(node for node in registry_tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "ROUTERS" for target in node.targets))
    prefix = dict(ast.literal_eval(registry.value))["src.routes.outfits"]
    assert "from .routes import router" in (path.parent / "__init__.py").read_text()
    app = FastAPI()
    app.include_router(namespace["router"], prefix=prefix)
    return app, nodes[0], tree


class SavedOutfitApiTests(SavedOutfitFixture):
    def setUp(self):
        super().setUp()
        firebase = ModuleType("src.config.firebase")
        firebase.db = self.db
        modules = patch.dict("sys.modules", {"src.config.firebase": firebase})
        modules.start()
        self.addCleanup(modules.stop)
        auth = patch.object(verified_user.auth, "verify_id_token", return_value={"uid": "owner"})
        self.verify = auth.start()
        self.addCleanup(auth.stop)
        self.app, self.route_node, self.route_tree = actual_saved_outfit_app()
        self.client = TestClient(self.app)

    def get(self, outfit_id="look", token="real-token"):
        headers = {} if token is None else {"Authorization": "Bearer " + token}
        return self.client.get("/api/outfits/" + outfit_id, headers=headers)

    def test_registered_detail_route_is_get_only_and_follows_fixed_routes(self):
        routes = [route for route in self.app.routes if route.path == "/api/outfits/{outfit_id}"]
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0].methods, {"GET"})
        for node in self.route_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute)
                            and decorator.func.attr == "get" and decorator.args
                            and isinstance(decorator.args[0], ast.Constant)
                            and decorator.args[0].value in ("/stats", "/analytics/worn-this-week")):
                        self.assertLess(node.lineno, self.route_node.lineno)

    def test_http_detail_is_private_no_store_read_only_and_json_serializable(self):
        self.outfit["createdAt"] = datetime(2026, 9, 22, tzinfo=timezone.utc)
        before = copy.deepcopy(self.db.rows)
        response = self.get()
        self.assertEqual(response.status_code, 200, response.text)
        self.verify.assert_called_once_with("real-token", check_revoked=True)
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        self.assertEqual(response.json()["id"], "look")
        self.assertEqual(response.json()["createdAt"], "2026-09-22T00:00:00+00:00")
        self.assertEqual(self.db.rows, before)

    def test_http_reload_reads_the_same_result_without_side_effects(self):
        self.ledger(status="processing", credit_status="reserved")
        first = self.get()
        self.assertEqual(first.status_code, 200)
        for _ in range(3):
            self.assertEqual(self.get().json(), first.json())
        self.assertNotIn("outfit_wear_receipts", self.db.rows)
        self.assertNotIn("outfit_history", self.db.rows)

    def test_missing_and_foreign_detail_have_identical_hidden_404(self):
        missing = self.get("missing")
        self.outfit["user_id"] = "foreign"
        foreign = self.get()
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(foreign.status_code, 404)
        self.assertEqual(missing.json(), foreign.json())
        self.assertEqual(missing.json(), {"detail": "Outfit not found"})

    def test_every_owned_soft_delete_marker_returns_hidden_404(self):
        for field, value in (("deleted", True), ("isDeleted", True),
                             ("deletedAt", 1790118000000), ("deleted_at", "2026-09-22T16:00:00Z")):
            with self.subTest(field=field):
                self.outfit[field] = value
                response = self.get()
                self.assertEqual(response.status_code, 404, response.text)
                self.assertEqual(response.json(), {"detail": "Outfit not found"})
                self.outfit.pop(field)

    def test_missing_fake_expired_revoked_and_unverifiable_auth_fail_closed(self):
        for token in (None, "", "test", "TEST", "two words"):
            self.assertEqual(self.get(token=token).status_code, 401)
        self.verify.assert_not_called()
        for error in (verified_user.auth.InvalidIdTokenError("private invalid"),
                      verified_user.auth.ExpiredIdTokenError("private expired", ValueError()),
                      verified_user.auth.RevokedIdTokenError("private revoked")):
            self.verify.side_effect = error
            response = self.get()
            self.assertEqual(response.status_code, 401)
            self.assertNotIn("private", response.text)
        self.verify.side_effect = RuntimeError("private verification failure")
        response = self.get()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private", response.text)

    def test_storage_error_and_unavailable_database_return_503_without_false_empty_success(self):
        self.db.fail_read = True
        response = self.get()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private read failure", response.text)
        self.assertNotIn("items", response.json())
        firebase = ModuleType("src.config.firebase")
        firebase.db = None
        with patch.dict("sys.modules", {"src.config.firebase": firebase}):
            self.assertEqual(self.get().status_code, 503)


if __name__ == "__main__":
    unittest.main()
