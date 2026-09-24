import ast
import asyncio
import logging
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, Dict
import unittest
from unittest.mock import patch
from fastapi import APIRouter, Depends, HTTPException

class BadgeResponseTests(unittest.TestCase):
    def test_newly_earned_badge_is_in_same_response(self):
        source=Path(__file__).resolve().parents[1]/'src/routes/gamification.py'
        node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.AsyncFunctionDef) and n.name=='get_user_badges')
        state={'badges':[]};reads=[]
        class Ref:
            def get(self):
                snapshot=dict(state);snapshot['badges']=list(state['badges']);reads.append(snapshot)
                return SimpleNamespace(exists=True,to_dict=lambda:snapshot)
        config=ModuleType('src.config.firebase');config.db=SimpleNamespace(collection=lambda _:SimpleNamespace(document=lambda _:Ref()))
        async def unlock(_):state['badges']=['starter_closet'];return ['starter_closet']
        ns={'__package__':'src.routes','router':APIRouter(),'Dict':Dict,'Any':Any,'UserProfile':Any,'Depends':Depends,'get_current_user':lambda:None,'HTTPException':HTTPException,'logger':logging.getLogger(__name__),'gamification_service':SimpleNamespace(check_badge_unlock_conditions=unlock)}
        exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
        with patch.dict(sys.modules,{'src.config.firebase':config}):result=asyncio.run(ns['get_user_badges'](SimpleNamespace(id='owner')))
        self.assertEqual(result['data']['count'],1)
        self.assertEqual(result['data']['badges'][0]['id'],'starter_closet')
        self.assertEqual(result['data']['newly_unlocked'],['starter_closet'])
        self.assertEqual(reads[0]['badges'],[])

if __name__=='__main__':unittest.main()
