import asyncio, sys
from datetime import datetime, timezone, timedelta
from types import ModuleType
from unittest.mock import patch
from test_outfit_wear import WearTestFixture
from src.custom_types.gamification import CHALLENGE_CATALOG, badge_details, get_xp_for_level
from src.services.challenge_actions import action_progress, target_for, is_action_challenge, reconcile_action_challenges
from src.services.challenge_periods import challenge_period
from src.services import wear_projection as projection
from src.services.wear_rewards import level_for

class CatalogTests(WearTestFixture):
    def service(self):
        fake=ModuleType('src.config.firebase');fake.db=self.db
        with patch.dict(sys.modules, {'src.config.firebase':fake}):
            from src.services.challenge_service import ChallengeService
        service=ChallengeService();service.db=self.db;return service

    def instance(self,cid,progress=0):
        ref=self.db.collection('user_challenges').document('owner').collection('active').document(cid)
        self.db.seed(ref.collection_name,ref.id,{'user_id':'owner','challenge_id':cid,'status':'in_progress','started_at':self.now-timedelta(days=1),'expires_at':None,'progress':progress,'target':target_for(CHALLENGE_CATALOG[cid])})
        return ref

    def test_every_catalog_reward_and_annual_cycle_has_badge_metadata(self):
        for d in CHALLENGE_CATALOG.values():
            bid=d.rewards.get('badge')
            if bid:
                with self.subTest(challenge=d.id):
                    rendered=badge_details(bid);self.assertEqual(rendered['id'],bid);self.assertTrue(rendered['name']);self.assertTrue(rendered['icon'])
        for cycle in [1,2,57,1000]:self.assertIn(str(cycle),badge_details(f'annual_master_cycle_{cycle}')['name'])
        self.assertEqual(badge_details('old_saved_badge')['id'],'old_saved_badge')

    def test_annual_award_render_and_replay(self):
        ref=self.instance('annual_wardrobe_master',{'weeks_completed':52});self.db.rows[ref.collection_name][ref.id]['metadata']={'badge_id':'annual_master_cycle_57'}
        result=asyncio.run(self.service().complete_challenge('owner',ref.id));again=asyncio.run(self.service().complete_challenge('owner',ref.id))
        self.assertEqual(result['xp_awarded'],5000);self.assertEqual(again['xp_awarded'],0)
        self.assertEqual(self.db.rows['users']['owner']['badges'].count('annual_master_cycle_57'),1)

    def test_level_threshold_boundaries(self):
        for n in range(2,101):
            self.assertEqual(level_for(get_xp_for_level(n)-1),n-1);self.assertEqual(level_for(get_xp_for_level(n)),n)

    def test_all_nonwear_targets_follow_catalog_and_never_count_wear(self):
        for d in CHALLENGE_CATALOG.values():
            if is_action_challenge(d):
                self.assertGreater(target_for(d),0)
                for key in ('ratings_required','ratings_days','pulls_required','token_balance_required','target_level','badges_required'):
                    if key in d.rules:self.assertEqual(target_for(d),d.rules[key])
                self.assertEqual(projection.event_contribution({'recorded_at':10,'items':[]}, {'started_at':0},d),[])

    def test_feedback_consecutive_distinct_immutable_days(self):
        start=self.now-timedelta(days=10);inst={'started_at':start};now=int(self.now.timestamp()*1000)
        rows=[{'_id':str(i),'outfit_id':str(i),'created_at':int((start+timedelta(days=i)).timestamp()*1000)} for i in [0,1,1,3,4]]
        self.assertEqual(action_progress(CHALLENGE_CATALOG['feedback_streak'],inst,{}, {'feedback':rows},now),2)
        rows.append({'_id':'old','created_at':int((start-timedelta(days=1)).timestamp()*1000),'updated_at':now})
        self.assertEqual(action_progress(CHALLENGE_CATALOG['feedback_contributor'],inst,{}, {'feedback':rows},now),4)

    def test_period_rollover(self):
        now=datetime(2026,12,31,12,tzinfo=timezone.utc)
        for cadence in ['daily','monthly','quarterly']:
            suffix,end=challenge_period(cadence,now);self.assertEqual(end,datetime(2027,1,1,tzinfo=timezone.utc));self.assertTrue(suffix)
        self.assertEqual(challenge_period('always',now),('',None))

    def test_expiry_idempotent_preserves_completion(self):
        ref=self.instance('daily_logger');self.db.rows[ref.collection_name][ref.id]['expires_at']=self.now-timedelta(days=1)
        service=self.service();self.assertEqual(asyncio.run(service.expire_old_challenges('owner')),1);self.assertEqual(asyncio.run(service.expire_old_challenges('owner')),0)
        self.db.rows[ref.collection_name][ref.id]['status']='completed';self.assertEqual(asyncio.run(service.expire_old_challenges('owner')),0)

    def test_coldstart_real_counts_and_replay(self):
        service=self.service();self.assertIsNone(asyncio.run(service.check_cold_start_progress('owner',999)))
        for i in range(8):self.db.seed('wardrobe',f'extra{i}',self.garment(f'extra{i}','shirt'))
        result=asyncio.run(service.check_cold_start_progress('owner',0));self.assertEqual(result['xp_awarded'],50)
        self.assertIsNone(asyncio.run(service.check_cold_start_progress('owner',999)));self.assertEqual(self.db.rows['users']['owner']['xp'],50)

    def test_action_inventory_completion_once(self):
        ref=self.instance('wardrobe_builder')
        for i in range(23):self.db.seed('wardrobe',f'extra{i}',self.garment(f'extra{i}','shirt'))
        reconcile_action_challenges(self.db,'owner');reconcile_action_challenges(self.db,'owner')
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['status'],'completed');self.assertEqual(self.db.rows['users']['owner']['xp'],150)

    def test_selected_gems_require_true_dormancy(self):
        now=int(self.now.timestamp()*1000)
        e={'recorded_at':now,'items':[{'id':'new','lastWorn':None},{'id':'old','lastWorn':now-90*86400000}],'item_ids':['new','old']}
        self.assertEqual(projection.event_contribution(e,{'started_at':0,'items':['new','old']},CHALLENGE_CATALOG['forgotten_gems_weekly']),['old'])

    def test_every_nonwear_catalog_rule_has_positive_persisted_evidence(self):
        now=int(self.now.timestamp()*1000);start=self.now-timedelta(days=100)
        facts={'feedback':[{'_id':str(i),'outfit_id':str(i),'created_at':now-i*86400000} for i in range(30)],'pulls':[{'pulled_at':now,'rarity':'LEGENDARY'} for _ in range(5)],'wardrobe':[{'type':['shirt','pants','dress','skirt','shoes','sweater','jacket','shorts'][i%8],'_created_at':now} for i in range(100)]}
        user={'xp':get_xp_for_level(10),'badges':[str(i) for i in range(10)],'style_tokens':{'balance':1000},'role':{'current_role':'master','role_earned_at':start.isoformat()}}
        for definition in CHALLENGE_CATALOG.values():
            if is_action_challenge(definition):
                with self.subTest(challenge=definition.id):
                    self.assertGreaterEqual(action_progress(definition,{'started_at':start},user,facts,now),target_for(definition))

    def test_every_wear_catalog_rule_accepts_matching_event_and_rejects_undo(self):
        now=int(self.now.timestamp()*1000)
        for definition in CHALLENGE_CATALOG.values():
            if is_action_challenge(definition) or definition.id=='cold_start_quest':continue
            items=[{'id':str(i),'type':f'category{i}','color':['red','green','blue','yellow','purple'][i%5],'pattern':['stripe','floral'][i%2],'material':['cotton','wool'][i%2],'lastWorn':now-90*86400000,'isFavorite':True,'estimated_cost':10,'season':['fall']} for i in range(8)]
            for item in items:
                if definition.rules.get('color_rule')=='monochrome':item['color']='blue'
                if definition.rules.get('color_rule')=='neutral':item['color']='black'
                if definition.rules.get('no_patterns'):item['pattern']='solid'
            event={'recorded_at':now,'wear_date':'2026-09-20','event_id':'event','outfit_id':'outfit','items':items,'item_ids':[i['id'] for i in items],'garment_counts_before':{i['id']:0 for i in items},'garment_counts_after':{i['id']:30 for i in items},'occasion':'Wedding','weather':{'condition':'clear'},'mood':'Happy','style':'Minimalist','base_rewards':{'is_first_log_today':True}}
            with self.subTest(challenge=definition.id):
                self.assertTrue(projection.event_contribution(event,{'started_at':self.now-(timedelta(days=7) if definition.id=='annual_wardrobe_master' else timedelta(hours=1))},definition))
                self.assertFalse(projection.event_contribution({**event,'undone':True},{'started_at':0},definition))

    def test_formality_distinguishes_levels_not_arbitrary_casual_labels(self):
        d=CHALLENGE_CATALOG['formality_range']
        values={tuple(projection.event_contribution({'recorded_at':10,'items':[],'occasion':label},{'started_at':0},d)) for label in ['Casual','Weekend','Errands','Brunch']}
        self.assertEqual(values,{('casual',)})

    def test_legacy_annual_seconds_and_existing_enrollment(self):
        self.db.rows['users']['owner']['createdAt']=int((self.now-timedelta(days=20)).timestamp())
        cid=projection.ensure_annual_challenge(self.db,'owner',int(self.now.timestamp()*1000));self.assertEqual(cid,'annual_wardrobe_master-1')
        self.assertEqual(projection._ms(int(self.now.timestamp())),int(self.now.timestamp())*1000)
        ref=self.db.collection('user_challenges').document('owner').collection('active').document(cid)
        self.db.rows[ref.collection_name][cid]['cycle_number']=57
        self.assertEqual(projection.ensure_annual_challenge(self.db,'owner',int(self.now.timestamp()*1000)),cid)

    def addiction(self):
        fake=ModuleType('src.config.firebase');fake.db=self.db
        with patch.dict(sys.modules, {'src.config.firebase':fake}):
            from src.services.addiction_service import AddictionService
        service=AddictionService();service.db=self.db;return service

    def test_two_common_pulls_accumulate_bonus_and_replay_current_balance(self):
        self.db.rows['users']['owner']['style_tokens']={'balance':1500,'total_earned':1500,'total_spent':0}
        service=self.addiction()
        with patch('src.services.addiction_service.random.random',return_value=.99):
            asyncio.run(service.perform_style_gacha_pull('owner','first'))
            asyncio.run(service.perform_style_gacha_pull('owner','second'))
            replay=asyncio.run(service.perform_style_gacha_pull('owner','first'))
        self.assertTrue(replay['already_recorded']);self.assertEqual(replay['remaining_tokens'],500)
        user=self.db.rows['users']['owner'];self.assertEqual(user['pending_xp_bonus'],100);self.assertEqual(user['style_tokens']['total_spent'],1000)
        receipt=self.record();self.assertEqual(receipt['rewards']['pending_bonus_consumed'],100)
        self.assertEqual(self.record()['rewards']['xp_awarded'],0)

    def test_gacha_all_rarities_deliver_one_reward_and_insufficient_no_debit(self):
        for roll,rarity in [(.99,'COMMON'),(.1,'RARE'),(.01,'LEGENDARY')]:
            self.setUp();self.db.rows['users']['owner']['style_tokens']={'balance':500,'total_earned':500,'total_spent':0}
            service=self.addiction()
            with patch('src.services.addiction_service.random.random',return_value=roll):
                result=asyncio.run(service.perform_style_gacha_pull('owner','pull'))
                repeat=asyncio.run(service.perform_style_gacha_pull('owner','pull'))
                denied=asyncio.run(service.perform_style_gacha_pull('owner','next'))
            self.assertEqual(result['rarity'],rarity);self.assertTrue(repeat['already_recorded']);self.assertEqual(denied['error'],'Insufficient tokens')
            self.assertEqual(self.db.rows['users']['owner']['style_tokens']['total_spent'],500)
            if rarity=='RARE':self.assertEqual(len(self.db.rows['users/owner/style_insights']),1)
            if rarity=='LEGENDARY':self.assertIn('gacha_legendary',self.db.rows['users']['owner']['badges'])

    def test_role_promotion_ignores_undone_and_repeated_checks_cannot_farm_recovery(self):
        for i in range(10):self.db.seed('outfit_history',str(i),{'user_id':'owner','undone':i==9,'date_worn':int(self.now.timestamp()*1000)})
        service=self.addiction();self.assertFalse(asyncio.run(service.check_and_update_role('owner'))['promoted'])
        self.db.rows['outfit_history']['9']['undone']=False
        self.assertTrue(asyncio.run(service.check_and_update_role('owner'))['promoted'])
        self.assertEqual(self.db.rows['users']['owner']['role']['current_role'],'explorer')
        self.db.rows['users']['owner']['role']={'current_role':'curator','recovery':{'in_recovery':True,'recovery_started_at':datetime.now(timezone.utc).isoformat()}}
        for _ in range(3):asyncio.run(service.check_role_recovery('owner',{'recovery_weeks_completed':999},999))
        self.assertEqual(self.db.rows['users']['owner']['role']['current_role'],'curator')
        self.assertEqual(self.db.rows['users']['owner']['role']['recovery']['recovery_weeks_completed'],0)

    def test_conflicting_and_legacy_wardrobe_owners(self):
        ref=self.instance('wardrobe_builder')
        for i in range(23):
            item=self.garment(f'legacy{i}','shirt');item.pop('userId',None);item['ownerId']='owner';self.db.seed('wardrobe',item['id'],item)
        conflicting=self.garment('conflict','shirt');conflicting['user_id']='foreign';self.db.seed('wardrobe','conflict',conflicting)
        reconcile_action_challenges(self.db,'owner');self.assertEqual(self.db.rows[ref.collection_name][ref.id]['progress'],25)

    def test_expired_feedback_settles_predeadline_only_once(self):
        ref=self.instance('feedback_contributor');deadline=self.now
        self.db.rows[ref.collection_name][ref.id].update(status='expired',expires_at=deadline)
        for i in range(10):self.db.seed('outfit_feedback',str(i),{'user_id':'owner','outfit_id':str(i),'created_at':int((deadline-timedelta(minutes=1)).timestamp()*1000)})
        reconcile_action_challenges(self.db,'owner');reconcile_action_challenges(self.db,'owner')
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['status'],'completed');self.assertEqual(self.db.rows['users']['owner']['xp'],100)

    def test_expired_feedback_does_not_count_after_deadline_or_edited_old_rating(self):
        ref=self.instance('feedback_contributor');deadline=self.now
        self.db.rows[ref.collection_name][ref.id].update(status='expired',expires_at=deadline)
        for i in range(10):self.db.seed('outfit_feedback',str(i),{'user_id':'owner','outfit_id':str(i),'created_at':int((deadline+timedelta(seconds=1)).timestamp()*1000)})
        reconcile_action_challenges(self.db,'owner');self.assertEqual(self.db.rows[ref.collection_name][ref.id]['status'],'expired');self.assertEqual(self.db.rows['users']['owner']['xp'],0)

    def test_expired_wear_accepts_eligible_outbox_once(self):
        ref=self.instance('first_log_bonus');self.db.rows[ref.collection_name][ref.id].update(status='expired',expires_at=self.now+timedelta(minutes=1))
        receipt=self.record();projection.project_instance(self.db,receipt['event_id'],1,ref);projection.project_instance(self.db,receipt['event_id'],1,ref)
        self.assertEqual(self.db.rows[ref.collection_name][ref.id]['status'],'completed');self.assertEqual(self.db.rows['users']['owner']['xp'],36)

    def test_gacha_debit_failure_and_epoch_reject_without_rewards(self):
        from src.services.app_data_privacy import AppDataDeletionError
        self.db.rows['users']['owner']['style_tokens']={'balance':1000};self.db.rows['users']['owner']['app_data_deletion']={'status':'running'}
        with self.assertRaises(AppDataDeletionError):asyncio.run(self.addiction().perform_style_gacha_pull('owner','pull'))
        self.assertEqual(self.db.rows['users']['owner']['style_tokens']['balance'],1000)

    def test_complete_legacy_target_does_not_bypass_real_catalog_requirement(self):
        ref=self.instance('feedback_contributor',1);self.db.rows[ref.collection_name][ref.id]['target']=1
        result=asyncio.run(self.service().complete_challenge('owner',ref.id));self.assertFalse(result['success']);self.assertEqual(self.db.rows['users']['owner']['xp'],0)

    def test_rolling_feedback_enrollment_does_not_overlap_after_period_change(self):
        service=self.service();result=asyncio.run(service.start_challenge('owner','feedback_streak'))
        challenge=result['challenge'];self.assertEqual(challenge['expires_at']-challenge['started_at'],timedelta(days=5))
        again=asyncio.run(service.start_challenge('owner','feedback_streak'));self.assertTrue(again['already_started'])

    def test_archived_completion_blocks_reenrollment_for_lifetime_and_current_period(self):
        now=datetime.now(timezone.utc)
        for cid in ['first_10_outfits','outfit_variety_week']:
            ref=self.db.collection('user_challenges').document('owner').collection('completed').document('old-'+cid)
            self.db.seed(ref.collection_name,ref.id,{'challenge_id':cid,'status':'completed','completed_at':now,'user_id':'owner'})
            result=asyncio.run(self.service().start_challenge('owner',cid));self.assertFalse(result['success'])
        available=asyncio.run(self.service().get_available_challenges('owner'))
        self.assertFalse({'first_10_outfits','outfit_variety_week'}.intersection(r['challenge_id'] for r in available))

    def test_role_defender_has_full_rolling_four_week_window(self):
        result=asyncio.run(self.service().start_challenge('owner','role_defender'))
        self.assertEqual(result['challenge']['expires_at']-result['challenge']['started_at'],timedelta(weeks=4))

    def test_forgotten_gems_accepts_pydantic_shape_and_excludes_unknown_age(self):
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        fake=ModuleType('src.routes.forgotten_gems')
        fake.get_forgotten_gems=AsyncMock(return_value=SimpleNamespace(model_dump=lambda:{'success':True,'data':{'forgottenItems':[{'id':'new','daysSinceWorn':None,'lastWorn':None},{'id':'old1','name':'Old1','type':'shirt','daysSinceWorn':90,'lastWorn':1},{'id':'old2','name':'Old2','type':'pants','daysSinceWorn':90,'lastWorn':1}]}}))
        with patch.dict(sys.modules,{'src.routes.forgotten_gems':fake}):result=asyncio.run(self.service().generate_forgotten_gems_challenge('owner'))
        self.assertEqual(result['items'],['old1','old2'])

    def test_gacha_concurrent_pulls_debit_each_once_and_keep_both_bonuses(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor
        self.db.rows['users']['owner']['style_tokens']={'balance':1000,'total_spent':0}
        self.db.barrier=threading.Barrier(2);service=self.addiction()
        with patch('src.services.addiction_service.random.random',return_value=.99),ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda key:asyncio.run(service.perform_style_gacha_pull('owner',key)),['one','two']))
        self.assertEqual(self.db.rows['users']['owner']['style_tokens']['balance'],0);self.assertEqual(self.db.rows['users']['owner']['pending_xp_bonus'],100)

    def test_master_decay_and_recovery_uses_actual_two_completed_weeks(self):
        now=datetime.now(timezone.utc)
        self.db.rows['users']['owner']['role']={'current_role':'master','role_earned_at':(now-timedelta(days=30)).isoformat()}
        service=self.addiction();self.assertTrue(asyncio.run(service.check_master_decay('owner'))['demoted'])
        current_week=(now-timedelta(days=now.weekday())).replace(hour=0,minute=0,second=0,microsecond=0)
        self.db.rows['users']['owner']['role']['recovery']['recovery_started_at']=(current_week-timedelta(days=21)).isoformat()
        for week in [1,2]:
            for i in range(5):self.db.seed('outfit_history',f'{week}-{i}',{'user_id':'owner','date_worn':int((current_week-timedelta(days=week*7)+timedelta(hours=i)).timestamp()*1000)})
        self.assertTrue(asyncio.run(service.check_role_recovery('owner'))['recovered']);self.assertEqual(self.db.rows['users']['owner']['role']['current_role'],'master')

    def test_seasonal_hemisphere_and_themed_occasion_are_real_evidence(self):
        now=int(self.now.timestamp()*1000);event={'recorded_at':now,'event_id':'event','wear_date':'2026-09-20','items':[{'id':'one','season':['spring']}],'occasion':'Casual'}
        seasonal=CHALLENGE_CATALOG['seasonal_stylist'];themed=CHALLENGE_CATALOG['holiday_special']
        self.assertFalse(projection.event_contribution(event,{'started_at':0},seasonal))
        self.assertTrue(projection.event_contribution({**event,'southern_hemisphere':True},{'started_at':0},seasonal))
        self.assertFalse(projection.event_contribution(event,{'started_at':0},themed));self.assertTrue(projection.event_contribution({**event,'occasion':'Wedding'},{'started_at':0},themed))

    def test_every_catalog_completion_threshold_pays_existing_formula_once(self):
        for definition in CHALLENGE_CATALOG.values():
            if definition.id=='cold_start_quest':continue
            with self.subTest(challenge=definition.id):
                self.setUp()
                target=52 if definition.id=='annual_wardrobe_master' else projection._target(definition)
                progress={'weeks_completed':target} if definition.id=='annual_wardrobe_master' else target
                ref=self.instance(definition.id,progress)
                service=self.service();first=asyncio.run(service.complete_challenge('owner',ref.id));repeat=asyncio.run(service.complete_challenge('owner',ref.id))
                self.assertEqual(first['xp_awarded'],definition.rewards.get('xp',0));self.assertEqual(first['tokens_awarded'],definition.rewards.get('tokens',definition.rewards.get('xp',0)));self.assertEqual(repeat['xp_awarded'],0)

    def test_expired_stock_cannot_use_postdeadline_balance(self):
        ref=self.instance('token_saver');self.db.rows[ref.collection_name][ref.id].update(status='expired',expires_at=self.now)
        self.db.rows['users']['owner']['style_tokens']={'balance':1000}
        reconcile_action_challenges(self.db,'owner');self.assertEqual(self.db.rows['users']['owner']['xp'],0)

    def test_iso_offset_and_numeric_seconds_represent_same_instant(self):
        self.assertEqual(projection._ms('2026-09-24T01:00:00-04:00'),projection._ms('2026-09-24T05:00:00Z'))
        self.assertEqual(projection._ms(1790226000),1790226000000)

    def test_coldstart_fifty_completes_once_with_staged_xp_and_tokens(self):
        for i in range(48):self.db.seed('wardrobe',f'extra{i}',self.garment(f'extra{i}','shirt'))
        service=self.service();result=asyncio.run(service.check_cold_start_progress('owner',0));again=asyncio.run(service.check_cold_start_progress('owner',999))
        user=self.db.rows['users']['owner'];self.assertEqual(result['xp_awarded'],350);self.assertIsNone(again)
        self.assertEqual(user['xp'],350);self.assertEqual(user['style_tokens']['balance'],200)
        self.assertEqual(self.db.rows['user_challenges/owner/active']['cold_start_quest']['status'],'completed')
        self.assertEqual(len(self.db.rows['user_challenges/owner/completed']),1)

    def test_legacy_coldstart_completion_not_repaid(self):
        ref=self.instance('cold_start_quest',50);self.db.rows[ref.collection_name][ref.id]['milestones_reached']=[10,25,50]
        for i in range(48):self.db.seed('wardrobe',f'extra{i}',self.garment(f'extra{i}','shirt'))
        self.assertIsNone(asyncio.run(self.service().check_cold_start_progress('owner',50)))
        self.assertEqual(self.db.rows['users']['owner']['xp'],0);self.assertEqual(self.db.rows[ref.collection_name][ref.id]['status'],'completed')

    def test_action_timestamp_exact_deadline_excluded(self):
        now=int(self.now.timestamp()*1000);definition=CHALLENGE_CATALOG['feedback_contributor']
        instance={'started_at':self.now-timedelta(days=1),'expires_at':self.now}
        facts={'feedback':[{'_id':'one','created_at':now},{'_id':'two','created_at':now-1}]}
        self.assertEqual(action_progress(definition,instance,{},facts,now+1),1)


    def test_late_completion_does_not_consume_next_enrollment_period(self):
        from src.services.challenge_periods import completed_in_period
        now=datetime(2026,9,28,12,tzinfo=timezone.utc)
        record={'challenge_id':'outfit_variety_week','status':'completed','started_at':now-timedelta(days=7),'completed_at':now,'instance_id':'outfit_variety_week-2026-W39'}
        self.assertFalse(completed_in_period(CHALLENGE_CATALOG['outfit_variety_week'],[record],now))


    def test_annual_actual_wear_date_must_be_within_enrolled_cycle(self):
        started=datetime(2026,9,21,tzinfo=timezone.utc);expires=started+timedelta(weeks=52)
        challenge={'started_at':started,'expires_at':expires}
        event={'recorded_at':int((started+timedelta(days=3)).timestamp()*1000),'timezone':'UTC','items':[]}
        definition=CHALLENGE_CATALOG['annual_wardrobe_master']
        for value in ['2025-01-06','2026-09-20','2027-09-20','2027-09-21']:
            self.assertEqual(projection.event_contribution({**event,'wear_date':value},challenge,definition),[],value)
        self.assertEqual(projection.event_contribution({**event,'wear_date':'2026-09-22'},challenge,definition),['2026-09-21'])

    def test_recent_streak_required_for_role_promotion(self):
        today=datetime.now(timezone.utc).date()
        for i in range(25):self.db.seed('outfit_history',str(i),{'user_id':'owner','date_worn':1})
        for age,expected in [(2,False),(1,True),(0,True)]:
            self.db.rows['users']['owner'].update(role={'current_role':'explorer'},reward_timezone='UTC',streak={'current_streak':14,'last_log_date':(today-timedelta(days=age)).isoformat()})
            self.assertEqual(asyncio.run(self.addiction().check_and_update_role('owner'))['promoted'],expected)

    def test_upload_uses_server_creation_and_categories_normalize(self):
        now=int(self.now.timestamp()*1000);inst={'started_at':now-1000,'expires_at':now+1000}
        d=CHALLENGE_CATALOG['new_upload_week']
        self.assertEqual(action_progress(d,inst,{}, {'wardrobe':[{'createdAt':now}]},now),0)
        self.assertEqual(action_progress(d,inst,{}, {'wardrobe':[{'createdAt':now,'_created_at':now+2000}]},now),0)
        self.assertEqual(action_progress(d,inst,{}, {'wardrobe':[{'createdAt':0,'_created_at':now}]},now),1)
        rows=[{'type':v} for v in ['shirt','Shirt','top','tops','upper','tshirt','t-shirt','T-Shirt']]
        self.assertEqual(action_progress(CHALLENGE_CATALOG['complete_catalog'],inst,{}, {'wardrobe':rows},now),2)

    def test_role_defender_spring_dst_four_calendar_weeks(self):
        from zoneinfo import ZoneInfo
        start=datetime(2026,3,1,12,tzinfo=ZoneInfo('America/New_York'));end=start+timedelta(weeks=4)
        inst={'started_at':start,'expires_at':end}
        user={'location_data':{'timezone':'America/New_York'},'role':{'current_role':'master','role_earned_at':start}}
        self.assertEqual(action_progress(CHALLENGE_CATALOG['role_defender'],inst,user,{},int(end.timestamp()*1000)),4)

    def test_available_hides_dormant_controls(self):
        result=asyncio.run(self.service().get_available_challenges('owner'))
        for row in result:
            d=CHALLENGE_CATALOG[row['challenge_id']]
            self.assertFalse(any(k in d.rules for k in ('pulls_required','rarity_required','token_balance_required','target_role')))
            self.assertNotEqual(d.id,'role_defender')

    def test_archived_coldstart_completion_never_backfills_rewards(self):
        for i in range(48):self.db.seed('wardrobe',f'legacy{i}',self.garment(f'legacy{i}','shirt'))
        archive=self.db.collection('user_challenges').document('owner').collection('completed').document('old-coldstart')
        for markers in ([],[10,25,50]):
            self.db.seed(archive.collection_name,archive.id,{'challenge_id':'cold_start_quest','status':'completed','progress':50,'milestones_reached':markers})
            before=dict(self.db.rows['users']['owner'])
            self.assertIsNone(asyncio.run(self.service().check_cold_start_progress('owner',50)))
            self.assertIsNone(asyncio.run(self.service().check_cold_start_progress('owner',50)))
            self.assertEqual(self.db.rows['users']['owner'],before)
            self.assertFalse(self.db.rows.get('reward_ledger'))

    def test_archived_partial_coldstart_markers_preserved(self):
        for i in range(23):self.db.seed('wardrobe',f'legacy{i}',self.garment(f'legacy{i}','shirt'))
        archive=self.db.collection('user_challenges').document('owner').collection('completed').document('old-partial')
        self.db.seed(archive.collection_name,archive.id,{'challenge_id':'cold_start_quest','status':'expired','milestones_reached':[10]})
        result=asyncio.run(self.service().check_cold_start_progress('owner',25))
        self.assertEqual(result['xp_awarded'],100)
        self.assertIsNone(asyncio.run(self.service().check_cold_start_progress('owner',25)))

    def test_shared_feedback_badges_do_not_claim_wrong_threshold(self):
        for badge in ('style_contributor','ai_trainer'):
            details=badge_details(badge)
            self.assertIn('feedback',details['description'])
            self.assertEqual(details['unlock_condition'],'Earned through outfit feedback')

    def test_wear_projected_catalog_copy_requires_recorded_activity(self):
        for definition in CHALLENGE_CATALOG.values():
            if not is_action_challenge(definition):
                self.assertFalse(definition.description.lower().startswith('create '),definition.id)
        definition=CHALLENGE_CATALOG['complete_catalog']
        self.assertEqual(definition.rules['categories_required'],8)
        self.assertIn('clothing types',definition.description)
