"""Offline role/worker integration for historical wear-date compatibility."""
import asyncio
import copy
from datetime import datetime, timedelta, timezone
from types import ModuleType
from unittest.mock import patch

from test_outfit_wear import WearTestFixture, FakeQuery, Document
from src.services import wear_projection as projection
from src.services.wear_statistics import weekly_wear_summary


def firestore_stream(query, transaction=None):
    """Use Firestore scalar type brackets for the worker's numeric date range."""
    rows = []
    for identifier in query.db.rows.get(query.name, {}):
        if query.cursor and identifier <= query.cursor:
            continue
        snapshot = Document(query.db, query.name, identifier).get(transaction)
        row = snapshot.to_dict()
        keep = True
        for field, op, expected in query.filters:
            actual = row.get(field)
            if op in ('<', '<=', '>='):
                numeric = lambda value: type(value) in (int, float)
                if field not in row or numeric(actual) != numeric(expected) or (not numeric(actual) and type(actual) is not type(expected)):
                    keep = False
                    break
            if op == '==': keep = actual == expected
            elif op == 'in': keep = actual in expected
            elif op == '<': keep = actual < expected
            elif op == '<=': keep = actual <= expected
            elif op == '>=': keep = actual >= expected
            else: raise AssertionError('Unexpected filter: ' + op)
            if not keep:
                break
        if keep:
            rows.append(snapshot)
    if query.ordering:
        field, direction = query.ordering
        rows.sort(key=lambda snapshot: snapshot.id if field == '__name__' else snapshot.to_dict()[field], reverse=direction == 'DESCENDING')
    return iter(rows[:query.cap] if query.cap else rows)


class RoleHistoryTimestampTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        fake = ModuleType('src.config.firebase')
        fake.db = self.db
        with patch.dict('sys.modules', {'src.config.firebase': fake}):
            from src.services import addiction_service
        self.roles = addiction_service
        self.service = addiction_service.AddictionService()
        self.service.db = self.db
        instant = self.now

        class Clock(datetime):
            @classmethod
            def now(cls, tz=None):
                return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)

        for item in (patch.object(addiction_service, 'datetime', Clock),
                     patch.object(projection, 'datetime', Clock),
                     patch.object(FakeQuery, 'stream', firestore_stream),
                     patch('socket.socket.connect', side_effect=AssertionError('Network forbidden'))):
            item.start()
            self.addCleanup(item.stop)

    def history(self, identifier, value, **updates):
        self.db.seed('outfit_history', identifier, {'user_id': 'owner', 'outfit_id': 'look', 'date_worn': value, **updates})

    def role(self):
        return asyncio.run(self.service.check_and_update_role('owner', 0))

    def test_legacy_shapes_match_shared_statistics_without_rewriting_history(self):
        for value in (self.now, self.now.replace(tzinfo=None), self.now.isoformat(), self.now.timestamp(),
                      int(self.now.timestamp() * 1000), str(int(self.now.timestamp())),
                      str(int(self.now.timestamp() * 1000)), {'seconds': self.now.timestamp()},
                      {'_seconds': self.now.timestamp(), '_nanoseconds': 0}):
            with self.subTest(value=value):
                self.history('legacy', value)
                before = copy.deepcopy(self.db.rows['outfit_history'])
                self.assertEqual(self.role()['outfits_this_week'], 1)
                self.assertEqual(weekly_wear_summary(self.db, 'owner', self.now)['outfits_worn_this_week'], 1)
                self.assertEqual(self.db.rows['outfit_history'], before)

    def test_invalid_dates_are_not_promotion_evidence(self):
        for index in range(9):
            self.history(str(index), int(self.now.timestamp() * 1000))
        for value in ('not-a-date', None, True, float('nan'), float('inf'), {}, {'seconds': True}):
            with self.subTest(value=value):
                self.history('invalid', value)
                result = self.role()
                self.assertFalse(result['promoted'])
                self.assertEqual(result['progress']['outfits'], '9/10')
                self.assertEqual(result['outfits_this_week'], 9)
        self.history('invalid', str(int(self.now.timestamp() * 1000)))
        self.assertTrue(self.role()['promoted'])
        self.assertEqual(self.db.rows['users']['owner']['role']['current_role'], 'explorer')

    def test_malformed_history_cannot_block_valid_wear_job_or_repeat_rewards(self):
        event = self.record()
        self.history('malformed', 'not-a-date')
        rewards = copy.deepcopy(self.db.rows['reward_ledger'])
        xp = self.db.rows['users']['owner']['xp']
        key = event['event_id'] + ':1'
        self.assertTrue(projection.process_page(self.db, key, 'worker'))
        self.assertEqual(self.db.rows['wear_projection_jobs'][key]['status'], 'complete')
        self.assertEqual(self.db.rows['outfit_history'][event['event_id']]['projection_status'], 'complete')
        self.assertFalse(projection.process_page(self.db, key, 'worker'))
        self.assertEqual(self.db.rows['users']['owner']['xp'], xp)
        self.assertEqual(self.db.rows['reward_ledger'], rewards)
        self.assertEqual(self.db.rows['outfit_history']['malformed']['date_worn'], 'not-a-date')

    def test_transient_role_failure_remains_retryable_then_settles_once(self):
        event = self.record()
        self.history('malformed', 'not-a-date')
        key = event['event_id'] + ':1'
        rewards = copy.deepcopy(self.db.rows['reward_ledger'])
        xp = self.db.rows['users']['owner']['xp']
        with patch.object(self.roles.AddictionService, 'check_and_update_role', side_effect=RuntimeError('transient local read failure')):
            with self.assertRaises(RuntimeError):
                projection.process_page(self.db, key, 'worker')
        job = self.db.rows['wear_projection_jobs'][key]
        self.assertEqual((job['status'], job['attempts']), ('pending', 1))
        self.assertEqual(self.db.rows['outfit_history'][event['event_id']]['projection_status'], 'pending')
        with patch.object(projection, 'milliseconds', return_value=job['available_at'] + 1):
            self.assertTrue(projection.process_page(self.db, key, 'worker'))
        self.assertEqual(self.db.rows['wear_projection_jobs'][key]['status'], 'complete')
        self.assertEqual(self.db.rows['users']['owner']['xp'], xp)
        self.assertEqual(self.db.rows['reward_ledger'], rewards)

    def test_recovery_counts_legacy_shapes_and_excludes_invalid_and_undone_rows(self):
        began = self.now - timedelta(days=21)
        self.db.rows['users']['owner']['role'] = {'current_role': 'curator', 'recovery': {'in_recovery': True, 'recovery_started_at': began.isoformat()}}
        monday = (self.now - timedelta(days=self.now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        for week in (1, 2):
            for day in range(5):
                worn = monday - timedelta(weeks=week) + timedelta(days=day, hours=12)
                value = {'seconds': worn.timestamp()} if week == 1 else str(int(worn.timestamp() * 1000))
                self.history(f'{week}-{day}', value)
        self.history('invalid', 'not-a-date')
        self.history('undone', int(self.now.timestamp() * 1000), undone=True)
        result = self.role()
        self.assertTrue(result['recovered'])
        self.assertEqual(result['weeks_completed'], 2)
        self.assertEqual(self.db.rows['users']['owner']['role']['current_role'], 'master')

    def test_date_only_wear_uses_profile_timezone_like_shared_reader(self):
        # At 02:30 UTC Los Angeles is still September 21. September 22's
        # local midnight is future, unlike a mistaken UTC interpretation.
        self.db.rows['users']['owner']['location_data'] = {'timezone': 'America/Los_Angeles'}
        self.history('local-day', '2026-09-22')
        self.assertEqual(self.role()['outfits_this_week'], 0)
        self.assertEqual(weekly_wear_summary(self.db, 'owner', self.now)['outfits_worn_this_week'], 0)

    def test_invalid_recovery_policy_date_still_fails_closed(self):
        self.history('valid', int(self.now.timestamp() * 1000))
        self.db.rows['users']['owner']['role'] = {'current_role': 'curator', 'recovery': {'in_recovery': True, 'recovery_started_at': 'bad-policy-date'}}
        before = copy.deepcopy(self.db.rows)
        with self.assertRaises(ValueError):
            self.role()
        self.assertEqual(self.db.rows, before)

    def test_date_only_wear_prefers_event_timezone_with_profile_fallback(self):
        for profile_zone, event_zone, expected in (
            ('America/Los_Angeles', 'UTC', 1),
            ('UTC', 'America/Los_Angeles', 0),
            ('America/Los_Angeles', None, 0),
            ('America/Los_Angeles', 'Invalid/Zone', 0),
            ('UTC', 'Invalid/Zone', 1),
            ('America/Los_Angeles', 123, 0),
        ):
            with self.subTest(profile_zone=profile_zone, event_zone=event_zone):
                self.db.rows['users']['owner']['location_data'] = {'timezone': profile_zone}
                self.history('event-day', '2026-09-22', timezone=event_zone)
                before = copy.deepcopy(self.db.rows['outfit_history'])
                self.assertEqual(self.role()['outfits_this_week'], expected)
                shared = weekly_wear_summary(self.db, 'owner', self.now)
                self.assertEqual(shared['outfits_worn_this_week'], expected)
                self.assertEqual(self.db.rows['outfit_history'], before)
