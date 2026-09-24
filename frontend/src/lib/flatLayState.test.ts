declare const expect: jest.Expect;
declare const it: jest.It;
import { extractFlatLayState, validStylingScore } from './flatLayState';

it('lets explicit canonical clears replace stale legacy errors and URLs', () => {
  expect(extractFlatLayState({ flat_lay_status: 'PENDING', flat_lay_error: null, flat_lay_url: null,
    flatLayError: 'old error', metadata: { flatLayUrl: '/old.png', flat_lay_error: 'old error' } }))
    .toEqual({ status: 'pending', url: null, error: null, requestAllowed: true, admissionPaused: false, admissionReason: null });
});
it('reads older nested fields and preserves a review hold', () => {
  expect(extractFlatLayState({ metadata: { flatLayUrl: '/look.png', flatLayRequestAllowed: false } }))
    .toEqual({ status: 'done', url: '/look.png', error: null, requestAllowed: false, admissionPaused: false, admissionReason: null });
});
it.each([null, undefined, NaN, Infinity, -0.1, 1.1, '0.85', true])('does not invent a score for %s', value => {
  expect(validStylingScore(value)).toBeNull();
});
it.each([0, 0.72, 1])('preserves actual score %s', score => expect(validStylingScore(score)).toBe(score));

it('pauses requests without hiding an existing completed preview', () => {
  expect(extractFlatLayState({ flat_lay_url: '/saved.png', flat_lay_status: 'done', flat_lay_request_allowed: true, flat_lay_admission_paused: true, flat_lay_admission_reason: 'Paused' }))
    .toEqual({ status: 'done', url: '/saved.png', error: null, requestAllowed: false, admissionPaused: true, admissionReason: 'Paused' });
});
