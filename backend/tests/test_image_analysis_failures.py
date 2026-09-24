"""Real analysis handlers fail closed without calling an image provider or network."""
import base64
from contextlib import ExitStack
from functools import partial
import importlib.util
from io import BytesIO
from pathlib import Path
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from firebase_admin import auth
from PIL import Image

from src.auth import auth_service
from test_app_data_privacy import Database


HEADERS = {"Authorization": "Bearer signed-token"}
PATHS = (
    "/analyze", "/analyze-image", "/analyze-image-legacy",
    "/analyze-image-clip-only", "/analyze-batch", "/analyze-batch-legacy",
    "/generate-image-hash",
)
SINGLE_PATHS = PATHS[:4]
GOOD_ANALYSIS = {
    "name": "Navy cotton shirt", "type": "shirt", "subType": "button-down",
    "dominantColors": [{"name": "navy", "hex": "#000080"}],
    "metadata": {"visualAttributes": {"material": "cotton"}},
}


def fake_module(name, **attributes):
    module = ModuleType(name)
    module.__dict__.update(attributes)
    return module


class ImageAnalysisFailureTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        buffer = BytesIO()
        Image.new("RGB", (2, 2), "navy").save(buffer, format="PNG")
        self.png = buffer.getvalue()
        self.data_url = "data:image/png;base64," + base64.b64encode(self.png).decode()
        self.direct = AsyncMock(return_value=GOOD_ANALYSIS)
        self.simple = AsyncMock(return_value=GOOD_ANALYSIS)
        self.analytics = Mock()
        self.cohort = Mock(return_value=False)
        self.queue = Mock(return_value={"id": "analysis-job"})
        self.job = Mock(return_value=None)
        modules = {
            "src.services.openai_service": fake_module(
                "src.services.openai_service", analyze_image_with_gpt4=self.direct),
            "src.services.simple_image_analysis_service": fake_module(
                "src.services.simple_image_analysis_service",
                simple_analyzer=SimpleNamespace(analyze_clothing_item=self.simple)),
            "src.utils.image_processing": fake_module(
                "src.utils.image_processing", process_image_for_analysis=lambda path: path),
            "src.services.analytics_service": fake_module(
                "src.services.analytics_service", log_analytics_event=self.analytics),
            "src.models.analytics_event": fake_module(
                "src.models.analytics_event", AnalyticsEvent=lambda **kwargs: SimpleNamespace(**kwargs)),
            "src.services.ai_runtime": fake_module(
                "src.services.ai_runtime", UPLOAD_IMAGE_ANALYSIS_JOB_KIND="upload_image_analysis",
                build_pending_codex_analysis=lambda **kwargs: {"name": "Processing item", "type": "unknown"},
                codex_fast_path_poll_ms=lambda: 1, codex_fast_path_timeout_ms=lambda: 0,
                get_codex_job_for_user=self.job, is_codex_image_analysis_user=self.cohort,
                normalize_codex_upload_analysis_result=lambda result, **kwargs: result,
                queue_codex_job=self.queue),
        }
        self.stack.enter_context(patch.dict("sys.modules", modules))
        self.stack.enter_context(patch("dotenv.load_dotenv"))
        spec = importlib.util.spec_from_file_location(
            "src.routes.isolated_image_analysis",
            Path(__file__).resolve().parents[1] / "src/routes/image_analysis.py",
        )
        self.route = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.route)
        self.route.tempfile = SimpleNamespace(
            NamedTemporaryFile=partial(tempfile.NamedTemporaryFile, dir=self.directory))
        self.download = Mock(return_value=SimpleNamespace(content=self.png, raise_for_status=lambda: None))
        self.route.requests = SimpleNamespace(get=self.download)
        self.verify = self.stack.enter_context(patch(
            "src.auth.verified_user.auth.verify_id_token", return_value={"uid": "owner"}))
        self.db = Database({"users/owner": {"gender": "female"}})
        self.stack.enter_context(patch.object(auth_service, "_profile_database", return_value=self.db))
        app = FastAPI()
        app.include_router(self.route.router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def request(self, path, headers=HEADERS, body=None):
        if path == "/analyze":
            return self.client.post(path, headers=headers, files={"file": ("shirt.png", self.png, "image/png")})
        if body is None:
            if path == "/analyze-image":
                body = {"image_url": self.data_url}
            elif path == "/generate-image-hash":
                body = {"image_url": "https://images.invalid/shirt.png"}
            elif "batch" in path:
                body = [{"url": "https://images.invalid/shirt.png"}]
            else:
                body = {"url": "https://images.invalid/shirt.png"}
        return self.client.post(path, headers=headers, json=body)

    def assert_no_work(self):
        self.direct.assert_not_called()
        self.simple.assert_not_called()
        self.download.assert_not_called()
        self.queue.assert_not_called()
        self.analytics.assert_not_called()
        self.assertEqual(list(Path(self.directory).iterdir()), [])

    def assert_failure(self, response, status=503):
        self.assertEqual(response.status_code, status, response.text)
        self.assertNotIn("analysis", response.json())
        self.assertNotIn("private provider failure", response.text)
        self.assertNotIn("Analysis Failed", response.text)
        self.assertEqual(list(Path(self.directory).iterdir()), [])

    def test_every_active_route_requires_credentials_before_any_work(self):
        self.assertEqual({route.path for route in self.route.router.routes}, set(PATHS))
        for path in PATHS:
            for header in (None, "", "Basic token", "Bearer test", "Bearer TEST", "Bearer a b"):
                with self.subTest(path=path, header=header):
                    response = self.request(path, {"Authorization": header} if header is not None else {})
                    self.assertEqual(response.status_code, 401, response.text)
        self.verify.assert_not_called()
        self.assert_no_work()

    def test_revoked_disabled_invalid_and_verifier_failure_do_not_reach_analysis(self):
        for error, status in (
            (auth.RevokedIdTokenError("revoked"), 401),
            (auth.UserDisabledError("disabled"), 401),
            (auth.InvalidIdTokenError("invalid"), 401),
            (RuntimeError("private verifier failure"), 503),
        ):
            self.verify.side_effect = error
            for path in PATHS:
                with self.subTest(path=path, error=type(error).__name__):
                    response = self.request(path)
                    self.assertEqual(response.status_code, status, response.text)
                    self.assertNotIn(str(error), response.text)
        for call in self.verify.call_args_list:
            self.assertEqual(call.args, ("signed-token",))
            self.assertEqual(call.kwargs, {"check_revoked": True})
        self.assert_no_work()

    def test_anonymous_firebase_accounts_cannot_analyze(self):
        self.verify.return_value = {"uid": "guest", "firebase": {"sign_in_provider": "anonymous"}}
        for path in PATHS:
            self.assertEqual(self.request(path).status_code, 403)
        self.assert_no_work()

    def test_single_image_provider_failures_return_503_without_saveable_placeholder(self):
        self.direct.side_effect = RuntimeError("private provider failure")
        self.simple.side_effect = RuntimeError("private provider failure")
        for path in SINGLE_PATHS:
            with self.subTest(path=path):
                self.assert_failure(self.request(path))
        self.analytics.assert_not_called()

    def test_unavailable_provider_does_not_become_fake_garment(self):
        self.route.analyze_image_with_gpt4 = None
        self.route.simple_analyzer = None
        for path in SINGLE_PATHS:
            with self.subTest(path=path):
                self.assert_failure(self.request(path))

    def test_provider_error_payload_or_empty_result_is_not_normalized_to_clothing(self):
        for result in (None, {}, [], {"error": "private provider failure"},
                       {"name": "Analysis Failed", "type": "clothing"}):
            self.direct.return_value = result
            self.assert_failure(self.request("/analyze-image"))

    def test_http_errors_keep_their_status_and_cleanup_temporary_images(self):
        self.direct.side_effect = HTTPException(status_code=429, detail="Please retry later")
        self.simple.side_effect = HTTPException(status_code=429, detail="Please retry later")
        for path in SINGLE_PATHS:
            with self.subTest(path=path):
                self.assert_failure(self.request(path), 429)

    def test_provider_errors_keep_503_even_when_optional_analytics_is_unavailable(self):
        self.route.AnalyticsEvent = None
        self.route.log_analytics_event = None
        self.direct.side_effect = RuntimeError("private provider failure")
        self.simple.side_effect = RuntimeError("private provider failure")
        for path in SINGLE_PATHS:
            self.assert_failure(self.request(path))

    def test_missing_image_and_empty_batch_are_400_instead_of_500(self):
        for path in PATHS[1:]:
            body = [] if "batch" in path else {"image_url": ""} if path == "/generate-image-hash" else {}
            with self.subTest(path=path):
                self.assert_failure(self.request(path, body=body), 400)
        self.assert_no_work()

    def test_download_validation_error_keeps_400(self):
        self.download.side_effect = RuntimeError("unavailable image")
        self.assert_failure(self.request("/analyze-image", body={"image_url": "https://images.invalid/shirt.png"}), 400)
        self.direct.assert_not_called()

    def test_successful_direct_analysis_preserves_normalized_fields(self):
        response = self.request("/analyze-image")
        self.assertEqual(response.status_code, 200, response.text)
        analysis = response.json()["analysis"]
        self.assertEqual(analysis["name"], "Navy cotton shirt")
        self.assertEqual(analysis["clothing_type"], "shirt")
        self.assertEqual(analysis["primary_color"], "navy")
        self.assertEqual(analysis["material"], "cotton")
        self.assertEqual(list(Path(self.directory).iterdir()), [])

    def test_batch_preserves_partial_results_without_success_for_failed_provider(self):
        for path, provider in (("/analyze-batch", self.simple), ("/analyze-batch-legacy", self.direct)):
            provider.side_effect = [GOOD_ANALYSIS, RuntimeError("private provider failure")]
            response = self.request(path, body=[{"url": "https://images.invalid/good.png"},
                                               {"url": "https://images.invalid/failed.png"}])
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.json()["summary"], {"total": 2, "successful": 1, "errors": 1})
            results = response.json()["results"]
            self.assertEqual(results[0]["status"], "success")
            self.assertEqual(results[1]["status"], "error")
            self.assertNotIn("analysis", results[1])
            self.assertNotIn("private provider failure", response.text)
            self.assertEqual(list(Path(self.directory).iterdir()), [])

    def test_codex_pending_response_stays_explicitly_pending(self):
        self.cohort.return_value = True
        response = self.request("/analyze-image")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["analysis_status"], "pending")
        self.assertEqual(response.json()["codex_job_id"], "analysis-job")
        self.assertEqual(self.queue.call_args.kwargs["requested_by"], "owner")
        self.direct.assert_not_called()
        self.download.assert_not_called()

    def test_codex_failed_job_status_is_not_swallowed_by_outer_exception(self):
        self.cohort.return_value = True
        self.job.return_value = {"status": "failed", "error_message": "Analysis could not finish"}
        self.assert_failure(self.request("/analyze-image"), 502)
        self.direct.assert_not_called()


if __name__ == "__main__":
    unittest.main()
