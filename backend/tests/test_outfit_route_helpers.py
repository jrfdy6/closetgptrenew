"""Regression tests for helpers used by the production outfit generator."""

import unittest

from fastapi import status

from src.core.exceptions import DatabaseError, handle_easy_outfit_exception
from src.routes.outfit_generation_contract import (
    RequiredBaseItemNotFound,
    enforce_required_base_item,
    normalize_generation_user_profile,
)
from src.routes.outfits.routes import safe_get


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


if __name__ == "__main__":
    unittest.main()
