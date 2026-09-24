import { act, renderHook } from '@testing-library/react';
import { useWardrobeActivityRefresh } from './useWardrobeActivityRefresh';

declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;

beforeEach(() => { jest.useFakeTimers(); });
afterEach(() => { jest.useRealTimers(); });
const receipt = (uid: string, status = 'pending') => window.dispatchEvent(new CustomEvent('outfitMarkedAsWorn', { detail: { uid, projection_status: status } }));

it('makes one bounded follow-up read for pending projection, combining successive pending receipts', () => {
  const refresh = jest.fn();
  renderHook(() => useWardrobeActivityRefresh('owner', refresh));
  act(() => { receipt('other'); });
  expect(refresh).not.toHaveBeenCalled();
  act(() => { receipt('owner'); });
  expect(refresh).toHaveBeenCalledTimes(1);
  act(() => { jest.advanceTimersByTime(3000); receipt('owner'); });
  expect(refresh).toHaveBeenCalledTimes(2);
  act(() => { jest.advanceTimersByTime(4999); });
  expect(refresh).toHaveBeenCalledTimes(2);
  act(() => { jest.advanceTimersByTime(1); });
  expect(refresh).toHaveBeenCalledTimes(3);
  act(() => { jest.advanceTimersByTime(60000); });
  expect(refresh).toHaveBeenCalledTimes(3);
});

it('cancels delayed reads on account change and unmount', () => {
  const refresh = jest.fn();
  const { rerender, unmount } = renderHook(({ uid }) => useWardrobeActivityRefresh(uid, refresh), { initialProps: { uid: 'owner' } });
  act(() => { receipt('owner'); });
  rerender({ uid: 'other' });
  act(() => { jest.advanceTimersByTime(5000); });
  expect(refresh).toHaveBeenCalledTimes(1);
  act(() => { receipt('other'); });
  unmount();
  act(() => { jest.advanceTimersByTime(5000); });
  expect(refresh).toHaveBeenCalledTimes(2);
});
