"""Project persisted non-wear actions into existing challenge instances.

No client supplied counters; all reads precede each atomic progress/reward commit.
"""
from datetime import datetime, timezone
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from ..custom_types.gamification import CHALLENGE_CATALOG
from .reward_ledger import read, key_for, reward_patch, WriteEpochFence
from .wear_rewards import TOKEN_MULTIPLIERS, level_for, reward_timezone
from .wear_projection import _ms
from zoneinfo import ZoneInfo

INVENTORY = {'wardrobe_builder', 'wardrobe_expander', 'complete_catalog', 'new_upload_week'}
ACTION_RULES = {'ratings_required', 'ratings_days', 'pulls_required', 'rarity_required', 'target_role', 'token_balance_required', 'target_level', 'badges_required'}

def is_action_challenge(definition):
    return definition.id in INVENTORY or definition.id == 'role_defender' or bool(ACTION_RULES.intersection(definition.rules))

def target_for(definition):
    for key in ('ratings_required', 'ratings_days', 'pulls_required', 'token_balance_required', 'target_level', 'badges_required', 'items_required', 'categories_required', 'weeks_required'):
        if key in definition.rules:
            return int(definition.rules[key])
    return 1

def action_progress(definition, instance, user, facts, now):
    rules = definition.rules
    start = _ms(instance.get('started_at'))
    end = min(_ms(instance.get('expires_at')) or (now + 1), now + 1)
    def during(row, fields):
        value = next((row.get(key) for key in fields if row.get(key) is not None), None)
        return start <= _ms(value) < end if value is not None else False
    if 'ratings_required' in rules or 'ratings_days' in rules:
        # Immutable creation marker prevents edits and old ratings from replaying.
        eligible = [r for r in facts.get('feedback', []) if during(r, ('created_at',))]
        if 'ratings_required' in rules:
            return len({r.get('outfit_id') or r['_id'] for r in eligible})
        zone = ZoneInfo(reward_timezone(user, 'UTC'))
        days = sorted({datetime.fromtimestamp(_ms(r['created_at']) / 1000, zone).date() for r in eligible})
        longest = run = 0; previous = None
        for day in days:
            run = run + 1 if previous and (day - previous).days == 1 else 1
            longest = max(longest, run); previous = day
        return longest
    if 'pulls_required' in rules or 'rarity_required' in rules:
        pulls = [r for r in facts.get('pulls', []) if during(r, ('pulled_at',))]
        return sum(str(r.get('rarity', '')).lower() == rules['rarity_required'].lower() for r in pulls) if 'rarity_required' in rules else len(pulls)
    if definition.id in INVENTORY:
        rows = facts.get('wardrobe', [])
        if definition.id == 'new_upload_week':
            rows = [r for r in rows if during(r, ('_created_at',))]
        if 'categories_required' in rules:
            from ..custom_types.wardrobe import ClothingType
            from .robust_hydrator import normalize_item_type_to_enum
            valid = {v.value for v in ClothingType} - {'other'}
            types = {normalize_item_type_to_enum(str(r.get('type', '')).lower().replace(' ', '_')) for r in rows if r.get('type')}
            return len(types & valid)
        return len(rows)
    if 'token_balance_required' in rules:
        return int((user.get('style_tokens') or {}).get('balance', 0))
    if 'target_level' in rules:
        return level_for(int(user.get('xp', 0)))
    if 'badges_required' in rules:
        return len(set(user.get('badges') or []))
    role = user.get('role') or {}
    if 'target_role' in rules:
        roles = ['starter', 'explorer', 'stylist', 'curator', 'master']
        current = role.get('current_role', 'starter')
        return int(current in roles and roles.index(current) >= roles.index(rules['target_role']))
    if definition.id == 'role_defender':
        earned = _ms(role.get('role_earned_at'))
        if role.get('current_role') != rules['role'] or not earned:
            return 0
        zone = ZoneInfo(reward_timezone(user, 'UTC'))
        beginning = datetime.fromtimestamp(max(start, earned)/1000, zone)
        ending = datetime.fromtimestamp(end/1000, zone)
        return max(0, (ending - beginning).days // 7)
    return 0

def _rows(query, transaction):
    rows = [{'_id':s.id, **s.to_dict()} for s in query.limit(5001).stream(transaction=transaction)]
    if len(rows) > 5000:
        raise RuntimeError('Challenge source exceeds bounded reconciliation window')
    return [r for r in rows if not any(r.get(k) for k in ('deleted', 'isDeleted', 'deletedAt', 'deleted_at'))]

def reconcile_action_challenges(db, uid, expected_epoch=None):
    collection = db.collection('user_challenges').document(uid).collection('active')
    fence = WriteEpochFence(db, uid, expected_epoch)
    for snapshot in collection.stream():
        definition = CHALLENGE_CATALOG.get(snapshot.to_dict().get('challenge_id'))
        if not definition or not is_action_challenge(definition):
            continue
        @firestore.transactional
        def project(transaction):
            fence.check(transaction)
            user_ref = db.collection('users').document(uid)
            user = read(user_ref, transaction)
            instance = read(snapshot.reference, transaction)
            if not instance or instance.get('status') not in {'in_progress', 'expired'} or instance.get('user_id') != uid:
                return
            now = int(datetime.now(timezone.utc).timestamp()*1000)
            expired = bool(instance.get('expires_at') and _ms(instance['expires_at']) <= now)
            if expired and any(key in definition.rules for key in ('token_balance_required','target_level','badges_required','target_role')):
                return  # Current stock cannot prove a threshold before the deadline.
            ledger = db.collection('reward_ledger').document(key_for(uid, 'challenge', snapshot.reference.path, str(instance.get('started_at'))))
            prior = read(ledger, transaction)
            facts = {}
            if definition.id in INVENTORY:
                from .wardrobe_reads import owned_wardrobe_documents
                facts['wardrobe'] = [{**r.to_dict(), '_id':r.id, '_created_at':getattr(r, 'create_time', None)} for r in owned_wardrobe_documents(db, uid, transaction)]
            if 'ratings_required' in definition.rules or 'ratings_days' in definition.rules:
                facts['feedback'] = _rows(db.collection('outfit_feedback').where(filter=FieldFilter('user_id', '==', uid)), transaction)
            if 'pulls_required' in definition.rules or 'rarity_required' in definition.rules:
                facts['pulls'] = _rows(user_ref.collection('gacha_pulls'), transaction)
            progress = action_progress(definition, instance, user, facts, now)
            target = target_for(definition)
            patch = {'progress': progress, 'target': target}
            if progress >= target:
                patch.update(status='completed', completed_at=datetime.now(timezone.utc))
                if not prior:
                    reward = definition.rewards
                    tokens = int(reward.get('tokens', reward.get('xp', 0)) * TOKEN_MULTIPLIERS.get((user.get('role') or {}).get('current_role', 'starter'), 1))
                    mutation, result = reward_patch(user, xp=reward.get('xp', 0), tokens=tokens, badge=reward.get('badge'), timestamp=now)
                    transaction.update(user_ref, mutation)
                    transaction.set(ledger, {'user_id': uid, 'kind': 'challenge', 'result': result, 'created_at': now})
                archive = db.collection('user_challenges').document(uid).collection('completed').document(key_for(snapshot.reference.path, str(instance.get('started_at'))))
                transaction.set(archive, {**instance, **patch})
            transaction.update(snapshot.reference, patch)
        project(db.transaction())


async def reconcile_action_challenges_async(db, uid, expected_epoch=None):
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(reconcile_action_challenges, db, uid, expected_epoch)


async def refresh_action_rewards(user_id, *, expected_epoch, include_upload_milestones=False):
    """Post-commit hook. Failure must not roll back the already saved user action."""
    import asyncio
    from starlette.concurrency import run_in_threadpool
    from ..config.firebase import db
    def refresh():
        from .addiction_service import AddictionService
        roles = AddictionService(); roles.db = db
        asyncio.run(roles.check_and_update_role(user_id, expected_epoch))
        milestone = None
        if include_upload_milestones:
            from .challenge_service import ChallengeService
            service = ChallengeService(); service.db = db
            milestone = asyncio.run(service.check_cold_start_progress(user_id, 0, expected_epoch=expected_epoch))
        reconcile_action_challenges(db, user_id, expected_epoch)
        return {'success': True, 'milestone': milestone}
    return await run_in_threadpool(refresh)
