"""Actual read routes and reward services return committed values or honest errors."""
import ast
import copy
import logging
import sys
from datetime import timedelta
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict
from unittest.mock import patch
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from test_outfit_wear import WearTestFixture, FakeQuery


class GamificationReadConsistencyTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        config = ModuleType('src.config.firebase'); config.db = self.db
        mock_config = patch.dict(sys.modules, {'src.config.firebase': config})
        mock_config.start(); self.addCleanup(mock_config.stop)
        from src.services.challenge_service import ChallengeService
        from src.services.gamification_service import GamificationService
        import src.services.challenge_service as challenge_module
        self.service = ChallengeService(); self.service.db = self.db
        singleton = patch.object(challenge_module, 'challenge_service', self.service)
        singleton.start(); self.addCleanup(singleton.stop)
        async def derived(_): return {}
        namespace = {'__package__': 'src.routes', 'router': APIRouter(),
                     'Dict': Dict, 'Any': Any, 'UserProfile': Any, 'Depends': Depends,
                     'get_current_user': lambda: SimpleNamespace(id='owner'),
                     'HTTPException': HTTPException, 'logger': logging.getLogger(__name__),
                     'gamification_service': GamificationService(), 'challenge_service': self.service,
                     'ai_fit_score_service': SimpleNamespace(get_score_explanation=derived),
                     'tve_service': SimpleNamespace(calculate_wardrobe_tve=derived)}
        app = FastAPI()
        for filename, functions, prefix in [
            ('gamification.py', {'get_gamification_stats'}, '/api/gamification'),
            ('challenges.py', {'get_active_challenges', 'get_available_challenges'}, '/api/challenges'),
        ]:
            source = Path(__file__).resolve().parents[1] / 'src/routes' / filename
            namespace['router'] = APIRouter()
            nodes = [n for n in ast.parse(source.read_text()).body
                     if isinstance(n, ast.AsyncFunctionDef) and n.name in functions]
            exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
            app.include_router(namespace['router'], prefix=prefix)
        self.client = TestClient(app)

    def instance(self, cid):
        self.db.seed('user_challenges/owner/active', cid, {
            'user_id': 'owner', 'challenge_id': cid, 'status': 'in_progress',
            'started_at': self.now - timedelta(days=1), 'expires_at': None, 'progress': 0, 'target': 25})

    def eligible_builder(self):
        self.instance('wardrobe_builder')
        self.db.rows['users']['owner'].update(xp=249, style_tokens={'balance': 50, 'total_earned': 75, 'total_spent': 25})
        for i in range(23): self.db.seed('wardrobe', f'item-{i}', self.garment(f'item-{i}', 'shirt'))

    def test_stats_reflects_its_own_award_in_xp_level_tokens_and_badges(self):
        self.eligible_builder()
        response = self.client.get('/api/gamification/stats')
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['xp'], 399)
        self.assertEqual(data['xp'], self.db.rows['users']['owner']['xp'])
        self.assertEqual((data['level']['level'], data['level']['current_xp']), (2, 399))
        self.assertEqual((data['tokens_balance'], data['tokens_total_earned'], data['tokens_total_spent']), (200, 225, 25))
        self.assertEqual(data['badges'], ['wardrobe_builder'])
        self.assertEqual(data['active_challenges_count'], 0)
        self.assertEqual(self.db.rows['user_challenges/owner/active']['wardrobe_builder']['status'], 'completed')

    def test_repeated_stats_reads_keep_one_reward_and_one_completed_archive(self):
        self.eligible_builder()
        first = self.client.get('/api/gamification/stats')
        before = copy.deepcopy(self.db.rows)
        for _ in range(3): self.assertEqual(self.client.get('/api/gamification/stats').json(), first.json())
        self.assertEqual(before, self.db.rows)
        self.assertEqual(len(self.db.rows['reward_ledger']), 1)
        self.assertEqual(len(self.db.rows['user_challenges/owner/completed']), 1)

    def test_failed_final_snapshot_retries_without_reawarding_committed_challenge(self):
        self.eligible_builder()
        original = self.service.get_active_challenges
        async def reconcile_then_lose_read(uid):
            value = await original(uid)
            self.db.fail_read = True
            return value
        with patch.object(self.service, 'get_active_challenges', reconcile_then_lose_read):
            response = self.client.get('/api/gamification/stats')
        self.db.fail_read = False
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Failed to get gamification stats'})
        self.assertEqual(self.db.rows['users']['owner']['xp'], 399)
        self.assertEqual(self.client.get('/api/gamification/stats').json()['data']['xp'], 399)
        self.assertEqual(len(self.db.rows['reward_ledger']), 1)

    def test_missing_user_keeps_404_before_reconciliation(self):
        self.db.rows['users'].pop('owner')
        with patch.object(self.service, 'get_active_challenges') as reconcile:
            response = self.client.get('/api/gamification/stats')
        self.assertEqual(response.status_code, 404)
        reconcile.assert_not_called()

    def test_user_disappearing_during_reconciliation_is_404_not_stale_success(self):
        async def disappears(_):
            self.db.rows['users'].pop('owner')
            return []
        with patch.object(self.service, 'get_active_challenges', disappears):
            response = self.client.get('/api/gamification/stats')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'detail': 'User not found'})

    def test_catalog_failure_is_sanitized_error_and_recovers_without_empty_success(self):
        self.instance('color_harmony')
        path = '/api/challenges/available'; healthy = self.client.get(path)
        self.assertGreater(healthy.json()['data']['count'], 0)
        original = FakeQuery.stream
        def failing(query, *args, **kwargs):
            if query.name == 'challenges': raise RuntimeError('private catalog credential detail')
            return original(query, *args, **kwargs)
        before = copy.deepcopy(self.db.rows)
        with patch.object(FakeQuery, 'stream', failing): response = self.client.get(path)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Failed to get available challenges'})
        self.assertEqual(before, self.db.rows)
        self.assertEqual(self.client.get(path).json(), healthy.json())

    def test_post_reconcile_active_stream_failure_is_error_and_recovers(self):
        self.instance('color_harmony')
        path = '/api/challenges/active'; healthy = self.client.get(path)
        self.assertEqual(healthy.json()['data']['count'], 1)
        original = FakeQuery.stream; streams = [0]
        def failing(query, *args, **kwargs):
            if query.name == 'user_challenges/owner/active':
                streams[0] += 1
                if streams[0] == 2: raise RuntimeError('private active storage detail')
            return original(query, *args, **kwargs)
        before = copy.deepcopy(self.db.rows)
        with patch.object(FakeQuery, 'stream', failing): response = self.client.get(path)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Failed to get active challenges'})
        self.assertEqual(before, self.db.rows)
        self.assertEqual(self.client.get(path).json(), healthy.json())

    def test_partial_active_stream_failure_does_not_return_a_partial_success(self):
        self.instance('color_harmony')
        original = FakeQuery.stream; streams = [0]
        def failing(query, *args, **kwargs):
            result = original(query, *args, **kwargs)
            if query.name == 'user_challenges/owner/active':
                streams[0] += 1
                if streams[0] == 2:
                    def partial():
                        yield next(result)
                        raise RuntimeError('private stream interrupted')
                    return partial()
            return result
        with patch.object(FakeQuery, 'stream', failing): response = self.client.get('/api/challenges/active')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Failed to get active challenges'})

    def test_reconciliation_failure_propagates_through_available_and_stats_routes(self):
        self.instance('color_harmony')
        original = FakeQuery.stream
        def failing(query, *args, **kwargs):
            if query.name == 'user_challenges/owner/active': raise RuntimeError('private reconciliation detail')
            return original(query, *args, **kwargs)
        before = copy.deepcopy(self.db.rows)
        with patch.object(FakeQuery, 'stream', failing):
            for path, message in [('available', 'Failed to get available challenges'), ('active', 'Failed to get active challenges')]:
                response = self.client.get('/api/challenges/' + path)
                self.assertEqual(response.status_code, 500)
                self.assertEqual(response.json(), {'detail': message})
            response = self.client.get('/api/gamification/stats')
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json(), {'detail': 'Failed to get gamification stats'})
        self.assertEqual(before, self.db.rows)

    def test_genuinely_empty_active_list_remains_successful(self):
        before = copy.deepcopy(self.db.rows)
        response = self.client.get('/api/challenges/active')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True, 'data': {'challenges': [], 'count': 0}})
        self.assertEqual(before, self.db.rows)
