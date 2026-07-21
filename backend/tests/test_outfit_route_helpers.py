"""Regression tests for helpers used by the production outfit generator."""

import unittest

from fastapi import status

from src.core.exceptions import DatabaseError, handle_easy_outfit_exception
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


if __name__ == "__main__":
    unittest.main()
