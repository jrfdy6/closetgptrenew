declare const expect: jest.Expect;
declare const it: jest.It;
import { formatProfileDate } from './profilePresentation';

const joined = '2026-09-22T12:30:00+00:00';
const expected = new Date(joined).toLocaleDateString();
const milliseconds = new Date(joined).getTime();

it('renders the ISO timestamp returned for a newly bootstrapped account', () => {
  expect(formatProfileDate(joined)).toBe(expected);
});

it.each([milliseconds, milliseconds / 1000, String(milliseconds / 1000),
  { seconds: milliseconds / 1000 }, { _seconds: milliseconds / 1000 }])(
  'preserves historical profile timestamp format %p', value => {
    expect(formatProfileDate(value)).toBe(expected);
  },
);

it('falls back to a valid legacy date and never renders Invalid Date or the epoch for missing data', () => {
  expect(formatProfileDate('bad date', milliseconds)).toBe(expected);
  for (const value of [undefined, null, '', 0, '0', NaN, Infinity, {}, new Date('bad date')]) {
    expect(formatProfileDate(value)).toBe('Not available');
  }
});
