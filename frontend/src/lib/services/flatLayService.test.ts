declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { requestFlatLay, flatLayRequestFields } from './flatLayService';
const result = { success: true as const, id: 'look-1', outfit_id: 'look-1', flat_lay_status: 'pending', flat_lay_url: null, flat_lay_error: null, request_id: 'request-1', retryable: false, request_allowed: false };
beforeEach(() => { global.fetch = jest.fn(); });
it('makes one authenticated request with no client-controlled quota or status', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => result });
  expect(await requestFlatLay('look-1', 'token')).toEqual(result);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(fetch).toHaveBeenCalledWith('/api/outfits/look-1/flat-lay-request', {
    method: 'POST', headers: { Authorization: 'Bearer token', 'Content-Type': 'application/json' }, body: '{}',
  });
});
it('preserves the server review hold instead of treating HTTP success as queued', async () => {
  const hold = { ...result, flat_lay_status: 'failed', flat_lay_error: 'No new credit was used.' };
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => hold });
  expect(flatLayRequestFields(await requestFlatLay('look-1', 'token'))).toMatchObject({ flat_lay_status: 'failed', flatLayError: hold.flat_lay_error, flat_lay_request_allowed: false });
});
it.each([{ ...result, id: 'other-look' }, {}, { success: false }])('rejects an unconfirmed response %j', async data => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => data });
  await expect(requestFlatLay('look-1', 'token')).rejects.toThrow('Could not confirm');
});
it('preserves credit/ownership errors without a second call', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: false, json: async () => ({ error: 'No flat lay credits remaining.' }) });
  await expect(requestFlatLay('look-1', 'token')).rejects.toThrow('No flat lay credits');
  expect(fetch).toHaveBeenCalledTimes(1);
});
it('does not call the server without a saved outfit and token', async () => {
  await expect(requestFlatLay('', 'token')).rejects.toThrow('Sign in and save');
  await expect(requestFlatLay('look-1', '')).rejects.toThrow('Sign in and save');
  expect(fetch).not.toHaveBeenCalled();
});
