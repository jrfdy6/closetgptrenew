"""Profile schema, transaction races and the actual verified HTTP boundary."""
import asyncio
import copy
from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.auth import verified_user
from src.routes import auth_working as legacy_route
from src.routes import user_profile as route
from src.services import user_profile as service
from src.services import onboarding_state
from test_onboarding_state import Database
from test_outfit_wear import transactional


class ProfileFixture(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        self.now = datetime(2026, 9, 22, 12, 30, tzinfo=timezone.utc)
        self.claims = {"uid": "owner", "email": "owner@example.test", "name": "Verified Name",
                       "iat": int(self.now.timestamp()), "firebase": {"sign_in_provider": "password"}}
        self.db.seed("users", "owner", {"name": "Entered Name", "gender": "Non-binary",
                     "measurements": {"height": "5'8\" - 5'11\"", "skinTone": "skin_tone_82"},
                     "stylePreferences": ["Minimalist"], "stylePersona": {"id": "saved-persona"},
                     "styleQuizSubmissionHash": "saved-receipt", "styleQuizCompletedAt": "2026-09-21T09:00:00Z",
                     "subscription": {"role": "tier1", "flatlays_remaining": 1}, "role": "tier1",
                     "created_at": self.now, "photos": {"fullBodyPhoto": "https://saved.test/owned"}})
        patcher = patch.object(service.firestore, "transactional", transactional)
        patcher.start()
        self.addCleanup(patcher.stop)

    @property
    def stored(self):
        return self.db.rows["users"]["owner"]

    def save(self, body=None):
        return service.persist_profile(self.db, self.claims, body, now=self.now)


class ProfilePersistenceTests(ProfileFixture):
    def test_read_retains_schema_and_normalizes_identity_without_writing(self):
        original = copy.deepcopy(self.db.rows)
        result = self.save()
        self.assertEqual(self.db.rows, original)
        self.assertEqual(result["userId"], "owner")
        self.assertEqual(result["name"], "Entered Name")
        for key in ("measurements", "stylePreferences", "stylePersona", "subscription", "photos"):
            self.assertEqual(result[key], self.stored[key])

    def test_historical_timestamps_keep_seconds_and_fall_back_to_valid_alias(self):
        seconds = int(self.now.timestamp())
        values = [self.now, self.now.replace(tzinfo=None), seconds, seconds * 1000,
                  str(seconds), str(seconds * 1000), self.now.isoformat(),
                  {"seconds": seconds}, {"_seconds": seconds}]
        for value in values:
            with self.subTest(value=value):
                result = service.normalize_profile({"created_at": value, "updatedAt": value}, self.claims)
                self.assertEqual((result["created_at"], result["updated_at"]), (seconds, seconds))
        result = service.normalize_profile({"created_at": "invalid", "createdAt": self.now}, self.claims)
        self.assertEqual(result["created_at"], seconds)

    def test_partial_save_preserves_entered_name_derived_profile_and_receipts(self):
        measurements = copy.deepcopy(self.stored["measurements"])
        result = self.save({"gender": "Female", "measurements": {"topSize": "M"}})
        self.assertEqual(result["name"], "Entered Name")
        self.assertEqual(result["measurements"], {**measurements, "topSize": "M"})
        self.assertEqual(result["styleQuizSubmissionHash"], "saved-receipt")
        self.assertEqual(result["stylePersona"], {"id": "saved-persona"})
        self.assertEqual(result["created_at"], int(self.now.timestamp()))
        self.assertEqual(result["gender"], "Female")

    def test_whole_form_echo_cannot_change_account_authority_or_quiz_and_photo_records(self):
        protected = {key: copy.deepcopy(value) for key, value in self.stored.items()
                     if key in ("subscription", "role", "stylePersona", "styleQuizSubmissionHash", "styleQuizCompletedAt", "photos", "created_at")}
        result = self.save({**self.save(), "name": "New Name", "role": "admin", "admin": True,
                           "subscription": {"role": "admin", "flatlays_remaining": 999},
                           "flatlays_remaining": 999, "credits": 999, "quota": 999,
                           "stylePersona": {"id": "forged"}, "styleQuizSubmissionHash": "forged",
                           "styleQuizCompletedAt": "2099-01-01", "onboardingCompleted": True,
                           "photos": {"fullBodyPhoto": "https://foreign.test/photo"},
                           "avatarUrl": "https://foreign.test/avatar", "email": "foreign@example.test",
                           "createdAt": 1, "created_at": 1})
        self.assertEqual(result["name"], "New Name")
        for key, value in protected.items():
            self.assertEqual(self.stored[key], value, key)
        for key in ("admin", "credits", "quota", "flatlays_remaining", "onboardingCompleted", "avatarUrl", "createdAt"):
            self.assertNotIn(key, self.stored)
        self.assertEqual(result["email"], "owner@example.test")

    def test_new_profile_ignores_completion_forgeries_and_saves_signup_name(self):
        self.db.rows["users"].pop("owner")
        result = self.save({"name": "Signup Name", "styleQuizSubmissionHash": "forged",
                            "styleQuizCompletedAt": "2099-01-01", "admin": True})
        self.assertEqual(result["name"], "Signup Name")
        self.assertEqual(result["userId"], "owner")
        self.assertNotIn("styleQuizCompletedAt", self.stored)
        self.assertNotIn("admin", self.stored)

    def test_fresh_profile_style_aliases_cannot_create_onboarding_completion(self):
        for existing in ({}, {"name": "Signup Name"}, {"stylePreferences": [], "preferences": {"style": [" "]}}):
            for attempted in ({"stylePreferences": ["Minimalist"]}, {"preferences": {"style": ["Minimalist"]}},
                              {"stylePreferences": ["Minimalist"], "preferences": {"style": ["Classic"], "colors": ["Blue"]},
                               "stylePersona": {"id": "forged"}, "styleQuizCompletedAt": "2026-09-22"}):
                with self.subTest(existing=existing, attempted=attempted):
                    self.db.seed("users", "owner", existing)
                    self.save({"name": "Signup Name", **attempted})
                    readback = self.save()
                    self.assertEqual(readback["name"], "Signup Name")
                    self.assertFalse(onboarding_state.has_style_profile(readback))
                    read = onboarding_state.read_onboarding_state(self.db, "owner")
                    reconciled = onboarding_state.reconcile_onboarding_state(self.db, "owner")
                    for state in (read, reconciled):
                        self.assertFalse(state["profileComplete"])
                        self.assertEqual(state["stage"], "style")
                        self.assertIsNone(state["milestones"]["styleCompletedAt"])
                    self.assertNotIn("onboarding_states", self.db.rows)

    def test_name_only_signup_remains_incomplete_and_preserves_name(self):
        self.db.rows["users"].pop("owner")
        self.save({"name": "Signup Name"})
        result = onboarding_state.reconcile_onboarding_state(self.db, "owner")
        self.assertEqual(self.save()["name"], "Signup Name")
        self.assertFalse(result["profileComplete"])
        self.assertEqual(result["stage"], "style")
        self.assertNotIn("onboarding_states", self.db.rows)

    def test_completed_and_legacy_profiles_can_edit_both_style_aliases(self):
        evidence = ({"styleQuizCompletedAt": "2026-09-21T09:00:00Z"},
                    {"stylePersona": {"id": "legacy-persona"}}, {"stylePersona": "legacy-persona"},
                    {"stylePreferences": ["Legacy"]}, {"style_preferences": ["Legacy"]},
                    {"preferences": {"style": ["Legacy"]}})
        for existing in evidence:
            with self.subTest(existing=existing):
                self.db.seed("users", "owner", existing)
                result = self.save({"stylePreferences": ["Classic"], "preferences": {"style": ["Modern"]}})
                self.assertEqual(result["stylePreferences"], ["Classic"])
                self.assertEqual(result["preferences"]["style"], ["Modern"])
                self.assertTrue(onboarding_state.has_style_profile(result))

    def test_style_edit_guard_rechecks_stored_completion_after_transaction_conflict(self):
        self.db.before_commit = lambda db: db.seed("users", "owner", {"name": "Incomplete"})
        result = self.save({"name": "Saved Name", "stylePreferences": ["Classic"],
                            "preferences": {"style": ["Modern"], "colors": ["Blue"]}})
        self.assertEqual(self.db.conflicts, 1)
        self.assertEqual(result["name"], "Saved Name")
        self.assertEqual(result["preferences"]["colors"], ["Blue"])
        self.assertFalse(onboarding_state.has_style_profile(result))
        self.assertFalse(onboarding_state.reconcile_onboarding_state(self.db, "owner")["profileComplete"])

    def test_get_seed_racing_quiz_creation_returns_concurrent_profile_without_replacing_it(self):
        self.db.rows["users"].pop("owner")
        quiz = {"name": "Concurrent Quiz", "styleQuizSubmissionHash": "new-receipt",
                "stylePersona": {"id": "concurrent"}, "createdAt": 1234567890000}
        self.db.before_commit = lambda db: db.seed("users", "owner", quiz)
        result = self.save()
        self.assertEqual(self.stored, quiz)
        self.assertEqual(result["name"], "Concurrent Quiz")
        self.assertEqual(self.db.conflicts, 1)

    def test_post_racing_quiz_preserves_new_receipt_and_unedited_nested_values(self):
        def concurrent(db):
            db.seed("users", "owner", {**self.stored, "styleQuizSubmissionHash": "new-receipt",
                    "stylePersona": {"id": "concurrent"}, "measurements": {"height": "6'0\" - 6'3\""}})
        self.db.before_commit = concurrent
        result = self.save({"name": "Saved Name"})
        self.assertEqual(result["name"], "Saved Name")
        self.assertEqual(result["styleQuizSubmissionHash"], "new-receipt")
        self.assertEqual(result["stylePersona"], {"id": "concurrent"})
        self.assertEqual(result["measurements"], {"height": "6'0\" - 6'3\""})

    def test_unknown_nested_fields_are_not_mass_assigned_and_raw_measurements_survive(self):
        self.save({"measurements": {"height": "Prefer not to say", "plusSize": False, "role": "admin"},
                   "preferences": {"style": ["Minimalist"], "admin": True}})
        self.assertNotIn("role", self.stored["measurements"])
        self.assertNotIn("admin", self.stored["preferences"])
        self.assertEqual(self.stored["measurements"]["height"], "Prefer not to say")
        self.assertFalse(self.stored["measurements"]["plusSize"])

    def test_spending_change_queues_atomically_and_no_op_retries_keep_request_time(self):
        self.stored.update(spending_ranges={"tops": "$50-100", "shoes": "$100-200"},
                           tveRecalcStatus="completed", tveRecalcRequestedAt=123)
        result = self.save({"spending_ranges": {"tops": "$100-150"}})
        self.assertEqual(result["spending_ranges"], {"tops": "$100-150", "shoes": "$100-200"})
        self.assertEqual(result["tveRecalcStatus"], "queued")
        queued_at = int(self.now.timestamp())
        self.assertEqual(self.stored["tveRecalcRequestedAt"], queued_at)
        for body in ({"name": "Changed Name"}, {"spending_ranges": {"tops": "$100-150"}},
                     {"spending_ranges": {"admin": True}, "tveRecalcRequestedAt": 999}):
            service.persist_profile(self.db, self.claims, body, now=self.now + timedelta(seconds=60))
            self.assertEqual(self.stored["tveRecalcRequestedAt"], queued_at)
        original = copy.deepcopy(self.stored)
        self.db.fail_at_write = 0
        with self.assertRaises(Exception):
            self.save({"spending_ranges": {"shoes": "$200-300"}})
        self.assertEqual(self.stored, original)

    def test_retry_compares_spending_ranges_against_concurrent_committed_save(self):
        self.stored.update(spending_ranges={"tops": "$50-100"}, tveRecalcStatus="completed")
        def concurrent(db):
            db.seed("users", "owner", {**self.stored, "spending_ranges": {"tops": "$100-150"},
                                       "tveRecalcStatus": "queued", "tveRecalcRequestedAt": 456})
        self.db.before_commit = concurrent
        result = self.save({"spending_ranges": {"tops": "$100-150"}, "name": "Saved Name"})
        self.assertEqual(result["tveRecalcRequestedAt"], 456)
        self.assertEqual(result["name"], "Saved Name")
        self.assertEqual(self.db.conflicts, 1)


class ProfileHTTPTests(ProfileFixture):
    def setUp(self):
        super().setUp()
        app = FastAPI()
        app.include_router(route.router, prefix="/api/user")
        app.include_router(legacy_route.router, prefix="/api/auth")
        self.client = TestClient(app)
        verifier = patch.object(verified_user.auth, "verify_id_token", return_value=self.claims)
        self.verify = verifier.start()
        self.addCleanup(verifier.stop)
        database = patch.object(route, "profile_database", return_value=self.db)
        self.database = database.start()
        self.addCleanup(database.stop)
        self.headers = {"Authorization": "Bearer actual-token"}

    def test_profile_storage_runs_outside_request_event_loop(self):
        on_request_loop = []
        def persist(*args, **kwargs):
            try:
                asyncio.get_running_loop()
                on_request_loop.append(True)
            except RuntimeError:
                on_request_loop.append(False)
            return service.persist_profile(*args, **kwargs)
        with patch.object(route, "persist_profile", side_effect=persist):
            for method, path in (("get", "/api/user/profile"), ("post", "/api/user/profile"),
                                 ("get", "/api/auth/profile"), ("put", "/api/auth/profile")):
                with self.subTest(method=method, path=path):
                    options = {"json": {"name": "Saved Name"}} if method != "get" else {}
                    response = getattr(self.client, method)(path, headers=self.headers, **options)
                    self.assertEqual(response.status_code, 200)
                    self.assertFalse(on_request_loop[-1])
        self.assertEqual(len(on_request_loop), 4)

    def test_valid_read_and_save_use_real_revocation_verification_and_private_readback(self):
        result = self.client.get("/api/user/profile", headers=self.headers)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers["cache-control"], "private, no-store")
        self.verify.assert_called_with("actual-token", check_revoked=True)
        saved = self.client.post("/api/user/profile", headers=self.headers, json={"name": "Saved Name"})
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json()["name"], "Saved Name")
        self.assertEqual(self.client.get("/api/user/profile", headers=self.headers).json()["name"], "Saved Name")

    def test_every_identity_override_is_rejected_before_database_access(self):
        for key in ("userId", "user_id", "firebase_uid", "uid"):
            with self.subTest(key=key):
                self.assertEqual(self.client.post("/api/user/profile", headers=self.headers, json={key: "foreign"}).status_code, 403)
                self.assertEqual(self.client.get("/api/user/profile", headers=self.headers, params={key: "foreign"}).status_code, 403)
        for key in ("x-user-id", "x-userid", "x-firebase-uid", "user-id", "userid", "user_id", "firebase_uid", "uid"):
            self.assertEqual(self.client.get("/api/user/profile", headers={**self.headers, key: "foreign"}).status_code, 403)
        self.database.assert_not_called()

    def test_missing_forged_revoked_disabled_and_anonymous_auth_never_reach_storage(self):
        for header in ({}, {"Authorization": "Bearer test"}, {"Authorization": "Basic actual-token"}):
            self.assertEqual(self.client.get("/api/user/profile", headers=header).status_code, 401)
        for error in (verified_user.auth.InvalidIdTokenError("private"),
                      verified_user.auth.RevokedIdTokenError("private"),
                      verified_user.auth.UserDisabledError("private")):
            self.verify.side_effect = error
            self.assertEqual(self.client.post("/api/user/profile", headers=self.headers, json={"name": "No"}).status_code, 401)
        self.verify.side_effect = None
        self.verify.return_value = {**self.claims, "firebase": {"sign_in_provider": "anonymous"}}
        self.assertEqual(self.client.get("/api/user/profile", headers=self.headers).status_code, 403)
        self.database.assert_not_called()

    def test_verified_token_is_rechecked_on_each_request_without_prefix_cache(self):
        self.assertEqual(self.client.get("/api/user/profile", headers=self.headers).status_code, 200)
        self.verify.side_effect = verified_user.auth.RevokedIdTokenError("private")
        self.assertEqual(self.client.get("/api/user/profile", headers=self.headers).status_code, 401)
        self.assertEqual(self.verify.call_count, 2)
        self.assertEqual(self.database.call_count, 1)

    def test_two_accounts_with_shared_jwt_prefix_never_share_profile_reads(self):
        self.db.seed("users", "other", {"name": "Other Name"})
        first = self.client.get("/api/user/profile", headers=self.headers)
        self.verify.return_value = {**self.claims, "uid": "other"}
        second = self.client.get("/api/user/profile", headers={"Authorization": "Bearer actual-token-other"})
        self.assertEqual(first.json()["name"], "Entered Name")
        self.assertEqual(second.json()["name"], "Other Name")
        self.assertEqual(second.json()["userId"], "other")

    def test_bad_json_shapes_and_invalid_edit_values_return_422_without_writes(self):
        original = copy.deepcopy(self.db.rows)
        for payload in (None, [], "text", {"name": {}}, {"measurements": []}, {"stylePreferences": [False]}):
            self.assertEqual(self.client.post("/api/user/profile", headers=self.headers, json=payload).status_code, 422)
        self.assertEqual(self.client.post("/api/user/profile", headers=self.headers, content="{").status_code, 422)
        self.assertEqual(self.db.rows, original)

    def test_failure_is_not_a_success_and_lost_ack_can_be_confirmed_by_readback(self):
        before = copy.deepcopy(self.db.rows)
        self.db.fail_at_write = 0
        result = self.client.post("/api/user/profile", headers=self.headers, json={"name": "Not Saved"})
        self.assertEqual(result.status_code, 503)
        self.assertEqual(self.db.rows, before)
        self.assertNotIn("private", result.text)
        self.db.fail_at_write = None
        self.db.lose_ack = True
        self.assertEqual(self.client.post("/api/user/profile", headers=self.headers, json={"name": "Committed"}).status_code, 503)
        self.assertEqual(self.client.get("/api/user/profile", headers=self.headers).json()["name"], "Committed")

    def test_identity_service_outage_returns_503_without_downgrading_to_a_hint(self):
        self.verify.side_effect = RuntimeError("private service outage")
        result = self.client.get("/api/user/profile", headers={**self.headers, "x-user-id": "owner"})
        self.assertEqual(result.status_code, 503)
        self.database.assert_not_called()
        self.assertNotIn("private service outage", result.text)

    def test_exhausted_database_transaction_is_unavailable_not_invalid_input(self):
        with patch.object(route, "persist_profile", side_effect=ValueError("Failed to commit in 5 attempts")):
            result = self.client.post("/api/user/profile", headers=self.headers, json={"name": "Valid Name"})
        self.assertEqual(result.status_code, 503)
        self.assertNotIn("5 attempts", result.text)

    def test_both_profile_write_routes_cannot_shortcut_a_fresh_quiz(self):
        for method, path in (("post", "/api/user/profile"), ("put", "/api/auth/profile")):
            with self.subTest(method=method):
                self.db.seed("users", "owner", {"name": "Fresh"})
                response = getattr(self.client, method)(path, headers=self.headers, json={
                    "name": "Signup Name", "stylePreferences": ["Minimalist"],
                    "preferences": {"style": ["Classic"]}, "styleQuizCompletedAt": "forged"})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["name"], "Signup Name")
                self.assertFalse(onboarding_state.has_style_profile(response.json()))
                self.assertFalse(onboarding_state.reconcile_onboarding_state(self.db, "owner")["profileComplete"])
                self.assertNotIn("onboarding_states", self.db.rows)

    def test_legacy_get_keeps_active_dashboard_and_persona_schema(self):
        before = copy.deepcopy(self.stored)
        result = self.client.get("/api/auth/profile", headers=self.headers)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers["cache-control"], "private, no-store")
        self.verify.assert_called_once_with("actual-token", check_revoked=True)
        for key in ("measurements", "stylePreferences", "stylePersona", "styleQuizSubmissionHash", "subscription"):
            self.assertEqual(result.json()[key], before[key])
        self.assertEqual(self.stored, before)
        self.assertEqual(result.json()["created_at"], int(self.now.timestamp()))

    def test_legacy_put_preserves_authority_and_returns_actual_wardrobe_aliases(self):
        self.stored.update(wardrobeItemCount=12, spending_ranges={"tops": "$50-100"})
        protected = {key: copy.deepcopy(self.stored[key]) for key in
                     ("created_at", "subscription", "stylePersona", "styleQuizSubmissionHash", "photos")}
        result = self.client.put("/api/auth/profile", headers=self.headers, json={
            "name": "Legacy Save", "heightFeetInches": "5 feet 10 inches", "stylePreferences": ["Classic"],
            "spending_ranges": {"tops": "$100-150"}, "email": "foreign@example.test",
            "wardrobeItemCount": 999, "wardrobeCount": 999, "wardrobe_count": 999,
            "created_at": 1, "updated_at": 1, "subscription": {"role": "admin"},
            "stylePersona": {"id": "forged"}, "styleQuizSubmissionHash": "forged",
            "photos": {}, "avatar_url": "https://foreign.test/photo", "admin": True})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["wardrobeCount"], 12)
        self.assertEqual(result.json()["wardrobe_count"], 12)
        self.assertEqual(result.json()["tveRecalcStatus"], "queued")
        self.assertEqual(result.json()["name"], "Legacy Save")
        self.assertEqual(result.json()["heightFeetInches"], "5 feet 10 inches")
        self.assertNotEqual(result.json()["updated_at"], 1)
        for key, value in protected.items():
            self.assertEqual(self.stored[key], value, key)
        self.assertNotIn("admin", self.stored)
        self.assertNotIn("avatar_url", self.stored)
        readback = self.client.get("/api/user/profile", headers=self.headers)
        self.assertEqual(readback.json()["name"], "Legacy Save")
        self.assertEqual(readback.json()["stylePreferences"], ["Classic"])

    def test_legacy_routes_reject_invalid_auth_and_every_spoof_channel(self):
        for method in ("get", "put"):
            request = getattr(self.client, method)
            kwargs = {"json": {"name": "No"}} if method == "put" else {}
            for headers in ({}, {"Authorization": "Bearer test"}, {"Authorization": "Basic actual-token"}):
                self.assertEqual(request("/api/auth/profile", headers=headers, **kwargs).status_code, 401)
            for error in (verified_user.auth.InvalidIdTokenError("private"),
                          verified_user.auth.RevokedIdTokenError("private"),
                          verified_user.auth.UserDisabledError("private")):
                self.verify.side_effect = error
                self.assertEqual(request("/api/auth/profile", headers=self.headers, **kwargs).status_code, 401)
            self.verify.side_effect = None
            self.verify.return_value = {**self.claims, "firebase": {"sign_in_provider": "anonymous"}}
            self.assertEqual(request("/api/auth/profile", headers=self.headers, **kwargs).status_code, 403)
            self.verify.return_value = self.claims
            for key in ("userId", "user_id", "firebase_uid", "uid"):
                self.assertEqual(request("/api/auth/profile", headers=self.headers, params={key: "foreign"}, **kwargs).status_code, 403)
            for key in ("x-user-id", "x-userid", "x-firebase-uid", "user-id", "userid", "user_id", "firebase_uid", "uid"):
                self.assertEqual(request("/api/auth/profile", headers={**self.headers, key: "foreign"}, **kwargs).status_code, 403)
        for key in ("userId", "user_id", "firebase_uid", "uid"):
            self.assertEqual(self.client.put("/api/auth/profile", headers=self.headers, json={key: "foreign"}).status_code, 403)
        self.database.assert_not_called()

    def test_legacy_storage_outage_does_not_return_token_only_success(self):
        with patch.object(route, "persist_profile", side_effect=ValueError("Failed to commit in 5 attempts")):
            read = self.client.get("/api/auth/profile", headers=self.headers)
            save = self.client.put("/api/auth/profile", headers=self.headers, json={"name": "Valid Name"})
        self.assertEqual(read.status_code, 503)
        self.assertEqual(save.status_code, 503)
        self.assertNotIn("Verified Name", read.text)
        self.assertNotIn("5 attempts", save.text)

    def test_legacy_put_rejects_invalid_payload_without_writing(self):
        before = copy.deepcopy(self.stored)
        for body in ([], {"name": {}}, {"spending_ranges": []}):
            self.assertEqual(self.client.put("/api/auth/profile", headers=self.headers, json=body).status_code, 422)
        self.assertEqual(self.client.put("/api/auth/profile", headers=self.headers, content="{").status_code, 422)
        self.assertEqual(self.stored, before)


if __name__ == "__main__":
    unittest.main()
