"""Calendar, legacy timestamp, ownership, and undo regressions without cloud I/O."""
import copy
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
import unittest

from src.services.wear_statistics import parse_wear_timestamp, week_bounds, weekly_wear_summary


UTC = timezone.utc
NOW = datetime(2026, 9, 23, 16, 30, tzinfo=UTC)
PROFILE = {"location_data": {"timezone": "America/New_York"}}


class Snapshot:
    def __init__(self, identifier, data):
        self.id, self.exists, self.data = identifier, data is not None, copy.deepcopy(data)

    def to_dict(self):
        return copy.deepcopy(self.data)


class Document:
    def __init__(self, db, collection, identifier):
        self.db, self.collection, self.id = db, collection, identifier

    def get(self):
        if self.db.fail_reads:
            raise RuntimeError("database unavailable")
        self.db.reads.append((self.collection, self.id))
        return Snapshot(self.id, self.db.rows.get(self.collection, {}).get(self.id))


class Query:
    def __init__(self, db, collection, predicate=None):
        self.db, self.collection, self.predicate = db, collection, predicate

    def document(self, identifier):
        return Document(self.db, self.collection, identifier)

    def where(self, *, filter):
        return Query(self.db, self.collection, (filter.field_path, filter.value))

    def stream(self):
        self.db.queries.append(self.collection)
        for identifier, row in self.db.rows.get(self.collection, {}).items():
            if self.db.fail_queries:
                raise RuntimeError("history unavailable")
            if not self.predicate or row.get(self.predicate[0]) == self.predicate[1]:
                yield Snapshot(identifier, row)


class Store:
    def __init__(self):
        self.rows = {"users": {"owner": copy.deepcopy(PROFILE)}, "outfit_history": {}, "outfits": {}}
        self.reads, self.queries = [], []
        self.fail_reads = self.fail_queries = False

    def collection(self, name):
        return Query(self, name)


class WeekBoundsTests(unittest.TestCase):
    def test_monday_profile_timezone_start_and_next_monday_end(self):
        start, end, zone = week_bounds(PROFILE, NOW)
        self.assertEqual(start, datetime(2026, 9, 21, 4, tzinfo=UTC))
        self.assertEqual(end, datetime(2026, 9, 28, 4, tzinfo=UTC))
        self.assertEqual(zone, "America/New_York")

    def test_utc_monday_before_local_monday_still_belongs_to_previous_week(self):
        start, end, _ = week_bounds(PROFILE, datetime(2026, 9, 21, 3, 59, tzinfo=UTC))
        self.assertEqual(start, datetime(2026, 9, 14, 4, tzinfo=UTC))
        self.assertEqual(end, datetime(2026, 9, 21, 4, tzinfo=UTC))
        start, _, _ = week_bounds(PROFILE, end)
        self.assertEqual(start, end)

    def test_dst_weeks_preserve_local_midnights(self):
        for instant, expected_hours, expected_start, expected_end in (
            (datetime(2026, 3, 8, 16, tzinfo=UTC), 167, datetime(2026, 3, 2, 5, tzinfo=UTC), datetime(2026, 3, 9, 4, tzinfo=UTC)),
            (datetime(2026, 11, 1, 16, tzinfo=UTC), 169, datetime(2026, 10, 26, 4, tzinfo=UTC), datetime(2026, 11, 2, 5, tzinfo=UTC)),
        ):
            with self.subTest(instant=instant):
                start, end, _ = week_bounds(PROFILE, instant)
                self.assertEqual((start, end), (expected_start, expected_end))
                self.assertEqual((end - start).total_seconds() / 3600, expected_hours)

    def test_year_boundary_and_non_hour_timezone(self):
        start, end, zone = week_bounds({"location_data": {"timezone": "Asia/Kathmandu"}}, datetime(2027, 1, 1, tzinfo=UTC))
        self.assertEqual(start, datetime(2026, 12, 27, 18, 15, tzinfo=UTC))
        self.assertEqual(end, datetime(2027, 1, 3, 18, 15, tzinfo=UTC))
        self.assertEqual(zone, "Asia/Kathmandu")

    def test_missing_invalid_and_malformed_profile_timezone_use_utc(self):
        for profile in (None, {}, {"location_data": "invalid"}, {"location_data": {"timezone": "Invalid/Zone"}},
                        {"location_data": {"timezone": 123}}, {"location_data": {"timezone": "../UTC"}}):
            with self.subTest(profile=profile):
                start, end, zone = week_bounds(profile, NOW)
                self.assertEqual(start, datetime(2026, 9, 21, tzinfo=UTC))
                self.assertEqual(end, datetime(2026, 9, 28, tzinfo=UTC))
                self.assertEqual(zone, "UTC")

    def test_naive_clock_is_rejected_instead_of_using_host_timezone(self):
        with self.assertRaises(ValueError):
            week_bounds(PROFILE, NOW.replace(tzinfo=None))


class TimestampTests(unittest.TestCase):
    def test_supported_absolute_timestamp_formats(self):
        for value in (NOW, NOW.replace(tzinfo=None), NOW.isoformat(), NOW.isoformat().replace("+00:00", "Z"),
                      "2026-09-23T12:30:00-04:00", NOW.timestamp(), NOW.timestamp() * 1000,
                      str(int(NOW.timestamp())), str(int(NOW.timestamp() * 1000)),
                      {"seconds": NOW.timestamp(), "nanoseconds": 0},
                      {"_seconds": NOW.timestamp(), "_nanoseconds": 0},
                      SimpleNamespace(timestamp=lambda: NOW.timestamp())):
            with self.subTest(value=value):
                self.assertEqual(parse_wear_timestamp(value), NOW)

    def test_date_only_values_use_selected_calendar_timezone(self):
        for value in ("2026-09-21", date(2026, 9, 21)):
            self.assertEqual(parse_wear_timestamp(value, date_timezone="America/New_York"),
                             datetime(2026, 9, 21, 4, tzinfo=UTC))
        self.assertEqual(parse_wear_timestamp({"seconds": NOW.timestamp(), "nanoseconds": 123000000}),
                         NOW + timedelta(microseconds=123000))

    def test_malformed_nonfinite_boolean_and_out_of_range_values_are_unknown(self):
        for value in (None, True, False, "", "tomorrow", "2026-02-30", float("nan"), float("inf"),
                      -float("inf"), 10 ** 1000, [], {}, {"seconds": True},
                      {"seconds": NOW.timestamp(), "nanoseconds": -1}, {"seconds": NOW.timestamp(), "nanoseconds": 1e9}):
            with self.subTest(value=str(value)[:50]):
                self.assertIsNone(parse_wear_timestamp(value))


class WeeklySummaryTests(unittest.TestCase):
    def setUp(self):
        self.db = Store()

    def history(self, key, **values):
        self.db.rows["outfit_history"][key] = {"user_id": "owner", "date_worn": NOW.timestamp() * 1000, **values}

    def outfit(self, key, **values):
        self.db.rows["outfits"][key] = {"user_id": "owner", "lastWorn": NOW.isoformat(), **values}

    def summary(self):
        return weekly_wear_summary(self.db, "owner", NOW)

    def test_managed_history_uses_monday_half_open_window_and_excludes_future(self):
        start, end, _ = week_bounds(PROFILE, NOW)
        for key, instant in (("before", start - timedelta(microseconds=1)), ("start", start), ("now", NOW),
                             ("future", NOW + timedelta(milliseconds=1)), ("next-week", end)):
            self.history(key, date_worn=instant.timestamp() * 1000, wear_operation_version=2,
                         wear_date=instant.date().isoformat(), timezone="UTC")
        result = self.summary()
        self.assertEqual(result["outfits_worn_this_week"], 2)
        self.assertEqual(result["source"], "outfit_history_individual_events")
        self.assertEqual(result["timezone"], "America/New_York")
        self.assertEqual(result["week_start"], start.isoformat())
        self.assertEqual(result["week_end"], end.isoformat())
        self.assertEqual(result["calculated_at"], NOW.isoformat())

    def test_canonical_legacy_and_dual_owners_count_once_and_conflicts_are_excluded(self):
        self.history("canonical")
        self.history("legacy", user_id=None, userId="owner")
        self.history("dual", userId="owner")
        self.history("conflict-a", userId="other")
        self.history("conflict-b", user_id="other", userId="owner")
        self.history("foreign", user_id="other")
        self.history("unowned", user_id=None)
        self.assertEqual(self.summary()["outfits_worn_this_week"], 3)

    def test_events_of_deleted_or_missing_outfits_still_count_without_reading_outfits(self):
        self.outfit("deleted", deleted=True)
        self.history("first", outfit_id="deleted")
        self.history("second", outfit_id="deleted", date_worn=(NOW - timedelta(days=1)).timestamp() * 1000)
        self.history("third", outfit_id="missing", items=[{"id": "removed-garment", "name": "Saved snapshot"}])
        self.assertEqual(self.summary()["outfits_worn_this_week"], 3)
        self.assertNotIn("outfits", self.db.queries)
        self.assertTrue(all(collection != "outfits" for collection, _ in self.db.reads))

    def test_undo_cannot_resurrect_a_count_from_last_worn(self):
        self.outfit("still-has-last-worn")
        self.history("undone", undone=True)
        result = self.summary()
        self.assertEqual(result["outfits_worn_this_week"], 0)
        self.assertEqual(result["source"], "outfit_history_individual_events")
        self.assertNotIn("outfits", self.db.queries)
        self.db.rows["outfit_history"]["undone"]["undone"] = False
        self.assertEqual(self.summary()["outfits_worn_this_week"], 1)

    def test_old_or_invalid_owned_history_also_disables_fallback(self):
        self.outfit("fallback")
        for instant in ("invalid", (NOW - timedelta(days=20)).isoformat()):
            self.history("history", date_worn=instant)
            result = self.summary()
            self.assertEqual(result["outfits_worn_this_week"], 0)
            self.assertEqual(result["source"], "outfit_history_individual_events")

    def test_legacy_date_fields_and_managed_calendar_fallback_are_supported(self):
        self.history("legacy-date", date_worn=None, date="2026-09-21")
        self.history("createdAt", date_worn="bad", createdAt=NOW.replace(tzinfo=None))
        self.history("created_at", date_worn=None, created_at=NOW.timestamp())
        self.history("managed-calendar", date_worn=None, wear_date="2026-09-21", timezone="America/New_York")
        self.history("travel-monday", date_worn=None, wear_date="2026-09-21", timezone="Pacific/Kiritimati")
        self.assertEqual(self.summary()["outfits_worn_this_week"], 4)

    def test_bad_managed_instant_does_not_fall_back_to_later_creation_time(self):
        self.history("managed", wear_operation_version=2, date_worn="invalid", wear_date="2026-09-01", createdAt=NOW)
        self.assertEqual(self.summary()["outfits_worn_this_week"], 0)

    def test_fallback_counts_only_active_owned_outfits_and_never_future(self):
        self.outfit("canonical")
        self.outfit("legacy", user_id=None, userId="owner", lastWorn=NOW.timestamp() * 1000)
        self.outfit("dual", userId="owner", lastWorn=NOW.timestamp())
        self.outfit("conflict", userId="other")
        self.outfit("old", lastWorn=(NOW - timedelta(days=20)).isoformat())
        self.outfit("future", lastWorn=(NOW + timedelta(seconds=1)).isoformat())
        self.outfit("bad", lastWorn="bad")
        for field in ("deleted", "isDeleted", "deletedAt", "deleted_at"):
            self.outfit(field, **{field: True})
        result = self.summary()
        self.assertEqual(result["outfits_worn_this_week"], 3)
        self.assertEqual(result["source"], "lastWorn_fallback")

    def test_foreign_conflicting_history_does_not_disable_owned_fallback(self):
        self.history("foreign", user_id="other")
        self.history("conflict", userId="other")
        self.outfit("owned")
        result = self.summary()
        self.assertEqual(result["source"], "lastWorn_fallback")
        self.assertEqual(result["outfits_worn_this_week"], 1)

    def test_missing_profile_defaults_utc_and_empty_store_returns_zero(self):
        self.db.rows["users"].clear()
        result = self.summary()
        self.assertEqual(result["timezone"], "UTC")
        self.assertEqual(result["outfits_worn_this_week"], 0)

    def test_database_errors_propagate_instead_of_returning_zero(self):
        self.db.fail_reads = True
        with self.assertRaises(RuntimeError):
            self.summary()
        self.db.fail_reads = False
        self.history("unavailable")
        self.db.fail_queries = True
        with self.assertRaises(RuntimeError):
            self.summary()

    def test_summary_is_read_only(self):
        self.history("event")
        before = copy.deepcopy(self.db.rows)
        self.summary()
        self.assertEqual(self.db.rows, before)


if __name__ == "__main__":
    unittest.main()
