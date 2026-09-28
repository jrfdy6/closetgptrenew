import '@testing-library/jest-dom';
declare const afterEach: jest.Lifecycle;
declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import OutfitGenerationPage from './page';

const mockPush = jest.fn();
const mockGenerate = jest.fn();
const mockCreateOutfit = jest.fn();
const mockRequestFlatLay = jest.fn();
const mockToast = jest.fn();
const makeUser = (uid: string) => ({ uid, getIdToken: jest.fn().mockResolvedValue(`token-${uid}`) });
let mockUser = makeUser('owner');
const mockWeather = { temperature: 72, condition: 'Clear', location: 'Test City', fallback: false };
const items = [
  { id: 'shirt', name: 'Plain shirt', type: 'shirt', color: 'White', imageUrl: '/shirt.jpg' },
  { id: 'pants', name: 'Chinos', type: 'pants', color: 'Beige', imageUrl: '/pants.jpg' },
  { id: 'shoes', name: 'Sneakers', type: 'shoes', color: 'Navy', imageUrl: '/shoes.jpg' },
];
const savedResponse = (id: unknown = 'saved-look') => ({ data: { id, name: 'Saved look', items } });

jest.mock('next/navigation', () => ({ useRouter: () => ({ push: mockPush, back: jest.fn() }) }));
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/hooks/useWeather', () => ({ useAutoWeather: () => ({ weather: mockWeather, loading: false, fetchWeatherByLocation: jest.fn() }) }));
jest.mock('@/lib/outfitDataConverter', () => ({ convertToPydanticShape: (data: unknown) => data, validateConvertedData: () => true }));
jest.mock('@/lib/robustApiClient', () => ({ generateOutfit: (...args: unknown[]) => mockGenerate(...args) }));
jest.mock('@/lib/services/outfitService_proper', () => ({ outfitService: { createOutfit: (...args: unknown[]) => mockCreateOutfit(...args) } }));
jest.mock('@/lib/services/flatLayService', () => ({ requestFlatLay: (...args: unknown[]) => mockRequestFlatLay(...args) }));
jest.mock('@/components/Navigation', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/ClientOnlyNav', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/onboarding/FirstLookSetup', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/OutfitRevealAnimation', () => ({ __esModule: true, default: () => <p role="status">Creating your look</p> }));
jest.mock('@/components/ui/use-toast', () => ({ useToast: () => ({ toast: mockToast }) }));

beforeEach(() => {
  jest.clearAllMocks();
  mockUser = makeUser('owner');
  mockGenerate.mockReset().mockResolvedValue(savedResponse());
  window.history.replaceState({}, '', '/outfits/generate');
  localStorage.clear();
  sessionStorage.clear();
  global.fetch = jest.fn(async (url: RequestInfo | URL) => {
    if (url === '/api/wardrobe') return { ok: true, json: async () => ({ items }) } as Response;
    if (url === '/api/user/profile?fresh=1') return { ok: true, json: async () => ({ gender: 'Non-binary', stylePreferences: ['Minimalist'] }) } as Response;
    throw new Error(`Unexpected request: ${String(url)}`);
  });
  jest.spyOn(console, 'log').mockImplementation(() => undefined);
  jest.spyOn(console, 'warn').mockImplementation(() => undefined);
  jest.spyOn(console, 'error').mockImplementation(() => undefined);
});
afterEach(() => { jest.restoreAllMocks(); });

async function openConfiguredPage() {
  const view = render(<OutfitGenerationPage />);
  const open = screen.getByRole('button', { name: 'Choose outfit settings' });
  await waitFor(() => expect(open).toBeEnabled());
  expect(mockGenerate).not.toHaveBeenCalled();
  fireEvent.click(open);
  expect(mockGenerate).not.toHaveBeenCalled();
  fireEvent.click(await screen.findByRole('button', { name: 'Casual' }));
  fireEvent.click(screen.getByRole('button', { name: 'Minimalist' }));
  fireEvent.click(screen.getByRole('button', { name: 'Serene' }));
  return { view, create: screen.getByRole('button', { name: 'Create outfit' }) };
}

function expectNoAdditionalWrites() {
  expect(mockCreateOutfit).not.toHaveBeenCalled();
  expect(mockRequestFlatLay).not.toHaveBeenCalled();
  expect((fetch as jest.Mock).mock.calls.every(([, options]) => !options?.method || options.method === 'GET')).toBe(true);
}

it('shows the required garment before opening settings and waits for an explicit create request', async () => {
  window.history.replaceState({}, '', '/outfits/generate?baseItemId=shirt');
  render(<OutfitGenerationPage />);
  const open = screen.getByRole('button', { name: 'Choose outfit settings' });
  await waitFor(() => expect(open).toBeEnabled());
  expect(screen.getByText('Plain shirt')).toBeVisible();
  expect(screen.getByText('Choose your occasion, style and mood to create an outfit.')).toBeVisible();
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  expect(mockGenerate).not.toHaveBeenCalled();

  fireEvent.click(open);
  const settings = await screen.findByRole('dialog', { name: 'Create your outfit' });
  expect(within(settings).getByText('Plain shirt')).toBeVisible();
  expect(within(settings).getByRole('button', { name: 'Create outfit' })).toBeDisabled();
  expect(mockGenerate).not.toHaveBeenCalled();
  expectNoAdditionalWrites();
});

it('opens the encoded persisted ID after one configured generation without another save or flatlay request', async () => {
  mockGenerate.mockResolvedValue(savedResponse('saved look?#'));
  const { create } = await openConfiguredPage();
  fireEvent.click(create);
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits/saved%20look%3F%23'));
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expect(mockGenerate).toHaveBeenCalledWith(expect.objectContaining({
    occasion: 'Casual', style: 'Minimalist', mood: 'Serene', generation_mode: 'robust', wardrobe: items,
  }), 'token-owner');
  expectNoAdditionalWrites();
  fireEvent.click(screen.getByRole('button', { name: 'Open saved outfit' }));
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expect(mockPush).toHaveBeenLastCalledWith('/outfits/saved%20look%3F%23');
  expectNoAdditionalWrites();
});

it('admits one generation for concurrent clicks while the saved response is pending', async () => {
  let complete!: (value: ReturnType<typeof savedResponse>) => void;
  mockGenerate.mockImplementation(() => new Promise(resolve => { complete = resolve; }));
  const { create } = await openConfiguredPage();
  act(() => {
    fireEvent.click(create);
    fireEvent.click(create);
  });
  await waitFor(() => expect(mockGenerate).toHaveBeenCalledTimes(1));
  expect(mockPush).not.toHaveBeenCalled();
  await act(async () => complete(savedResponse()));
  expect(mockPush).toHaveBeenCalledTimes(1);
  expect(mockPush).toHaveBeenCalledWith('/outfits/saved-look');
  expectNoAdditionalWrites();
});

it('opens the same persisted result route after an explicit Surprise Me request', async () => {
  render(<OutfitGenerationPage />);
  const shuffle = screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' });
  await waitFor(() => expect(shuffle).toBeEnabled());
  expect(mockGenerate).not.toHaveBeenCalled();
  fireEvent.click(shuffle);
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits/saved-look'));
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expect(mockGenerate).toHaveBeenCalledWith(expect.objectContaining({
    occasion: expect.any(String), style: expect.any(String), mood: expect.any(String),
  }), 'token-owner');
  expectNoAdditionalWrites();
});

it.each([undefined, null, '', '   ', 17])('does not claim success or navigate when the response has no usable saved ID: %j', async id => {
  mockGenerate.mockResolvedValue(id === undefined ? { data: { name: 'Unsaved look', items } } : savedResponse(id));
  const { create } = await openConfiguredPage();
  fireEvent.click(create);
  expect(await screen.findByRole('alert')).toHaveTextContent('The server did not confirm that your outfit was saved.');
  expect(mockPush).not.toHaveBeenCalled();
  expect(screen.queryByRole('button', { name: 'Open saved outfit' })).not.toBeInTheDocument();
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expectNoAdditionalWrites();
});

it('does not navigate or expose an earlier account result after switching accounts during generation', async () => {
  let complete!: (value: ReturnType<typeof savedResponse>) => void;
  mockGenerate.mockImplementation(() => new Promise(resolve => { complete = resolve; }));
  const { view, create } = await openConfiguredPage();
  fireEvent.click(create);
  await waitFor(() => expect(mockGenerate).toHaveBeenCalledTimes(1));
  mockUser = makeUser('different-owner');
  view.rerender(<OutfitGenerationPage />);
  await act(async () => complete(savedResponse('first-owner-private-look')));
  expect(mockPush).not.toHaveBeenCalled();
  expect(screen.queryByRole('button', { name: 'Open saved outfit' })).not.toBeInTheDocument();
  expect(screen.queryByText(/Your outfit is saved/)).not.toBeInTheDocument();
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expectNoAdditionalWrites();
});

it('does not navigate after leaving the generator before the saved response returns', async () => {
  let complete!: (value: ReturnType<typeof savedResponse>) => void;
  mockGenerate.mockImplementation(() => new Promise(resolve => { complete = resolve; }));
  const { view, create } = await openConfiguredPage();
  fireEvent.click(create);
  await waitFor(() => expect(mockGenerate).toHaveBeenCalledTimes(1));
  view.unmount();
  await act(async () => complete(savedResponse()));
  expect(mockPush).not.toHaveBeenCalled();
  expectNoAdditionalWrites();
});

it('links a blocked new-user creation to the existing setup without losing required items', async () => {
  const { ApiRequestError } = await import('@/lib/apiRequestError');
  mockGenerate.mockRejectedValue(new ApiRequestError('Finish your style profile and ten-item capsule.', 409, 'onboarding_required'));
  window.history.replaceState({}, '', '/outfits/generate?baseItemId=shirt');
  const { create } = await openConfiguredPage();
  fireEvent.click(create);
  expect(await screen.findByRole('link', { name: 'Continue my setup' })).toHaveAttribute('href', '/onboarding');
  expect(screen.getByText('Plain shirt')).toBeVisible();
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expectNoAdditionalWrites();
});


it('holds configured and random generation when the URL-required garment is missing, then retries without dropping it', async () => {
  window.history.replaceState({}, '', '/outfits/generate?baseItemId=missing-shirt');
  render(<OutfitGenerationPage />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Your required wardrobe item is no longer available.');
  expect(screen.getByRole('button', { name: 'Choose outfit settings' })).toBeDisabled();
  expect(screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' })).toBeDisabled();
  expect(mockGenerate).not.toHaveBeenCalled();

  const restored = { ...items[0], id: 'missing-shirt', name: 'Restored shirt' };
  (fetch as jest.Mock).mockImplementation(async (url: RequestInfo | URL) => {
    if (url === '/api/wardrobe') return { ok: true, json: async () => ({ items: [restored, ...items.slice(1)] }) };
    throw new Error(`Unexpected request: ${String(url)}`);
  });
  mockGenerate.mockResolvedValue({ data: { id: 'anchored-look', items: [restored, ...items.slice(1)] } });
  fireEvent.click(screen.getByRole('button', { name: 'Retry wardrobe' }));
  await waitFor(() => expect(screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' })).toBeEnabled());
  expect(screen.getByText('Restored shirt')).toBeVisible();
  fireEvent.click(screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' }));
  await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/outfits/anchored-look'));
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expect(mockGenerate).toHaveBeenCalledWith(expect.objectContaining({ baseItemId: 'missing-shirt' }), 'token-owner');
  expectNoAdditionalWrites();
});

it.each(['success', 'failure'])('discards an earlier account wardrobe %s and preserves the new account missing-anchor block', async outcome => {
  window.history.replaceState({}, '', '/outfits/generate?baseItemId=shirt');
  let finishEarlier!: (value: unknown) => void;
  let wardrobeReads = 0;
  let earlierSignal: AbortSignal | undefined;
  (fetch as jest.Mock).mockImplementation(async (url: RequestInfo | URL, init?: RequestInit) => {
    if (url === '/api/wardrobe') {
      wardrobeReads += 1;
      if (wardrobeReads === 1) {
        earlierSignal = init?.signal as AbortSignal;
        return new Promise(resolve => { finishEarlier = resolve; });
      }
      return { ok: true, json: async () => ({ items: [] }) };
    }
    if (url === '/api/user/profile?fresh=1') return { ok: true, json: async () => ({ gender: 'Non-binary' }) };
    throw new Error(`Unexpected request: ${String(url)}`);
  });
  const view = render(<OutfitGenerationPage />);
  await waitFor(() => expect(wardrobeReads).toBe(1));
  mockUser = makeUser('different-owner');
  view.rerender(<OutfitGenerationPage />);
  expect(earlierSignal?.aborted).toBe(true);
  expect(await screen.findByRole('alert')).toHaveTextContent('Your required wardrobe item is no longer available.');
  await act(async () => finishEarlier({ ok: outcome === 'success', json: async () => ({
    items: [{ ...items[0], name: 'Private first-owner shirt' }, ...items.slice(1)],
  }) }));
  expect(screen.queryByText('Private first-owner shirt')).not.toBeInTheDocument();
  expect(screen.getByRole('alert')).toHaveTextContent('Your required wardrobe item is no longer available.');
  expect(screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' })).toBeDisabled();
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('hides a loaded earlier account piece while the replacement wardrobe is pending and ignores its late failure after sign-out', async () => {
  window.history.replaceState({}, '', '/outfits/generate?baseItemId=shirt');
  const view = render(<OutfitGenerationPage />);
  expect(await screen.findByText('Plain shirt')).toBeVisible();
  let rejectRead!: (reason: Error) => void;
  (fetch as jest.Mock).mockImplementation(async (url: RequestInfo | URL) => {
    if (url === '/api/wardrobe') return new Promise((_, reject) => { rejectRead = reject; });
    if (url === '/api/user/profile?fresh=1') return { ok: true, json: async () => ({ gender: 'Non-binary' }) };
    throw new Error(`Unexpected request: ${String(url)}`);
  });
  mockUser = makeUser('different-owner');
  view.rerender(<OutfitGenerationPage />);
  expect(screen.queryByText('Plain shirt')).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' })).toBeDisabled();
  await waitFor(() => expect(rejectRead).toBeDefined());
  mockUser = null as unknown as ReturnType<typeof makeUser>;
  view.rerender(<OutfitGenerationPage />);
  await act(async () => rejectRead(new Error('Earlier account read failed')));
  expect(screen.queryByText('Plain shirt')).not.toBeInTheDocument();
  expect(screen.queryByText(/Your saved wardrobe could not be loaded/)).not.toBeInTheDocument();
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('does not dispatch an earlier account wardrobe request when its token arrives after the account changed', async () => {
  let finishToken!: (token: string) => void;
  const delayedToken = new Promise<string>(resolve => { finishToken = resolve; });
  mockUser.getIdToken.mockImplementation(() => delayedToken);
  const view = render(<OutfitGenerationPage />);
  mockUser = makeUser('different-owner');
  view.rerender(<OutfitGenerationPage />);
  await waitFor(() => expect(screen.getByRole('button', { name: 'Surprise Me! (Shuffle)' })).toBeEnabled());
  await act(async () => finishToken('token-owner'));
  const wardrobeRequests = (fetch as jest.Mock).mock.calls.filter(([url]) => url === '/api/wardrobe');
  expect(wardrobeRequests).toHaveLength(1);
  expect(wardrobeRequests[0][1].headers.Authorization).toBe('Bearer token-different-owner');
});
