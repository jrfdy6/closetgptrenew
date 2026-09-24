"""Execute app.py's actual registry, guarded loader and mounting loop.

Only unrelated routers are replaced with empty routers, so this does not claim
to boot every legacy AI service. The three migrated routers and their import
graphs are real; missing packaged data/import errors cannot hide behind
include_router_safe. HTTP assertions then exercise those registered endpoints.
"""
import ast
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import traceback
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient


BACKEND = Path(__file__).resolve().parents[1]
REGISTRATIONS = {
    "src.routes.onboarding": "/api/onboarding",
    "src.routes.style_quiz": "/api/style-quiz",
    "src.routes.user_profile": "/api/user",
}
EXPECTED = {
    ("/api/onboarding", "GET"): ("src.routes.onboarding", "get_onboarding"),
    ("/api/onboarding", "POST"): ("src.routes.onboarding", "reconcile_onboarding"),
    ("/api/onboarding", "PATCH"): ("src.routes.onboarding", "patch_onboarding"),
    ("/api/style-quiz/submit", "POST"): ("src.routes.style_quiz", "submit_style_quiz"),
    ("/api/user/profile", "GET"): ("src.routes.user_profile", "get_profile"),
    ("/api/user/profile", "POST"): ("src.routes.user_profile", "save_profile"),
}


def registered_app(*, failing_import=None):
    source = BACKEND / "app.py"
    tree = ast.parse(source.read_text())
    registry = [node for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ROUTERS" for target in node.targets)]
    loader = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "include_router_safe"]
    loop = [node for node in tree.body if isinstance(node, ast.For) and isinstance(node.iter, ast.Name) and node.iter.id == "ROUTERS"]
    assert len(registry) == len(loader) == len(loop) == 1, "The app's real router bootstrap must exist exactly once"
    imported = []
    def isolated_import(name):
        if name in REGISTRATIONS:
            imported.append(name)
            if name == failing_import:
                raise ImportError("deliberate missing migrated dependency")
            return importlib.import_module(name)
        return SimpleNamespace(router=APIRouter())
    namespace = {"app": FastAPI(), "importlib": SimpleNamespace(import_module=isolated_import), "traceback": traceback, "ROUTER_DEBUG": False}
    exec(compile(ast.Module(body=registry, type_ignores=[]), str(source), "exec"), namespace)
    selected = [entry for entry in namespace["ROUTERS"] if entry[0] in REGISTRATIONS]
    assert selected == list(REGISTRATIONS.items()), "Missing, duplicate, wrongly prefixed or reordered privileged registration"
    exec(compile(ast.Module(body=loader + loop, type_ignores=[]), str(source), "exec"), namespace)
    assert imported == list(REGISTRATIONS), "The actual app mounting loop must import every migrated router"
    return namespace["app"]


def assert_registered(app):
    for (path, method), (module, name) in EXPECTED.items():
        found = [route for route in app.routes if route.path == path and method in getattr(route, "methods", set())]
        assert len(found) == 1, f"Expected exactly one live registration for {method} {path}, got {len(found)}"
        assert found[0].endpoint.__module__ == module and found[0].endpoint.__name__ == name, f"Wrong actual handler for {method} {path}"


def verify_cold_import():
    """A subprocess prevents other tests' cached modules/mocks hiding imports."""
    import firebase_admin
    with patch.object(firebase_admin, "initialize_app", side_effect=AssertionError("Import must not initialize Firebase")) as initialize, patch("socket.socket.connect", side_effect=AssertionError("Import must not make a network connection")):
        app = registered_app()
        assert_registered(app)
        initialize.assert_not_called()
    assert "src.config.firebase" not in sys.modules, "Storage initialization belongs after verified HTTP authentication"


class PrivilegedRouteRegistrationTests(unittest.TestCase):
    def test_cold_boot_imports_real_routers_and_services_through_actual_app_loop_without_credentials(self):
        environment = {key: value for key, value in os.environ.items() if not key.startswith(("FIREBASE_", "GOOGLE_", "OPENAI_"))}
        environment["PYTHONPATH"] = os.pathsep.join((str(BACKEND), str(BACKEND / "tests")))
        result = subprocess.run([sys.executable, "-c", "from test_privileged_route_registration import verify_cold_import; verify_cold_import(); print('six real endpoints registered')"], cwd=BACKEND, env=environment, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("six real endpoints registered", result.stdout)

    def test_required_import_failure_prevents_startup(self):
        for name in REGISTRATIONS:
            with self.subTest(module=name), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), patch("logging.error"):
                with self.assertRaisesRegex(RuntimeError, "Required application router unavailable"):
                    registered_app(failing_import=name)

    def test_every_registered_endpoint_requires_the_real_verified_bearer_dependency(self):
        app = registered_app(); assert_registered(app)
        from src.auth import verified_user
        with patch.object(verified_user.auth, "verify_id_token") as verify:
            client = TestClient(app)
            for path, method in EXPECTED:
                with self.subTest(path=path, method=method):
                    response = client.request(method, path, json={})
                    self.assertEqual(response.status_code, 401)
            verify.assert_not_called()

    def test_registered_handlers_dispatch_verified_identity_and_quiz_offloads_sync_commit(self):
        app = registered_app(); assert_registered(app)
        from src.auth import verified_user
        from src.routes import onboarding, style_quiz, user_profile
        claims = {"uid": "verified-owner", "email": "owner@example.test"}
        database = object()
        config = ModuleType("src.config.firebase"); config.db = database
        state = {"schemaVersion": 1, "revision": 3, "stage": "style"}
        draft = {"answers": [{"question_id": "gender", "selected_option": "Male"}], "currentQuestionId": "height"}
        full_quiz = json.loads((BACKEND / "tests/fixtures/quiz-profile-parity.json").read_text())["cases"][0]["input"]
        submission = {**full_quiz, "answers": [{"question_id": key, "selected_option": value} for key, value in full_quiz["answers"].items()]}
        quiz_result = {"success": True, "persisted": True, "hybridStyleName": "The Architect"}
        thread_ids = {}
        async def observed_threadpool(function, *args, **kwargs):
            thread_ids["async_handler"] = threading.get_ident()
            from starlette.concurrency import run_in_threadpool
            return await run_in_threadpool(function, *args, **kwargs)
        def save_quiz(*args, **kwargs):
            thread_ids["sync_commit"] = threading.get_ident()
            return quiz_result
        with ExitStack() as stack:
            stack.enter_context(patch.dict(sys.modules, {"src.config.firebase": config}))
            verify = stack.enter_context(patch.object(verified_user.auth, "verify_id_token", return_value=claims))
            read = stack.enter_context(patch.object(onboarding, "read_onboarding_state", return_value=state))
            reconcile = stack.enter_context(patch.object(onboarding, "reconcile_onboarding_state", return_value=state))
            save_draft = stack.enter_context(patch.object(onboarding, "save_onboarding_draft", return_value=state))
            profile = stack.enter_context(patch.object(user_profile, "persist_profile", return_value={"userId": claims["uid"], "name": "Owner"}))
            quiz = stack.enter_context(patch.object(style_quiz, "save_quiz_profile", side_effect=save_quiz))
            offload = stack.enter_context(patch.object(style_quiz, "run_in_threadpool", side_effect=observed_threadpool))
            client = TestClient(app)
            headers = {"authorization": "Bearer verified-token"}
            for method, path, body in (
                ("GET", "/api/onboarding", None), ("POST", "/api/onboarding", {}),
                ("PATCH", "/api/onboarding", {"draft": draft, "expectedRevision": 2}),
                ("GET", "/api/user/profile", None), ("POST", "/api/user/profile", {"name": "Owner"}),
                ("POST", "/api/style-quiz/submit", submission),
            ):
                with self.subTest(method=method, path=path):
                    response = client.request(method, path, headers=headers, json=body)
                    self.assertEqual(response.status_code, 200, response.text)
                    self.assertEqual(response.headers["cache-control"], "private, no-store")
            self.assertEqual(verify.call_count, 6)
            for call in verify.call_args_list:
                self.assertEqual(call.args, ("verified-token",)); self.assertEqual(call.kwargs, {"check_revoked": True})
            read.assert_called_once_with(database, claims["uid"])
            reconcile.assert_called_once_with(database, claims["uid"])
            save_draft.assert_called_once_with(database, claims["uid"], 2, draft)
            self.assertEqual(profile.call_args_list[0].args, (database, claims))
            self.assertEqual(profile.call_args_list[1].args, (database, claims, {"name": "Owner"}))
            quiz.assert_called_once_with(database, claims, submission)
            offload.assert_called_once()
            self.assertNotEqual(thread_ids["async_handler"], thread_ids["sync_commit"], "Firestore quiz transaction must not block the ASGI event loop")


if __name__ == "__main__":
    unittest.main()
