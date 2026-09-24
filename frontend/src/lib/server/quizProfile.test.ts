declare const expect: jest.Expect;
declare const it: jest.It;
import { mapQuizAnswersToProfile } from './quizProfile';

it('omits unanswered measurements, body, skin, size and color fields instead of clearing existing values', () => {
  const patch = mapQuizAnswersToProfile({ gender: 'Male' }, null, ['Minimalist'], [], 'Alex', 'a@example.test', 'account-a');
  for (const field of ['measurements', 'height', 'heightFeetInches', 'weight', 'bodyType', 'skinTone', 'colorPalette', 'created_at', 'createdAt', 'onboardingCompleted']) expect(patch).not.toHaveProperty(field);
  expect(patch.preferences).toEqual({ style: ['Minimalist'] });
});
it('keeps answered measurements without manufacturing omissions', () => {
  const patch = mapQuizAnswersToProfile({ gender: 'Male', height: '5’8–6’0', top_size: 'M' }, null, [], [], 'Alex', 'a@example.test', 'account-a');
  expect(patch.measurements).toEqual({ height: '5’8–6’0', topSize: 'M' });
  expect(patch.height).toBe('5’8–6’0');
});
