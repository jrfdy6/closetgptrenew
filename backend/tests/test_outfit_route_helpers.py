"""Regression tests for helpers used by the production outfit generator."""

import io
import time
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import status

from src.core.exceptions import DatabaseError, handle_easy_outfit_exception
from src.routes.outfit_generation_contract import (
    RequiredBaseItemNotFound,
    enforce_required_base_item,
    normalize_generation_user_profile,
)
from src.routes.outfits.routes import safe_get
from src.services.filters.formality_tier_system import FormalityTier, FormalityTierSystem
from src.services.diversity_filter_service import DiversityFilterService
import src.services.diversity_filter_service as diversity_filter_module
from src.services.robust_outfit_generation_service import RobustOutfitGenerationService
import src.services.robust_outfit_generation_service as robust_generation_module


class WardrobeItem:
    name = "Blue Oxford"


class SafeGetTests(unittest.TestCase):
    def test_reads_mapping_values(self):
        self.assertEqual(safe_get({"name": "Blue Oxford"}, "name"), "Blue Oxford")

    def test_uses_mapping_default(self):
        self.assertEqual(safe_get({}, "name", "Unknown"), "Unknown")

    def test_reads_object_attributes(self):
        self.assertEqual(safe_get(WardrobeItem(), "name"), "Blue Oxford")


class ExceptionContractTests(unittest.TestCase):
    def test_database_error_maps_to_http_500(self):
        http_error = handle_easy_outfit_exception(DatabaseError("Database unavailable"))
        self.assertEqual(http_error.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(http_error.detail["error"], "DATABASE_ERROR")


class RequiredBaseItemContractTests(unittest.TestCase):
    def setUp(self):
        self.wardrobe = [
            {"id": "shirt-1", "name": "Navy Oxford", "type": "SHIRT", "color": "navy"},
            {"id": "pants-1", "name": "Gray Trousers", "type": "PANTS", "color": "gray"},
        ]

    def test_replaces_the_same_category_when_required_item_is_missing(self):
        generated = [
            {"id": "shirt-2", "name": "White Shirt", "type": "SHIRT"},
            {"id": "pants-1", "name": "Gray Trousers", "type": "PANTS"},
        ]

        items, metadata = enforce_required_base_item(generated, self.wardrobe, "shirt-1")

        self.assertEqual([item["id"] for item in items], ["shirt-1", "pants-1"])
        self.assertTrue(metadata["base_item_included"])
        self.assertTrue(metadata["base_item_repaired"])
        self.assertEqual(metadata["base_item_repair_action"], "replaced_same_category")

    def test_deduplicates_a_required_item_that_is_already_present(self):
        generated = [self.wardrobe[0], self.wardrobe[0], self.wardrobe[1]]

        items, metadata = enforce_required_base_item(generated, self.wardrobe, "shirt-1")

        self.assertEqual([item["id"] for item in items], ["shirt-1", "pants-1"])
        self.assertEqual(metadata["base_item_repair_action"], "deduplicated")

    def test_prepends_when_no_same_category_exists(self):
        generated = [{"id": "shoes-1", "name": "Loafers", "type": "SHOES"}]

        items, metadata = enforce_required_base_item(generated, self.wardrobe, "pants-1")

        self.assertEqual([item["id"] for item in items], ["pants-1", "shoes-1"])
        self.assertEqual(metadata["base_item_repair_action"], "prepended")

    def test_rejects_a_required_item_outside_the_submitted_wardrobe(self):
        with self.assertRaises(RequiredBaseItemNotFound):
            enforce_required_base_item([], self.wardrobe, "missing-item")


class GenerationProfileNormalizationTests(unittest.TestCase):
    def test_normalizes_quiz_aliases_and_skin_tone_depth(self):
        normalized = normalize_generation_user_profile(
            {
                "id": "spoofed-user",
                "bodyType": "Round/Apple",
                "skinTone": "skin_tone_95",
                "style_preferences": ["Classic"],
                "color_preferences": ["navy", "camel"],
            },
            "user-1",
        )

        self.assertEqual(normalized["id"], "user-1")
        self.assertEqual(normalized["bodyType"], "apple")
        self.assertEqual(normalized["skinTone"], "deep")
        self.assertEqual(normalized["stylePreferences"]["preferredStyles"], ["Classic"])
        self.assertEqual(normalized["stylePreferences"]["favoriteColors"], ["navy", "camel"])

    def test_normalizes_legacy_numeric_skin_tone(self):
        normalized = normalize_generation_user_profile({"skinTone": "82"}, "user-1")

        self.assertEqual(normalized["skinTone"], "deep")

    def test_uses_nested_measurements_and_does_not_infer_undertone(self):
        normalized = normalize_generation_user_profile(
            {
                "measurements": {
                    "bodyType": "Inverted Triangle",
                    "skinTone": "skin_tone_20",
                }
            }
        )

        self.assertEqual(normalized["bodyType"], "inverted_triangle")
        self.assertEqual(normalized["skinTone"], "light")


class RobustGenerationLatencyContractTests(unittest.TestCase):
    def test_constructor_defers_heavy_flat_lay_services(self):
        service = RobustOutfitGenerationService()

        self.assertTrue(service.enable_flat_lay_generation)
        self.assertIsNone(service.flat_lay_service)
        self.assertIsNone(service.flat_lay_storage)

    def test_recent_items_are_reused_from_cache_without_a_firestore_client(self):
        now_seconds = time.time()
        now_ms = int(now_seconds * 1000)
        recent_iso = datetime.now(timezone.utc).isoformat()
        old_datetime = datetime.now(timezone.utc) - timedelta(days=10)
        cached_history = {
            "user-1": [
                {"createdAt": now_ms, "items": [{"id": "ms-item"}]},
                {"createdAt": now_seconds, "items": [SimpleNamespace(id="seconds-item")]},
                {"createdAt": recent_iso, "items": ["iso-item"]},
                {"createdAt": old_datetime, "items": [{"id": "old-item"}]},
                {"items": [{"id": "legacy-item"}]},
            ]
        }

        with patch.object(
            robust_generation_module,
            "diversity_filter",
            SimpleNamespace(outfit_history=cached_history),
        ):
            service = RobustOutfitGenerationService()
            item_ids = service._get_recently_used_items("user-1", hours=48)

        self.assertEqual(item_ids, {"ms-item", "seconds-item", "iso-item", "legacy-item"})


class FormalityFilterLoggingTests(unittest.TestCase):
    def test_tier_filter_keeps_item_diagnostics_out_of_stdout(self):
        system = FormalityTierSystem()
        wardrobe = [
            {"id": "shirt-1", "name": "Navy dress shirt", "type": "shirt"},
            {"id": "slides-1", "name": "Pool slides", "type": "shoes"},
        ]

        output = io.StringIO()
        with redirect_stdout(output):
            filtered = system._filter_by_tier(
                wardrobe,
                FormalityTier.TIER_1_STRICT_FORMAL,
                lambda item, key, default=None: item.get(key, default),
            )

        self.assertEqual([item["id"] for item in filtered], ["shirt-1"])
        self.assertEqual(output.getvalue(), "")


class DiversityHistoryContractTests(unittest.TestCase):
    def test_firestore_history_is_bounded_and_cached_oldest_first(self):
        class FakeDocument:
            def __init__(self, document_id, data):
                self.id = document_id
                self._data = data

            def to_dict(self):
                return self._data

        class FakeQuery:
            timeout = None

            def where(self, *_args, **_kwargs):
                return self

            def order_by(self, *_args, **_kwargs):
                return self

            def limit(self, *_args, **_kwargs):
                return self

            def stream(self, timeout=None):
                self.timeout = timeout
                return [
                    FakeDocument("newest", {"createdAt": 2, "items": [{"id": "new"}]}),
                    FakeDocument("oldest", {"createdAt": 1, "items": [{"id": "old"}]}),
                ]

        query = FakeQuery()
        fake_db = SimpleNamespace(collection=lambda _name: query)

        with patch.object(diversity_filter_module, "FIREBASE_AVAILABLE", True), patch.object(
            diversity_filter_module, "db", fake_db
        ):
            history = DiversityFilterService()._load_outfit_history_from_firestore("user-1")

        self.assertEqual(query.timeout, 3.0)
        self.assertEqual([outfit["id"] for outfit in history], ["oldest", "newest"])


if __name__ == "__main__":
    unittest.main()
