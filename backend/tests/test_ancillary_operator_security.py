"""Real ancillary HTTP routes with fake storage/embeddings and no cloud access."""
from contextlib import ExitStack
import asyncio
import importlib.util
import os
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from firebase_admin import auth
from src.services import app_data_privacy as privacy
from test_app_data_privacy import Database, transactional


BACKEND = Path(__file__).resolve().parents[1]
HEADERS = {"Authorization": "Bearer signed-token"}
RAG_REQUESTS = (
    ("POST", "/api/ingest_drive", {"folder_id": "folder-1"}),
    ("POST", "/api/chat", {"query": "shirt"}),
    ("GET", "/api/knowledge/search?query=shirt", None),
    ("GET", "/api/knowledge/get?chunk_id=own", None),
)
UTILITY_PATHS = (
    "/api/image/create-firebase-bucket",
    "/api/image/test-firebase-upload",
    "/api/image/debug-firebase",
)


def load_route(name):
    spec = importlib.util.spec_from_file_location(
        f"src.routes.isolated_{name}", BACKEND / "src/routes" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def snapshot(key, data, exists=True):
    return SimpleNamespace(id=key, exists=exists, to_dict=lambda: data)


class AncillaryOperatorSecurityTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.dict(os.environ, {
            "EASYOUTFIT_OPERATOR_USER_IDS": " owner, second-operator ",
            "ENABLE_INTERNAL_DEBUG_ROUTES": "false",
        }))
        self.verify = self.stack.enter_context(patch(
            "src.auth.verified_user.auth.verify_id_token", return_value={"uid": "owner"}))
        self.rows = [
            snapshot("own", {"user_id": "owner", "text": "shirt own", "embedding": [1.0, 0.0]}),
            snapshot("foreign", {"user_id": "foreign", "text": "shirt foreign", "embedding": [1.0, 0.0]}),
            snapshot("legacy", {"text": "shirt unscoped", "embedding": [1.0, 0.0]}),
            snapshot("conflicting", {"user_id": "owner", "userId": "foreign", "text": "shirt conflict", "embedding": [1.0, 0.0]}),
        ]
        self.collection = Mock()
        self.collection.where.return_value = self.collection
        self.collection.limit.return_value = self.collection
        self.collection.stream.side_effect = lambda: iter(self.rows)
        self.collection.document.side_effect = lambda key: SimpleNamespace(get=lambda: next(
            (row for row in self.rows if row.id == key), snapshot(key, None, exists=False)))
        self.database = Mock()
        user_collection = SimpleNamespace(document=lambda key: SimpleNamespace(
            get=lambda **kwargs: snapshot(key, {"app_data_epoch": 0})))
        self.database.collection.side_effect = lambda name: user_collection if name == "users" else self.collection
        firebase = ModuleType("src.config.firebase")
        firebase.db = self.database
        firebase.firebase_initialized = True
        embedding = ModuleType("src.services.ai_runtime.embedding_runtime")
        embedding.generate_text_embedding = AsyncMock(return_value=[1.0, 0.0])
        self.stack.enter_context(patch.dict("sys.modules", {
            "src.config.firebase": firebase,
            "src.services.ai_runtime.embedding_runtime": embedding,
        }))
        self.knowledge = load_route("knowledge")
        self.ingest = load_route("rag_ingest")
        self.upload = load_route("image_upload_minimal")
        self.embed = embedding.generate_text_embedding
        self.real_background = self.ingest._ingest_drive_background_rag
        self.background = self.stack.enter_context(patch.object(
            self.ingest, "_ingest_drive_background_rag", new_callable=AsyncMock))
        self.storage = self.stack.enter_context(patch.object(self.upload.storage, "bucket"))
        self.gcs = self.stack.enter_context(patch("google.cloud.storage.Client"))
        app = FastAPI()
        app.include_router(self.knowledge.router, prefix="/api")
        app.include_router(self.ingest.router, prefix="/api")
        app.include_router(self.upload.router, prefix="/api/image")
        self.client = TestClient(app)

    def request_rag(self, request, headers=HEADERS):
        method, path, body = request
        return self.client.request(method, path, headers=headers, json=body)

    def assert_no_work(self):
        self.database.collection.assert_not_called()
        self.embed.assert_not_called()
        self.background.assert_not_called()
        self.storage.assert_not_called()
        self.gcs.assert_not_called()

    def test_all_rag_routes_require_real_bearer_authentication_before_work(self):
        for request in RAG_REQUESTS:
            for header in (None, "", "Basic token", "Bearer test", "Bearer TEST", "Bearer a b"):
                with self.subTest(path=request[1], header=header):
                    response = self.request_rag(request, {"Authorization": header} if header is not None else {})
                    self.assertEqual(response.status_code, 401, response.text)
        self.verify.assert_not_called()
        self.assert_no_work()

    def test_allowlist_is_default_deny_and_admin_claim_is_not_an_alternative(self):
        with patch.dict(os.environ, {"EASYOUTFIT_OPERATOR_USER_IDS": ""}):
            self.verify.return_value = {"uid": "owner", "admin": True}
            for request in RAG_REQUESTS:
                self.assertEqual(self.request_rag(request).status_code, 403)
        self.assert_no_work()

    def test_allowlist_matches_complete_uid_not_substring(self):
        self.verify.return_value = {"uid": "own"}
        for request in RAG_REQUESTS:
            self.assertEqual(self.request_rag(request).status_code, 403)
        self.assert_no_work()

    def test_revoked_disabled_invalid_and_verifier_outage_fail_closed(self):
        for error, status in (
            (auth.RevokedIdTokenError("private revoked"), 401),
            (auth.UserDisabledError("private disabled"), 401),
            (auth.InvalidIdTokenError("private invalid"), 401),
            (RuntimeError("private outage"), 503),
        ):
            self.verify.side_effect = error
            for request in RAG_REQUESTS:
                response = self.request_rag(request)
                self.assertEqual(response.status_code, status)
                self.assertNotIn(str(error), response.text)
        for call in self.verify.call_args_list:
            self.assertEqual(call.kwargs, {"check_revoked": True})
        self.assert_no_work()

    def test_anonymous_firebase_user_is_not_an_operator(self):
        self.verify.return_value = {"uid": "owner", "firebase": {"sign_in_provider": "anonymous"}}
        for request in RAG_REQUESTS:
            self.assertEqual(self.request_rag(request).status_code, 403)
        self.assert_no_work()

    def test_conflicting_header_or_query_identity_cannot_change_operator_scope(self):
        for request in RAG_REQUESTS:
            self.assertEqual(self.request_rag(request, {**HEADERS, "X-User-ID": "foreign"}).status_code, 403)
            method, path, body = request
            for alias in ("user_id", "userId", "firebase_uid", "uid"):
                separator = "&" if "?" in path else "?"
                scoped = (method, path + separator + alias + "=foreign", body)
                self.assertEqual(self.request_rag(scoped).status_code, 403)
        self.assert_no_work()

    def test_ingestion_uses_verified_uid_when_body_owner_is_omitted_or_matching(self):
        for extra in ({}, {"user_id": "owner"}):
            response = self.client.post("/api/ingest_drive", headers=HEADERS,
                                        json={"folder_id": "folder-1", **extra})
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["user_id"], "owner")
            self.assertEqual(response.headers["Cache-Control"], "private, no-store")
            self.background.assert_awaited_with("owner", "folder-1", 10, 0)

    def test_ingestion_rejects_spoofed_owner_and_unrecognized_identity_aliases(self):
        for alias in ("user_id", "userId", "uid", "firebase_uid"):
            response = self.client.post("/api/ingest_drive", headers=HEADERS,
                                        json={"folder_id": "folder-1", alias: "foreign"})
            self.assertEqual(response.status_code, 403 if alias == "user_id" else 422)
        self.assert_no_work()

    def test_ingested_chunks_and_job_receipt_persist_the_verified_owner(self):
        self.background.side_effect = self.real_background
        database = Database({'users/owner': {'app_data_epoch': 0}})
        with patch.object(self.ingest, 'db', database), \
                patch.object(privacy.firestore, 'transactional', transactional), \
                patch.object(self.ingest, "google_drive_ready", True), \
                patch.object(self.ingest, "_build_drive_service", return_value=object()), \
                patch.object(self.ingest, "_fallback_list_files_in_folder", return_value=[
                    {"id": "file-1", "name": "Style notes", "mimeType": "application/pdf"}]), \
                patch.object(self.ingest, "_fallback_extract_text", return_value="shirt wardrobe notes " * 5):
            response = self.client.post("/api/ingest_drive", headers=HEADERS, json={"folder_id": "folder-1"})
        self.assertEqual(response.status_code, 200)
        chunks = [value for path, value in database.rows.items() if path.startswith('knowledge_chunks/')]
        self.assertEqual(len(chunks), 1)
        stored = chunks[0]
        self.assertEqual(stored["user_id"], "owner")
        self.assertEqual(stored["file_id"], "file-1")
        self.assertEqual(stored['app_data_epoch'], 0)
        receipts = [value for path, value in database.rows.items() if path.startswith('ingest_jobs/')]
        self.assertEqual(len(receipts), 1)
        receipt = receipts[0]
        self.assertEqual(receipt["user_id"], "owner")
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["details"]["total_chunks"], 1)

    def test_ingestion_rejects_unbounded_work_and_folder_query_injection(self):
        for extra in ({"max_files": 0}, {"max_files": -1}, {"max_files": 101}, {"folder_id": "x' or trashed=true"}):
            response = self.client.post("/api/ingest_drive", headers=HEADERS,
                                        json={"folder_id": "folder-1", **extra})
            self.assertEqual(response.status_code, 422)
        self.assert_no_work()

    def test_ingestion_admission_rejects_missing_account_or_active_clear_before_queue(self):
        for user, status in ((None, 404), ({'app_data_epoch': 0, 'app_data_deletion': {'status': 'pending'}}, 409),
                             ({'app_data_epoch': 0, 'app_data_deletion': {'status': 'failed'}}, 409)):
            database = Database({'users/owner': user} if user is not None else {})
            with patch.object(self.ingest, 'db', database):
                response = self.client.post('/api/ingest_drive', headers=HEADERS, json={'folder_id': 'folder-1'})
            self.assertEqual(response.status_code, status)
        self.background.assert_not_called()
        self.embed.assert_not_called()

    def test_stale_background_ingestion_cannot_read_drive_or_write_a_failure_receipt(self):
        database = Database({'users/owner': {'app_data_epoch': 1}})
        with patch.object(self.ingest, 'db', database), \
                patch.object(privacy.firestore, 'transactional', transactional), \
                patch.object(self.ingest, '_build_drive_service') as drive:
            asyncio.run(self.real_background('owner', 'folder-1', 10, 0))
        drive.assert_not_called()
        self.embed.assert_not_called()
        self.assertEqual(set(database.rows), {'users/owner'})

    def test_data_clear_during_embedding_prevents_old_chunk_publication(self):
        database = Database({'users/owner': {'app_data_epoch': 0}})
        async def clear_during_embedding(*args, **kwargs):
            database.rows['users/owner']['app_data_epoch'] = 1
            return [1.0, 0.0]
        self.embed.side_effect = clear_during_embedding
        with patch.object(self.ingest, 'db', database), \
                patch.object(privacy.firestore, 'transactional', transactional):
            stored = asyncio.run(self.ingest._process_and_store_chunks(
                'owner', 'file-1', 'Style notes', 'folder-1', 'shirt wardrobe notes ' * 5, 'application/pdf', 0))
        self.assertEqual(stored, 0)
        self.assertEqual(set(database.rows), {'users/owner'})

    def test_embedding_retrieval_queries_owner_before_limit_and_never_returns_unscoped_or_foreign_chunks(self):
        response = self.client.post("/api/chat", headers=HEADERS, json={"query": "shirt"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([row["chunk_id"] for row in response.json()["chunks"]], ["own"])
        self.collection.where.assert_called_once_with("user_id", "==", "owner")
        self.collection.limit.assert_called_once_with(1000)
        self.assertEqual(response.headers["Cache-Control"], "private, no-store")

    def test_keyword_search_and_embedding_fallback_both_enforce_owner(self):
        self.embed.return_value = None
        for method, path, body in (
            ("GET", "/api/knowledge/search?query=shirt", None),
            ("POST", "/api/chat", {"query": "shirt"}),
        ):
            response = self.client.request(method, path, headers=HEADERS, json=body)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual([row["chunk_id"] for row in response.json()["chunks"]], ["own"])
        self.assertEqual(self.collection.where.call_count, 2)
        for call in self.collection.where.call_args_list:
            self.assertEqual(call.args, ("user_id", "==", "owner"))

    def test_direct_chunk_lookup_hides_foreign_missing_conflicting_and_unscoped_records(self):
        missing = None
        for key in ("foreign", "legacy", "conflicting", "missing"):
            response = self.client.get(f"/api/knowledge/get?chunk_id={key}", headers=HEADERS)
            self.assertEqual(response.status_code, 404)
            missing = missing or response.json()
            self.assertEqual(response.json(), missing)
        own = self.client.get("/api/knowledge/get?chunk_id=own", headers=HEADERS)
        self.assertEqual(own.status_code, 200)
        self.assertEqual(own.json()["text"], "shirt own")

    def test_direct_chunk_lookup_rejects_document_path_traversal(self):
        response = self.client.get("/api/knowledge/get", params={"chunk_id": "own/nested/foreign"}, headers=HEADERS)
        self.assertEqual(response.status_code, 422)
        self.collection.document.assert_not_called()

    def test_storage_utilities_are_hidden_by_default_before_auth_or_storage_access(self):
        for enabled in ("", "false", "1", "yes"):
            with patch.dict(os.environ, {"ENABLE_INTERNAL_DEBUG_ROUTES": enabled}):
                for path in UTILITY_PATHS:
                    self.assertEqual(self.client.get(path, headers=HEADERS).status_code, 404)
        self.verify.assert_not_called()
        self.assert_no_work()

    def test_enabled_utilities_still_hide_unauthenticated_nonoperator_and_revoked_callers(self):
        with patch.dict(os.environ, {"ENABLE_INTERNAL_DEBUG_ROUTES": "true"}):
            for path in UTILITY_PATHS:
                self.assertEqual(self.client.get(path).status_code, 404)
                self.assertEqual(self.client.get(path, headers={"Authorization": "Bearer test"}).status_code, 404)
            self.verify.return_value = {"uid": "customer", "admin": True}
            for path in UTILITY_PATHS:
                self.assertEqual(self.client.get(path, headers=HEADERS).status_code, 404)
            self.verify.side_effect = auth.RevokedIdTokenError("revoked")
            for path in UTILITY_PATHS:
                self.assertEqual(self.client.get(path, headers=HEADERS).status_code, 404)
        self.assert_no_work()

    def test_explicit_debug_operator_can_reach_utility_with_only_fake_cloud_clients(self):
        with patch.dict(os.environ, {"ENABLE_INTERNAL_DEBUG_ROUTES": "true"}):
            self.gcs.return_value.create_bucket.return_value = SimpleNamespace(name="fake-created-bucket")
            response = self.client.get("/api/image/create-firebase-bucket", headers=HEADERS)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertTrue(response.json()["success"])
            self.gcs.return_value.create_bucket.assert_called_once()
            self.verify.assert_called_once_with("signed-token", check_revoked=True)

    def test_disabling_debug_does_not_disable_customer_upload(self):
        self.verify.return_value = {"uid": "customer"}
        blob = Mock(public_url="https://storage.example/original.jpg")
        self.storage.return_value.name = "fake-bucket"
        self.storage.return_value.blob.return_value = blob
        response = self.client.post("/api/image/upload", headers=HEADERS,
                                    files={"file": ("shirt.jpg", b"original-photo", "image/jpeg")})
        self.assertEqual(response.status_code, 200, response.text)
        blob.upload_from_string.assert_called_once_with(b"original-photo", content_type="image/jpeg")
        self.assertTrue(self.storage.return_value.blob.call_args.args[0].startswith("wardrobe/customer/"))


if __name__ == "__main__":
    unittest.main()
