"""Undo uses chronological instants across legacy and managed history formats."""
import copy
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

from test_outfit_wear import FakeQuery, WearTestFixture
from src.services import outfit_wear as wear


_stream = FakeQuery.stream


def firestore_order(value):
    if value is None:
        return (0, 0)
    if isinstance(value, bool):
        return (1, value)
    if isinstance(value, (int, float)):
        return (2, value)
    if isinstance(value, (datetime, date)):
        return (3, value.isoformat())
    if isinstance(value, str):
        return (4, value)
    return (10, repr(value))


def firestore_type_order_stream(query, transaction=None):
    """Model Firestore's mixed-type order: strings sort above numbers DESC.

    The ordinary fake uses Python sorting, which cannot compare these types.
    All filters and transactional version reads still run through that fake.
    """
    unordered = FakeQuery(query.db, query.name, query.filters, None, query.cap, query.cursor)
    snapshots = list(_stream(unordered, transaction))
    if query.ordering:
        field, direction = query.ordering
        snapshots.sort(
            key=lambda snap: firestore_order(snap.to_dict().get(field)),
            reverse=direction == "DESCENDING",
        )
    return iter(snapshots)


class MixedHistoryUndoTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        ordered = patch.object(FakeQuery, "stream", firestore_type_order_stream)
        ordered.start()
        self.addCleanup(ordered.stop)

    def legacy(self, key, worn_at, **overrides):
        self.db.seed("outfit_history", key, {
            "user_id": "owner", "outfit_id": "look", "date_worn": worn_at,
            "items": [{"id": "dress"}, {"id": "shoes"}], **overrides,
        })

    def test_undo_retains_newest_active_instant_not_highest_firestore_type(self):
        first = self.record()
        latest = self.record("next-day", now=self.now + timedelta(days=1))
        self.db.seed("outfit_history", "legacy-iso", {
            "user_id": "owner", "outfit_id": "look",
            "date_worn": (self.now - timedelta(days=30)).isoformat(),
            "items": [{"id": "dress"}, {"id": "shoes"}],
        })
        with patch.object(FakeQuery, "stream", firestore_type_order_stream):
            wear.undo_wear(self.db, "owner", latest["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], first["date_worn"])
        for item in ("dress", "shoes"):
            self.assertEqual(self.db.rows["wardrobe"][item]["lastWorn"], first["date_worn"])
        self.assertEqual(self.db.rows["outfits"]["look"]["wearCount"], 5)

    def test_supported_legacy_formats_choose_the_same_instant(self):
        instant = self.now + timedelta(days=1)
        formats = [instant, instant.replace(tzinfo=None), instant.isoformat(),
                   instant.astimezone(timezone(timedelta(hours=-4))).isoformat(),
                   instant.timestamp(), instant.timestamp() * 1000,
                   str(int(instant.timestamp())), str(int(instant.timestamp() * 1000)),
                   {"seconds": instant.timestamp(), "nanoseconds": 0},
                   {"_seconds": instant.timestamp(), "_nanoseconds": 0}]
        self.record()
        newest = self.record("newest", now=self.now + timedelta(days=2))
        before = copy.deepcopy(self.db.rows)
        for value in formats:
            with self.subTest(value=value):
                self.db.rows = copy.deepcopy(before)
                self.legacy("legacy", value)
                wear.undo_wear(self.db, "owner", newest["event_id"])
                expected = int(instant.timestamp() * 1000)
                self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], expected)
                for item in ("dress", "shoes"):
                    self.assertEqual(self.db.rows["wardrobe"][item]["lastWorn"], expected)

    def test_date_only_history_uses_its_saved_timezone(self):
        self.record()
        newest = self.record("newest", now=self.now + timedelta(days=3))
        before = copy.deepcopy(self.db.rows)
        for value in ("2026-09-23", date(2026, 9, 23)):
            with self.subTest(value=value):
                self.db.rows = copy.deepcopy(before)
                self.legacy("legacy-date", value, timezone="America/New_York")
                wear.undo_wear(self.db, "owner", newest["event_id"])
                expected = int(datetime(2026, 9, 23, 4, tzinfo=timezone.utc).timestamp() * 1000)
                self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], expected)

    def test_tombstones_and_conflicting_owners_never_replace_active_time(self):
        first = self.record()
        newest = self.record("newest", now=self.now + timedelta(days=2))
        middle = (self.now + timedelta(days=1)).isoformat()
        for field in ("undone", "deleted", "isDeleted", "deletedAt", "deleted_at"):
            self.legacy(field, middle, **{field: True})
        self.legacy("foreign", middle, user_id="other")
        self.legacy("conflicting", middle, userId="other")
        self.legacy("irrelevant", middle, outfit_id="another", items=[{"id": "another-item"}])
        wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], first["date_worn"])
        for item in ("dress", "shoes"):
            self.assertEqual(self.db.rows["wardrobe"][item]["lastWorn"], first["date_worn"])

    def test_shared_garment_history_does_not_change_other_outfit_or_items(self):
        first = self.record()
        newest = self.record("newest", now=self.now + timedelta(days=2))
        middle = self.now + timedelta(days=1)
        self.legacy("shared-dress", middle.isoformat(), outfit_id="another", item_ids=["dress"])
        wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], first["date_worn"])
        self.assertEqual(self.db.rows["wardrobe"]["shoes"]["lastWorn"], first["date_worn"])
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["lastWorn"], int(middle.timestamp() * 1000))

    def test_retains_unrepresented_baseline_but_clears_deleted_baseline(self):
        baseline = int((self.now - timedelta(days=1)).timestamp() * 1000)
        self.db.rows["outfits"]["look"]["lastWorn"] = baseline
        self.db.rows["wardrobe"]["dress"]["lastWorn"] = baseline
        event = self.record()
        before = copy.deepcopy(self.db.rows)
        wear.undo_wear(self.db, "owner", event["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], baseline)
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["lastWorn"], baseline)
        self.db.rows = before
        self.legacy("deleted-baseline", (self.now - timedelta(days=1)).isoformat(), deleted=True)
        wear.undo_wear(self.db, "owner", event["event_id"])
        self.assertIsNone(self.db.rows["outfits"]["look"]["lastWorn"])
        self.assertIsNone(self.db.rows["wardrobe"]["dress"]["lastWorn"])

    def test_empty_legacy_baselines_remain_absent(self):
        event = self.record()
        before = copy.deepcopy(self.db.rows)
        for value in (None, "", 0):
            with self.subTest(value=value):
                self.db.rows = copy.deepcopy(before)
                self.db.rows["outfits"]["look"]["wear_baseline_last_worn"] = value
                self.db.rows["wardrobe"]["dress"]["wear_baseline_last_worn"] = value
                wear.undo_wear(self.db, "owner", event["event_id"])
                self.assertIsNone(self.db.rows["outfits"]["look"]["lastWorn"])
                self.assertIsNone(self.db.rows["wardrobe"]["dress"]["lastWorn"])

    def test_malformed_item_membership_never_counts_as_a_garment_reference(self):
        first = self.record()
        newest = self.record("newest", now=self.now + timedelta(days=2))
        middle = (self.now + timedelta(days=1)).isoformat()
        self.legacy("string-ids", middle, outfit_id="another", item_ids="dress", items=None)
        self.legacy("mapping-items", middle, outfit_id="another", items={"dress": True})
        wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["lastWorn"], first["date_worn"])

    def test_undo_does_not_mutate_outfit_or_garment_with_conflicting_owner(self):
        event = self.record()
        self.db.rows["outfits"]["look"]["userId"] = "other"
        self.db.rows["wardrobe"]["dress"]["user_id"] = "other"
        outfit = copy.deepcopy(self.db.rows["outfits"]["look"])
        dress = copy.deepcopy(self.db.rows["wardrobe"]["dress"])
        rewards = copy.deepcopy(self.db.rows["reward_ledger"])
        wear.undo_wear(self.db, "owner", event["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"], outfit)
        self.assertEqual(self.db.rows["wardrobe"]["dress"], dress)
        self.assertEqual(self.db.rows["reward_ledger"], rewards)

    def test_tombstone_at_active_instant_cannot_erase_that_active_wear(self):
        baseline = int(self.now.timestamp() * 1000)
        self.db.rows["outfits"]["look"]["lastWorn"] = baseline
        first = self.record()
        newest = self.record("newest", now=self.now + timedelta(days=1))
        self.legacy("old-tombstone", self.now.isoformat(), undone=True)
        wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], first["date_worn"])

    def test_invalid_active_timestamp_fails_atomically_but_deleted_one_is_ignored(self):
        first = self.record()
        newest = self.record("newest", now=self.now + timedelta(days=1))
        self.legacy("broken", "not-a-date")
        before = copy.deepcopy(self.db.rows)
        with self.assertRaises(wear.OutfitWearError) as failure:
            wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertEqual(failure.exception.status_code, 409)
        self.assertEqual(self.db.rows, before)
        self.db.rows["outfit_history"]["broken"]["deleted"] = True
        wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], first["date_worn"])

    def test_chronology_repair_undo_replay_and_reactivation_do_not_reaward(self):
        first = self.record()
        newest = self.record("newest", now=self.now + timedelta(days=1))
        self.legacy("old-iso", (self.now - timedelta(days=30)).isoformat())
        rewards = copy.deepcopy(self.db.rows["reward_ledger"])
        user = copy.deepcopy(self.db.rows["users"]["owner"])
        wear.undo_wear(self.db, "owner", newest["event_id"])
        state = copy.deepcopy(self.db.rows)
        retry = wear.undo_wear(self.db, "owner", newest["event_id"])
        self.assertTrue(retry["already_recorded"])
        self.assertEqual(self.db.rows, state)
        replay = self.record("newest", now=self.now + timedelta(days=1))
        self.assertEqual(replay["rewards"]["xp_awarded"], 0)
        self.assertEqual(replay["rewards"]["tokens_awarded"], 0)
        self.assertEqual(replay["last_worn"], first["date_worn"])
        active = self.record("reactivate", now=self.now + timedelta(days=1))
        self.assertEqual(active["event_id"], newest["event_id"])
        self.assertEqual(active["rewards"]["xp_awarded"], 0)
        self.assertEqual(active["rewards"]["tokens_awarded"], 0)
        self.assertEqual(self.db.rows["reward_ledger"], rewards)
        self.assertEqual(self.db.rows["users"]["owner"], user)

    def test_newer_legacy_wear_remains_authoritative_after_undo(self):
        first = self.record()
        latest = self.record("next-day", now=self.now + timedelta(days=2))
        legacy_time = self.now + timedelta(days=1)
        self.db.seed("outfit_history", "legacy-iso", {
            "user_id": "owner", "outfit_id": "look",
            "date_worn": legacy_time.isoformat(),
            "items": [{"id": "dress"}, {"id": "shoes"}],
        })
        with patch.object(FakeQuery, "stream", firestore_type_order_stream):
            wear.undo_wear(self.db, "owner", latest["event_id"])
        expected = int(legacy_time.timestamp() * 1000)
        self.assertGreater(expected, first["date_worn"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], expected)
        self.assertEqual(self.db.rows["wardrobe"]["dress"]["lastWorn"], expected)

    def test_undone_baseline_cannot_erase_newer_active_wear(self):
        baseline = self.now - timedelta(days=5)
        self.db.rows["outfits"]["look"]["lastWorn"] = int(baseline.timestamp() * 1000)
        first = self.record()
        latest = self.record("next-day", now=self.now + timedelta(days=1))
        self.db.seed("outfit_history", "legacy-undone", {
            "user_id": "owner", "outfit_id": "look", "undone": True,
            "date_worn": baseline.isoformat(), "items": [{"id": "dress"}],
        })
        with patch.object(FakeQuery, "stream", firestore_type_order_stream):
            wear.undo_wear(self.db, "owner", latest["event_id"])
        self.assertEqual(self.db.rows["outfits"]["look"]["lastWorn"], first["date_worn"])
