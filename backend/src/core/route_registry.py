"""Explicit boot contracts for customer-facing application routers."""
import importlib
import logging

logger = logging.getLogger(__name__)

REQUIRED_ROUTERS = frozenset({
    "src.routes.onboarding", "src.routes.style_quiz", "src.routes.user_profile",
    "src.routes.wardrobe", "src.routes.garment_processing",
    "src.routes.image_upload_minimal", "src.routes.image_analysis",
    "src.routes.auth_working", "src.routes.outfits",
    "src.routes.existing_data_personalized_outfits", "src.routes.outfit_history",
    "src.routes.payments", "src.routes.simple_analytics", "src.routes.outfit_stats_simple",
    "src.routes.gamification", "src.routes.challenges", "src.routes.data_privacy",
})


def mount_router(app, module_name, prefix, *, importer=importlib.import_module):
    mounted = getattr(app.state, "mounted_router_contracts", set())
    identity = (module_name, prefix)
    if identity in mounted:
        raise RuntimeError(f"Duplicate router registration: {module_name}")
    try:
        router = getattr(importer(module_name), "router", None)
        if router is None:
            raise ImportError("Module has no router")
        app.include_router(router, prefix=prefix)
    except Exception as error:
        logger.exception("Router unavailable: %s", module_name)
        if module_name in REQUIRED_ROUTERS:
            raise RuntimeError(f"Required application router unavailable: {module_name}") from error
        unavailable = getattr(app.state, "unavailable_optional_routers", set())
        app.state.unavailable_optional_routers = unavailable | {module_name}
        return False
    app.state.mounted_router_contracts = mounted | {identity}
    return True


def validate_route_table(app):
    """Reject ambiguous dispatch and put literal paths ahead of parameter paths."""
    seen = set()
    for route in app.routes:
        for method in getattr(route, "methods", ()):
            identity = (method, route.path)
            if identity in seen:
                raise RuntimeError(f"Duplicate HTTP route: {method} {route.path}")
            seen.add(identity)
    app.router.routes.sort(key=lambda route: getattr(route, "path", "").count("{"))
