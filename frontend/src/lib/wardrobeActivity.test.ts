declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { publishWearReceipt } from './wardrobeActivity';
const receipt = { success: true, event_id: 'wear-v1-' + 'a'.repeat(64), outfit_id: 'look-1', wear_count: 1, event_revision: 1, undone: false, projection_status: 'complete', rewards: { xp_awarded: 10, tokens_awarded: 1, level_up: false, new_level: 1 } };
beforeEach(() => { sessionStorage.clear(); jest.spyOn(window, 'dispatchEvent'); });
afterEach(() => jest.restoreAllMocks());
it('refreshes consumers from canonical receipts and shows a reward once across replays', () => {
  publishWearReceipt('owner-a', receipt); publishWearReceipt('owner-a', receipt);
  const events = (window.dispatchEvent as jest.Mock).mock.calls.map(([event]) => event);
  expect(events.filter(event => event.type === 'outfitMarkedAsWorn')).toHaveLength(2);
  expect(events.filter(event => event.type === 'xpAwarded')).toHaveLength(1);
  expect(events.find(event => event.type === 'outfitMarkedAsWorn').detail).toMatchObject({ uid: 'owner-a', event_id: receipt.event_id, outfitId: 'look-1', event_revision: 1 });
});
it.each([{ undone: true }, { rewards: { xp_awarded: 0 } }])('never awards local XP for %j', state => {
  publishWearReceipt('owner-b', { ...receipt, ...state });
  expect((window.dispatchEvent as jest.Mock).mock.calls.filter(([event]) => event.type === 'xpAwarded')).toHaveLength(0);
});
it('does not publish an unconfirmed response', () => {
  expect(() => publishWearReceipt('owner-c', { success: true })).toThrow('could not confirm');
  expect(window.dispatchEvent).not.toHaveBeenCalled();
});

it('announces committed receipt rewards while challenge projection is still pending', () => {
  publishWearReceipt('owner-pending', { ...receipt, projection_status: 'pending' });
  expect((window.dispatchEvent as jest.Mock).mock.calls.filter(([event]) => event.type === 'xpAwarded')).toHaveLength(1);
});
