"""Persisted onboarding contract; private state is owned exclusively by Railway."""
from datetime import datetime, timedelta, timezone
import math
import re
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from ..utils.outfit_admission import CATEGORY_ALIASES

ONBOARDING_COLLECTION = 'onboarding_states'
JS_WHITESPACE = '\u0009\u000a\u000b\u000c\u000d\u0020\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff'
JS_WHITESPACE_PATTERN = re.compile('[' + re.escape(JS_WHITESPACE) + ']+')

def record(value):
    return value if isinstance(value, dict) else {}

def text(value):
    return value.strip(JS_WHITESPACE) if isinstance(value, str) else ''

def js_truthy(value):
    """Keep persisted JS object/array flags and NaN semantics on migration."""
    return value is not None and value is not False and value != '' and not (
        isinstance(value, (int, float)) and (value == 0 or isinstance(value, float) and math.isnan(value)))

def classify_garment(value):
    """Use the onboarding classifier's exact normalization order.

    The generation admission helper has a different normalization contract;
    share its category labels, without changing that helper for other callers.
    """
    item = record(value)
    analysis = record(item.get('analysis'))
    for value in (item.get('type'), item.get('category'), analysis.get('type'), analysis.get('category')):
        normalized = text(value).lower().removeprefix('clothingtype.')
        normalized = JS_WHITESPACE_PATTERN.sub(' ', re.sub(r'[_-]+', ' ', normalized))
        for category, labels in CATEGORY_ALIASES.items():
            if normalized in labels:
                return category
    return 'unknown'

def has_complete_combination(items):
    found = {classify_garment(item) for item in items}
    return 'shoes' in found and ('one-piece' in found or {'top', 'bottom'} <= found)

def js_length(value):
    return len(value.encode('utf-16-le', errors='surrogatepass')) // 2

def timestamp(value):
    if isinstance(value, str):
        return text(value) or None
    try:
        if isinstance(value, datetime):
            parsed = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
            delta = parsed - datetime(1970, 1, 1, tzinfo=timezone.utc)
            milliseconds = delta.days * 86400000 + delta.seconds * 1000 + delta.microseconds / 1000
        else:
            if type(value) in (int, float):
                milliseconds = value * 1000 if value < 1e12 else value
            elif type(record(value).get('seconds')) in (int, float):
                milliseconds = value['seconds'] * 1000
            else:
                return None
        # ECMAScript Date TimeClip truncates toward zero, rather than rounding
        # microseconds or flooring negative fractional milliseconds.
        if not math.isfinite(milliseconds) or abs(milliseconds) > 8640000000000000:
            return None
        days, day_milliseconds = divmod(math.trunc(milliseconds), 86400000)
        # Gregorian dates repeat every 400 years. Work within a supported
        # datetime cycle, then restore the expanded year required by JS dates.
        cycles, cycle_day = divmod(days - 10957, 146097)
        within_cycle = datetime(2000, 1, 1) + timedelta(days=cycle_day)
        year = within_cycle.year + 400 * cycles
        year_text = f'{year:04d}' if 0 <= year <= 9999 else ('+' if year >= 0 else '-') + f'{abs(year):06d}'
        hour, rest = divmod(day_milliseconds, 3600000)
        minute, rest = divmod(rest, 60000)
        second, millisecond = divmod(rest, 1000)
        return f'{year_text}-{within_cycle.month:02d}-{within_cycle.day:02d}T{hour:02d}:{minute:02d}:{second:02d}.{millisecond:03d}Z'
    except (OverflowError, ValueError, OSError):
        return None

def owned_by(value, user_id):
    item = record(value)
    owners = [item[key] for key in ('userId', 'user_id', 'firebase_uid', 'uid', 'ownerId') if item.get(key) is not None]
    return bool(owners) and all(isinstance(owner, str) and owner == user_id for owner in owners)

def has_style_profile(value):
    profile = record(value)
    persona, preferences = record(profile.get('stylePersona')), record(profile.get('preferences'))
    return bool(js_truthy(profile.get('styleQuizCompletedAt')) or text(persona.get('id')) or text(persona.get('name')) or
                text(profile.get('stylePersona')) or any(isinstance(values, list) and any(text(entry) for entry in values)
                for values in (profile.get('stylePreferences'), profile.get('style_preferences'), preferences.get('style'))))

def parse_draft(value):
    draft = record(value)
    cursor = draft.get('currentQuestionId')
    if (not isinstance(draft.get('answers'), list) or len(draft['answers']) > 80 or 'currentQuestionId' not in draft or
            not (cursor is None or isinstance(cursor, str) and re.fullmatch(r'[a-z0-9_]{1,100}', cursor))):
        return None
    seen, answers = set(), []
    for value in draft['answers']:
        answer = record(value)
        key, selected = answer.get('question_id'), answer.get('selected_option')
        if (not isinstance(key, str) or not re.fullmatch(r'[a-z0-9_]{1,100}', key) or key in seen or
                not isinstance(selected, str) or js_length(selected) > 2000 or not text(selected)):
            return None
        seen.add(key)
        answers.append({'question_id': key, 'selected_option': selected})
    return {'answers': answers, 'currentQuestionId': cursor}

def evaluate_capsule(items):
    ids, images, usable = set(), set(), []
    for value in items:
        item = record(value)
        identifier = text(item.get('id'))
        if not identifier or identifier in ids or item.get('deleted') is True or item.get('isDeleted') is True or js_truthy(item.get('deletedAt')):
            continue
        ids.add(identifier)
        identities = [f'hash:{text(item.get(key))}' for key in ('contentHash', 'imageHash', 'image_hash') if text(item.get(key))]
        identities += [f'url:{text(item.get(key))}' for key in ('originalImageUrl', 'imageUrl', 'image_url') if text(item.get(key))]
        original = text(item.get('imageUrl')) or text(item.get('image_url')) or text(item.get('originalImageUrl'))
        if not original or not identities or classify_garment(item) == 'unknown':
            continue
        duplicate = any(identity in images for identity in identities)
        images.update(identities)
        if not duplicate:
            usable.append(item)
    found = {classify_garment(item) for item in usable}
    coverage = has_complete_combination(usable)
    missing = []
    if 'shoes' not in found:
        missing.append('shoes')
    if 'one-piece' not in found:
        if 'top' not in found:
            missing.append('top or one-piece')
        if 'bottom' not in found:
            missing.append('bottom or one-piece')
    return {'savedCount': len(ids), 'usableCount': len(usable), 'minimum': 10, 'hasCoverage': coverage,
            'missingCategories': missing, 'ready': len(usable) >= 10 and coverage}

def derive_onboarding_state(*, stored=None, profile=None, wardrobe, outfits):
    stored, profile = record(stored), record(profile)
    previous = record(stored.get('milestones'))
    capsule = evaluate_capsule(wardrobe)
    by_id = {text(item.get('id')): item for item in wardrobe}
    first_look = None
    for outfit in outfits:
        if not isinstance(outfit.get('items'), list):
            continue
        items = []
        for raw in outfit['items']:
            item = {'id': raw} if isinstance(raw, str) else record(raw)
            items.append({**record(by_id.get(text(item.get('id')))), **item})
        if has_complete_combination(items):
            first_look = outfit
            break
    first_id = text(previous.get('firstOutfitId')) or text(record(first_look).get('id')) or None
    complete = has_style_profile(profile) or js_truthy(previous.get('styleCompletedAt'))
    historical = bool(first_id) or js_truthy(previous.get('capsuleCompletedAt'))
    stage = 'complete' if first_id else 'style' if not complete and not historical else 'first-look' if capsule['ready'] or historical else 'capsule'
    revision = stored.get('revision')
    safe_revision = type(revision) in (int, float) and 0 <= revision <= 2**53 - 1 and (type(revision) is int or revision.is_integer())
    return {'schemaVersion': 1, 'revision': int(revision) if safe_revision else 0,
            'draft': parse_draft(stored.get('draft')) or {'answers': [], 'currentQuestionId': None},
            'profileComplete': complete, 'capsule': capsule, 'stage': stage,
            'milestones': {'styleCompletedAt': timestamp(previous.get('styleCompletedAt')) or timestamp(profile.get('styleQuizCompletedAt')),
                           'capsuleCompletedAt': timestamp(previous.get('capsuleCompletedAt')), 'firstOutfitId': first_id}}

def sources(db, user_id, transaction=None):
    from .wardrobe_reads import owned_wardrobe_documents, canonical_owned_garment
    options = {'transaction': transaction} if transaction is not None else {}
    def owned_records(collection):
        rows = {}
        for field in ('userId', 'user_id'):
            query = db.collection(collection).where(filter=FieldFilter(field, '==', user_id))
            for document in query.stream(**options):
                data = document.to_dict()
                if owned_by(data, user_id):
                    rows[document.id] = {**data, 'id': document.id}
        return list(rows.values())
    draft = db.collection(ONBOARDING_COLLECTION).document(user_id).get(**options)
    profile = db.collection('users').document(user_id).get(**options)
    wardrobe = [canonical_owned_garment(document.to_dict(), user_id, document.id)
                for document in owned_wardrobe_documents(db, user_id, transaction)]
    return {'stored': draft.to_dict() if draft.exists else {}, 'profile': profile.to_dict() if profile.exists else {},
            'wardrobe': wardrobe, 'outfits': owned_records('outfits')}

def read_onboarding_state(db, user_id):
    return derive_onboarding_state(**sources(db, user_id))

def reconcile_onboarding_state(db, user_id):
    expected_epoch = None
    @firestore.transactional
    def reconcile(transaction):
        nonlocal expected_epoch
        data = sources(db, user_id, transaction)
        from .app_data_privacy import app_data_write_allowed, data_epoch
        from fastapi import HTTPException
        if not app_data_write_allowed(data['profile'], expected_epoch):
            raise HTTPException(409, 'Your app data is being cleared. Reload before saving.')
        if expected_epoch is None:
            expected_epoch = data_epoch(data['profile'])
        state = derive_onboarding_state(**data)
        now = timestamp(datetime.now(timezone.utc))
        milestones = {**state['milestones'],
                      'styleCompletedAt': state['milestones']['styleCompletedAt'] or (now if state['profileComplete'] else None),
                      'capsuleCompletedAt': state['milestones']['capsuleCompletedAt'] or (now if state['profileComplete'] and state['capsule']['ready'] else None)}
        previous = record(data['stored'].get('milestones'))
        if any(value and value != previous.get(key) for key, value in milestones.items()):
            transaction.set(db.collection(ONBOARDING_COLLECTION).document(user_id), {
                **data['stored'], 'schemaVersion': 1, 'userId': user_id, 'revision': state['revision'],
                'draft': state['draft'], 'milestones': milestones, 'updatedAt': now})
        return {**state, 'milestones': milestones}
    return reconcile(db.transaction())

class DraftRevisionConflict(Exception):
    def __init__(self, state):
        super().__init__('Your questionnaire changed in another session. Load the newer draft before saving.')
        self.state = state

def save_onboarding_draft(db, user_id, expected_revision, draft):
    expected_epoch = None
    @firestore.transactional
    def save(transaction):
        nonlocal expected_epoch
        from .app_data_privacy import app_data_write_allowed, data_epoch
        from fastapi import HTTPException
        owner = db.collection('users').document(user_id).get(transaction=transaction)
        profile = owner.to_dict() or {}
        if not app_data_write_allowed(profile, expected_epoch):
            raise HTTPException(409, 'Your app data is being cleared. Reload before saving.')
        if expected_epoch is None:
            expected_epoch = data_epoch(profile)
        reference = db.collection(ONBOARDING_COLLECTION).document(user_id)
        snapshot = reference.get(transaction=transaction)
        state = derive_onboarding_state(stored=snapshot.to_dict() if snapshot.exists else {}, wardrobe=[], outfits=[])
        acknowledged = {key: state[key] for key in ('schemaVersion', 'revision', 'draft', 'milestones')}
        if state['revision'] == expected_revision + 1 and state['draft'] == draft:
            return acknowledged
        if state['revision'] != expected_revision:
            raise DraftRevisionConflict(acknowledged)
        next_state = {**acknowledged, 'revision': state['revision'] + 1, 'draft': draft}
        transaction.set(reference, {**next_state, 'userId': user_id, 'updatedAt': timestamp(datetime.now(timezone.utc))})
        return next_state
    return save(db.transaction())
