"""Paid flat-lay HTTP admission with real auth and reservation code, no cloud."""
import copy
import os
import sys
import unittest
from types import ModuleType
from unittest.mock import Mock, call, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.auth import verified_user
from src.services import flatlay_lifecycle as lifecycle
from test_flatlay_lifecycle import Database, transactional


class FlatlayRequestAuthTests(unittest.TestCase):
    UID = "firebaseUser_A7x42"
    TOKEN = "firebase-signed-token"
    PATH = "/api/outfits/look/flat-lay-request"

    @classmethod
    def setUpClass(cls):
        # Import the router exported by the canonical package, not a copied
        # handler or an AST reconstruction. No auth dependency is overridden.
        from src.routes.outfits import router
        cls.app = FastAPI()
        cls.app.include_router(router, prefix="/api/outfits")
        cls.client = TestClient(cls.app)
        cls.addClassCleanup(cls.client.close)

    def setUp(self):
        self.assertEqual(self.app.dependency_overrides, {})
        environment = patch.dict(os.environ)
        environment.start()
        self.addCleanup(environment.stop)
        os.environ.pop("EASYOUTFIT_FLATLAY_REQUESTS_PAUSED", None)

        self.db = Database()
        self.db.records["users"][self.UID] = self.db.records["users"].pop("owner")
        self.db.records["users"][self.UID]["quotas"]["lastRefillAt"] = lifecycle._now()
        self.db.records["outfits"]["look"]["user_id"] = self.UID
        self.db.records["wardrobe"]["shirt"]["userId"] = self.UID
        self.db.records["wardrobe"]["pants"]["user_id"] = self.UID
        self.db.collection = Mock(wraps=self.db.collection)
        self.db.transaction = Mock(wraps=self.db.transaction)

        firebase = ModuleType("src.config.firebase")
        firebase.db, firebase.firebase_initialized = self.db, True
        for replacement in (
            patch.dict(sys.modules, {"src.config.firebase": firebase}),
            patch.object(lifecycle.firestore, "transactional", transactional),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)
        self.verifier = self.enterContext(patch.object(
            verified_user.auth, "verify_id_token",
            return_value={"uid": self.UID, "firebase": {"sign_in_provider": "password"}},
        ))
        self.reserve = self.enterContext(patch.object(
            lifecycle, "reserve_request", wraps=lifecycle.reserve_request,
        ))
        self.before = copy.deepcopy(self.db.records)

    def post(self, authorization="Bearer " + TOKEN, *, headers=None, **kwargs):
        request_headers = dict(headers or {})
        if authorization is not None:
            request_headers["Authorization"] = authorization
        return self.client.post(self.PATH, headers=request_headers, **kwargs)

    def assert_no_admission(self):
        self.reserve.assert_not_called()
        self.db.collection.assert_not_called()
        self.db.transaction.assert_not_called()
        self.assertEqual(self.db.records, self.before)

    def test_exported_router_has_one_post_with_strict_identity_dependency(self):
        from src.routes.outfits.routes import request_outfit_flat_lay
        routes = [route for route in self.app.routes
                  if getattr(route, "path", None) == "/api/outfits/{outfit_id}/flat-lay-request"
                  and "POST" in getattr(route, "methods", set())]
        self.assertEqual(len(routes), 1)
        self.assertIs(routes[0].endpoint, request_outfit_flat_lay)
        self.assertEqual([dependency.call for dependency in routes[0].dependant.dependencies],
                         [verified_user.verified_user_id])

    def test_missing_malformed_and_literal_test_headers_never_verify_or_reserve(self):
        for header in (None, "", "Basic token", "Bearer", "Bearer one two", "Bearer test", "bEaReR TeSt"):
            with self.subTest(header=header):
                response = self.post(header)
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response.json(), {"detail": "A valid sign-in is required"})
                self.verifier.assert_not_called()
                self.assert_no_admission()

    def test_test_token_has_no_bypass_and_requires_revocation_verification(self):
        self.verifier.side_effect = verified_user.auth.InvalidIdTokenError("private token failure")
        response = self.post("Bearer test-token")
        self.assertEqual(response.status_code, 401)
        self.verifier.assert_called_once_with("test-token", check_revoked=True)
        self.assertNotIn("private", response.text)
        self.assert_no_admission()

    def test_invalid_expired_revoked_disabled_and_deleted_users_never_reserve(self):
        auth = verified_user.auth
        failures = (
            auth.InvalidIdTokenError("private invalid token"),
            auth.ExpiredIdTokenError("private expired token", cause=None),
            auth.RevokedIdTokenError("private revoked token"),
            auth.UserDisabledError("private disabled user"),
            auth.UserNotFoundError("private deleted user"),
            ValueError("private malformed token"),
        )
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                self.verifier.reset_mock()
                self.verifier.side_effect = failure
                response = self.post()
                self.assertEqual(response.status_code, 401)
                self.verifier.assert_called_once_with(self.TOKEN, check_revoked=True)
                self.assertNotIn("private", response.text)
                self.assert_no_admission()

    def test_anonymous_identity_cannot_reserve(self):
        self.verifier.return_value = {"uid": self.UID, "firebase": {"sign_in_provider": "anonymous"}}
        self.assertEqual(self.post().status_code, 403)
        self.verifier.assert_called_once_with(self.TOKEN, check_revoked=True)
        self.assert_no_admission()

    def test_missing_or_malformed_verified_uid_cannot_reserve(self):
        claims_cases = (None, [], "claims", {}, {"uid": None}, {"uid": ""}, {"uid": "  "},
                        {"uid": 17}, {"uid": True}, {"uid": []}, {"uid": {"id": self.UID}})
        for claims in claims_cases:
            with self.subTest(claims=claims):
                self.verifier.reset_mock()
                self.verifier.return_value = claims
                self.assertEqual(self.post().status_code, 401)
                self.verifier.assert_called_once_with(self.TOKEN, check_revoked=True)
                self.assert_no_admission()

    def test_unavailable_verification_returns_safe_503_without_debit(self):
        self.verifier.side_effect = RuntimeError("private credential or transport details")
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Sign-in verification is temporarily unavailable"})
        self.verifier.assert_called_once_with(self.TOKEN, check_revoked=True)
        self.assert_no_admission()

    def test_verified_non_uuid_owner_reserves_once_and_replays_exact_contract(self):
        # Caller identity hints cannot replace the verified identity. The route
        # has no body/query/header identity parameters and ignores these hints.
        first = self.post(
            headers={"X-User-ID": "foreign", "X-Firebase-UID": "foreign"},
            params={"userId": "foreign", "user_id": "foreign", "firebase_uid": "foreign"},
            json={"userId": "foreign", "user_id": "foreign", "firebase_uid": "foreign"},
        )
        self.assertEqual(first.status_code, 200)
        data = first.json()
        self.assertTrue(data["success"])
        self.assertEqual((data["id"], data["outfit_id"]), ("look", "look"))
        self.assertEqual((data["flat_lay_status"], data["credit_status"]), ("pending", "reserved"))
        self.assertTrue(data["request_id"])
        self.assertIsNone(data["flat_lay_url"])
        self.assertIsNone(data["flat_lay_error"])
        request = self.db.records[lifecycle.REQUESTS_COLLECTION]["look"]
        self.assertEqual(request["user_id"], self.UID)
        self.assertEqual(request["request_id"], data["request_id"])
        self.assertIsNone(request.get("provider_admitted_at"))
        quota = self.db.records["users"][self.UID]["quotas"]
        self.assertEqual(quota["flatlaysRemaining"], 6)
        self.assertEqual(quota["lastRefillAt"], self.before["users"][self.UID]["quotas"]["lastRefillAt"])
        after_first = copy.deepcopy(self.db.records)
        second = self.post(json={"request_id": "caller-cannot-replace-existing-request"})
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json(), data)
        self.assertEqual(self.db.records, after_first)
        self.assertEqual(self.verifier.call_args_list, [call(self.TOKEN, check_revoked=True)] * 2)
        self.assertEqual(self.reserve.call_args_list, [call(self.db, "look", self.UID)] * 2)

    def test_foreign_verified_user_cannot_spoof_owner_with_identity_hints(self):
        self.verifier.return_value = {"uid": "foreign"}
        response = self.post(
            headers={"X-User-ID": self.UID, "X-Firebase-UID": self.UID},
            params={"userId": self.UID, "user_id": self.UID, "firebase_uid": self.UID},
            json={"userId": self.UID, "user_id": self.UID, "firebase_uid": self.UID},
        )
        self.assertEqual(response.status_code, 403)
        self.verifier.assert_called_once_with(self.TOKEN, check_revoked=True)
        self.reserve.assert_called_once_with(self.db, "look", "foreign")
        self.assertEqual(self.db.records, self.before)

    def test_stored_outfit_and_garment_ownership_conflicts_prevent_debit(self):
        for collection, item_id, alias, expected in (
            ("outfits", "look", "userId", 403),
            ("wardrobe", "shirt", "user_id", 422),
        ):
            with self.subTest(collection=collection):
                self.db.records = copy.deepcopy(self.before)
                self.db.records[collection][item_id][alias] = "foreign"
                before_conflict = copy.deepcopy(self.db.records)
                self.assertEqual(self.post().status_code, expected)
                self.assertEqual(self.db.records, before_conflict)
                self.assertNotIn(lifecycle.REQUESTS_COLLECTION, self.db.records)

    def test_pause_returns_503_after_auth_and_before_storage_or_reservation(self):
        with patch.dict(os.environ, {"EASYOUTFIT_FLATLAY_REQUESTS_PAUSED": "true"}), \
                patch.dict(sys.modules, {"src.config.firebase": None}):
            response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["retry-after"], "60")
        self.assertIn("No credit was used", response.json()["detail"])
        self.verifier.assert_called_once_with(self.TOKEN, check_revoked=True)
        self.assert_no_admission()


if __name__ == "__main__":
    unittest.main()
