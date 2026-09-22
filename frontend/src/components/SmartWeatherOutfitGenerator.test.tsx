import React, { StrictMode } from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SmartWeatherOutfitGenerator from './SmartWeatherOutfitGenerator';
import { dailyOutfitKey } from '@/lib/dailyOutfitAttempt';

declare const expect: jest.Expect;
declare const it: jest.It;

let mockUser = { uid: 'owner', displayName: 'Owner', email: 'owner@example.test', getIdToken: jest.fn(async () => 'token') };
const mockWeather = { temperature: 72, condition: 'Clear', location: 'Test City' };
const mockFetchWeather = jest.fn();
const mockGenerate = jest.fn();
const savedProfile = {
  gender: 'Non-binary', stylePreferences: ['Minimalist'],
  measurements: { bodyType: 'Round/Apple', skinTone: 'skin_tone_82', height: '5\'8" - 5\'11"', weight: 'Prefer not to specify' },
};
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser }) }));
jest.mock('@/hooks/useWeather', () => ({ useAutoWeather: () => ({ weather: mockWeather, loading: false, fetchWeatherByLocation: mockFetchWeather }) }));
jest.mock('@/lib/weather', () => ({ formatWeatherForDisplay: () => ({ temperature: '72°F', condition: 'Clear' }) }));
jest.mock('@/lib/outfitDataConverter', () => ({ convertToPydanticShape: (data: unknown) => data, validateConvertedData: () => true }));
jest.mock('@/lib/robustApiClient', () => ({ generateOutfit: (...args: unknown[]) => mockGenerate(...args) }));
const items = [
  { id: 'shirt', type: 'shirt', name: 'Plain tee', imageUrl: 'https://example.test/tee.jpg', color: 'White' },
  { id: 'pants', type: 'pants', name: 'Chinos', color: 'Beige' },
  { id: 'shoes', type: 'shoes', name: 'Sneakers', color: 'Navy' },
];
const response = (body: unknown, ok = true) => ({ ok, json: async () => body }) as Response;
let account = 0;
beforeEach(() => {
  account += 1;
  mockUser = { ...mockUser, uid: `owner-${account}` };
  localStorage.clear();
  sessionStorage.clear();
  mockGenerate.mockReset().mockResolvedValue({ data: { id: 'look', name: 'Saved look', items, confidence: .8 } });
  global.fetch = jest.fn(async (url) => response(url === '/api/user/profile' ? savedProfile : items));
  jest.spyOn(console, 'log').mockImplementation(() => undefined);
  jest.spyOn(console, 'error').mockImplementation(() => undefined);
  jest.spyOn(console, 'warn').mockImplementation(() => undefined);
});
afterEach(() => jest.restoreAllMocks());

it('uses the saved quiz profile for dashboard generation without inventing age', async () => {
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  await waitFor(() => expect(mockGenerate).toHaveBeenCalledTimes(1));
  expect(fetch).toHaveBeenCalledWith('/api/user/profile', expect.objectContaining({
    headers: { Authorization: 'Bearer token' }, cache: 'no-store',
  }));
  expect(mockGenerate.mock.calls[0][0].user_profile).toMatchObject({
    id: mockUser.uid, gender: 'Non-binary', bodyType: 'Round/Apple', skinTone: 'skin_tone_82',
    height: '5\'8" - 5\'11"', weight: 'Prefer not to specify', style_preferences: ['Minimalist'],
  });
  expect(mockGenerate.mock.calls[0][0].user_profile.age).toBeUndefined();
});

it('retains the saved weather context and final style compromise in the dashboard result', async () => {
  const weather = { temperature: 91, condition: 'Cloudy', rawCondition: 'Partly Cloudy', source: 'estimated', fallback: true };
  const insight = 'Graphic hoodie has graphic detail, so this is a partial match for Minimalist.';
  mockGenerate.mockResolvedValue({ data: { id: 'look', name: 'Saved look', items, weather,
    outfitAnalysis: { styleSynergy: { insight } } } });
  const onOutfitGenerated = jest.fn();
  render(<SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={onOutfitGenerated} />);
  await waitFor(() => expect(onOutfitGenerated).toHaveBeenCalledWith(expect.objectContaining({
    weather, reasoning: insight, confidence: null,
  })));
});

it('shows a retryable failure when the saved style profile cannot be loaded', async () => {
  (fetch as jest.Mock).mockImplementation(async (url) => response(url === '/api/user/profile' ? {} : items, url !== '/api/user/profile'));
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  expect(await screen.findByRole('alert')).toHaveTextContent("We couldn't load your style profile");
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('does not post a profile that finishes loading after an account switch', async () => {
  let resolveProfile!: (value: Response) => void;
  (fetch as jest.Mock).mockImplementation((url) => url === '/api/user/profile'
    ? new Promise<Response>((resolve) => { resolveProfile = resolve; })
    : Promise.resolve(response(items)));
  const view = render(<SmartWeatherOutfitGenerator generationEnabled />);
  await waitFor(() => expect(resolveProfile).toBeDefined());
  mockUser = { ...mockUser, uid: 'switched-owner' };
  view.rerender(<SmartWeatherOutfitGenerator generationEnabled={false} />);
  await act(async () => resolveProfile(response(savedProfile)));
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('does not fetch or generate for an empty, loading or failed capsule', async () => {
  const view = render(<SmartWeatherOutfitGenerator generationEnabled={false} readinessMessage="Loading saved wardrobe…" />);
  await act(async () => undefined);
  view.rerender(<SmartWeatherOutfitGenerator generationEnabled={false} readinessMessage="We couldn't load your wardrobe." />);
  await act(async () => undefined);
  expect(mockGenerate).not.toHaveBeenCalled();
  expect(fetch).not.toHaveBeenCalled();
  expect(screen.getByText("We couldn't load your wardrobe.")).toBeInTheDocument();
});

it('rejects a newly empty wardrobe instead of POSTing generation', async () => {
  (fetch as jest.Mock).mockResolvedValue(response([]));
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  await screen.findByRole('alert');
  expect(mockGenerate).not.toHaveBeenCalled();
  expect(localStorage.getItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()))).toBeNull();
});

it('reports failed wardrobe reads rather than treating them as empty successful recommendations', async () => {
  (fetch as jest.Mock).mockResolvedValue(response({}, false));
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  expect(await screen.findByRole('alert')).toHaveTextContent("We couldn't load your wardrobe");
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('generates at most once through StrictMode, parent rerenders and remounts', async () => {
  const callback = jest.fn();
  const view = render(<StrictMode><SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} /></StrictMode>);
  await waitFor(() => expect(callback).toHaveBeenCalledTimes(1));
  view.rerender(<StrictMode><SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} /></StrictMode>);
  view.unmount();
  render(<SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} />);
  await screen.findByAltText('Plain tee');
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expect(callback).toHaveBeenCalledTimes(1);
});

it('keeps a failed attempt claimed across remounts and retries only after a click', async () => {
  mockGenerate.mockRejectedValueOnce(new Error('Generation unavailable'));
  const view = render(<SmartWeatherOutfitGenerator generationEnabled />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Generation unavailable');
  view.unmount();
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  await act(async () => undefined);
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button', { name: "Generate today's outfit" }));
  await screen.findByAltText('Plain tee');
  expect(mockGenerate).toHaveBeenCalledTimes(2);
});

it('does not cache or announce a successful empty server result', async () => {
  mockGenerate.mockResolvedValue({ data: { id: 'empty-look', items: [] } });
  const callback = jest.fn();
  render(<SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} />);
  expect(await screen.findByRole('alert')).toHaveTextContent("couldn't create a complete saved outfit");
  expect(callback).not.toHaveBeenCalled();
  expect(localStorage.getItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()))).toBeNull();
});

it('still shows an owned cached dress-and-shoes look when the current capsule is incomplete', async () => {
  const cached = { id: 'legacy-look', name: 'Saved dress', userId: mockUser.uid, confidence: .8,
    generatedAt: new Date().toISOString(), weather: mockWeather, reasoning: '',
    items: [{ id: 'dress', type: 'dress', name: 'Summer dress', imageUrl: 'https://example.test/dress.jpg' }, items[2]] };
  localStorage.setItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()), JSON.stringify(cached));
  render(<SmartWeatherOutfitGenerator generationEnabled={false} />);
  await screen.findByAltText('Summer dress');
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('does not display cached data without matching account ownership', async () => {
  localStorage.setItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()), JSON.stringify({
    id: 'foreign', userId: 'other-owner', name: 'Foreign look', items, confidence: .8,
  }));
  render(<SmartWeatherOutfitGenerator generationEnabled={false} />);
  await act(async () => undefined);
  expect(screen.queryByText('Plain tee')).not.toBeInTheDocument();
  expect(mockGenerate).not.toHaveBeenCalled();
});
