declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { GET, POST } from './route';

const mockProxy = jest.fn();
jest.mock('@/lib/server/backendProxy', () => ({
  proxyToBackend: (...args: unknown[]) => mockProxy(...args),
}));

beforeEach(() => jest.clearAllMocks());

it.each([['GET', GET], ['POST', POST]] as const)(
  '%s delegates the original request to the fixed verified Railway profile route', async (method, handler) => {
    const request = { method, url: 'https://spoof.test/api/user/profile?userId=foreign',
      headers: new Headers({ Authorization: 'Bearer original-token' }) } as Request;
    const response = { status: 200, json: async () => ({ userId: 'owner', name: 'Saved name' }) };
    mockProxy.mockResolvedValue(response);
    expect(await handler(request)).toBe(response);
    expect(mockProxy).toHaveBeenCalledWith(request, '/api/user/profile', { method });
  },
);

it.each([401, 403, 422, 503])('preserves a backend %s instead of reporting a successful save', async status => {
  const response = { status, json: async () => ({ detail: 'Not saved' }) };
  mockProxy.mockResolvedValue(response);
  expect(await POST({ method: 'POST' } as Request)).toBe(response);
});
