"""Canonical reward, reversal and retry integration with optimistic transactions."""
import copy
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from test_outfit_wear import WearTestFixture
from src.services import outfit_wear as wear, wear_projection as projection, reward_ledger
from src.services.app_data_privacy import AppDataDeletionError
from src.worker.gamification_tasks import rating_block_receipt, due_runs, award_rating_block

class CanonicalRewardTests(WearTestFixture):
    def test_first_later_day_and_retry_formula(self):
        first = self.record()
        self.assertEqual(first['rewards']['xp_awarded'], 11)
        self.assertEqual(first['rewards']['tokens_awarded'], 50)
        self.assertEqual(self.record('retry')['rewards']['xp_awarded'], 0)
        self.db.seed('outfits', 'other', self.db.rows['outfits']['look'])
        self.assertEqual(self.record('other-key', 'other')['rewards']['tokens_awarded'], 5)
        self.assertEqual(self.db.rows['users']['owner']['xp'], 22)

    def test_concurrent_outfits_bonus_and_daily_reward_once(self):
        self.db.seed('users', 'owner', {'xp': 100, 'pending_xp_bonus': 50, 'role': {'current_role': 'explorer'}})
        self.db.seed('outfits', 'other', self.db.rows['outfits']['look'])
        self.db.barrier = threading.Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda name: self.record(name, name), ['look', 'other']))
        self.assertEqual(sorted(r['rewards']['base_tokens'] for r in results), [5,50])
        self.assertEqual(sorted(r['rewards']['pending_bonus_consumed'] for r in results), [0,50])
        self.assertEqual(self.db.rows['users']['owner']['xp'],177)
        self.assertEqual(self.db.rows['users']['owner']['style_tokens']['balance'],62)

    def test_backdate_uses_current_engagement_day(self):
        result=wear.mark_outfit_worn(self.db,'look','owner','calendar','America/New_York',now=self.now,wear_date='2026-08-03')
        event=self.db.rows['outfit_history'][result['event_id']]
        self.assertEqual(event['wear_date'],'2026-08-03')
        self.assertEqual(event['engagement_day'],'2026-09-21')
        self.assertLess(event['date_worn'],event['recorded_at'])
        self.assertEqual(self.db.rows['users']['owner']['streak']['last_log_date'],'2026-09-21')

    def test_future_invalid_dates_do_not_mutate(self):
        before=copy.deepcopy(self.db.rows)
        for value in ('2027-01-01','yesterday','2026-02-30',7):
            with self.assertRaises(wear.OutfitWearError):
                wear.mark_outfit_worn(self.db,'look','owner','calendar',now=self.now,wear_date=value)
        self.assertEqual(before,self.db.rows)

    def test_profile_timezone_reward_and_browser_wear_date(self):
        self.db.seed('users','owner',{'xp':0,'location_data':{'timezone':'Asia/Tokyo'}})
        result=self.record();event=self.db.rows['outfit_history'][result['event_id']]
        self.assertEqual(event['wear_date'],'2026-09-21')
        self.assertEqual(event['engagement_day'],'2026-09-22')

    def test_undo_retry_reactivate_without_reward_farming(self):
        self.db.rows['wardrobe']['dress'].update(value_per_wear=2.5,current_tve=10)
        eid=self.record()['event_id']; user=copy.deepcopy(self.db.rows['users']['owner'])
        wear.undo_wear(self.db,'owner',eid); wear.undo_wear(self.db,'owner',eid)
        self.assertEqual(self.db.rows['wardrobe']['dress']['current_tve'],10)
        self.assertEqual(self.db.rows['wardrobe']['dress']['wearCount'],6)
        self.assertTrue(self.record()['undone'])
        reactivation=self.record('fresh-intent')
        self.assertEqual(reactivation['event_id'],eid)
        self.assertEqual(reactivation['event_revision'],3)
        self.assertEqual(reactivation['rewards']['xp_awarded'],0)
        self.assertEqual(self.db.rows['wardrobe']['dress']['current_tve'],12.5)
        self.assertEqual(user,self.db.rows['users']['owner'])

    def test_out_of_order_undo_keeps_last_worn(self):
        first=self.record(); second=self.record('tomorrow',now=self.now+timedelta(days=1))
        wear.undo_wear(self.db,'owner',first['event_id'])
        self.assertEqual(self.db.rows['wardrobe']['dress']['lastWorn'],second['date_worn'])
        wear.undo_wear(self.db,'owner',second['event_id'])
        self.assertIsNone(self.db.rows['wardrobe']['dress']['lastWorn'])

    def test_each_core_write_failure_atomic_and_write_budget(self):
        captured=[]; original=self.db.transaction
        def create():
            txn=original();captured.append(txn);return txn
        self.db.transaction=create
        self.record(); size=len(captured[-1].writes)
        self.assertLess(size,40)
        before=copy.deepcopy(self.db.rows)
        for index in range(size):
            self.db.fail_at_write=index
            with self.assertRaises(RuntimeError):
                self.record('tomorrow',now=self.now+timedelta(days=1))
            self.assertEqual(before,self.db.rows)

    def test_deletion_epoch_fences_delayed_rewards(self):
        self.db.rows['users']['owner']['app_data_deletion']={'status':'running'}
        with self.assertRaises(wear.OutfitWearError):self.record()
        self.db.rows['users']['owner'].update(app_data_deletion={'status':'complete'},app_data_epoch=1)
        with self.assertRaises(AppDataDeletionError):reward_ledger.award(self.db,'owner','rating',xp=10,expected_epoch=0)
        self.assertEqual(self.db.rows['users']['owner']['xp'],0)

    def test_metadata_cannot_rewrite_date_items_or_rewards(self):
        result=self.record();eid=result['event_id'];user=copy.deepcopy(self.db.rows['users']['owner'])
        wear.update_wear_metadata(self.db,'owner',eid,{'notes':'Trip','dateWorn':1,'items':[]})
        self.assertEqual(self.db.rows['outfit_history'][eid]['date_worn'],result['date_worn'])
        self.assertEqual(user,self.db.rows['users']['owner'])
        with self.assertRaises(wear.OutfitWearError):wear.update_wear_metadata(self.db,'owner',eid,{'tags':'bad'})

    def test_suggestion_and_detail_dedupe_same_linked_outfit(self):
        self.db.seed('daily_outfit_suggestions','suggestion',{'user_id':'owner','outfit_id':'look','outfit_data':self.db.rows['outfits']['look']})
        result=wear.mark_outfit_worn(self.db,'look','owner','suggestion-key',now=self.now,source='daily_suggestion',suggestion_id='suggestion')
        retry=wear.mark_outfit_worn(self.db,'look','owner','detail-key',now=self.now)
        self.assertEqual(result['event_id'],retry['event_id'])
        self.assertTrue(self.db.rows['daily_outfit_suggestions']['suggestion']['is_worn'])
        self.assertEqual(len(self.db.rows['reward_ledger']),1)

class ProjectionTests(WearTestFixture):
    def challenge(self):
        from src.custom_types.gamification import CHALLENGE_CATALOG
        definition=next(v for v in CHALLENGE_CATALOG.values() if v.rules=={'outfits_required':5})
        ref=self.db.collection('user_challenges').document('owner').collection('active').document('instance')
        self.db.seed(ref.collection_name,ref.id,{'user_id':'owner','challenge_id':definition.id,'started_at':self.now-timedelta(days=1),'progress':0,'target':5,'status':'in_progress'})
        return ref
    def test_projection_replay_undo_reactivate_once(self):
        ref=self.challenge();eid=self.record()['event_id']
        projection.project_instance(self.db,eid,1,ref);projection.project_instance(self.db,eid,1,ref)
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],1)
        wear.undo_wear(self.db,'owner',eid)
        projection.project_instance(self.db,eid,1,ref);projection.project_instance(self.db,eid,2,ref)
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],0)
        self.record('reactivate');projection.project_instance(self.db,eid,3,ref)
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],1)
    def test_projection_lost_ack_replays_safely(self):
        ref=self.challenge();eid=self.record()['event_id'];self.db.lose_ack=True
        with self.assertRaises(RuntimeError):projection.project_instance(self.db,eid,1,ref)
        projection.project_instance(self.db,eid,1,ref)
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],1)
    def test_projection_partial_failure_rolls_back_then_recovers(self):
        ref=self.challenge();eid=self.record()['event_id'];before=copy.deepcopy(self.db.rows)
        self.db.fail_at_write=1
        with self.assertRaises(RuntimeError):projection.project_instance(self.db,eid,1,ref)
        self.assertEqual(before,self.db.rows)
        self.db.fail_at_write=None;projection.project_instance(self.db,eid,1,ref)
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],1)
    def test_completion_reward_and_badge_once_retained_on_undo(self):
        ref=self.challenge()
        for i in range(5):
            event=self.record('day'+str(i),now=self.now+timedelta(days=i))
            projection.project_instance(self.db,event['event_id'],1,ref)
        user=copy.deepcopy(self.db.rows['users']['owner'])
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['status'],'completed')
        wear.undo_wear(self.db,'owner',event['event_id']);projection.project_instance(self.db,event['event_id'],2,ref)
        self.assertEqual(user,self.db.rows['users']['owner'])
    def test_milestones_require_crossing_never_retroactive(self):
        self.db.rows['wardrobe']['dress']['wearCount']=40
        eid=self.record()['event_id'];projection.project_milestones(self.db,eid,1)
        self.assertNotIn('sustainable_style_bronze',self.db.rows['users']['owner'].get('badges',[]))
        self.db.rows['wardrobe']['dress']['wearCount']=59
        event=self.record('day2',now=self.now+timedelta(days=1));projection.project_milestones(self.db,event['event_id'],1)
        user=copy.deepcopy(self.db.rows['users']['owner']);projection.project_milestones(self.db,event['event_id'],1)
        self.assertEqual(user,self.db.rows['users']['owner']);self.assertIn('sustainable_style_silver',user['badges'])
    def test_lease_fencing_rejects_old_finisher(self):
        key=self.record()['event_id']+':1';now=int(self.now.timestamp()*1000)
        first=projection.claim(self.db,key,'one',now)
        self.assertIsNone(projection.claim(self.db,key,'two',now+1))
        second=projection.claim(self.db,key,'two',now+61000)
        self.assertFalse(projection.finish_page(self.db,key,first,None,done=True))
        self.assertTrue(projection.finish_page(self.db,key,second,None,done=True))
    def test_new_epoch_discards_old_projection(self):
        ref=self.challenge();eid=self.record()['event_id'];self.db.rows['users']['owner']['app_data_epoch']=1
        self.assertFalse(projection.project_instance(self.db,eid,1,ref))
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],0)
    def test_distinct_consecutive_rating_days_nonoverlapping_blocks(self):
        days=[(self.now.date()+timedelta(days=i)).isoformat() for i in range(14)]
        self.assertEqual(len(rating_block_receipt(days)),2)
        self.assertEqual(rating_block_receipt([days[0]]*7),[])
        self.assertEqual(rating_block_receipt(days[:6]+days[7:13]),[])
        block=rating_block_receipt(days)[0]
        self.assertTrue(award_rating_block(self.db,'owner',block,0));self.assertFalse(award_rating_block(self.db,'owner',block,0))
        self.assertEqual(self.db.rows['users']['owner']['xp'],20)
    def test_daily_and_weekly_due_boundaries(self):
        early=datetime(2026,9,21,3,59,tzinfo=timezone.utc);late=datetime(2026,9,21,4,15,tzinfo=timezone.utc)
        self.assertEqual(due_runs(early)[0][0],'daily-2026-09-20')
        self.assertEqual(due_runs(late)[0][0],'daily-2026-09-21')
        self.assertNotEqual(due_runs(early)[1],due_runs(late)[1])

class WorkerBoundaryTests(WearTestFixture):
    challenge = ProjectionTests.challenge
    def test_paged_projection_resumes_without_duplicate_events(self):
        base=self.challenge(); original=copy.deepcopy(self.db.rows[base.collection_name][base.id])
        for index in range(51):
            self.db.seed(base.collection_name, 'challenge-'+str(index).zfill(3), original)
        eid=self.record()['event_id'];key=eid+':1'
        self.assertTrue(projection.process_page(self.db,key,'worker'))
        job=self.db.rows['wear_projection_jobs'][key]
        self.assertEqual(job['status'],'pending')
        self.assertTrue(job['cursor'])
        self.assertTrue(projection.process_page(self.db,key,'worker'))
        self.assertEqual(self.db.rows['wear_projection_jobs'][key]['status'],'complete')
        for value in self.db.rows[base.collection_name].values():
            if value['challenge_id']==original['challenge_id']:
                self.assertEqual(value['progress'],1)
    def test_old_job_does_not_create_annual_challenge_after_clear(self):
        event=self.record();self.db.rows['users']['owner']['app_data_epoch']=1
        projection.process_page(self.db,event['event_id']+':1','worker')
        self.assertFalse(self.db.rows.get('user_challenges/owner/active'))
    def test_twenty_piece_core_stays_below_forty_writes(self):
        outfit=self.db.rows['outfits']['look']
        for index in range(18):
            garment=self.garment('extra'+str(index),'accessory')
            self.db.seed('wardrobe',garment['id'],garment);outfit['items'].append(garment)
        captured=[];old=self.db.transaction
        def create():
            result=old();captured.append(result);return result
        self.db.transaction=create
        self.record()
        self.assertLess(len(captured[-1].writes),40)
    def test_concurrent_gacha_and_wear_preserve_both_token_changes(self):
        import sys
        from types import ModuleType
        from unittest.mock import patch
        fake=ModuleType('src.config.firebase');fake.db=self.db
        with patch.dict(sys.modules,{'src.config.firebase':fake}):
            from src.services.addiction_service import AddictionService
        service=AddictionService();service.db=self.db
        self.db.rows['users']['owner']['style_tokens']={'balance':500,'total_earned':500}
        import asyncio
        self.db.barrier=threading.Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            pull=pool.submit(lambda: asyncio.run(service.perform_style_gacha_pull('owner','pull1')))
            wearing=pool.submit(self.record)
            result=pull.result();wearing.result()
        self.db.barrier=None
        after=copy.deepcopy(self.db.rows['users']['owner'])
        replay=asyncio.run(service.perform_style_gacha_pull('owner','pull1'))
        self.assertTrue(replay['already_recorded'])
        self.assertEqual(after,self.db.rows['users']['owner'])
        self.assertEqual(self.db.rows['users']['owner']['style_tokens']['balance'],50)
        self.assertEqual(self.db.rows['users']['owner']['style_tokens']['total_spent'],500)

class AnnualAndBaselineTests(WearTestFixture):
    def test_annual_backdate_goes_into_actual_week_and_replays_once(self):
        from src.services.reward_ledger import key_for
        ref=self.db.collection('user_challenges').document('owner').collection('active').document('annual')
        self.db.seed(ref.collection_name,ref.id,{'user_id':'owner','challenge_id':'annual_wardrobe_master','cycle_number':1,'started_at':self.now-timedelta(days=100),'expires_at':self.now+timedelta(days=264),'status':'in_progress','progress':{'weeks_completed':3,'current_week_outfits':0},'metadata':{'badge_id':'annual_master_cycle_1'}})
        event=wear.mark_outfit_worn(self.db,'look','owner','backdate','UTC',now=self.now,wear_date='2026-08-03')
        projection.project_instance(self.db,event['event_id'],1,ref)
        projection.project_instance(self.db,event['event_id'],1,ref)
        row=self.db.rows[ref.collection_name][ref.id]
        self.assertEqual(row['wear_contributions'][key_for('2026-08-03')],1)
        self.assertEqual(row['wear_progress_baseline'],3)
        self.assertEqual(row['progress']['current_week_outfits'],0)
        self.assertEqual(row['progress']['total_outfits'],1)
    def test_sanitized_antifarming_receipt_replays_without_grant(self):
        key=reward_ledger.key_for('owner','old-grant')
        self.db.seed('reward_ledger',key,{'user_id':'owner','operation_id':'old-grant'})
        result=reward_ledger.award(self.db,'owner','old-grant',xp=100)
        self.assertEqual(result['xp_awarded'],0)
        self.assertEqual(self.db.rows['users']['owner']['xp'],0)
    def test_undo_ignores_newer_tombstones_when_finding_last_worn(self):
        first=self.record();second=self.record('next',now=self.now+timedelta(days=1));third=self.record('third',now=self.now+timedelta(days=2))
        wear.undo_wear(self.db,'owner',third['event_id'])
        wear.undo_wear(self.db,'owner',second['event_id'])
        self.assertEqual(self.db.rows['wardrobe']['dress']['lastWorn'],first['date_worn'])

class MaintenanceRetryTests(WearTestFixture):
    def test_one_failed_account_remains_retryable_other_account_completes(self):
        from src.worker import gamification_tasks as tasks
        from unittest.mock import patch
        self.db.seed('users','other',{'xp':0})
        for uid in ('owner','other'):
            self.db.seed('gamification_user_jobs',uid,{'user_id':uid,'app_data_epoch':0,'activation_ms':1,'status':'pending','available_at':0,'lease_until':0,'attempts':0})
        calls=[]
        async def reconcile(db,uid,activation,epoch):
            calls.append(uid)
            if uid=='owner':raise RuntimeError('temporary')
        with patch.object(tasks,'reconcile_user',reconcile):
            tasks.process_reconciliation_jobs(self.db,'worker',limit=2)
        self.assertEqual(set(calls),{'owner','other'})
        self.assertEqual(self.db.rows['gamification_user_jobs']['owner']['status'],'pending')
        self.assertEqual(self.db.rows['gamification_user_jobs']['owner']['attempts'],1)
        self.assertEqual(self.db.rows['gamification_user_jobs']['other']['status'],'complete')
    def test_invalid_old_epoch_never_creates_annual_challenge(self):
        self.db.rows['users']['owner']['app_data_epoch']=2
        self.assertIsNone(projection.ensure_annual_challenge(self.db,'owner',int(self.now.timestamp()*1000),expected_epoch=1))
        self.assertNotIn('user_challenges/owner/active',self.db.rows)

class TransactionEpochRetryTests(WearTestFixture):
    def clear_before_commit(self, database):
        database.seed('users','owner',{'xp':0,'app_data_epoch':1,'app_data_deletion':{'status':'complete'}})
    def test_wear_does_not_retry_into_recreated_profile(self):
        self.db.before_commit=self.clear_before_commit
        with self.assertRaises(wear.OutfitWearError):self.record()
        self.assertNotIn('outfit_history',self.db.rows)
        self.assertEqual(self.db.rows['users']['owner']['xp'],0)
    def test_award_without_explicit_epoch_binds_first_read(self):
        self.db.before_commit=self.clear_before_commit
        with self.assertRaises(AppDataDeletionError):reward_ledger.award(self.db,'owner','rating',xp=10)
        self.assertNotIn('reward_ledger',self.db.rows)
    def test_initialization_does_not_retry_into_recreated_profile(self):
        self.db.rows['users']['owner']={}
        self.db.before_commit=self.clear_before_commit
        with self.assertRaises(AppDataDeletionError):reward_ledger.initialize_missing(self.db,'owner')
        self.assertNotIn('badges',self.db.rows['users']['owner'])
    def test_metadata_edit_does_not_retry_into_new_epoch(self):
        eid=self.record()['event_id'];self.db.before_commit=self.clear_before_commit
        with self.assertRaises(wear.OutfitWearError):wear.update_wear_metadata(self.db,'owner',eid,{'notes':'stale'})
        self.assertEqual(self.db.rows['outfit_history'][eid]['notes'],'')

class LegacyAdapterStatusTests(WearTestFixture):
    def setUp(self):
        super().setUp()
        import ast
        from pathlib import Path
        from typing import Dict,Any
        from types import SimpleNamespace
        from fastapi import APIRouter,Depends,HTTPException,FastAPI
        from fastapi.testclient import TestClient
        path=Path(__file__).resolve().parents[1]/'src/routes/outfit_history.py'
        nodes=[node for node in ast.parse(path.read_text()).body if isinstance(node,ast.AsyncFunctionDef) and node.name in {'mark_outfit_as_worn','mark_today_suggestion_as_worn'}]
        namespace={'__package__':'src.routes','router':APIRouter(),'Dict':Dict,'Any':Any,'Depends':Depends,'get_current_user':lambda:SimpleNamespace(id='owner'),'UserProfile':Any,'HTTPException':HTTPException,'get_db':lambda:self.db,'datetime':datetime}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)
        app=FastAPI();app.include_router(namespace['router']);self.client=TestClient(app)
        self.db.seed('daily_outfit_suggestions','suggestion',{'user_id':'owner','outfit_id':'look'})
    def test_transaction_exhaustion_maps_to_retryable_503_both_adapters(self):
        from unittest.mock import patch
        with patch.object(wear,'mark_outfit_worn',side_effect=ValueError('Failed to commit transaction in 5 attempts.')):
            for path,payload in [('/mark-worn',{'outfitId':'look','dateWorn':'2026-09-21'}),('/today-suggestion/wear',{'suggestionId':'suggestion'})]:
                response=self.client.post(path,json=payload)
                self.assertEqual(response.status_code,503,response.text)
                self.assertNotIn('5 attempts',response.text)
    def test_invalid_input_stays_422_before_canonical_call(self):
        from unittest.mock import patch
        with patch.object(wear,'mark_outfit_worn') as mark:
            for path,payload in [('/mark-worn',{'outfitId':'look','dateWorn':1e100}),('/today-suggestion/wear',{'suggestionId':'suggestion','timezone':'invalid'})]:
                self.assertEqual(self.client.post(path,json=payload).status_code,422)
            mark.assert_not_called()
