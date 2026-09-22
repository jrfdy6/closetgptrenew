"""Credential-free HTTP coverage of the real retry route and app registration."""

import ast
import importlib
from pathlib import Path
from types import ModuleType
import traceback
import unittest
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from firebase_admin import auth

from src.routes import garment_processing as route


class RetryError(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code, self.detail = status_code, detail


def module(name, **values):
    result = ModuleType(name)
    vars(result).update(values)
    return result


def registered_app():
    """Exercise the real registry and mounting function, without booting AI SDKs.

    app.py also boots every unrelated service and debug route. Extract only its
    unchanged registration machinery, then import our actual route via it. A
    missing/wrong registry entry or swallowed import failure therefore fails the
    route lookup and HTTP assertions, rather than passing with a test-only mount.
    """
    source = Path(__file__).resolve().parents[1] / "app.py"
    tree = ast.parse(source.read_text())
    nodes = [node for node in tree.body if (
        isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "ROUTERS" for target in node.targets
        )
    ) or (isinstance(node, ast.FunctionDef) and node.name == "include_router_safe")]
    namespace = {
        "app": FastAPI(), "importlib": importlib, "traceback": traceback,
        "ROUTER_DEBUG": False,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
    registrations = [entry for entry in namespace["ROUTERS"] if entry[0] == "src.routes.garment_processing"]
    assert registrations == [("src.routes.garment_processing", "/api/wardrobe")]
    namespace["include_router_safe"](*registrations[0])
    return namespace["app"]


class GarmentRetryApiTests(unittest.TestCase):
    def setUp(self):
        self.database = object()
        self.retry = Mock(return_value={
            "success": True, "garment_id": "shirt-1", "status": "pending",
            "generation_id": "replacement-run", "attempt_count": 0, "idempotent": False,
        })
        collaborators = {
            "src.config.firebase": module("src.config.firebase", db=self.database),
            "src.services.garment_lifecycle": module(
                "src.services.garment_lifecycle", GarmentRetryError=RetryError, retry_garment=self.retry,
            ),
        }
        modules_patch = patch.dict("sys.modules", collaborators)
        modules_patch.start()
        self.addCleanup(modules_patch.stop)
        auth_patch = patch('src.auth.verified_user.auth.verify_id_token', return_value={"uid": "verified-owner"})
        self.verify = auth_patch.start()
        self.addCleanup(auth_patch.stop)
        self.client = TestClient(registered_app())

    def post(self, *, token="real-token", body=None, item_id="shirt-1"):
        headers = {} if token is None else {"Authorization": f"Bearer {token}"}
        return self.client.post(
            f"/api/wardrobe/{item_id}/retry-processing", headers=headers,
            json={"expected_attempt_id": "failed-attempt-3"} if body is None else body,
        )

    def test_actual_app_registry_exposes_exact_post_route(self):
        matches = [r for r in self.client.app.routes if r.path == "/api/wardrobe/{item_id}/retry-processing"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].methods, {"POST"})
        self.assertEqual(matches[0].endpoint, route.retry_garment_processing)

    def test_verified_identity_and_exact_failed_attempt_are_the_only_authorities(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.retry.return_value)
        self.verify.assert_called_once_with("real-token", check_revoked=True)
        self.retry.assert_called_once_with(self.database, "shirt-1", "verified-owner", "failed-attempt-3")

    def test_missing_malformed_and_test_token_never_reach_storage(self):
        for header in (None, "", "Basic abc", "Bearer", "Bearer a b", "Bearer test", "Bearer TEST"):
            with self.subTest(header=header):
                headers = {} if header is None else {"Authorization": header}
                response = self.client.post("/api/wardrobe/shirt-1/retry-processing", headers=headers,
                                            json={"expected_attempt_id": "failed-attempt-3"})
                self.assertEqual(response.status_code, 401)
        self.verify.assert_not_called()
        self.retry.assert_not_called()

    def test_invalid_expired_revoked_and_disabled_tokens_rejected(self):
        failures = [auth.InvalidIdTokenError("invalid"), auth.ExpiredIdTokenError("expired", ValueError()),
                    auth.RevokedIdTokenError("revoked"),
                    auth.UserDisabledError("disabled"), ValueError("bad token")]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                self.verify.side_effect = failure
                response = self.post()
                self.assertEqual(response.status_code, 401)
                self.assertNotIn(str(failure), response.text)
        self.retry.assert_not_called()

    def test_verification_outage_fails_closed_without_storage(self):
        self.verify.side_effect = RuntimeError("private provider error")
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private provider error", response.text)
        self.retry.assert_not_called()

    def test_missing_or_invalid_verified_uid_rejected(self):
        for claims in ({}, {"uid": None}, {"uid": ""}, {"uid": " "}, {"uid": 42}, {"userId": "body-owner"}):
            with self.subTest(claims=claims):
                self.verify.return_value = claims
                self.assertEqual(self.post().status_code, 401)
        self.retry.assert_not_called()

    def test_client_cannot_supply_owner_status_or_attempt_count(self):
        for field in ("userId", "user_id", "processing_status", "processing_attempts", "retryable"):
            with self.subTest(field=field):
                response = self.post(body={"expected_attempt_id": "failed-attempt-3", field: "spoofed"})
                self.assertEqual(response.status_code, 422)
        self.retry.assert_not_called()

    def test_spoofed_identity_headers_and_query_are_rejected_before_retry(self):
        for suffix, headers in (
            ('?userId=other', {}), ('?user_id=other', {}), ('?firebase_uid=other', {}),
            ('', {'X-User-ID': 'other'}), ('', {'X-Firebase-UID': 'other'}),
        ):
            response = self.client.post('/api/wardrobe/shirt-1/retry-processing' + suffix,
                                        headers={'Authorization': 'Bearer real-token', **headers},
                                        json={'expected_attempt_id': 'failed-attempt-3'})
            self.assertEqual(response.status_code, 403)
        self.retry.assert_not_called()

    def test_missing_empty_or_nonstring_failed_attempt_rejected(self):
        for body in ({}, {"expected_attempt_id": ""}, {"expected_attempt_id": " "},
                     {"expected_attempt_id": None}, {"expected_attempt_id": 4},
                     {"expected_attempt_id": "a" * 257}):
            with self.subTest(body=body):
                self.assertEqual(self.post(body=body).status_code, 422)
        self.retry.assert_not_called()

    def test_duplicate_ack_returns_persisted_state_without_invented_reset(self):
        first = self.post()
        # The transaction may already have been claimed before a lost-response
        # retry. The HTTP boundary must preserve the service's actual state.
        self.retry.return_value = {
            "success": True, "garment_id": "shirt-1", "status": "processing",
            "generation_id": "replacement-run", "attempt_count": 1, "idempotent": True,
        }
        duplicate = self.post()
        self.assertEqual(first.status_code, 200)
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(duplicate.json(), self.retry.return_value)
        self.assertEqual(self.retry.call_count, 2)
        self.assertEqual(self.retry.call_args_list[0], self.retry.call_args_list[1])

    def test_missing_or_other_owned_item_returns_same_hidden_404(self):
        for reason in ("missing", "different owner", "conflicting ownership"):
            with self.subTest(reason=reason):
                self.retry.side_effect = RetryError(404, "Garment not found")
                response = self.post()
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {"detail": "Garment not found"})

    def test_stale_attempt_and_nonterminal_item_cannot_start_new_run(self):
        for detail in ("Processing attempt changed", "Garment processing is not retryable"):
            with self.subTest(detail=detail):
                self.retry.side_effect = RetryError(409, detail)
                response = self.post()
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response.json(), {"detail": detail})

    def test_database_failure_is_503_without_false_success_or_internal_error(self):
        self.retry.side_effect = RuntimeError("private storage error")
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private storage error", response.text)
        self.assertNotIn("success", response.json())

    def test_unavailable_database_is_503_without_calling_retry(self):
        with patch.dict("sys.modules", {"src.config.firebase": module("src.config.firebase", db=None)}):
            response = self.post()
        self.assertEqual(response.status_code, 503)
        self.retry.assert_not_called()


if __name__ == "__main__":
    unittest.main()
