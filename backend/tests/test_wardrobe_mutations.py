import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from fastapi import HTTPException
from test_outfit_wear import Database, transactional
from src.services import wardrobe_mutations as service

class WardrobeMutationTests(unittest.TestCase):
    def setUp(self):
        self.db=Database()
        self.db.rows={'users':{'u':{'app_data_epoch':0}},'wardrobe':{'shirt':{'userId':'u','wearCount':0,'name':'Shirt'}}}
        self.mock=patch.object(service.firestore,'transactional',transactional)
        self.mock.start();self.addCleanup(self.mock.stop)
        self.now=datetime(2026,9,23,12,tzinfo=timezone.utc)
    def call(self,action='wear',**kwargs):
        return service.mutate_wardrobe(self.db,'u','shirt',action,now=self.now,**kwargs)
    def test_retry_is_single_wear(self):
        first=self.call();self.assertEqual(first,self.call())
        self.assertEqual(self.db.rows['wardrobe']['shirt']['wearCount'],1)
    def test_lost_ack_retry(self):
        self.db.lose_ack=True
        with self.assertRaises(RuntimeError):self.call()
        self.assertEqual(self.call()['newWearCount'],1)
    def test_concurrent_same_key_has_one_effect(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            result=list(pool.map(lambda _:self.call(idempotency_key='attempt'),range(8)))
        self.assertTrue(all(x['newWearCount']==1 for x in result))
    def test_new_explicit_operation_can_record_another_wear(self):
        self.call(idempotency_key='one');self.call(idempotency_key='two')
        self.assertEqual(self.db.rows['wardrobe']['shirt']['wearCount'],2)
    def test_epoch_change_rejects_delayed_edit(self):
        self.db.rows['users']['u']['app_data_epoch']=1
        with self.assertRaises(HTTPException) as caught:self.call('edit',patch={'name':'Old'},expected_epoch=0)
        self.assertEqual(caught.exception.status_code,409)
        self.assertEqual(self.db.rows['wardrobe']['shirt']['name'],'Shirt')
    def test_clear_blocks_every_mutation(self):
        self.db.rows['users']['u']['app_data_deletion']={'status':'running'}
        for action in ('edit','wear','delete'):
            with self.assertRaises(HTTPException) as caught:self.call(action,patch={'name':'Old'})
            self.assertEqual(caught.exception.status_code,409)
        self.assertEqual(self.db.rows['wardrobe']['shirt']['wearCount'],0)
    def test_conflicting_alias_denied(self):
        self.db.rows['wardrobe']['shirt']['user_id']='other'
        with self.assertRaises(HTTPException) as caught:self.call()
        self.assertEqual(caught.exception.status_code,403)
    def test_partial_commit_rolls_back(self):
        self.db.fail_at_write=1
        with self.assertRaises(RuntimeError):self.call()
        self.assertEqual(self.db.rows['wardrobe']['shirt']['wearCount'],0)
        self.assertNotIn('wardrobe_wear_receipts',self.db.rows)

if __name__=='__main__':unittest.main()
