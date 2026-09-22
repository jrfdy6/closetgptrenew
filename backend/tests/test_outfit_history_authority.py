"""History routes must authorize all referenced records before writing."""

import copy
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from src.routes import outfit_history as history


class Document:
    def __init__(self, db, collection, key):
        self.db, self.collection, self.id = db, collection, key

    def get(self):
        data = self.db.data.get((self.collection, self.id))
        return SimpleNamespace(exists=data is not None, to_dict=lambda: copy.deepcopy(data))

    def update(self, data):
        self.db.writes.append((self.collection, self.id, data))
        self.db.data[(self.collection, self.id)].update(data)

    def set(self, data, **kwargs):
        self.db.writes.append((self.collection, self.id, data))
        self.db.data.setdefault((self.collection, self.id), {}).update(data)

    def delete(self):
        self.db.writes.append((self.collection, self.id, 'delete'))
        self.db.data.pop((self.collection, self.id), None)


class Collection:
    def __init__(self, db, name):
        self.db, self.name = db, name

    def document(self, key):
        return Document(self.db, self.name, key)

    def add(self, data):
        ref = self.document('new-history')
        ref.set(data)
        return None, ref


class Database:
    def __init__(self, data):
        self.data, self.writes = copy.deepcopy(data), []

    def collection(self, name):
        return Collection(self, name)

    def batch(self):
        pending = []
        return SimpleNamespace(
            update=lambda ref, values: pending.append((ref, values)),
            commit=lambda: [ref.update(values) for ref, values in pending],
        )


class HistoryAuthorityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id='alice')
        self.db = Database({
            ('outfits', 'look'): {'user_id': 'alice', 'items': [{'id': 'shirt'}], 'wearCount': 1},
            ('wardrobe', 'shirt'): {'userId': 'alice', 'wearCount': 2},
            ('wardrobe', 'foreign'): {'userId': 'bob', 'wearCount': 3},
            ('outfit_history', 'entry'): {'user_id': 'bob'},
            ('daily_outfit_suggestions', 'today'): {
                'user_id': 'alice', 'outfit_data': {'items': [{'id': 'shirt'}]},
            },
        })
        self.addCleanup(patch.stopall)
        patch.object(history, 'get_db', return_value=self.db).start()
        patch.object(history, 'log_analytics_event').start()
        patch.object(history, 'logger').start()
        # Nonessential reward services are outside the ownership contract.
        patch.dict('sys.modules', {
            'src.services.addiction_service': None,
            'src.services.gamification_service': None,
            'src.services.tve_service': None,
        }).start()

    async def assert_rejected(self, callback, code):
        with self.assertRaises(HTTPException) as raised:
            await callback
        self.assertEqual(raised.exception.status_code, code)
        self.assertEqual(self.db.writes, [])

    async def wear(self, **values):
        return await history.mark_outfit_as_worn({
            'outfitId': 'look', 'dateWorn': '2026-09-22', **values,
        }, self.user)

    async def test_foreign_outfit_cannot_change_any_counts(self):
        self.db.data[('outfits', 'look')]['user_id'] = 'bob'
        await self.assert_rejected(self.wear(), 403)

    async def test_conflicting_outfit_owner_aliases_are_rejected(self):
        self.db.data[('outfits', 'look')]['userId'] = 'bob'
        await self.assert_rejected(self.wear(), 403)

    async def test_owned_outfit_with_foreign_item_has_no_partial_writes(self):
        self.db.data[('outfits', 'look')]['items'].append({'id': 'foreign'})
        await self.assert_rejected(self.wear(), 403)

    async def test_missing_outfit_fallback_cannot_write_foreign_item(self):
        await self.assert_rejected(self.wear(outfitId='missing', items=['foreign']), 403)

    async def test_conflicting_garment_aliases_are_rejected(self):
        self.db.data[('wardrobe', 'shirt')]['user_id'] = 'bob'
        await self.assert_rejected(self.wear(), 403)

    async def test_missing_garment_has_no_partial_writes(self):
        self.db.data[('outfits', 'look')]['items'].append({'id': 'missing'})
        await self.assert_rejected(self.wear(), 422)

    async def test_owned_outfit_and_unique_garments_are_updated(self):
        self.db.data[('outfits', 'look')]['items'].append({'id': 'shirt'})
        response = await self.wear()
        self.assertTrue(response['success'])
        self.assertEqual(self.db.data[('outfits', 'look')]['wearCount'], 2)
        self.assertEqual(self.db.data[('wardrobe', 'shirt')]['wearCount'], 3)
        self.assertEqual(self.db.data[('wardrobe', 'foreign')]['wearCount'], 3)
        self.assertEqual(self.db.data[('outfit_history', 'new-history')]['user_id'], 'alice')

    async def test_foreign_history_update_and_delete_return_forbidden(self):
        await self.assert_rejected(history.update_outfit_history_entry('entry', {'notes': 'x'}, self.user), 403)
        await self.assert_rejected(history.delete_outfit_history_entry('entry', self.user), 403)

    async def test_foreign_suggestion_is_rejected(self):
        self.db.data[('daily_outfit_suggestions', 'today')]['user_id'] = 'bob'
        await self.assert_rejected(history.mark_today_suggestion_as_worn({'suggestionId': 'today'}, self.user), 403)

    async def test_owned_suggestion_cannot_change_foreign_garment(self):
        self.db.data[('daily_outfit_suggestions', 'today')]['outfit_data']['items'].append({'id': 'foreign'})
        await self.assert_rejected(history.mark_today_suggestion_as_worn({'suggestionId': 'today'}, self.user), 403)

    async def test_owned_suggestion_can_be_worn(self):
        response = await history.mark_today_suggestion_as_worn({'suggestionId': 'today'}, self.user)
        self.assertTrue(response['success'])
        self.assertTrue(self.db.data[('daily_outfit_suggestions', 'today')]['is_worn'])
        self.assertEqual(self.db.data[('wardrobe', 'shirt')]['wearCount'], 3)

    async def test_owned_history_can_be_updated_without_changing_owner(self):
        self.db.data[('outfit_history', 'entry')]['user_id'] = 'alice'
        response = await history.update_outfit_history_entry(
            'entry', {'notes': 'Saved note', 'user_id': 'bob'}, self.user)
        self.assertTrue(response['success'])
        self.assertEqual(self.db.data[('outfit_history', 'entry')]['notes'], 'Saved note')
        self.assertEqual(self.db.data[('outfit_history', 'entry')]['user_id'], 'alice')

    async def test_cache_clear_skips_conflicting_owner_alias(self):
        db = MagicMock()
        query = db.collection.return_value.where.return_value
        query.where.return_value = query
        own, conflicting = MagicMock(), MagicMock()
        own.to_dict.return_value = {'user_id': 'alice'}
        conflicting.to_dict.return_value = {'user_id': 'alice', 'userId': 'bob'}
        query.stream.return_value = [own, conflicting]
        with patch.object(history, 'get_db', return_value=db):
            result = await history.clear_todays_suggestion_cache(self.user)
        self.assertEqual(result['deleted_count'], 1)
        own.reference.delete.assert_called_once()
        conflicting.reference.delete.assert_not_called()
