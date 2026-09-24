"""Accepted TS golden parity plus credential-free HTTP/atomic persistence tests."""
import copy
from concurrent.futures import ThreadPoolExecutor
import functools
import hashlib
import json
from pathlib import Path
import threading
from types import ModuleType
import unittest
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from firebase_admin import auth

from src.auth import verified_user
from src.routes import style_quiz as route
from src.services import quiz_profile as quiz


FIXTURE = json.loads((Path(__file__).parent / "fixtures/quiz-profile-parity.json").read_text())
IDENTITY = {"uid": "verified-owner", "name": "Alex Élan", "email": "alex@example.test"}


def payload(gender="Male"):
    value = copy.deepcopy(next(case["input"] for case in FIXTURE["cases"] if case["name"] == "full-" + gender))
    value["answers"] = [{"question_id": key, "selected_option": answer} for key, answer in value["answers"].items()]
    return value


def merge_maps(original, update):
    result = copy.deepcopy(original)
    for key, value in update.items():
        result[key] = merge_maps(result.get(key, {}), value) if isinstance(value, dict) and isinstance(result.get(key, {}), dict) else copy.deepcopy(value)
    return result


class Conflict(Exception):
    pass


class Reference:
    def __init__(self, db, collection, uid):
        self.db, self.path = db, (collection, uid)

    def get(self, transaction):
        self.db.reads += 1
        if self.db.fail_read:
            raise RuntimeError("private Firestore read failure")
        with self.db.lock:
            transaction.version = self.db.version
            value = copy.deepcopy(self.db.rows.get(self.path))
        class Snapshot:
            exists = value is not None
            def to_dict(self):
                return copy.deepcopy(value)
        return Snapshot()


class Transaction:
    def __init__(self, db):
        self.db, self.version, self.writes = db, None, []

    def set(self, reference, value, merge=False):
        self.writes.append((reference.path, copy.deepcopy(value), merge))

    def commit(self):
        with self.db.lock:
            if self.db.version != self.version:
                self.db.conflicts += 1
                raise Conflict()
            if self.db.fail_commit:
                raise RuntimeError("private Firestore commit failure")
            for path, value, merge in self.writes:
                self.db.rows[path] = merge_maps(self.db.rows.get(path, {}), value) if merge else value
                self.db.version += 1
                self.db.committed_writes += 1
            if self.writes and self.db.lose_ack:
                self.db.lose_ack = False
                raise RuntimeError("committed but acknowledgment was lost")


def transactional(function):
    @functools.wraps(function)
    def run(transaction):
        for attempt in range(8):
            result = function(transaction)
            if attempt == 0 and transaction.db.barrier:
                transaction.db.barrier.wait(timeout=5)
            try:
                transaction.commit()
                return result
            except Conflict:
                transaction = Transaction(transaction.db)
        raise AssertionError("Exhausted optimistic retries")
    return run


class Database:
    def __init__(self, stored=None):
        self.rows = {} if stored is None else {("users", IDENTITY["uid"]): copy.deepcopy(stored)}
        self.version = self.reads = self.committed_writes = self.conflicts = 0
        self.fail_read = self.fail_commit = self.lose_ack = False
        self.barrier = None
        self.lock = threading.RLock()

    def collection(self, collection):
        db = self
        class Collection:
            def document(self, uid):
                return Reference(db, collection, uid)
        return Collection()

    def transaction(self):
        return Transaction(self)

    @property
    def profile(self):
        return self.rows.get(("users", IDENTITY["uid"]), {})


class QuizGoldenParityTests(unittest.TestCase):
    def test_189_outputs_hashes_and_canonical_bytes_match_executed_accepted_typescript(self):
        self.assertEqual(len(FIXTURE["cases"]), 189)
        for case in FIXTURE["cases"]:
            with self.subTest(case=case["name"]):
                submission = case["input"]
                actual = quiz.map_quiz_answers_to_profile(submission["answers"], submission["colorAnalysis"], submission["stylePreferences"], submission["colorPreferences"], IDENTITY["name"], IDENTITY["email"], IDENTITY["uid"], submission["spending_ranges"], now=FIXTURE["now_seconds"])
                self.assertEqual(actual, case["profile"])
                self.assertEqual(quiz.submission_hash(submission, submission["answers"]), case["hash"])
                hash_input = {"answers": submission["answers"], "stylePreferences": submission["stylePreferences"], "colorPreferences": submission["colorPreferences"], "colorAnalysis": submission["colorAnalysis"], "spendingRanges": submission["spending_ranges"]}
                self.assertEqual(quiz.js_json(hash_input, canonical=True), case["canonical"])

    def test_question_ids_are_exactly_the_accepted_four_gender_variants(self):
        self.assertEqual(quiz.REQUIRED_QUESTION_IDS, FIXTURE["required_question_ids"])
        self.assertEqual({gender: len(ids) for gender, ids in quiz.REQUIRED_QUESTION_IDS.items()}, {"Male": 25, "Female": 27, "Non-binary": 35, "Prefer not to say": 35})

    def test_frozen_fixture_records_the_unchanged_typescript_source(self):
        root = Path(__file__).resolve().parents[2]
        for relative, expected in FIXTURE["source_sha256"].items():
            # Frontend sources are absent in an API-only container; the Node
            # parity suite also runs this check on the full repository source.
            path = root / relative
            if path.exists():
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_canonical_object_order_is_irrelevant_but_array_order_and_empty_objects_are_not(self):
        original = payload()
        answers = quiz.validate_submission(original, IDENTITY)
        reordered = copy.deepcopy(original)
        reordered["spending_ranges"] = dict(reversed(list(reordered["spending_ranges"].items())))
        self.assertEqual(quiz.submission_hash(original, answers), quiz.submission_hash(reordered, dict(reversed(list(answers.items())))))
        reordered["colorPreferences"].reverse()
        self.assertNotEqual(quiz.submission_hash(original, answers), quiz.submission_hash(reordered, answers))
        self.assertNotEqual(quiz.submission_hash({"colorAnalysis": {}}, answers), quiz.submission_hash({"colorAnalysis": None}, answers))


class QuizTransactionTests(unittest.TestCase):
    def setUp(self):
        self.decorator = patch.object(quiz.firestore, "transactional", transactional)
        self.decorator.start()
        self.addCleanup(self.decorator.stop)

    def save(self, db, body=None, **kwargs):
        return quiz.save_quiz_profile(db, IDENTITY, payload() if body is None else body, now=1790100000, **kwargs)

    def test_all_four_full_quizzes_persist_identity_schema_and_timestamp_without_completing_capsule(self):
        for gender in quiz.REQUIRED_QUESTION_IDS:
            with self.subTest(gender=gender):
                db = Database({"created_at": 100, "name": "old name", "measurements": {"customFit": "saved"}, "preferences": {"custom": True}, "subscription": {"tier": "paid"}})
                response = self.save(db, payload(gender))
                self.assertEqual(response["persisted"], True)
                self.assertEqual(db.committed_writes, 1)
                self.assertEqual(db.profile["created_at"], 100)
                self.assertEqual(db.profile["name"], IDENTITY["name"])
                self.assertEqual(db.profile["measurements"]["customFit"], "saved")
                self.assertEqual(db.profile["preferences"]["custom"], True)
                self.assertEqual(db.profile["subscription"], {"tier": "paid"})
                self.assertEqual(db.profile["styleQuizCompletedAt"], 1790100000)
                self.assertEqual(db.profile["updatedAt"], db.profile["updated_at"])
                self.assertNotIn("onboardingCompleted", db.profile)
                self.assertEqual(set(db.rows), {("users", "verified-owner")})

    def test_old_typescript_receipt_replays_without_another_write_or_retake_flag(self):
        case = FIXTURE["cases"][0]
        stored = {**case["profile"], "styleQuizSubmissionHash": case["hash"], "styleQuizCompletedAt": 12}
        db = Database(stored)
        response = self.save(db)
        self.assertTrue(response["persisted"])
        self.assertEqual(db.committed_writes, 0)
        self.assertEqual(db.profile, stored)

    def test_retake_required_for_every_supported_existing_style_evidence(self):
        for profile in ({"stylePersona": {"id": "classic"}}, {"stylePersona": {"name": "Classic"}}, {"stylePersona": "Classic"}, {"stylePreferences": ["minimal"]}, {"style_preferences": ["minimal"]}, {"preferences": {"style": ["minimal"]}}, {"styleQuizCompletedAt": 1}):
            with self.subTest(profile=profile):
                db = Database(profile)
                with self.assertRaises(quiz.QuizSubmissionError) as raised:
                    self.save(db)
                self.assertEqual((raised.exception.status_code, raised.exception.code), (409, "RETAKE_REQUIRED"))
                self.assertEqual(db.committed_writes, 0)
                body = payload(); body["retake"] = True
                self.assertTrue(self.save(db, body)["persisted"])

    def test_retake_string_or_integer_is_not_an_explicit_retake(self):
        for retake in (1, "true", "1"):
            db = Database({"stylePersona": {"id": "classic"}})
            with self.assertRaises(quiz.QuizSubmissionError):
                self.save(db, {**payload(), "retake": retake})
            self.assertEqual(db.committed_writes, 0)

    def test_preserves_omitted_optional_fields_and_prior_creation_zero(self):
        db = Database({"created_at": 0, "createdAt": 1, "measurements": {"braSize": "saved-size", "customFit": "saved"}, "preferences": {"colors": ["burgundy"], "custom": True}})
        body = payload(); body["colorPreferences"] = []; body["colorAnalysis"] = None
        self.save(db, body)
        self.assertEqual(db.profile["created_at"], 0)
        self.assertEqual(db.profile["measurements"]["braSize"], "saved-size")
        self.assertEqual(db.profile["preferences"]["colors"], ["burgundy"])

    def test_created_at_falls_back_to_createdAt_and_name_to_saved_name_then_verified_email(self):
        for stored, name in (({"createdAt": 12, "name": "Entered Name"}, "Entered Name"), ({"createdAt": 12}, "alex")):
            db = Database(stored)
            quiz.save_quiz_profile(db, {"uid": IDENTITY["uid"], "email": IDENTITY["email"]}, payload(), now=50)
            self.assertEqual(db.profile["name"], name)
            self.assertEqual(db.profile["created_at"], 12)

    def test_spending_tve_fields_follow_existing_change_contract_and_replay_does_not_requeue(self):
        body = payload()
        db = Database({"spending_ranges": body["spending_ranges"], "tveRecalcStatus": "complete"})
        self.save(db, body)
        self.assertEqual(db.profile["tveRecalcStatus"], "complete")
        self.assertNotIn("tveRecalcRequestedAt", db.profile)
        changed = copy.deepcopy(body); changed["spending_ranges"]["tops"] = "$500-$1,000"; changed["retake"] = True
        self.save(db, changed)
        self.assertEqual(db.profile["tveRecalcStatus"], "queued")
        self.assertEqual(db.profile["tveRecalcRequestedAt"], 1790100000)
        count = db.committed_writes
        self.save(db, changed)
        self.assertEqual(db.committed_writes, count)

    def test_concurrent_identical_submission_commits_once_then_replays(self):
        db = Database(); db.barrier = threading.Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.save(db), range(2)))
        self.assertEqual(results[0], results[1])
        self.assertEqual(db.committed_writes, 1)
        self.assertEqual(db.conflicts, 1)

    def test_concurrent_different_submissions_cannot_silently_replace_each_other(self):
        db = Database(); db.barrier = threading.Barrier(2)
        bodies = [payload(), {**payload(), "stylePreferences": ["Classic Elegant"]}]
        def save(body):
            try:
                return self.save(db, body)["success"]
            except quiz.QuizSubmissionError as error:
                return error.code
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(save, bodies))
        self.assertCountEqual(results, [True, "RETAKE_REQUIRED"])
        self.assertEqual(db.committed_writes, 1)


class QuizHttpTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
        config = ModuleType("src.config.firebase"); config.db = self.db
        for patcher in (patch.dict("sys.modules", {"src.config.firebase": config}), patch.object(quiz.firestore, "transactional", transactional)):
            patcher.start(); self.addCleanup(patcher.stop)
        patcher = patch.object(verified_user.auth, "verify_id_token", return_value=IDENTITY)
        self.verify = patcher.start(); self.addCleanup(patcher.stop)
        app = FastAPI(); app.include_router(route.router, prefix="/api/style-quiz")
        self.client = TestClient(app)

    def post(self, body=None, authorization="Bearer signed-token", **kwargs):
        headers = kwargs.pop("headers", {})
        if authorization is not None:
            headers["authorization"] = authorization
        return self.client.post("/api/style-quiz/submit", json=payload() if body is None else body, headers=headers, **kwargs)

    def test_verified_bearer_is_checked_for_revocation_and_response_preserves_schema(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.verify.assert_called_once_with("signed-token", check_revoked=True)
        self.assertEqual(response.headers["cache-control"], "private, no-store")
        self.assertEqual(set(response.json()), {"success", "persisted", "message", "hybridStyleName", "quizResults", "colorAnalysis"})

    def test_missing_malformed_test_and_body_tokens_never_authorize_a_write(self):
        for authorization in (None, "", "Basic value", "Bearer", "Bearer a b", "Bearer test", "Bearer TEST"):
            with self.subTest(authorization=authorization):
                self.assertEqual(self.post({**payload(), "token": "body-token"}, authorization).status_code, 401)
        self.verify.assert_not_called()
        self.assertEqual(self.db.reads, 0)

    def test_invalid_revoked_expired_disabled_and_anonymous_tokens_fail_closed(self):
        for failure in (auth.InvalidIdTokenError("invalid"), auth.RevokedIdTokenError("revoked"), auth.ExpiredIdTokenError("expired", ValueError()), auth.UserDisabledError("disabled")):
            self.verify.side_effect = failure
            self.assertEqual(self.post().status_code, 401)
        self.verify.side_effect = None
        self.verify.return_value = {"uid": "anonymous", "firebase": {"sign_in_provider": "anonymous"}}
        self.assertIn(self.post().status_code, (401, 403))
        self.assertEqual(self.db.reads, 0)

    def test_verification_outage_returns_503_without_disclosing_provider_error_or_storage_access(self):
        self.verify.side_effect = RuntimeError("secret-provider-detail")
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("secret-provider-detail", response.text)
        self.assertEqual(self.db.reads, 0)

    def test_body_header_and_query_id_spoofs_are_denied_before_profile_read(self):
        for field in ("userId", "user_id", "firebase_uid", "uid"):
            self.assertEqual(self.post({**payload(), field: "another-owner"}).status_code, 403)
        for header in ("x-user-id", "x-firebase-uid", "uid"):
            self.assertEqual(self.post(headers={header: "another-owner"}).status_code, 403)
        self.assertEqual(self.post(params={"userId": "another-owner"}).status_code, 403)
        self.assertEqual(self.db.reads, 0)

    def test_matching_legacy_owner_hints_do_not_override_verified_name_email_or_server_fields(self):
        body = {**payload(), "userId": IDENTITY["uid"], "name": "spoofed", "email": "spoofed", "admin": True, "credits": 10000, "styleQuizSubmissionHash": "spoofed", "onboardingCompleted": True}
        self.assertEqual(self.post(body).status_code, 200)
        self.assertEqual(self.db.profile["name"], IDENTITY["name"])
        self.assertEqual(self.db.profile["email"], IDENTITY["email"])
        self.assertNotEqual(self.db.profile["styleQuizSubmissionHash"], "spoofed")
        for field in ("admin", "credits", "onboardingCompleted"):
            self.assertNotIn(field, self.db.profile)

    def test_guest_intents_and_every_short_gender_variant_reject_without_writes(self):
        for field in ("guest", "guestMode", "isGuestFlow", "isGuest"):
            for value in (True, "true", "1", 1):
                self.assertEqual(self.post({**payload(), field: value}).status_code, 403)
        self.assertEqual(self.post({**payload(), "mode": "guest"}).status_code, 403)
        for gender in quiz.REQUIRED_QUESTION_IDS:
            body = payload(gender)
            body["answers"] = [answer for answer in body["answers"] if not answer["question_id"].startswith("category_spend_")]
            response = self.post(body)
            self.assertEqual((response.status_code, response.json()["code"]), (422, "FULL_QUIZ_REQUIRED"))
        self.assertEqual(self.db.reads, 0)

    def test_duplicate_empty_wrong_typed_answers_preferences_and_nonjson_fail_validation(self):
        for answers in ([], "answers", [{"question_id": "gender", "selected_option": 1}], [{"question_id": "gender", "selected_option": "  "}], payload()["answers"] * 2):
            self.assertEqual(self.post({**payload(), "answers": answers}).status_code, 422)
        for preferences in (None, "minimal", [1], {}):
            self.assertEqual(self.post({**payload(), "stylePreferences": preferences}).status_code, 422)
        self.assertEqual(self.post([]).status_code, 422)
        response = self.client.post("/api/style-quiz/submit", content="{ invalid json", headers={"authorization": "Bearer signed-token"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.db.reads, 0)

    def test_read_and_commit_outages_never_claim_success(self):
        for failure in ("fail_read", "fail_commit"):
            setattr(self.db, failure, True)
            response = self.post()
            setattr(self.db, failure, False)
            self.assertEqual(response.status_code, 503)
            self.assertFalse(response.json()["success"])
            self.assertNotIn("private Firestore", response.text)
            self.assertEqual(self.db.profile, {})

    def test_lost_commit_ack_returns_retryable_failure_then_replays_without_second_commit(self):
        self.db.lose_ack = True
        self.assertEqual(self.post().status_code, 503)
        saved = copy.deepcopy(self.db.profile)
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.db.committed_writes, 1)
        self.assertEqual(self.db.profile, saved)


if __name__ == "__main__":
    unittest.main()
