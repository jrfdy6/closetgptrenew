"""The dashboard must not turn missing wear dates into an invented elapsed age."""
import ast
import copy
from datetime import datetime, timedelta, timezone
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional
import unittest
from unittest.mock import patch

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from src.services.wear_statistics import parse_wear_timestamp


NOW = datetime(2026, 9, 24, 5, 30, tzinfo=timezone.utc)


class Clock(datetime):
    @classmethod
    def now(cls, tz=None):
        return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)


def load_handler():
    source = Path(__file__).parents[1] / 'src/routes/forgotten_gems.py'
    names = {'ForgottenItem', 'ForgottenGemsResponse', '_wear_recency', 'get_forgotten_gems'}
    nodes = [node for node in ast.parse(source.read_text()).body
             if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
    namespace = {
        '__name__': 'src.routes.forgotten_gems', '__package__': 'src.routes',
        'router': APIRouter(), 'Depends': Depends, 'HTTPException': HTTPException,
        'BaseModel': BaseModel, 'Dict': Dict, 'Any': Any, 'List': List, 'Optional': Optional,
        'datetime': Clock, 'timezone': timezone, 'parse_wear_timestamp': parse_wear_timestamp,
        'logger': logging.getLogger(__name__), 'get_current_user': lambda: SimpleNamespace(id='owner'),
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), namespace)
    return namespace


class Query:
    def __init__(self, items):
        self.items = items

    def collection(self, name):
        assert name == 'wardrobe'
        return self

    def where(self, field, operator, owner):
        assert (field, operator, owner) == ('userId', '==', 'owner')
        return self

    def stream(self):
        return [SimpleNamespace(id=str(index), to_dict=lambda value=item: copy.deepcopy(value))
                for index, item in enumerate(self.items)]


class ForgottenGemsRecencyTests(unittest.TestCase):
    def setUp(self):
        self.namespace = load_handler()

    def read(self, items, **params):
        app = FastAPI()
        app.include_router(self.namespace['router'], prefix='/api/wardrobe-insights/insights')
        with patch.dict('sys.modules', {'src.config.firebase': SimpleNamespace(db=Query(items))}), TestClient(app) as client:
            response = client.get('/api/wardrobe-insights/insights/forgotten-gems', params=params)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()['data']

    def test_actual_new_upload_values_remain_never_worn_without_an_age(self):
        # Values observed in the disposable authenticated browser session.
        items = [{'name': name, 'type': kind, 'createdAt': created, 'lastWorn': None, 'wearCount': 0}
                 for name, kind, created in (
                     ('white sweatshirt', 'shirt', '2026-09-24T04:58:19.715Z'),
                     ('brown dress shoes floor', 'shoes', '2026-09-24T04:58:19.426Z'),
                 )]
        data = self.read(items)
        self.assertEqual(len(data['forgottenItems']), 2)
        for item in data['forgottenItems']:
            self.assertIsNone(item['lastWorn'])
            self.assertIsNone(item['daysSinceWorn'])
            self.assertEqual(item['usageCount'], 0)
            self.assertGreaterEqual(item['rediscoveryPotential'], 70)

    def test_supported_wear_dates_have_identical_milliseconds_and_elapsed_days(self):
        last = NOW - timedelta(days=45)
        expected = (int(last.timestamp() * 1000), 45)
        for value in (last, last.timestamp(), last.timestamp() * 1000, last.isoformat(),
                      {'seconds': last.timestamp()}, {'_seconds': last.timestamp()}):
            with self.subTest(value=value):
                self.assertEqual(self.namespace['_wear_recency']({'lastWorn': value}, NOW), expected)
        self.assertEqual(self.namespace['_wear_recency']({'last_worn': last.isoformat()}, NOW), expected)

    def test_invalid_and_unknown_dates_never_invent_age_even_when_previously_worn(self):
        for value in (None, 0, -1, True, 'invalid', float('nan'), NOW + timedelta(days=1)):
            with self.subTest(value=value):
                self.assertEqual(self.namespace['_wear_recency']({'lastWorn': value, 'wearCount': 3}, NOW), (None, None))
        # Also cover the fallback scoring path; it cannot reintroduce a sentinel.
        item = self.read([{'name': 'Previously worn', 'wearCount': 3}], min_rediscovery_potential=100)['forgottenItems'][0]
        self.assertIsNone(item['daysSinceWorn'])
        self.assertIsNone(item['lastWorn'])
        self.assertEqual(item['usageCount'], 3)

    def test_real_recent_wear_remains_excluded_by_threshold(self):
        data = self.read([
            {'name': 'Recent', 'lastWorn': (NOW - timedelta(days=2)).isoformat(), 'wearCount': 1},
            {'name': 'Older', 'lastWorn': (NOW - timedelta(days=45)).isoformat(), 'wearCount': 1},
        ])
        self.assertEqual([item['name'] for item in data['forgottenItems']], ['Older'])
        self.assertEqual(data['forgottenItems'][0]['daysSinceWorn'], 45)


if __name__ == '__main__':
    unittest.main()
