"""Execute the exact registered route definitions with provider bodies forbidden."""
import ast
import os
from pathlib import Path
from typing import Any, Dict
import unittest
from unittest.mock import patch
from fastapi import FastAPI, APIRouter, Depends
from fastapi.testclient import TestClient
from src.auth.operator import require_internal_operator, require_operator
from src.auth import verified_user

ROOT = Path(__file__).resolve().parents[1]

class GlobalOperatorRoutesTests(unittest.TestCase):
    def app(self, file, name, prefix):
        tree = ast.parse((ROOT / 'src/routes' / file).read_text())
        function = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == name)
        # Keep real route declaration/signature; forbid entry into business code.
        function.body = ast.parse("raise AssertionError('unauthorized business handler entered')").body
        ast.fix_missing_locations(function)
        namespace = dict(router=APIRouter(), Depends=Depends, Dict=Dict, Any=Any,
                         require_operator=require_operator, require_internal_operator=require_internal_operator)
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(ROOT / file), 'exec'), namespace)
        app = FastAPI(); app.include_router(namespace['router'], prefix=prefix)
        return TestClient(app)

    def test_force_refresh_hidden_when_disabled_even_for_operator(self):
        client = self.app('wardrobe_analysis.py', 'force_refresh_trends', '/api/wardrobe-analysis')
        with patch.dict(os.environ, {'ENABLE_INTERNAL_DEBUG_ROUTES':'false','EASYOUTFIT_OPERATOR_USER_IDS':'operator'}), patch.object(verified_user.auth, 'verify_id_token') as verify:
            for headers in ({}, {'Authorization':'Bearer token'}):
                self.assertEqual(client.post('/api/wardrobe-analysis/force-refresh-trends', headers=headers).status_code,404)
            verify.assert_not_called()

    def test_force_refresh_hidden_from_nonoperator_when_enabled(self):
        client = self.app('wardrobe_analysis.py', 'force_refresh_trends', '/api/wardrobe-analysis')
        with patch.dict(os.environ, {'ENABLE_INTERNAL_DEBUG_ROUTES':'true','EASYOUTFIT_OPERATOR_USER_IDS':'operator'}), patch.object(verified_user.auth, 'verify_id_token', return_value={'uid':'ordinary'}):
            for headers in ({}, {'Authorization':'Bearer token'}):
                self.assertEqual(client.post('/api/wardrobe-analysis/force-refresh-trends',headers=headers).status_code,404)

    def test_aggregate_analytics_requires_verified_allowlisted_operator(self):
        client = self.app('simple_personalized_outfits_minimal.py','get_system_analytics','/api/outfits-simple-minimal')
        with patch.dict(os.environ, {'EASYOUTFIT_OPERATOR_USER_IDS':'operator'}), patch.object(verified_user.auth, 'verify_id_token', return_value={'uid':'ordinary'}) as verify:
            self.assertEqual(client.get('/api/outfits-simple-minimal/analytics').status_code,401)
            verify.assert_not_called()
            self.assertEqual(client.get('/api/outfits-simple-minimal/analytics',headers={'Authorization':'Bearer token'}).status_code,403)
            verify.assert_called_once_with('token',check_revoked=True)

if __name__ == '__main__':unittest.main()
