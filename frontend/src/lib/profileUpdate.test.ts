declare const expect: jest.Expect;
declare const it: jest.It;
import { buildProfileUpdate } from './profileUpdate';

it('edits the name and style without echoing server-owned data from a real-shaped readback', () => {
  const profile = {
    userId: 'owner', name: 'Updated name', gender: 'Non-binary', stylePreferences: ['Minimalist'],
    subscription: { role: 'tier1', flatlays_remaining: 1 }, role: 'tier1', credits: 1,
    styleQuizSubmissionHash: 'receipt', styleQuizCompletedAt: '2026-09-22T12:00:00Z',
    stylePersona: { id: 'saved-persona' }, photos: { fullBodyPhoto: 'https://saved.test/photo' },
    measurements: { height: 'Prefer not to say' }, created_at: 1790078400,
    email: 'owner@example.test', _source: 'firestore',
  };
  const payload = buildProfileUpdate(profile);
  expect(payload).toEqual({ name: 'Updated name', gender: 'Non-binary', stylePreferences: ['Minimalist'] });
  expect(JSON.stringify(payload)).not.toContain('receipt');
  payload.stylePreferences?.push('Classic');
  expect(profile.stylePreferences).toEqual(['Minimalist']);
  expect(profile.subscription.flatlays_remaining).toBe(1);
});

it('preserves explicit editable clears and omits absent fields', () => {
  expect(buildProfileUpdate({ name: '', stylePreferences: [] })).toEqual({ name: '', stylePreferences: [] });
  expect(buildProfileUpdate({})).toEqual({});
  expect(buildProfileUpdate({ name: 'Legacy profile', stylePreferences: null })).toEqual({ name: 'Legacy profile' });
});
