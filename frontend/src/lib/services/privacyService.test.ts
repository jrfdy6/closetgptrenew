declare const beforeEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { privacyService } from './privacyService';
jest.mock('@/lib/publicBackendUrl', () => ({ buildPublicBackendUrl: (path: string) => path }));
const user = { uid: 'owner', getIdToken: async () => 'token' } as any;
beforeEach(() => { global.fetch = jest.fn(); });
it('returns queued data clearing as pending, never completed', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, status: 202, json: async () => ({ success: true, job_id: 'job', status: 'pending', completed: false }) });
  await expect(privacyService.deleteUserData(user)).resolves.toMatchObject({ status: 'pending', completed: false });
});
it('exposes failed retryable status for the same queued job', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, job_id: 'job', status: 'failed', completed: false, retryable: true }) });
  await expect(privacyService.getDataClearStatus(user)).resolves.toMatchObject({ status: 'failed', retryable: true });
  expect(fetch).toHaveBeenCalledWith('/api/privacy-data/status', expect.objectContaining({ cache: 'no-store' }));
});
it('rejects contradictory completion claims', async () => {
  (fetch as jest.Mock).mockResolvedValue({ ok: true, json: async () => ({ success: true, status: 'pending', completed: true }) });
  await expect(privacyService.deleteUserData(user)).rejects.toThrow('could not be confirmed');
});
