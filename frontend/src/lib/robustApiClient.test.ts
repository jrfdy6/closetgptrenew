import { generateOutfit, RobustApiClient } from './robustApiClient';

const successfulResponse = (data: unknown): Response => ({
  ok: true,
  status: 200,
  statusText: 'OK',
  headers: new Headers(),
  json: async () => data,
} as Response);

describe('RobustApiClient retry contract', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    (RobustApiClient as unknown as { instance?: RobustApiClient }).instance = undefined;
    jest.restoreAllMocks();
    global.fetch = jest.fn();
  });

  afterAll(() => {
    global.fetch = originalFetch;
  });

  it('does not replay a non-retryable request', async () => {
    const fetchMock = global.fetch as jest.MockedFunction<typeof fetch>;
    fetchMock.mockRejectedValue(new TypeError('network unavailable'));
    const client = RobustApiClient.getInstance({
      maxRetries: 3,
      retryDelay: 1,
      enableCircuitBreaker: false,
      enableMetrics: false,
    });

    await expect(client.request({
      method: 'GET',
      endpoint: '/non-idempotent-operation',
      retryable: false,
    })).rejects.toThrow('network unavailable');

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('creates a fresh AbortSignal for each allowed retry', async () => {
    const fetchMock = global.fetch as jest.MockedFunction<typeof fetch>;
    fetchMock
      .mockRejectedValueOnce(new TypeError('temporary network failure'))
      .mockResolvedValueOnce(successfulResponse({ ok: true }));
    const client = RobustApiClient.getInstance({
      maxRetries: 1,
      retryDelay: 1,
      timeout: 1000,
      enableCircuitBreaker: false,
      enableMetrics: false,
    });

    const result = await client.request<{ ok: boolean }>({
      method: 'GET',
      endpoint: '/retryable-operation',
      retryable: true,
    });

    expect(result.data).toEqual({ ok: true });
    expect(fetchMock).toHaveBeenCalledTimes(2);
    const firstSignal = (fetchMock.mock.calls[0][1] as RequestInit).signal;
    const secondSignal = (fetchMock.mock.calls[1][1] as RequestInit).signal;
    expect(firstSignal).toBeDefined();
    expect(secondSignal).toBeDefined();
    expect(firstSignal).not.toBe(secondSignal);
  });

  it('marks outfit generation as non-retryable', async () => {
    const client = RobustApiClient.getInstance();
    const requestSpy = jest.spyOn(client, 'request').mockResolvedValue({
      data: { id: 'outfit-1', items: [] },
      status: 200,
      headers: {},
      timestamp: Date.now(),
      requestId: 'test-request',
    });

    await generateOutfit({ wardrobe: [] }, 'test-token');

    expect(requestSpy).toHaveBeenCalledWith(expect.objectContaining({
      method: 'POST',
      endpoint: '/outfits-existing-data/generate-personalized',
      retryable: false,
      timeout: 120000,
      authToken: 'test-token',
    }));
  });

  it('sends a failed generation request only once', async () => {
    const fetchMock = global.fetch as jest.MockedFunction<typeof fetch>;
    fetchMock.mockRejectedValue(new TypeError('generation transport failed'));

    await expect(generateOutfit({
      occasion: 'Interview',
      style: 'Urban Professional',
      mood: 'Bold',
      weather: { temperature: 72, condition: 'Clear' },
      wardrobe: [],
      user_profile: { id: 'user-1' },
    }, 'test-token')).rejects.toThrow('generation transport failed');

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});
