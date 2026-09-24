/** @jest-environment node */
declare const expect: jest.Expect;
declare const it: jest.It;
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fullQuizQuestions } from '@/lib/onboarding/questions';
import { mapQuizAnswersToProfile } from './quizProfile';

const fixture = JSON.parse(readFileSync(resolve(process.cwd(), '../backend/tests/fixtures/quiz-profile-parity.json'), 'utf8'));
const digest = (value: string | Buffer) => createHash('sha256').update(value).digest('hex');
function canonical(value: any): any {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  return value;
}

it('pins Railway golden fixtures to the unchanged accepted TS source and full gender question IDs', () => {
  for (const [path, expected] of Object.entries(fixture.source_sha256)) {
    expect(digest(readFileSync(resolve(process.cwd(), '..', path)))).toBe(expected);
  }
  for (const [gender, expected] of Object.entries(fixture.required_question_ids)) {
    expect(fullQuizQuestions(gender).map(question => question.id)).toEqual(expected);
  }
});

it('executes the accepted mapper and JavaScript hash oracle for all 189 Railway regression cases', () => {
  const clock = jest.spyOn(Date, 'now').mockReturnValue(fixture.now_seconds * 1000);
  try {
    expect(fixture.cases).toHaveLength(189);
    for (const example of fixture.cases) {
      const input = example.input;
      const profile = mapQuizAnswersToProfile(input.answers, input.colorAnalysis, input.stylePreferences, input.colorPreferences,
        'Alex Élan', 'alex@example.test', 'verified-owner', input.spending_ranges);
      expect({ name: example.name, profile }).toEqual({ name: example.name, profile: example.profile });
      const encoded = JSON.stringify(canonical({ answers: input.answers, stylePreferences: input.stylePreferences || [],
        colorPreferences: input.colorPreferences || [], colorAnalysis: input.colorAnalysis || null, spendingRanges: input.spending_ranges || null }));
      expect(encoded).toBe(example.canonical);
      expect(digest(encoded)).toBe(example.hash);
    }
  } finally {
    clock.mockRestore();
  }
});
