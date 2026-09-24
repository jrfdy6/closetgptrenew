import importlib
from types import SimpleNamespace
from unittest import TestCase
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from src.core.route_registry import mount_router, validate_route_table


class RegistryTests(TestCase):
    def test_required_import_failure_fails_closed(self):
        def fail(_):
            raise ImportError("missing dependency")
        with self.assertRaisesRegex(RuntimeError, "Required application router"):
            mount_router(FastAPI(), "src.routes.outfits", "/api/outfits", importer=fail)

    def test_optional_failure_recorded_and_does_not_claim_mounted(self):
        app = FastAPI()
        self.assertFalse(mount_router(app, "optional", "", importer=lambda _: SimpleNamespace()))
        self.assertEqual(app.state.unavailable_optional_routers, {"optional"})
        self.assertFalse(hasattr(app.state, "mounted_router_contracts"))

    def test_duplicate_registration_rejected(self):
        app = FastAPI()
        module = SimpleNamespace(router=APIRouter())
        mount_router(app, "module", "", importer=lambda _: module)
        with self.assertRaisesRegex(RuntimeError, "Duplicate router"):
            mount_router(app, "module", "", importer=lambda _: module)

    def test_static_endpoint_cannot_be_swallowed_by_owned_id_reader(self):
        app = FastAPI()
        @app.get("/items/{item_id}")
        def item(item_id: str):
            return {"id": item_id}
        @app.get("/items/stats")
        def stats():
            return {"count": 3}
        validate_route_table(app)
        client = TestClient(app)
        self.assertEqual(client.get("/items/stats").json(), {"count": 3})
        self.assertEqual(client.get("/items/owned").json(), {"id": "owned"})

    def test_duplicate_http_path_is_rejected(self):
        app = FastAPI()
        app.get("/items")(lambda: {})
        app.get("/items")(lambda: {})
        with self.assertRaisesRegex(RuntimeError, "Duplicate HTTP route"):
            validate_route_table(app)
